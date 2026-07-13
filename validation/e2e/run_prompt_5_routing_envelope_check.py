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

EXPECTED_VALID = {
    "prompt_5_routing_route.valid.json",
    "prompt_5_routing_reject.valid.json",
}
EXPECTED_INVALID = {
    "prompt_5_routing_missing_lineage.invalid.json",
    "prompt_5_routing_unsupported_target.invalid.json",
    "prompt_5_routing_authority_substitution.invalid.json",
    "prompt_5_routing_boundary_upgrade.invalid.json",
}
EXPECTED_BOUNDARY_CLAIMS = {
    "submitted_evidence_created",
    "issue_8_mutated",
    "pilot_authorized",
    "production_ready",
    "release_ready",
    "live_render_validated",
    "export_json_validated",
    "accessibility_passed",
    "pixel_perfect",
    "responsive_correctness_validated",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_errors(validator: Draft202012Validator, payload: dict) -> list:
    return sorted(
        validator.iter_errors(payload),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )


def validate_envelope(validator: Draft202012Validator, payload: dict) -> None:
    found = schema_errors(validator, payload)
    if found:
        raise ValueError(found[0].message)

    route = payload["route"]
    decision = route["decision"]
    diagnostics = route["diagnostic_codes"]
    if decision == "route":
        if route["transport_eligible"] is not True:
            raise ValueError("route decision requires transport_eligible=true")
        if diagnostics != []:
            raise ValueError("route decision must not contain diagnostic codes")
    elif decision == "reject":
        if route["transport_eligible"] is not False:
            raise ValueError("reject decision requires transport_eligible=false")
        if not diagnostics:
            raise ValueError("reject decision requires at least one diagnostic code")
    else:
        raise ValueError(f"unsupported decision: {decision}")

    authority = payload["authority"]
    if authority["routing_decision_owner"] != "responsive":
        raise ValueError("routing decision owner must remain responsive")
    if authority["transport_execution_owner"] != "ev4-project-gate":
        raise ValueError("transport execution owner must remain ev4-project-gate")
    if authority["responsive_executes_transport"] is not False:
        raise ValueError("Responsive transport execution is forbidden")
    if authority["responsive_substitutes_project_gate_decision"] is not False:
        raise ValueError("Project Gate decision substitution is forbidden")

    boundary_claims = payload["boundary_claims"]
    if set(boundary_claims) != EXPECTED_BOUNDARY_CLAIMS:
        raise ValueError("boundary claim registry mismatch")
    upgraded = sorted(name for name, value in boundary_claims.items() if value is not False)
    if upgraded:
        raise ValueError(f"boundary claims must remain false: {', '.join(upgraded)}")


def assert_valid(label: str, validator: Draft202012Validator, payload: dict) -> None:
    try:
        validate_envelope(validator, payload)
    except ValueError as exc:
        raise AssertionError(f"{label}: {exc}") from exc


def assert_invalid(label: str, validator: Draft202012Validator, payload: dict) -> None:
    try:
        validate_envelope(validator, payload)
    except ValueError:
        return
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

    authority_substitution = copy.deepcopy(valid_route)
    authority_substitution["authority"]["responsive_substitutes_project_gate_decision"] = True
    assert_invalid("authority substitution", validator, authority_substitution)

    boundary_upgrade = copy.deepcopy(valid_route)
    boundary_upgrade["boundary_claims"]["responsive_correctness_validated"] = True
    assert_invalid("boundary upgrade", validator, boundary_upgrade)


def main() -> None:
    schema = load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    valid_files = sorted(VALID_DIR.glob("*.valid.json"))
    if {path.name for path in valid_files} != EXPECTED_VALID:
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
