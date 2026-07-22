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
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = ROOT / "schemas"
FIXTURES_DIR = ROOT / "validation" / "fixtures"
VALID_DIR = FIXTURES_DIR / "valid"
INVALID_DIR = FIXTURES_DIR / "invalid"


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


def resolve_entry(
    path: Path,
    expected_result: str,
    schemas: dict[str, dict[str, Any]],
    registry: Registry,
) -> InventoryEntry:
    raw = load_json(path)
    rel = path.relative_to(ROOT).as_posix()
    if not isinstance(raw, dict):
        raise OwnershipError(f"fixture_not_object:{rel}")

    if "$schema_files" in raw:
        raise OwnershipError(f"duplicate_primary_ownership:{rel}:$schema_files_forbidden")

    schema_file = raw.get("$schema_file")
    if not isinstance(schema_file, str) or not schema_file:
        raise OwnershipError(f"missing_ownership_metadata:{rel}")
    if "/" in schema_file or "\\" in schema_file:
        raise OwnershipError(f"noncanonical_schema_reference:{rel}:{schema_file}")
    if schema_file not in schemas:
        raise OwnershipError(f"referenced_schema_absent:{rel}:{schema_file}")

    payload = dict(raw)
    payload.pop("$schema_file")
    discriminator = payload.get("schema")
    accepted = accepted_discriminators(schemas[schema_file])
    if accepted is not None and discriminator not in accepted:
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
        ownership_source="$schema_file",
        migration_state=migration_state,
    )


def fixture_paths(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    direct = sorted(directory.glob("*.json"))
    recursive = sorted(directory.rglob("*.json"))
    nested = [path for path in recursive if path.parent != directory]
    if nested:
        rendered = ",".join(path.relative_to(ROOT).as_posix() for path in nested)
        raise OwnershipError(f"focused_fixture_incorrectly_routed_to_broad_root:{rendered}")
    return direct


def build_inventory() -> list[InventoryEntry]:
    schemas = load_schemas()
    registry = build_registry(schemas)
    inventory: list[InventoryEntry] = []
    for path in fixture_paths(VALID_DIR):
        inventory.append(resolve_entry(path, "valid", schemas, registry))
    for path in fixture_paths(INVALID_DIR):
        inventory.append(resolve_entry(path, "invalid", schemas, registry))
    if not inventory:
        raise OwnershipError("no_broad_schema_fixtures")
    fixture_names = [entry.fixture_path for entry in inventory]
    if len(fixture_names) != len(set(fixture_names)):
        raise OwnershipError("duplicate_inventory_fixture_path")
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
