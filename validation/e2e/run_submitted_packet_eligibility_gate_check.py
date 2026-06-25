#!/usr/bin/env python3
"""Validate submitted-packet eligibility gates for Issue #8 real shadow-mode use.

This check is intentionally local and fixture-based. It does not call GitHub,
create submitted evidence, mutate Issue #8, or run the real pilot. It hardens
eligibility semantics only: a packet may request real shadow-mode eligibility
only when it is a real submitted/validated Issue #8 packet with a consistent
issue reference, non-stale state, and no sample/placeholder markers.
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
    DEFAULT_PACKET,
    REAL_ELIGIBLE_STATUSES,
    REAL_SHADOW_SCOPE,
    load_json,
    sample_indicators,
)

INVALID_FIXTURE_DIR = ROOT / "validation" / "fixtures" / "invalid"
NEGATIVE_FIXTURES = {
    "wrong Issue #8 reference": (
        INVALID_FIXTURE_DIR / "submitted_packet_eligibility_wrong_issue_ref.invalid.json",
        "Issue #8",
    ),
    "stale submitted state": (
        INVALID_FIXTURE_DIR / "submitted_packet_eligibility_stale_state.invalid.json",
        "stale",
    ),
    "sample marker": (
        INVALID_FIXTURE_DIR / "submitted_packet_eligibility_sample_marker.invalid.json",
        "sample or placeholder",
    ),
    "placeholder hash": (
        INVALID_FIXTURE_DIR / "submitted_packet_eligibility_placeholder_hash.invalid.json",
        "placeholder identity hash",
    ),
}

ISSUE_8_REF_VALUES = {
    "#8",
    "issue #8",
    "Issue #8",
    "issues/8",
    "https://github.com/rezahh107/EV4-Responsive-Architect/issues/8",
}
STALE_STATES = {"stale", "superseded", "archived", "closed", "cancelled", "draft", "pending"}
PLACEHOLDER_HASH_VALUES = {
    "",
    "sha256-placeholder",
    "sha256-sample",
    "sha256-fixture-main-handoff",
    "sha256-real-issue8-main-handoff",
}


def real_eligible_packet() -> dict[str, Any]:
    packet = load_json(DEFAULT_PACKET)
    packet["packet_id"] = "SHP-ISSUE8-REAL-ELIGIBLE-001"
    packet["packet_status"] = "submitted"
    packet["packet_origin"] = "real_issue_submission"
    packet["issue_reference"] = {
        "issue_number": 8,
        "issue_url_or_ref": "#8",
        "issue_state": "open",
        "evidence_submission_status": "submitted",
    }
    packet["main_ev4_handoff"]["source_ref"] = "issues/8/main-ev4-handoff.md"
    packet["main_ev4_handoff"]["payload_identity_hash"] = "sha256-issue8-main-handoff-real-20260625"
    packet["intake_verdict"]["sample_dry_run_allowed"] = False
    packet["intake_verdict"]["real_pilot_allowed_to_start"] = True
    packet["intake_verdict"]["allowed_scope"] = REAL_SHADOW_SCOPE
    return packet


def real_eligibility_requested(packet: dict[str, Any]) -> bool:
    verdict = packet.get("intake_verdict")
    if not isinstance(verdict, dict):
        verdict = {}
    return (
        verdict.get("allowed_scope") == REAL_SHADOW_SCOPE
        or verdict.get("real_pilot_allowed_to_start") is True
        or (verdict.get("pilot_allowed_to_start") is True and verdict.get("sample_dry_run_allowed") is not True)
    )


def _normalized_ref(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return value.strip()


def _has_stale_state(value: Any) -> bool:
    return isinstance(value, str) and value.strip().lower() in STALE_STATES


def _payload_identity_hash(packet: dict[str, Any]) -> str | None:
    handoff = packet.get("main_ev4_handoff")
    if not isinstance(handoff, dict):
        return None
    value = handoff.get("payload_identity_hash")
    if not isinstance(value, str):
        return None
    return value.strip()


def validate_submitted_packet_eligibility_gate(packet: dict[str, Any]) -> None:
    """Apply the coupled Issue #8 real submitted-packet eligibility gate."""
    if not real_eligibility_requested(packet):
        return

    origin = packet.get("packet_origin")
    packet_status = packet.get("packet_status")
    issue_reference = packet.get("issue_reference")
    verdict = packet.get("intake_verdict") if isinstance(packet.get("intake_verdict"), dict) else {}

    if origin != "real_issue_submission":
        raise AssertionError("real eligibility requires packet_origin=real_issue_submission")
    if packet_status not in REAL_ELIGIBLE_STATUSES:
        raise AssertionError("real eligibility requires packet_status=submitted or validated")
    if not isinstance(issue_reference, dict):
        raise AssertionError("real eligibility requires structured issue_reference")
    if issue_reference.get("issue_number") != 8:
        raise AssertionError("real eligibility is locked to Issue #8")

    issue_url_or_ref = _normalized_ref(issue_reference.get("issue_url_or_ref"))
    if issue_url_or_ref not in ISSUE_8_REF_VALUES:
        raise AssertionError("real eligibility requires issue_reference.issue_url_or_ref to identify Issue #8")
    if issue_reference.get("evidence_submission_status") not in REAL_ELIGIBLE_STATUSES:
        raise AssertionError("real eligibility requires issue_reference.evidence_submission_status=submitted or validated")
    if verdict.get("real_pilot_allowed_to_start") is not True:
        raise AssertionError("real eligibility requires real_pilot_allowed_to_start=true")

    stale_fields = [
        ("packet_status", packet_status),
        ("packet_lifecycle_state", packet.get("packet_lifecycle_state")),
        ("issue_reference.issue_state", issue_reference.get("issue_state")),
        ("issue_reference.evidence_state", issue_reference.get("evidence_state")),
    ]
    stale_hits = [field for field, value in stale_fields if _has_stale_state(value)]
    if stale_hits:
        raise AssertionError(f"real eligibility rejects stale state fields: {stale_hits}")

    identity_hash = _payload_identity_hash(packet)
    lowered_hash = identity_hash.lower() if isinstance(identity_hash, str) else ""
    if lowered_hash in PLACEHOLDER_HASH_VALUES or "placeholder" in lowered_hash or "sample" in lowered_hash or "fixture" in lowered_hash:
        raise AssertionError("real eligibility rejects placeholder identity hash")

    indicators = sample_indicators(packet)
    if indicators:
        raise AssertionError(f"real eligibility rejects sample or placeholder markers: {indicators}")


def assert_accepts(packet: dict[str, Any]) -> None:
    validate_submitted_packet_eligibility_gate(packet)


def assert_rejects(packet: dict[str, Any], expected_fragment: str) -> None:
    try:
        validate_submitted_packet_eligibility_gate(packet)
    except AssertionError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"wrong rejection message: {exc}") from exc
        return
    raise AssertionError(f"packet unexpectedly accepted; expected rejection containing: {expected_fragment}")


def run_self_test() -> None:
    assert_accepts(real_eligible_packet())

    for label, (fixture_path, expected_fragment) in NEGATIVE_FIXTURES.items():
        if not fixture_path.is_file():
            raise AssertionError(f"missing negative fixture for {label}: {fixture_path.relative_to(ROOT)}")
        assert_rejects(load_json(fixture_path), expected_fragment)

    missing_url_ref = copy.deepcopy(real_eligible_packet())
    missing_url_ref["issue_reference"].pop("issue_url_or_ref")
    assert_rejects(missing_url_ref, "issue_reference.issue_url_or_ref")


def main() -> int:
    try:
        run_self_test()
    except AssertionError as exc:
        print(f"Submitted packet eligibility gate check failed: {exc}", file=sys.stderr)
        return 1
    except Exception:
        print("Submitted packet eligibility gate check crashed unexpectedly:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1
    print("Submitted packet eligibility gate check passed: real eligibility is locked to non-stale submitted Issue #8 packets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
