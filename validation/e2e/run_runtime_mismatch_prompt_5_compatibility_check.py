#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "contracts/compatibility/runtime-mismatch-prompt-5-routing-compatibility.v1.schema.json"
VALID_PATH = ROOT / "validation/fixtures/compatibility/runtime-mismatch-prompt5/valid/runtime_mismatch_prompt5_compatibility.valid.json"
INVALID_DIR = ROOT / "validation/fixtures/compatibility/runtime-mismatch-prompt5/invalid"
EXPECTED_INVALID = {"runtime_mismatch_prompt5_missing_lineage.invalid.json"}
EXPECTED_BOUNDARY_CLAIMS = {
    "submitted_evidence_created", "issue_8_mutated", "pilot_authorized",
    "production_ready", "release_ready", "live_render_validated",
    "export_json_validated", "accessibility_passed", "pixel_perfect",
    "responsive_correctness_validated",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_payload(validator: Draft202012Validator, payload: dict) -> None:
    errors = sorted(validator.iter_errors(payload), key=lambda e: tuple(map(str, e.absolute_path)))
    if errors:
        raise ValueError(errors[0].message)
    route = payload["routing_compatibility"]
    if route["reopen_requested_action"] != "reopen_for_authoritative_review":
        raise ValueError("unsupported reopen action")
    if route["prompt_5_decision"] != "route" or route["transport_eligible"] is not True:
        raise ValueError("reopen request must map to an eligible Prompt 5 route")
    if route["diagnostic_codes"] != []:
        raise ValueError("eligible route must not carry rejection diagnostics")
    authority = payload["authority_boundary"]
    if authority["kernel_decision_owner"] != "ev4-decision-kernel":
        raise ValueError("Kernel authority substitution is forbidden")
    if authority["transport_execution_owner"] != "ev4-project-gate":
        raise ValueError("Project Gate must remain transport owner")
    if authority["responsive_may_replace_decision"] or authority["responsive_executes_transport"]:
        raise ValueError("Responsive authority escalation is forbidden")
    claims = payload["boundary_claims"]
    if set(claims) != EXPECTED_BOUNDARY_CLAIMS:
        raise ValueError("boundary claim registry mismatch")
    if any(value is not False for value in claims.values()):
        raise ValueError("all evidence and readiness boundary claims must remain false")


def assert_invalid(label: str, validator: Draft202012Validator, payload: dict) -> None:
    try:
        validate_payload(validator, payload)
    except ValueError:
        return
    raise AssertionError(f"{label}: expected validation failure")


def run_self_tests(validator: Draft202012Validator, valid: dict) -> None:
    cases = []
    lineage = copy.deepcopy(valid)
    del lineage["shared_lineage"]["decision_id"]
    cases.append(("missing lineage", lineage))

    action = copy.deepcopy(valid)
    action["routing_compatibility"]["reopen_requested_action"] = "continue_without_review"
    cases.append(("unsupported action", action))

    diagnostics = copy.deepcopy(valid)
    diagnostics["routing_compatibility"]["diagnostic_codes"] = ["P5R-DIVERGENT"]
    cases.append(("diagnostic mismatch", diagnostics))

    authority = copy.deepcopy(valid)
    authority["authority_boundary"]["responsive_may_replace_decision"] = True
    cases.append(("authority substitution", authority))

    version = copy.deepcopy(valid)
    version["dependencies"]["prompt_5_routing"]["schema_version"] = "prompt-5-routing-envelope.v2"
    cases.append(("schema version drift", version))

    boundary = copy.deepcopy(valid)
    boundary["boundary_claims"]["responsive_correctness_validated"] = True
    cases.append(("boundary upgrade", boundary))

    for label, payload in cases:
        assert_invalid(label, validator, payload)


def main() -> None:
    schema = load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    valid = load(VALID_PATH)
    validate_payload(validator, valid)

    invalid_files = sorted(INVALID_DIR.glob("*.invalid.json"))
    if {path.name for path in invalid_files} != EXPECTED_INVALID:
        raise AssertionError("invalid compatibility fixture registry mismatch")
    for path in invalid_files:
        assert_invalid(path.name, validator, load(path))

    run_self_tests(validator, valid)
    print("Runtime mismatch to Prompt 5 compatibility validation passed")


if __name__ == "__main__":
    main()
