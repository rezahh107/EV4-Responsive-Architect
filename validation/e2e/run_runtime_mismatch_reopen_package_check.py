#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import runpy
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "contracts/runtime/runtime-mismatch-reopen-package.v1.schema.json"
VALID_DIR = ROOT / "validation/fixtures/runtime-mismatch/valid"
INVALID_DIR = ROOT / "validation/fixtures/runtime-mismatch/invalid"
COMPATIBILITY_VALIDATOR = ROOT / "validation/e2e/run_runtime_mismatch_prompt_5_compatibility_check.py"

EXPECTED_VALID = {"runtime_mismatch_reopen.valid.json"}
EXPECTED_INVALID = {
    "runtime_mismatch_missing_lineage.invalid.json",
    "runtime_mismatch_replacement_decision.invalid.json",
    "runtime_mismatch_unsupported_observation.invalid.json",
    "runtime_mismatch_boundary_upgrade.invalid.json",
}
EXPECTED_BOUNDARY_CLAIMS = {
    "submitted_evidence_created", "issue_8_mutated", "pilot_authorized",
    "production_ready", "release_ready", "live_render_validated",
    "export_json_validated", "accessibility_passed", "pixel_perfect",
    "responsive_correctness_validated",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_package(validator: Draft202012Validator, payload: dict) -> None:
    errors = sorted(
        validator.iter_errors(payload),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        raise ValueError(errors[0].message)

    lineage = payload["prior_decision_lineage"]
    if lineage["evidence_state"] != "reopen_required":
        raise ValueError("prior decision evidence_state must remain reopen_required")
    if lineage["consumer_stage"] != "runtime_evidence_conflict":
        raise ValueError("prior decision consumer_stage must identify runtime evidence conflict")
    if not lineage.get("evidence_refs"):
        raise ValueError("prior decision evidence_refs must contain at least one reference")
    if any(not isinstance(ref, str) or not ref.strip() for ref in lineage["evidence_refs"]):
        raise ValueError("prior decision evidence_refs must contain non-empty strings")

    authority = payload["authority_boundary"]
    if authority["responsive_may_observe"] is not True:
        raise ValueError("Responsive observation authority must remain enabled")
    if authority["responsive_may_replace_decision"] is not False:
        raise ValueError("Responsive decision replacement is forbidden")
    if authority["authoritative_redecision_required"] is not True:
        raise ValueError("authoritative redecision must remain required")

    if payload["requested_action"] != "reopen_for_authoritative_review":
        raise ValueError("only authoritative reopen review may be requested")

    evidence_references = payload.get("evidence_references", [])
    if not evidence_references:
        raise ValueError("evidence_references must contain at least one reference")
    for ref in evidence_references:
        if not isinstance(ref, dict):
            raise ValueError("evidence reference must be an object")
        if not ref.get("kind") or not ref.get("uri") or not ref.get("sha256"):
            raise ValueError("invalid evidence reference structure")

    boundary_claims = payload["boundary_claims"]
    if set(boundary_claims) != EXPECTED_BOUNDARY_CLAIMS:
        raise ValueError("boundary claim registry mismatch")
    upgraded = sorted(name for name, value in boundary_claims.items() if value is not False)
    if upgraded:
        raise ValueError(f"boundary claims must remain false: {', '.join(upgraded)}")


def assert_valid(label: str, validator: Draft202012Validator, payload: dict) -> None:
    try:
        validate_package(validator, payload)
    except ValueError as exc:
        raise AssertionError(f"{label}: {exc}") from exc


def assert_invalid(label: str, validator: Draft202012Validator, payload: dict) -> None:
    try:
        validate_package(validator, payload)
    except ValueError:
        return
    raise AssertionError(f"{label}: expected validation failure")


def run_self_test(validator: Draft202012Validator, valid_payload: dict) -> None:
    replacement = copy.deepcopy(valid_payload)
    replacement["authority_boundary"]["responsive_may_replace_decision"] = True
    assert_invalid("responsive replacement decision", validator, replacement)

    missing_lineage_evidence = copy.deepcopy(valid_payload)
    missing_lineage_evidence["prior_decision_lineage"]["evidence_refs"] = []
    assert_invalid("missing prior decision evidence refs", validator, missing_lineage_evidence)

    missing_evidence = copy.deepcopy(valid_payload)
    missing_evidence["evidence_references"] = []
    assert_invalid("missing evidence references", validator, missing_evidence)

    wrong_action = copy.deepcopy(valid_payload)
    wrong_action["requested_action"] = "continue_without_review"
    assert_invalid("unsupported requested action", validator, wrong_action)

    boundary_upgrade = copy.deepcopy(valid_payload)
    boundary_upgrade["boundary_claims"]["production_ready"] = True
    assert_invalid("boundary upgrade", validator, boundary_upgrade)


def main() -> None:
    schema = load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    valid_files = sorted(VALID_DIR.glob("*.valid.json"))
    if {path.name for path in valid_files} != EXPECTED_VALID:
        raise AssertionError("valid runtime mismatch fixture registry mismatch")

    invalid_files = sorted(INVALID_DIR.glob("*.invalid.json"))
    if {path.name for path in invalid_files} != EXPECTED_INVALID:
        raise AssertionError("invalid runtime mismatch fixture registry mismatch")

    for path in valid_files:
        assert_valid(path.name, validator, load(path))
    for path in invalid_files:
        assert_invalid(path.name, validator, load(path))

    run_self_test(validator, load(VALID_DIR / "runtime_mismatch_reopen.valid.json"))
    if not COMPATIBILITY_VALIDATOR.is_file():
        raise AssertionError("runtime mismatch to Prompt 5 compatibility validator is missing")
    runpy.run_path(str(COMPATIBILITY_VALIDATOR), run_name="__main__")
    print("Runtime mismatch reopen package validation passed")


if __name__ == "__main__":
    main()
