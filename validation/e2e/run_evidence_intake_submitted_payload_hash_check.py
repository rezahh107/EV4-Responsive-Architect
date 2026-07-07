#!/usr/bin/env python3
"""Validate real submitted Issue #8 payload identity hash format.

This guard is intentionally evidence-bound: it only constrains real_issue_submission
packets and never treats hash format as responsive correctness, pilot readiness,
production readiness, or release readiness evidence.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import traceback
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PACKET = ROOT / "validation" / "fixtures" / "valid" / "evidence_intake_packet.valid.json"
SUBMITTED_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
REAL_ORIGIN = "real_issue_submission"
VALID_HASH = "sha256:" + "0" * 64


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    payload.pop("$schema_file", None)
    return payload


def payload_identity_hash(packet: dict[str, Any]) -> Any:
    handoff = packet.get("main_ev4_handoff")
    if not isinstance(handoff, dict):
        raise AssertionError("real_issue_submission requires structured main_ev4_handoff")
    return handoff.get("payload_identity_hash")


def is_real_issue_submission(packet: dict[str, Any]) -> bool:
    return packet.get("packet_origin") == REAL_ORIGIN


def validate_real_submitted_payload_identity_hash(packet: dict[str, Any]) -> None:
    if not is_real_issue_submission(packet):
        return
    digest = payload_identity_hash(packet)
    if not isinstance(digest, str) or SUBMITTED_HASH_RE.fullmatch(digest) is None:
        raise AssertionError("real_issue_submission main_ev4_handoff.payload_identity_hash must be sha256:<64 lowercase hex>")


def real_probe() -> dict[str, Any]:
    packet = load_json(DEFAULT_PACKET)
    packet["packet_id"] = "issue-8-submitted-payload-hash-probe"
    packet["packet_status"] = "submitted"
    packet["packet_origin"] = REAL_ORIGIN
    packet["issue_reference"] = {
        "issue_number": 8,
        "issue_url_or_ref": "#8",
        "evidence_submission_status": "submitted",
    }
    packet["main_ev4_handoff"]["source_ref"] = "issue-8/main-ev4-handoff.md"
    packet["main_ev4_handoff"]["payload_identity_hash"] = VALID_HASH
    packet["intake_verdict"] = {
        "status": "blocked",
        "missing_required_items": ["self-test probe only; no real submitted evidence"],
        "blocker_conflicts": [],
        "evidence_quality_summary": "Self-test probe only; not submitted evidence.",
        "pilot_allowed_to_start": False,
        "sample_dry_run_allowed": False,
        "real_pilot_allowed_to_start": False,
        "allowed_scope": "not_allowed",
    }
    return packet


def assert_rejected(label: str, packet: dict[str, Any], expected_fragment: str) -> None:
    try:
        validate_real_submitted_payload_identity_hash(packet)
    except AssertionError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"{label} rejection must cite {expected_fragment!r}, got: {exc}") from exc
    else:
        raise AssertionError(f"{label} must be rejected")


def run_self_test() -> None:
    validate_real_submitted_payload_identity_hash(real_probe())

    missing_hash = deepcopy(real_probe())
    del missing_hash["main_ev4_handoff"]["payload_identity_hash"]
    assert_rejected("missing payload identity hash", missing_hash, "payload_identity_hash")

    malformed_hash = deepcopy(real_probe())
    malformed_hash["main_ev4_handoff"]["payload_identity_hash"] = "sha256-not-a-real-digest"
    assert_rejected("malformed payload identity hash", malformed_hash, "sha256:<64 lowercase hex>")

    uppercase_hash = deepcopy(real_probe())
    uppercase_hash["main_ev4_handoff"]["payload_identity_hash"] = "sha256:" + "A" * 64
    assert_rejected("uppercase payload identity hash", uppercase_hash, "sha256:<64 lowercase hex>")

    fixture_packet = load_json(DEFAULT_PACKET)
    validate_real_submitted_payload_identity_hash(fixture_packet)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate real Issue #8 submitted payload identity hash format.")
    parser.add_argument("--packet", type=Path, help="Optional submitted evidence-intake packet JSON to validate.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.packet is None:
            run_self_test()
            print("Submitted payload hash self-tests passed")
            return 0
        packet_path = args.packet if args.packet.is_absolute() else ROOT / args.packet
        packet = load_json(packet_path)
        validate_real_submitted_payload_identity_hash(packet)
    except AssertionError as exc:
        print(f"Submitted payload hash check failed: {exc}", file=sys.stderr)
        return 1
    except Exception:
        print("Submitted payload hash check crashed unexpectedly:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1
    if is_real_issue_submission(packet):
        print("Submitted payload hash check passed: real submitted payload identity hash is well-formed")
    else:
        print("Submitted payload hash check skipped: packet is not a real issue submission")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
