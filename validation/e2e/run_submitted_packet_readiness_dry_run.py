#!/usr/bin/env python3
"""Evidence-safe submitted-packet readiness dry run.

This harness is intentionally pre-pilot. It explains the minimum submitted
packet fields, rejects sample/default/placeholder packets, and delegates the
actual EDIS intake invariants to run_evidence_intake_check without upgrading
readiness, production, release, accessibility, export, live-render, or pixel
claims.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PACKET = ROOT / "validation" / "fixtures" / "valid" / "evidence_intake_packet.valid.json"
PLACEHOLDER_PACKET = ROOT / "validation" / "fixtures" / "invalid" / "submitted_packet_readiness_placeholder.invalid.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.e2e.run_evidence_intake_check import (  # noqa: E402
    load_json,
    sample_indicators,
    validate_packet,
)

REQUIRED_SUBMITTED_PACKET_FIELDS = {
    "schema": "ev4-responsive-evidence-intake-packet@1.1.0",
    "packet_id": "unique identifier for the submitted packet",
    "packet_origin": "real_issue_submission",
    "packet_status": "submitted or validated",
    "issue_reference": "structured Issue #8 submission state",
    "section_id": "target section identifier",
    "selected_candidate_id": "selected architecture candidate identifier",
    "main_ev4_handoff": "submitted source ref and payload identity hash",
    "desktop_baseline": "must-not-regress desktop baseline",
    "evidence_items": "desktop, tablet, and mobile evidence items with capability limits",
    "breakpoint_inventory": "source, confidence, and release-claim scope",
    "privacy_review": "all privacy acknowledgements true",
    "evidence_complete_definition": "required completion booleans",
    "intake_verdict": "blocked/allowed verdict with explicit real-pilot scope",
}

BOUNDARY_ASSERTIONS = (
    "dry_run_only",
    "no_real_evidence_created",
    "no_issue_8_mutation",
    "no_real_pilot_run",
    "no_readiness_claim_upgrade",
    "no_production_claim",
    "no_release_claim",
    "no_live_render_claim",
    "no_export_validation_claim",
    "no_accessibility_pass_claim",
    "no_pixel_claim",
    "sample_or_placeholder_rejected_before_pilot",
)


def readiness_report(packet_path: Path) -> dict[str, Any]:
    """Return a deterministic readiness verdict without starting any pilot."""
    packet = load_json(packet_path)
    missing = [field for field in REQUIRED_SUBMITTED_PACKET_FIELDS if field not in packet]
    indicators = sample_indicators(packet, packet_path)
    try:
        validate_packet(packet_path, run_full_schema_validator=False, submitted_mode=True)
    except AssertionError as exc:
        return {
            "status": "blocked",
            "packet": packet_path.relative_to(ROOT).as_posix() if packet_path.is_relative_to(ROOT) else str(packet_path),
            "missing_required_fields": missing,
            "sample_or_placeholder_indicators": indicators,
            "reason": str(exc),
            "required_fields": REQUIRED_SUBMITTED_PACKET_FIELDS,
            "boundary_assertions": BOUNDARY_ASSERTIONS,
        }
    return {
        "status": "submitted_packet_machine_check_passed",
        "packet": packet_path.relative_to(ROOT).as_posix() if packet_path.is_relative_to(ROOT) else str(packet_path),
        "missing_required_fields": missing,
        "sample_or_placeholder_indicators": indicators,
        "reason": "Packet passed submitted-mode machine checks; this is still not pilot execution or responsive correctness evidence.",
        "required_fields": REQUIRED_SUBMITTED_PACKET_FIELDS,
        "boundary_assertions": BOUNDARY_ASSERTIONS,
    }


def assert_blocked(report: dict[str, Any], expected_reason_fragment: str) -> None:
    if report["status"] != "blocked":
        raise AssertionError(f"expected blocked dry-run report, got {report['status']}: {report}")
    if expected_reason_fragment not in report["reason"]:
        raise AssertionError(f"expected reason containing {expected_reason_fragment!r}, got {report['reason']!r}")
    if "no_real_pilot_run" not in report["boundary_assertions"]:
        raise AssertionError("dry-run report must preserve no_real_pilot_run boundary")


def run_self_tests() -> None:
    default_report = readiness_report(DEFAULT_PACKET)
    assert_blocked(default_report, "submitted mode requires an explicit non-default --packet path")

    placeholder_report = readiness_report(PLACEHOLDER_PACKET)
    assert_blocked(placeholder_report, "sample or placeholder")

    required = set(REQUIRED_SUBMITTED_PACKET_FIELDS)
    complete_required_fields = {
        "schema",
        "packet_id",
        "packet_origin",
        "packet_status",
        "issue_reference",
        "section_id",
        "selected_candidate_id",
        "main_ev4_handoff",
        "desktop_baseline",
        "evidence_items",
        "breakpoint_inventory",
        "privacy_review",
        "evidence_complete_definition",
        "intake_verdict",
    }
    if complete_required_fields - required:
        raise AssertionError("required submitted packet field explanation is incomplete")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an evidence-safe submitted packet readiness dry run.")
    parser.add_argument("--packet", type=Path, help="Explicit submitted packet path to dry-run. Omit to run harness self-tests.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in negative self-tests for sample and placeholder packets.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.self_test or args.packet is None:
            run_self_tests()
            print("Submitted packet readiness dry-run self-tests passed: sample/default and placeholder packets are blocked before pilot.")
            return 0
        packet_path = args.packet.resolve()
        report = readiness_report(packet_path)
        print(report)
        return 0 if report["status"] == "submitted_packet_machine_check_passed" else 1
    except Exception as exc:
        print(f"Submitted packet readiness dry-run failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
