#!/usr/bin/env python3
"""Validate submitted-mode privacy-review guardrails.

This check is intentionally local and declarative. It derives in-memory/tempfile
contract packets from the existing fixture to prove submitted-mode readiness cannot
advance unless every privacy-review acknowledgement is explicit and complete.
It does not create submitted evidence, inspect private Issue #8 attachments, or run
the real pilot.
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

PRIVACY_KEYS = {
    "credentials_removed",
    "private_user_data_removed",
    "private_urls_reviewed",
    "client_identifiers_reviewed",
    "reviewer_acknowledgement",
}


def real_issue_packet_from_fixture() -> dict[str, Any]:
    """Build a contract-only real_issue_submission packet from the fixture.

    The derived packet is temporary test data, not real submitted evidence.
    """
    packet = copy.deepcopy(load_json(BASE_FIXTURE))
    packet["packet_id"] = "SHP-INTAKE-REAL-ISSUE-PRIVACY-CONTRACT-001"
    packet["packet_origin"] = "real_issue_submission"
    packet["issue_reference"] = {
        "repository": "rezahh107/EV4-Responsive-Architect",
        "issue_number": 8,
        "source_scope": "contract_self_test_only",
    }
    packet["main_ev4_handoff"]["payload_identity_hash"] = "sha256-contract-real-issue-privacy-guard"
    packet["intake_verdict"]["sample_dry_run_allowed"] = False
    packet["intake_verdict"]["real_pilot_allowed_to_start"] = True
    packet["intake_verdict"]["allowed_scope"] = "real_shadow_mode_only"
    return packet


def write_temp_packet(packet: dict[str, Any], tmp_dir: Path, name: str) -> Path:
    path = tmp_dir / name
    path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def assert_complete_privacy_review_can_reach_shadow_mode(tmp_dir: Path) -> None:
    packet = real_issue_packet_from_fixture()
    if set(packet["privacy_review"].keys()) != PRIVACY_KEYS:
        raise AssertionError("privacy_review must carry the expected explicit acknowledgement keys")
    path = write_temp_packet(packet, tmp_dir, "real_issue_privacy_complete.json")

    validated = validate_packet(path, run_full_schema_validator=False, submitted_mode=True)
    report = build_readiness(validated)
    validate_readiness_schema(report)

    authorization = report["pilot_start_authorization"]
    if authorization["authorized"] is not True:
        raise AssertionError("complete submitted privacy review should allow only shadow-mode readiness when other gates pass")
    if authorization["authorization_scope"] not in {"shadow_mode_only", "shadow_mode_only_with_visible_flags"}:
        raise AssertionError("submitted privacy guard must not authorize beyond shadow mode")


def assert_missing_privacy_review_blocks_submitted_mode(tmp_dir: Path) -> None:
    packet = real_issue_packet_from_fixture()
    packet["privacy_review"]["private_user_data_removed"] = False
    path = write_temp_packet(packet, tmp_dir, "real_issue_privacy_incomplete.json")

    try:
        validate_packet(path, run_full_schema_validator=False, submitted_mode=True)
    except AssertionError as exc:
        message = str(exc)
        if "privacy_review must be fully acknowledged" not in message:
            raise AssertionError(f"incomplete privacy review failed for the wrong reason: {message}") from exc
        if "private_user_data_removed" not in message:
            raise AssertionError("privacy failure must identify the incomplete privacy field") from exc
        return
    raise AssertionError("submitted-mode packet with incomplete privacy_review must not validate")


def assert_privacy_review_is_not_validation_evidence(tmp_dir: Path) -> None:
    packet = real_issue_packet_from_fixture()
    path = write_temp_packet(packet, tmp_dir, "real_issue_privacy_boundary.json")
    validated = validate_packet(path, run_full_schema_validator=False, submitted_mode=True)
    report = build_readiness(validated)

    boundary = report["validation_boundary"]
    for key in (
        "live_elementor_render_validated",
        "export_json_validated",
        "playwright_visual_regression_validated",
        "accessibility_pass_claimed",
        "production_ready_claimed",
    ):
        if boundary[key]["value"] is not False:
            raise AssertionError(f"privacy review must not imply {key}=true")


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="ev4-privacy-guard-") as raw_tmp:
            tmp_dir = Path(raw_tmp)
            assert_complete_privacy_review_can_reach_shadow_mode(tmp_dir)
            assert_missing_privacy_review_blocks_submitted_mode(tmp_dir)
            assert_privacy_review_is_not_validation_evidence(tmp_dir)
    except AssertionError as exc:
        print(f"Submitted privacy-review guard check failed: {exc}", file=sys.stderr)
        return 1
    except Exception:
        print("Submitted privacy-review guard check crashed unexpectedly:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1

    print("Submitted privacy-review guard check passed: incomplete privacy review blocks submitted-mode readiness")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
