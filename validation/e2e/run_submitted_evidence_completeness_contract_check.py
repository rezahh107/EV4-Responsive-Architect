#!/usr/bin/env python3
"""Validate submitted-mode evidence-completeness guardrails.

This check is intentionally local and declarative. It derives temporary
contract packets from the existing valid fixture to prove submitted-mode
readiness cannot advance when evidence_complete_definition and intake_verdict
contradict each other.

It does not create submitted evidence, inspect Issue #8 attachments, or run the
real pilot.
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from validation.e2e.run_evidence_intake_check import load_json, validate_packet  # noqa: E402
from validation.e2e.run_pilot_readiness_check import build_readiness, validate_readiness_schema  # noqa: E402

BASE_FIXTURE = ROOT / "validation" / "fixtures" / "valid" / "evidence_intake_packet.valid.json"


def real_issue_packet_from_fixture() -> dict[str, Any]:
    """Build a temporary real_issue_submission contract packet.

    The derived packet is self-test data only. It is not repo-stored real
    submitted evidence and must not be used to start the real pilot.
    """
    packet = copy.deepcopy(load_json(BASE_FIXTURE))
    packet["packet_id"] = "SHP-INTAKE-REAL-ISSUE-COMPLETENESS-CONTRACT-001"
    packet["packet_status"] = "submitted"
    packet["packet_origin"] = "real_issue_submission"
    packet["issue_reference"] = {
        "issue_number": 8,
        "issue_url_or_ref": "#8",
        "evidence_submission_status": "submitted",
    }
    packet["main_ev4_handoff"]["payload_identity_hash"] = "sha256-contract-real-issue-completeness-guard"
    packet["intake_verdict"]["sample_dry_run_allowed"] = False
    packet["intake_verdict"]["status"] = "allowed"
    packet["intake_verdict"]["pilot_allowed_to_start"] = True
    packet["intake_verdict"]["real_pilot_allowed_to_start"] = True
    packet["intake_verdict"]["allowed_scope"] = "real_shadow_mode_only"
    packet["intake_verdict"]["missing_required_items"] = []
    packet["intake_verdict"]["blocker_conflicts"] = []
    return packet


def write_temp_packet(packet: dict[str, Any], tmp_dir: Path, name: str) -> Path:
    path = tmp_dir / name
    path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def assert_complete_definition_can_reach_shadow_mode(tmp_dir: Path) -> None:
    packet = real_issue_packet_from_fixture()
    incomplete = [key for key, value in packet["evidence_complete_definition"].items() if value is not True]
    if incomplete:
        raise AssertionError(f"positive completeness contract fixture is unexpectedly incomplete: {incomplete}")

    path = write_temp_packet(packet, tmp_dir, "real_issue_completeness_complete.json")
    validated = validate_packet(path, run_full_schema_validator=False, submitted_mode=True)
    report = build_readiness(validated)
    validate_readiness_schema(report)

    authorization = report["pilot_start_authorization"]
    if authorization["authorized"] is not True:
        raise AssertionError("complete submitted evidence should allow only shadow-mode readiness when other gates pass")
    if authorization["authorization_scope"] not in {"shadow_mode_only", "shadow_mode_only_with_visible_flags"}:
        raise AssertionError("complete submitted evidence must not authorize beyond shadow mode")


def assert_incomplete_definition_blocks_allowed_verdict(tmp_dir: Path) -> None:
    packet = real_issue_packet_from_fixture()
    packet["evidence_complete_definition"]["tablet_screenshot_supplied"] = False
    path = write_temp_packet(packet, tmp_dir, "real_issue_completeness_inconsistent_allowed.json")

    try:
        validate_packet(path, run_full_schema_validator=False, submitted_mode=True)
    except AssertionError as exc:
        message = str(exc)
        if "pilot cannot start while completion checks are false" not in message:
            raise AssertionError(f"incomplete completeness failed for the wrong reason: {message}") from exc
        if "tablet_screenshot_supplied" not in message:
            raise AssertionError("completeness failure must identify the incomplete evidence field") from exc
        return
    raise AssertionError("submitted-mode packet with incomplete evidence_complete_definition must not validate as allowed")


def assert_blocked_incomplete_definition_remains_not_authorized(tmp_dir: Path) -> None:
    packet = real_issue_packet_from_fixture()
    packet["evidence_complete_definition"]["mobile_screenshot_supplied"] = False
    packet["intake_verdict"]["status"] = "blocked"
    packet["intake_verdict"]["pilot_allowed_to_start"] = False
    packet["intake_verdict"]["real_pilot_allowed_to_start"] = False
    packet["intake_verdict"]["allowed_scope"] = "not_allowed"
    packet["intake_verdict"]["missing_required_items"] = ["mobile_screenshot_supplied"]
    path = write_temp_packet(packet, tmp_dir, "real_issue_completeness_blocked.json")

    validated = validate_packet(path, run_full_schema_validator=False, submitted_mode=True)
    report = build_readiness(validated)
    validate_readiness_schema(report)

    if report["readiness_status"] != "blocked_missing_evidence":
        raise AssertionError("blocked incomplete evidence must map to blocked_missing_evidence")
    authorization = report["pilot_start_authorization"]
    if authorization["authorized"] is not False or authorization["authorization_scope"] != "not_authorized":
        raise AssertionError("blocked incomplete evidence must not authorize pilot start")


def assert_completeness_is_not_validation_evidence(tmp_dir: Path) -> None:
    packet = real_issue_packet_from_fixture()
    path = write_temp_packet(packet, tmp_dir, "real_issue_completeness_boundary.json")
    validated = validate_packet(path, run_full_schema_validator=False, submitted_mode=True)
    report = build_readiness(validated)

    for key in (
        "live_elementor_render_validated",
        "export_json_validated",
        "playwright_visual_regression_validated",
        "accessibility_pass_claimed",
        "production_ready_claimed",
    ):
        if report["validation_boundary"][key]["value"] is not False:
            raise AssertionError(f"evidence completeness must not imply {key}=true")


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="ev4-completeness-guard-") as raw_tmp:
            tmp_dir = Path(raw_tmp)
            assert_complete_definition_can_reach_shadow_mode(tmp_dir)
            assert_incomplete_definition_blocks_allowed_verdict(tmp_dir)
            assert_blocked_incomplete_definition_remains_not_authorized(tmp_dir)
            assert_completeness_is_not_validation_evidence(tmp_dir)
    except AssertionError as exc:
        print(f"Submitted evidence-completeness contract check failed: {exc}", file=sys.stderr)
        return 1
    except Exception:
        print("Submitted evidence-completeness contract check crashed unexpectedly:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1

    print("Submitted evidence-completeness contract check passed: inconsistent completeness blocks submitted-mode readiness")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
