#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "contracts/project-gate/prompt-5-routing-envelope.v1.schema.json"
VALID_DIR = ROOT / "validation/fixtures/prompt05/valid"
INVALID_DIR = ROOT / "validation/fixtures/prompt05/invalid"

EXPECTED_INVALID = {
    "prompt_5_routing_missing_lineage.invalid.json",
    "prompt_5_routing_unsupported_target.invalid.json",
    "prompt_5_routing_authority_substitution.invalid.json",
    "prompt_5_routing_boundary_upgrade.invalid.json",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def errors(validator: Draft202012Validator, payload: dict) -> list:
    return sorted(validator.iter_errors(payload), key=lambda error: list(error.absolute_path))


def assert_valid(label: str, validator: Draft202012Validator, payload: dict) -> None:
    found = errors(validator, payload)
    if found:
        raise AssertionError(f"{label}: {found[0].message}")


def assert_invalid(label: str, validator: Draft202012Validator, payload: dict) -> None:
    if not errors(validator, payload):
        raise AssertionError(f"{label}: expected validation failure")


def run_self_test(validator: Draft202012Validator, valid_route: dict) -> None:
    route_with_diagnostic = copy.deepcopy(valid_route)
    route_with_diagnostic["route"]["diagnostic_codes"] = ["P5R-UNEXPECTED"]
    assert_invalid("route with diagnostic", validator, route_with_diagnostic)

    reject_without_diagnostic = copy.deepcopy(valid_route)
    reject_without_diagnostic["route"] = {
        "target": "ev4-project-gate",
        "decision": "reject",
        "transport_eligible": False,
        "diagnostic_codes": [],
    }
    assert_invalid("reject without diagnostic", validator, reject_without_diagnostic)


def main() -> None:
    schema = load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    valid_files = sorted(VALID_DIR.glob("*.valid.json"))
    if {path.name for path in valid_files} != {
        "prompt_5_routing_route.valid.json",
        "prompt_5_routing_reject.valid.json",
    }:
        raise AssertionError("valid Prompt 5 routing fixture registry mismatch")

    invalid_files = sorted(INVALID_DIR.glob("*.invalid.json"))
    if {path.name for path in invalid_files} != EXPECTED_INVALID:
        raise AssertionError("invalid Prompt 5 routing fixture registry mismatch")

    for path in valid_files:
        assert_valid(path.name, validator, load(path))
    for path in invalid_files:
        assert_invalid(path.name, validator, load(path))

    run_self_test(validator, load(VALID_DIR / "prompt_5_routing_route.valid.json"))
    print("Prompt 5 routing envelope validation passed")


if __name__ == "__main__":
    main()
