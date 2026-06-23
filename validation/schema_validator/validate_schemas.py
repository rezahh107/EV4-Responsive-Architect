#!/usr/bin/env python3
"""Validate EV4 Responsive Architect JSON schemas and fixtures.

The validator deliberately has two layers:

1. JSON Schema validation:
   - every schema file parses as JSON;
   - every schema file is a valid Draft 2020-12 schema;
   - valid fixtures must pass their referenced schema;
   - invalid fixtures must fail either schema validation or semantic validation.

2. v0.1 semantic checks:
   - schema files should reject unknown top-level fields with additionalProperties=false;
   - payloads should expose a schema discriminator;
   - CSS selector safety payloads must not use global or broad Elementor selectors;
   - CSS selector payloads must include the project root class and target node class in the selector.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = ROOT / "schemas"
FIXTURES_DIR = ROOT / "validation" / "fixtures"

FORBIDDEN_ELEMENTOR_CLASSES = (
    ".elementor-widget-container",
    ".elementor-section",
    ".elementor-container",
)


class SemanticValidationError(AssertionError):
    """Raised when a payload passes JSON Schema but violates EV4 semantic gates."""


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_schema_files() -> dict[str, Any]:
    schemas: dict[str, Any] = {}
    for schema_path in sorted(SCHEMAS_DIR.glob("*.schema.json")):
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)
        if schema.get("type") == "object" and schema.get("additionalProperties") is not False:
            raise SemanticValidationError(f"{schema_path.name} must set additionalProperties=false")
        required = schema.get("required", [])
        if schema.get("type") == "object" and "schema" not in required:
            raise SemanticValidationError(f"{schema_path.name} must require schema discriminator")
        schemas[schema_path.name] = schema
    if not schemas:
        raise RuntimeError("No schema files found.")
    return schemas


def normalize_selector(selector: str) -> str:
    """Normalize selector whitespace without changing selector semantics."""

    return re.sub(r"\s+", " ", selector.strip())


def strip_attribute_selectors(selector: str) -> str:
    """Remove attribute selectors before token checks.

    Attribute values may legally contain characters such as # or *:
    [href="#section"], [class*="card"]. Those must not be interpreted as
    ID selectors or universal selectors by the coarse semantic safety gate.
    """

    return re.sub(r"\[[^\]]*\]", "", selector)


def semantic_validate_css_selector(payload: dict[str, Any]) -> None:
    if payload.get("schema") != "ev4-responsive-css-selector-safety@1.0.0":
        return

    selector = payload.get("selector", "")
    root_class = payload.get("project_root_class", "")
    target_class = payload.get("target_node_class", "")

    normalized = normalize_selector(selector)
    required_prefix = f".{root_class} .{target_class}"
    if not normalized.startswith(required_prefix):
        raise SemanticValidationError(
            "CSS selector must start with .<project_root_class> .<target_node_class>"
        )

    no_attributes = strip_attribute_selectors(normalized)

    if re.search(r"(?<![\w.-])(html|body)(?![\w-])", no_attributes):
        raise SemanticValidationError("CSS selector uses forbidden tag selector: html or body")
    if "*" in no_attributes:
        raise SemanticValidationError("CSS selector uses forbidden universal selector: *")
    if "#" in no_attributes:
        raise SemanticValidationError("CSS selector uses forbidden ID selector: #")

    for class_token in FORBIDDEN_ELEMENTOR_CLASSES:
        if class_token in no_attributes:
            raise SemanticValidationError(f"CSS selector uses forbidden Elementor class: {class_token}")

    if payload.get("uses_important") and not payload.get("important_justification"):
        raise SemanticValidationError("!important requires important_justification")

    if payload.get("breakpoint_source") in {"user_declaration", "assumed_default_with_unverified_label"}:
        if payload.get("production_ready_claim_allowed") is not False:
            raise SemanticValidationError(
                "Unverified breakpoint source must not allow production-ready claim"
            )


def semantic_validate_payload(payload: dict[str, Any]) -> None:
    semantic_validate_css_selector(payload)


def validate_fixture(path: Path, schemas: dict[str, Any], should_pass: bool) -> None:
    original_payload = load_json(path)
    if not isinstance(original_payload, dict):
        raise RuntimeError(f"Fixture {path} must be a JSON object")

    payload = dict(original_payload)
    schema_file = payload.pop("$schema_file", None)
    if not schema_file:
        raise RuntimeError(f"Fixture {path} is missing $schema_file")
    if schema_file not in schemas:
        raise RuntimeError(f"Fixture {path} references missing schema {schema_file}")

    validator = Draft202012Validator(schemas[schema_file])
    errors = sorted(validator.iter_errors(payload), key=lambda e: [str(p) for p in e.path])

    semantic_error: Exception | None = None
    if not errors:
        try:
            semantic_validate_payload(payload)
        except Exception as exc:  # noqa: BLE001 - report semantic failures uniformly
            semantic_error = exc

    failed = bool(errors) or semantic_error is not None

    if should_pass and failed:
        if errors:
            raise AssertionError(f"Expected {path} to pass, got schema error: {errors[0].message}")
        raise AssertionError(f"Expected {path} to pass, got semantic error: {semantic_error}")

    if not should_pass and not failed:
        raise AssertionError(f"Expected {path} to fail, but it passed")


def validate_fixtures(schemas: dict[str, Any]) -> None:
    valid_dir = FIXTURES_DIR / "valid"
    invalid_dir = FIXTURES_DIR / "invalid"
    for path in sorted(valid_dir.glob("*.json")) if valid_dir.exists() else []:
        validate_fixture(path, schemas, should_pass=True)
    for path in sorted(invalid_dir.glob("*.json")) if invalid_dir.exists() else []:
        validate_fixture(path, schemas, should_pass=False)


def main() -> int:
    try:
        schemas = validate_schema_files()
        validate_fixtures(schemas)
    except Exception as exc:  # noqa: BLE001 - CLI should print compact failure
        print(f"schema validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"schema validation passed: {len(schemas)} schema(s) checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
