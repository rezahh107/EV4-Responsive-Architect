#!/usr/bin/env python3
"""Assert readiness provenance boundaries stay visible and non-upgrading.

This check does not execute the responsive pilot and does not create a submitted
packet. It proves that readiness derivation keeps source references tied to
intake fields/fixture evidence instead of upgrading Issue prose, templates, or
sample fixtures into real visual/runtime evidence.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from validation.e2e.run_pilot_readiness_check import (  # noqa: E402
    DEFAULT_BLOCKED_PACKET,
    DEFAULT_CONFLICT_PACKET,
    DEFAULT_PACKET,
    run_readiness_for_packet,
)

FORBIDDEN_REAL_EVIDENCE_REFS = (
    "issue.body",
    "issue.title",
    "issue.checklist",
    "issue.prose",
    "template",
    "placeholder",
    "real_issue_submission",
)

REQUIRED_BOUNDARY_FLAGS = {
    "no_live_render_evidence",
    "no_export_json_evidence",
    "accessibility_not_validated",
}


def _source_refs_from_report(report: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for reason in report.get("blocking_reasons", []):
        refs.append(str(reason.get("source_ref", "")))
    for flag in report.get("visible_flags", []):
        refs.append(str(flag.get("source_ref", "")))
    for conflict in report.get("evidence_conflict_summary", {}).get("conflict_records", []):
        refs.extend(str(ref) for ref in conflict.get("source_refs", []))
    return refs


def _assert_no_forbidden_provenance_upgrade(report: dict[str, Any]) -> None:
    refs = _source_refs_from_report(report)
    bad_refs = [ref for ref in refs if any(marker in ref for marker in FORBIDDEN_REAL_EVIDENCE_REFS)]
    if bad_refs:
        raise AssertionError(f"readiness report upgrades non-evidence provenance: {bad_refs}")
    if not refs:
        raise AssertionError("readiness report must expose provenance source_ref values")


def _assert_boundary_flags(report: dict[str, Any]) -> None:
    flags = {flag["flag_code"] for flag in report.get("visible_flags", [])}
    missing = sorted(REQUIRED_BOUNDARY_FLAGS - flags)
    if missing:
        raise AssertionError(f"readiness report dropped required boundary flags: {missing}")


def _assert_fixture_is_not_real(report: dict[str, Any]) -> None:
    authorization = report["pilot_start_authorization"]
    forbidden = set(authorization["forbidden_claims"])
    required_forbidden = {"production_ready", "release_ready", "live_render_validated", "export_json_validated", "accessibility_passed"}
    missing = sorted(required_forbidden - forbidden)
    if missing:
        raise AssertionError(f"readiness authorization lost forbidden claims: {missing}")
    if authorization["authorization_scope"] not in {"not_authorized", "shadow_mode_only", "shadow_mode_only_with_visible_flags"}:
        raise AssertionError("readiness authorization scope must remain bounded to non-production states")


def run_check() -> None:
    positive = run_readiness_for_packet(
        DEFAULT_PACKET,
        out_path=None,
        allow_blocked=False,
        run_full_schema_validator=True,
    )
    _assert_no_forbidden_provenance_upgrade(positive)
    _assert_boundary_flags(positive)
    _assert_fixture_is_not_real(positive)

    blocked = run_readiness_for_packet(
        DEFAULT_BLOCKED_PACKET,
        out_path=None,
        allow_blocked=True,
        run_full_schema_validator=False,
    )
    _assert_no_forbidden_provenance_upgrade(blocked)
    _assert_boundary_flags(blocked)
    _assert_fixture_is_not_real(blocked)
    if blocked["pilot_start_authorization"]["authorized"] is not False:
        raise AssertionError("blocked fixture must not be upgraded into pilot authorization")

    conflict = run_readiness_for_packet(
        DEFAULT_CONFLICT_PACKET,
        out_path=None,
        allow_blocked=True,
        run_full_schema_validator=False,
    )
    _assert_no_forbidden_provenance_upgrade(conflict)
    _assert_boundary_flags(conflict)
    _assert_fixture_is_not_real(conflict)
    if conflict["evidence_conflict_summary"]["unresolved_blocking_conflict_count"] < 1:
        raise AssertionError("conflict fixture must preserve conflict provenance records")


def main() -> int:
    try:
        run_check()
    except AssertionError as exc:
        print(f"Readiness provenance policy check failed: {exc}", file=sys.stderr)
        return 1
    print("Readiness provenance policy check passed: source refs and non-real boundaries preserved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
