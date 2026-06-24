#!/usr/bin/env python3
"""Validate submitted-mode readiness authorization boundaries.

This check is intentionally narrow. It does not create a submitted packet and it
never runs the real pilot. It verifies the readiness status contract that any
submitted-mode authorization remains limited to shadow-mode and can only come
from a packet explicitly marked as a real issue submission.
"""
from __future__ import annotations

import copy
import sys
import traceback
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from validation.e2e.run_evidence_intake_check import (  # noqa: E402
    load_json,
    validate_packet_origin,
    validate_submitted_packet_source_kind_lock,
)
from validation.e2e.run_pilot_readiness_check import build_readiness, validate_readiness_schema  # noqa: E402

BASE_FIXTURE = ROOT / "validation" / "fixtures" / "valid" / "evidence_intake_packet.valid.json"

FORBIDDEN_AUTHORIZATION_SCOPES = {
    "production_ready",
    "release_ready",
    "live_render_validated",
    "export_json_validated",
    "accessibility_passed",
}

REQUIRED_FORBIDDEN_CLAIMS = {
    "production_ready",
    "release_ready",
    "live_render_validated",
    "export_json_validated",
    "accessibility_passed",
}

VALID_NON_REAL_REJECTION_FRAGMENTS = (
    "contract fixtures must not allow real pilot start",
    "only real_issue_submission may set real_pilot_allowed_to_start=true",
    "real shadow-mode eligibility requires packet_origin=real_issue_submission",
)


def real_issue_packet_from_fixture() -> dict[str, Any]:
    """Build an in-memory real_issue_submission packet from the complete fixture.

    The derived packet is not written to the repository and is not real evidence.
    It exists only to exercise the submitted readiness contract against the same
    readiness engine used by the normal validators.
    """
    packet = copy.deepcopy(load_json(BASE_FIXTURE))
    packet["packet_id"] = "SHP-INTAKE-REAL-ISSUE-CONTRACT-001"
    packet["packet_status"] = "submitted"
    packet["packet_origin"] = "real_issue_submission"
    packet["issue_reference"] = {
        "issue_number": 8,
        "issue_url_or_ref": "#8",
        "evidence_submission_status": "submitted",
    }
    packet["main_ev4_handoff"]["payload_identity_hash"] = "sha256-contract-real-issue-handoff"
    packet["intake_verdict"]["sample_dry_run_allowed"] = False
    packet["intake_verdict"]["real_pilot_allowed_to_start"] = True
    packet["intake_verdict"]["allowed_scope"] = "real_shadow_mode_only"
    return packet


def assert_authorized_real_issue_remains_shadow_mode_only() -> None:
    packet = real_issue_packet_from_fixture()
    validate_packet_origin(packet, BASE_FIXTURE)
    validate_submitted_packet_source_kind_lock(packet)
    report = build_readiness(packet)
    validate_readiness_schema(report)

    if packet["packet_origin"] != "real_issue_submission":
        raise AssertionError("submitted readiness authorization requires packet_origin=real_issue_submission")

    authorization = report["pilot_start_authorization"]
    if authorization["authorized"] is not True:
        raise AssertionError("complete real_issue_submission packet should authorize only shadow-mode readiness")
    if authorization["authorization_scope"] not in {"shadow_mode_only", "shadow_mode_only_with_visible_flags"}:
        raise AssertionError("submitted readiness authorization must remain shadow-mode only")
    if authorization["authorization_scope"] in FORBIDDEN_AUTHORIZATION_SCOPES:
        raise AssertionError("submitted readiness must not use production/release/export/live/accessibility authorization scope")

    boundary = report["validation_boundary"]
    for key in (
        "live_elementor_render_validated",
        "export_json_validated",
        "playwright_visual_regression_validated",
        "accessibility_pass_claimed",
        "production_ready_claimed",
    ):
        if boundary[key]["value"] is not False:
            raise AssertionError(f"submitted readiness must not mark {key}=true")

    forbidden_claims = set(authorization["forbidden_claims"])
    missing = sorted(REQUIRED_FORBIDDEN_CLAIMS - forbidden_claims)
    if missing:
        raise AssertionError(f"submitted readiness authorization missing forbidden claims: {missing}")


def assert_non_real_origin_cannot_self_authorize() -> None:
    packet = real_issue_packet_from_fixture()
    packet["packet_origin"] = "fixture_contract_validation"
    packet["issue_reference"] = None
    packet["intake_verdict"]["allowed_scope"] = "contract_fixture_only"
    packet["intake_verdict"]["real_pilot_allowed_to_start"] = True

    try:
        validate_packet_origin(packet, BASE_FIXTURE)
        validate_submitted_packet_source_kind_lock(packet)
    except AssertionError as exc:
        message = str(exc)
        if not any(fragment in message for fragment in VALID_NON_REAL_REJECTION_FRAGMENTS):
            raise
        return
    raise AssertionError("non-real packet origin must not set real_pilot_allowed_to_start=true")


def main() -> int:
    try:
        assert_authorized_real_issue_remains_shadow_mode_only()
        assert_non_real_origin_cannot_self_authorize()
    except AssertionError as exc:
        print(f"Submitted readiness status contract check failed: {exc}", file=sys.stderr)
        return 1
    except Exception:
        print("Submitted readiness status contract check crashed unexpectedly:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1

    print("Submitted readiness status contract check passed: authorization is real-issue and shadow-mode only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
