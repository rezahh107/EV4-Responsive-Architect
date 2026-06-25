#!/usr/bin/env python3
"""Validate submitted evidence artifact path allowlist semantics."""
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
    validate_submitted_packet_artifact_path_allowlist,
)


def real_issue_packet() -> dict[str, Any]:
    packet = load_json(DEFAULT_PACKET)
    packet["packet_id"] = "SHP-ISSUE8-REAL-ARTIFACTS-001"
    packet["packet_status"] = "submitted"
    packet["packet_origin"] = "real_issue_submission"
    packet["issue_reference"] = {
        "issue_number": 8,
        "issue_url_or_ref": "#8",
        "evidence_submission_status": "submitted",
    }
    packet["main_ev4_handoff"]["source_ref"] = "issues/8/main-ev4-handoff.md"
    packet["main_ev4_handoff"]["payload_identity_hash"] = "sha256-real-issue8-main-handoff"
    packet["evidence_items"][0]["file_name"] = "issues/8/desktop-baseline-1440.png"
    packet["evidence_items"][1]["file_name"] = "issues/8/tablet-768.png"
    packet["evidence_items"][2]["file_name"] = "issues/8/mobile-390.png"
    return packet


def assert_accepts(packet: dict[str, Any], packet_path: Path | None = None) -> None:
    validate_submitted_packet_artifact_path_allowlist(packet, packet_path)


def assert_rejects(packet: dict[str, Any], expected_fragment: str, packet_path: Path | None = None) -> None:
    try:
        validate_submitted_packet_artifact_path_allowlist(packet, packet_path)
    except AssertionError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"wrong rejection message: {exc}") from exc
        return
    raise AssertionError(f"packet unexpectedly accepted; expected rejection containing: {expected_fragment}")


def mutated_packet(mutator: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
    packet = copy.deepcopy(real_issue_packet())
    mutator(packet)
    return packet


def run_self_test() -> None:
    assert_accepts(real_issue_packet(), ROOT / "examples/smart-home-connector/intake/EVIDENCE_INTAKE_PACKET.submitted.json")

    assert_rejects(
        mutated_packet(lambda packet: packet["main_ev4_handoff"].__setitem__("source_ref", "examples/smart-home-connector/readiness/PILOT_READINESS_REPORT.generated.json")),
        "generated/report/bookkeeping",
    )
    assert_rejects(
        mutated_packet(lambda packet: packet["evidence_items"][0].__setitem__("file_name", "planning/EV4_RUN_LEDGER.json")),
        "generated/report/bookkeeping",
    )
    assert_rejects(
        mutated_packet(lambda packet: packet["evidence_items"][1].__setitem__("file_name", "STATUS.md")),
        "generated/report/bookkeeping",
    )
    assert_rejects(
        mutated_packet(lambda packet: packet["evidence_items"][2].__setitem__("file_name", "exports/latest-elementor-export.json")),
        "outside the submitted evidence artifact allowlist",
    )
    assert_rejects(
        real_issue_packet(),
        "generated/report/bookkeeping",
        ROOT / "examples/smart-home-connector/readiness/PILOT_READINESS_REPORT.generated.json",
    )

    fixture_packet = load_json(DEFAULT_PACKET)
    assert_accepts(fixture_packet, DEFAULT_PACKET)


def main() -> int:
    try:
        run_self_test()
    except AssertionError as exc:
        print(f"Submitted packet artifact-path allowlist check failed: {exc}", file=sys.stderr)
        return 1
    except Exception:
        print("Submitted packet artifact-path allowlist check crashed unexpectedly:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1
    print("Submitted packet artifact-path allowlist check passed: generated reports and bookkeeping cannot be submitted source evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
