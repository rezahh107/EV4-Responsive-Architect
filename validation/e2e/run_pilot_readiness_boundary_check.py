#!/usr/bin/env python3
"""Verify pilot readiness gates cannot be overridden by scores or CI state.

This gate is evidence-safe: it exercises repository fixtures only, does not read or
mutate Issue #8, does not create submitted evidence, and does not start a pilot.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from validation.e2e import run_pilot_readiness_check as readiness  # noqa: E402

OVERRIDE_FIELDS = {
    "readiness_score": 100,
    "repository_check_conclusion": "success",
    "ci_success": True,
    "merged_pr": 101,
}


def _assert_schema_rejects_override(base_report: dict[str, Any], field: str, value: Any) -> None:
    mutated = copy.deepcopy(base_report)
    mutated[field] = value
    try:
        readiness.validate_readiness_schema(mutated)
    except Exception:
        return
    raise AssertionError(f"pilot readiness schema accepted override-only field: {field}")


def _assert_not_authorized(report: dict[str, Any], label: str) -> None:
    authorization = report["pilot_start_authorization"]
    if authorization["authorized"] is not False:
        raise AssertionError(f"{label} must remain unauthorized")
    if authorization["authorization_scope"] != "not_authorized":
        raise AssertionError(f"{label} must remain not_authorized")
    if not report["readiness_status"].startswith("blocked_"):
        raise AssertionError(f"{label} must remain blocked, got {report['readiness_status']}")
    if not report["blocking_reasons"]:
        raise AssertionError(f"{label} must preserve explicit blocking reasons")


def _assert_forbidden_claims(report: dict[str, Any]) -> None:
    authorization = report["pilot_start_authorization"]
    required = set(readiness.FORBIDDEN_CLAIMS)
    actual = set(authorization["forbidden_claims"])
    missing = sorted(required - actual)
    if missing:
        raise AssertionError(f"readiness report lost forbidden claims: {missing}")
    for boundary_name, boundary in report["validation_boundary"].items():
        if boundary["value"] is not False:
            raise AssertionError(f"validation boundary unexpectedly true: {boundary_name}")


def main() -> int:
    try:
        blocked_missing = readiness.run_readiness_for_packet(
            readiness.DEFAULT_BLOCKED_PACKET,
            out_path=None,
            allow_blocked=True,
            run_full_schema_validator=False,
        )
        _assert_not_authorized(blocked_missing, "missing-evidence fixture")
        _assert_forbidden_claims(blocked_missing)

        blocked_conflict = readiness.run_readiness_for_packet(
            readiness.DEFAULT_CONFLICT_PACKET,
            out_path=None,
            allow_blocked=True,
            run_full_schema_validator=False,
        )
        _assert_not_authorized(blocked_conflict, "conflict fixture")
        _assert_forbidden_claims(blocked_conflict)

        for field, value in OVERRIDE_FIELDS.items():
            _assert_schema_rejects_override(blocked_missing, field, value)
            _assert_schema_rejects_override(blocked_conflict, field, value)
    except AssertionError as exc:
        print(f"pilot readiness boundary check failed: {exc}", file=sys.stderr)
        return 1

    print("pilot readiness boundary check passed: blocked gates ignore score, CI, merge, and check-state overrides")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
