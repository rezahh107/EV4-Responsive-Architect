#!/usr/bin/env python3
"""Validate submitted packet Issue #8 reference consistency for RQ-0023."""
from __future__ import annotations

import copy
import json
import sys
import traceback
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BASE_PACKET = ROOT / "validation" / "fixtures" / "valid" / "evidence_intake_packet.valid.json"
CASE_DIR = ROOT / "validation" / "fixtures" / "invalid" / "rq0023"

REAL_ELIGIBLE_STATUSES = {"submitted", "validated"}
REAL_SHADOW_SCOPE = "real_shadow_mode_only"
ISSUE_8_NUMBER = 8
ISSUE_8_REFS = {
    "#8",
    "https://github.com/rezahh107/EV4-Responsive-Architect/issues/8",
    "https://github.com/rezahh107/EV4-Responsive-Architect/issues/8/",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    payload.pop("$schema_file", None)
    return payload


def real_eligibility_requested(packet: dict[str, Any]) -> bool:
    verdict = packet.get("intake_verdict")
    if not isinstance(verdict, dict):
        verdict = {}
    return (
        verdict.get("allowed_scope") == REAL_SHADOW_SCOPE
        or verdict.get("real_pilot_allowed_to_start") is True
        or (verdict.get("pilot_allowed_to_start") is True and verdict.get("sample_dry_run_allowed") is not True)
    )


def issue_ref_targets_issue_8(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    normalized = value.strip()
    return normalized in ISSUE_8_REFS


def validate_issue_reference_consistency(packet: dict[str, Any]) -> None:
    if not real_eligibility_requested(packet):
        return

    if packet.get("packet_origin") != "real_issue_submission":
        raise AssertionError("Issue #8 eligibility requires packet_origin=real_issue_submission")

    issue_reference = packet.get("issue_reference")
    if not isinstance(issue_reference, dict):
        raise AssertionError("Issue #8 eligibility requires structured issue_reference")

    if issue_reference.get("issue_number") != ISSUE_8_NUMBER:
        raise AssertionError("Issue #8 eligibility requires issue_reference.issue_number=8")

    if not issue_ref_targets_issue_8(issue_reference.get("issue_url_or_ref")):
        raise AssertionError("Issue #8 eligibility requires issue_reference.issue_url_or_ref must target Issue #8")

    if issue_reference.get("evidence_submission_status") not in REAL_ELIGIBLE_STATUSES:
        raise AssertionError("Issue #8 eligibility requires issue_reference.evidence_submission_status=submitted or validated")


def real_eligible_packet() -> dict[str, Any]:
    packet = load_json(BASE_PACKET)
    packet["packet_id"] = "SHP-RQ0023-ISSUE8-001"
    packet["packet_status"] = "submitted"
    packet["packet_origin"] = "real_issue_submission"
    packet["issue_reference"] = {
        "issue_number": 8,
        "issue_url_or_ref": "#8",
        "evidence_submission_status": "submitted",
    }
    packet["main_ev4_handoff"]["source_ref"] = "issues/8/main-ev4-handoff.md"
    packet["main_ev4_handoff"]["payload_identity_hash"] = "sha256-rq0023-issue8-handoff"
    packet["intake_verdict"]["sample_dry_run_allowed"] = False
    packet["intake_verdict"]["real_pilot_allowed_to_start"] = True
    packet["intake_verdict"]["allowed_scope"] = "real_shadow_mode_only"
    return packet


def merge_patch(target: dict[str, Any], patch: dict[str, Any]) -> None:
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            merge_patch(target[key], value)
        else:
            target[key] = value


def assert_rejects(case_path: Path) -> None:
    case = load_json(case_path)
    expected = case.get("expected_error")
    if not isinstance(expected, str) or not expected:
        raise AssertionError(f"{case_path} must carry expected_error")

    packet = copy.deepcopy(real_eligible_packet())
    patch = case.get("patch")
    if not isinstance(patch, dict):
        raise AssertionError(f"{case_path} must carry patch")
    merge_patch(packet, patch)

    try:
        validate_issue_reference_consistency(packet)
    except AssertionError as exc:
        if expected not in str(exc):
            raise AssertionError(f"{case_path.name} failed for wrong reason: {exc}") from exc
        return
    raise AssertionError(f"{case_path.name} unexpectedly passed")


def run_self_test() -> None:
    validate_issue_reference_consistency(real_eligible_packet())

    canonical = real_eligible_packet()
    canonical["issue_reference"]["issue_url_or_ref"] = "https://github.com/rezahh107/EV4-Responsive-Architect/issues/8"
    validate_issue_reference_consistency(canonical)

    case_paths = sorted(CASE_DIR.glob("*.invalid.json"))
    if len(case_paths) != 4:
        raise AssertionError(f"RQ-0023 requires exactly 4 invalid fixtures, found {len(case_paths)}")
    for case_path in case_paths:
        assert_rejects(case_path)


def main() -> int:
    try:
        run_self_test()
    except AssertionError as exc:
        print(f"Submitted packet issue-reference check failed: {exc}", file=sys.stderr)
        return 1
    except Exception:
        print("Submitted packet issue-reference check crashed unexpectedly:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1
    print("Submitted packet issue-reference check passed: eligibility is locked to Issue #8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
