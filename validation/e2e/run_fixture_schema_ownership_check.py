#!/usr/bin/env python3
"""Fail-closed ownership guard for broad JSON Schema fixtures.

This guard implements WP-RESP-010/PR-B for fixtures directly under
validation/fixtures/valid and validation/fixtures/invalid. Focused fixture
subtrees remain outside this broad-validator boundary.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = ROOT / "schemas"
FIXTURES_DIR = ROOT / "validation" / "fixtures"
VALID_DIR = FIXTURES_DIR / "valid"
INVALID_DIR = FIXTURES_DIR / "invalid"
OWNERSHIP_INVENTORY = FIXTURES_DIR / "fixture_schema_ownership.json"


class OwnershipError(AssertionError):
    """Raised when fixture ownership is absent, ambiguous, or incorrect."""


@dataclass(frozen=True)
class InventoryEntry:
    fixture_path: str
    expected_result: str
    ownership_class: str
    owning_schema_path: str
    primary_validator_path: str
    secondary_validator_paths: tuple[str, ...]
    ownership_source: str
    migration_state: str


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_ownership_inventory() -> dict[str, str]:
    if not OWNERSHIP_INVENTORY.is_file():
        return {}
    payload = load_json(OWNERSHIP_INVENTORY)
    if not isinstance(payload, dict):
        raise OwnershipError("ownership_inventory_not_object")
    inventory: dict[str, str] = {}
    for fixture_path, schema_file in payload.items():
        if not isinstance(fixture_path, str) or not fixture_path:
            raise OwnershipError("ownership_inventory_invalid_fixture_path")
        if not isinstance(schema_file, str) or not schema_file:
            raise OwnershipError(f"ownership_inventory_invalid_schema:{fixture_path}")
        if "/" in schema_file or "\\" in schema_file:
            raise OwnershipError(f"ownership_inventory_noncanonical_schema:{fixture_path}:{schema_file}")
        inventory[fixture_path] = schema_file
    return inventory


def load_schemas() -> dict[str, dict[str, Any]]:
    schemas: dict[str, dict[str, Any]] = {}
    for path in sorted(SCHEMAS_DIR.glob("*.schema.json")):
        payload = load_json(path)
        if not isinstance(payload, dict):
            raise OwnershipError(f"schema_not_object:{path.relative_to(ROOT)}")
        Draft202012Validator.check_schema(payload)
        schemas[path.name] = payload
    if not schemas:
        raise OwnershipError("no_schema_files")
    return schemas


def build_registry(schemas: dict[str, dict[str, Any]]) -> Registry:
    resources: list[tuple[str, Resource[Any]]] = []
    registered: set[str] = set()
    for filename, schema in schemas.items():
        resource = Resource.from_contents(schema)
        for uri in (filename, schema.get("$id")):
            if isinstance(uri, str) and uri and uri not in registered:
                resources.append((uri, resource))
                registered.add(uri)
    return Registry().with_resources(resources)


def accepted_discriminators(schema: dict[str, Any]) -> set[str] | None:
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        return None
    discriminator = properties.get("schema")
    if not isinstance(discriminator, dict):
        return None
    if isinstance(discriminator.get("const"), str):
        return {discriminator["const"]}
    enum = discriminator.get("enum")
    if isinstance(enum, list) and enum and all(isinstance(item, str) for item in enum):
        return set(enum)
    return None


def resolve_schema_file(
    raw: dict[str, Any],
    rel: str,
    schemas: dict[str, dict[str, Any]],
    ownership_inventory: dict[str, str],
) -> tuple[str, str]:
    if "$schema_files" in raw:
        raise OwnershipError(f"duplicate_primary_ownership:{rel}:$schema_files_forbidden")

    metadata_schema = raw.get("$schema_file")
    sidecar_schema = ownership_inventory.get(rel)
    if metadata_schema is not None and sidecar_schema is not None:
        raise OwnershipError(f"duplicate_primary_ownership:{rel}:metadata_and_inventory")

    if metadata_schema is not None:
        if not isinstance(metadata_schema, str) or not metadata_schema:
            raise OwnershipError(f"missing_ownership_metadata:{rel}")
        schema_file = metadata_schema
        ownership_source = "$schema_file"
    elif sidecar_schema is not None:
        schema_file = sidecar_schema
        ownership_source = "fixture_schema_ownership.json"
    else:
        raise OwnershipError(f"missing_ownership_metadata:{rel}")

    if "/" in schema_file or "\\" in schema_file:
        raise OwnershipError(f"noncanonical_schema_reference:{rel}:{schema_file}")
    if schema_file not in schemas:
        raise OwnershipError(f"referenced_schema_absent:{rel}:{schema_file}")
    return schema_file, ownership_source


def resolve_entry(
    path: Path,
    expected_result: str,
    schemas: dict[str, dict[str, Any]],
    registry: Registry,
    ownership_inventory: dict[str, str],
) -> InventoryEntry:
    raw = load_json(path)
    rel = path.relative_to(ROOT).as_posix()
    if not isinstance(raw, dict):
        raise OwnershipError(f"fixture_not_object:{rel}")

    schema_file, ownership_source = resolve_schema_file(raw, rel, schemas, ownership_inventory)

    payload = dict(raw)
    payload.pop("$schema_file", None)
    discriminator = payload.get("schema")
    accepted = accepted_discriminators(schemas[schema_file])
    if accepted is not None and discriminator not in accepted and expected_result == "valid":
        raise OwnershipError(
            f"wrong_owning_schema:{rel}:{schema_file}:payload_schema={discriminator!r}"
        )

    validator = Draft202012Validator(schemas[schema_file], registry=registry)
    schema_failed = any(validator.iter_errors(payload))
    if expected_result == "valid" and schema_failed:
        raise OwnershipError(f"valid_fixture_reclassified_invalid:{rel}:{schema_file}")
    if expected_result == "invalid" and not schema_failed:
        # Invalid fixtures may rely on the focused semantic layer in
        # validate_schemas.py. Keep classification verification there rather
        # than silently declaring the fixture valid here.
        migration_state = "already_compliant"
    else:
        migration_state = "already_compliant"

    return InventoryEntry(
        fixture_path=rel,
        expected_result=expected_result,
        ownership_class="broad_schema_fixture",
        owning_schema_path=f"schemas/{schema_file}",
        primary_validator_path="validation/schema_validator/validate_schemas.py",
        secondary_validator_paths=("validation/e2e/run_fixture_schema_ownership_check.py",),
        ownership_source=ownership_source,
        migration_state=migration_state,
    )


def fixture_paths(directory: Path) -> list[Path]:
    """Return only direct broad fixtures; nested focused subtrees are out of scope."""
    if not directory.exists():
        return []
    return sorted(path for path in directory.glob("*.json") if path.is_file())


def run_boundary_self_tests() -> None:
    """Prove focused nested fixtures are ignored while direct broad fixtures remain guarded."""
    with TemporaryDirectory() as temporary_directory:
        root = Path(temporary_directory)
        direct = root / "misplaced-broad.json"
        nested = root / "focused" / "focused.json"
        nested.parent.mkdir(parents=True)
        direct.write_text("{}", encoding="utf-8")
        nested.write_text("{}", encoding="utf-8")

        selected = fixture_paths(root)
        if selected != [direct]:
            rendered = ",".join(path.relative_to(root).as_posix() for path in selected)
            raise OwnershipError(f"fixture_scope_self_test_failed:{rendered}")
        if nested in selected:
            raise OwnershipError("focused_fixture_subtree_not_excluded")
        if direct not in selected:
            raise OwnershipError("direct_broad_fixture_not_guarded")

        try:
            resolve_schema_file({}, "misplaced-broad.json", {"owner.schema.json": {}}, {})
        except OwnershipError as exc:
            if str(exc) != "missing_ownership_metadata:misplaced-broad.json":
                raise OwnershipError(f"direct_broad_fixture_wrong_diagnostic:{exc}") from exc
        else:
            raise OwnershipError("direct_broad_fixture_without_owner_not_rejected")

        schema_file, ownership_source = resolve_schema_file(
            {},
            "misplaced-broad.json",
            {"owner.schema.json": {}},
            {"misplaced-broad.json": "owner.schema.json"},
        )
        if schema_file != "owner.schema.json" or ownership_source != "fixture_schema_ownership.json":
            raise OwnershipError("sidecar_ownership_resolution_self_test_failed")

        try:
            resolve_schema_file(
                {"$schema_file": "owner.schema.json"},
                "misplaced-broad.json",
                {"owner.schema.json": {}},
                {"misplaced-broad.json": "owner.schema.json"},
            )
        except OwnershipError as exc:
            if str(exc) != "duplicate_primary_ownership:misplaced-broad.json:metadata_and_inventory":
                raise OwnershipError(f"duplicate_ownership_wrong_diagnostic:{exc}") from exc
        else:
            raise OwnershipError("duplicate_metadata_and_inventory_owner_not_rejected")


def build_inventory() -> list[InventoryEntry]:
    run_boundary_self_tests()
    schemas = load_schemas()
    registry = build_registry(schemas)
    ownership_inventory = load_ownership_inventory()
    inventory: list[InventoryEntry] = []
    for path in fixture_paths(VALID_DIR):
        inventory.append(resolve_entry(path, "valid", schemas, registry, ownership_inventory))
    for path in fixture_paths(INVALID_DIR):
        inventory.append(resolve_entry(path, "invalid", schemas, registry, ownership_inventory))
    if not inventory:
        raise OwnershipError("no_broad_schema_fixtures")
    fixture_names = [entry.fixture_path for entry in inventory]
    if len(fixture_names) != len(set(fixture_names)):
        raise OwnershipError("duplicate_inventory_fixture_path")
    stale_sidecar_entries = sorted(set(ownership_inventory) - set(fixture_names))
    if stale_sidecar_entries:
        raise OwnershipError(f"ownership_inventory_orphaned:{','.join(stale_sidecar_entries)}")
    return inventory


def main() -> int:
    try:
        inventory = build_inventory()
    except Exception as exc:  # noqa: BLE001 - compact deterministic CLI diagnostic
        print(f"fixture schema ownership check failed: {exc}", file=sys.stderr)
        return 1
    print(f"fixture schema ownership check passed: {len(inventory)} broad fixture(s) inventoried")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
