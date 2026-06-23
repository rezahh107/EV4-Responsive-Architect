#!/usr/bin/env python3
"""Validate JSON Schema files and sample fixture payloads.

This is a v0.1 prototype. It intentionally validates structural correctness first:
- all schema files parse as JSON;
- all schema files are valid JSON Schemas according to jsonschema;
- fixture payloads under validation/fixtures/valid pass their referenced schema when `$schema_file` is provided;
- fixture payloads under validation/fixtures/invalid fail their referenced schema when `$schema_file` is provided.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = ROOT / "schemas"
FIXTURES_DIR = ROOT / "validation" / "fixtures"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_schema_files() -> dict[str, Any]:
    schemas: dict[str, Any] = {}
    for schema_path in sorted(SCHEMAS_DIR.glob("*.schema.json")):
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)
        schemas[schema_path.name] = schema
    if not schemas:
        raise RuntimeError("No schema files found.")
    return schemas


def validate_fixture(path: Path, schemas: dict[str, Any], should_pass: bool) -> None:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise RuntimeError(f"Fixture {path} must be a JSON object")
    schema_file = payload.pop("$schema_file", None)
    if not schema_file:
        raise RuntimeError(f"Fixture {path} is missing $schema_file")
    if schema_file not in schemas:
        raise RuntimeError(f"Fixture {path} references missing schema {schema_file}")
    validator = Draft202012Validator(schemas[schema_file])
    errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.path))
    if should_pass and errors:
        raise AssertionError(f"Expected {path} to pass, got: {errors[0].message}")
    if not should_pass and not errors:
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
    except Exception as exc:
        print(f"schema validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"schema validation passed: {len(schemas)} schema(s) checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
