#!/usr/bin/env python3
"""Validate the submitted packet source-kind lock for real shadow-mode eligibility."""
from __future__ import annotations

import copy
import sys
import traceback
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from validation.e2e.run_evidence_intake_check import (  # noqa: E402
    DEFAULT_PACKET,
    load_json,
    validate_submitted_packet_source_kind_lock,
)


def real_eligible_packet() -> dict[str, Any]:
    packet = load_json(DEFAULT_PACKET)
    packet["packet_id"] = "SHP-ISSUE8-REAL-001"
    packet["packet_status"] = "submitted"
    packet["packet_origin"] = "real_issue_submission"
    packet["issue_reference"] = {
        "issue_number": 8,
        "issue_url_or_ref": "#8",
        "evidence_submission_status": "submitted",
    }
    packet["main_ev4_handoff"]["source_ref"] = "issues/8/main-ev4-handoff.md"
    packet["main_ev4_handoff"]["payload_identity_hash"] = "sha256-real-issue8-main-handoff"
    packet["intake_verdict"]["sample_dry_run_allowed"] = False
    packet["intake_verdict"]["real_pilot_allowed_to_start"] = True
    packet["intake_verdict"]["allowed_scope"] = "real_shadow_mode_only"
    return packet


def assert_accepts(packet: dict[str, Any]) -> None:
    validate_submitted_packet_source_kind_lock(packet)


def assert_rejects(packet: dict[str, Any], expected_fragment: str) -> None:
    try:
        validate_submitted_packet_source_kind_lock(packet)
    except AssertionError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"wrong rejection message: {exc}") from exc
        return
    raise AssertionError(f"packet unexpectedly accepted; expected rejection containing: {expected_fragment}")


def mutated_packet(mutator: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
    packet = copy.deepcopy(real_eligible_packet())
    mutator(packet)
    return packet


def run_self_test() -> None:
    assert_accepts(real_eligible_packet())

    assert_rejects(
        mutated_packet(lambda packet: packet.__setitem__("packet_origin", "fixture_contract_validation")),
        "packet_origin=real_issue_submission",
    )
    assert_rejects(
        mutated_packet(lambda packet: packet.__setitem__("packet_status", "draft")),
        "packet_status=submitted or validated",
    )
    assert_rejects(
        mutated_packet(lambda packet: packet["issue_reference"].__setitem__("evidence_submission_status", "draft")),
        "issue_reference.evidence_submission_status=submitted or validated",
    )
    assert_rejects(
        mutated_packet(lambda packet: packet["issue_reference"].__setitem__("issue_number", 99)),
        "Issue #8",
    )

    blocked_draft = real_eligible_packet()
    blocked_draft["packet_status"] = "draft"
    blocked_draft["issue_reference"]["evidence_submission_status"] = "draft"
    blocked_draft["intake_verdict"]["status"] = "blocked"
    blocked_draft["intake_verdict"]["pilot_allowed_to_start"] = False
    blocked_draft["intake_verdict"]["real_pilot_allowed_to_start"] = False
    blocked_draft["intake_verdict"]["allowed_scope"] = "not_allowed"
    assert_accepts(blocked_draft)


def main() -> int:
    try:
        run_self_test()
    except AssertionError as exc:
        print(f"Submitted packet source-kind lock check failed: {exc}", file=sys.stderr)
        return 1
    except Exception:
        print("Submitted packet source-kind lock check crashed unexpectedly:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1
    print("Submitted packet source-kind lock check passed: only real submitted Issue #8 packets can request real shadow-mode eligibility")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
