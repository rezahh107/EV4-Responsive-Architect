#!/usr/bin/env python3
"""Validate the smart-home evidence intake packet contract.

This runner is intentionally limited to repository-backed intake validation.
It does not validate live Elementor rendering, export JSON truth, screenshot
content, Playwright visual regression, accessibility pass, or production readiness.
"""

from __future__ import annotations

import json
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "validation" / "schema_validator" / "validate_schemas.py"
VALID_PACKET = ROOT / "validation" / "fixtures" / "valid" / "evidence_intake_packet.valid.json"

MINIMUM_DESKTOP_MUST_NOT_REGRESS = {
    "meaningful_text_visibility",
    "feature_card_group_integrity",
    "visual_core_presence",
    "connector_layer_containment",
    "no_horizontal_overflow",
}

REQUIRED_VIEWPORT_EVIDENCE = {"desktop", "tablet", "mobile"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    payload.pop("$schema_file", None)
    return payload


def run_schema_validator() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            "schema validator failed\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )


def validate_desktop_baseline(packet: dict[str, Any]) -> None:
    desktop = packet["desktop_baseline"]
    must_not_regress = set(desktop.get("must_not_regress", []))
    missing = MINIMUM_DESKTOP_MUST_NOT_REGRESS - must_not_regress
    if missing:
        raise AssertionError(f"desktop must_not_regress missing required items: {sorted(missing)}")


def validate_evidence_items(packet: dict[str, Any]) -> None:
    evidence_items = packet["evidence_items"]
    viewports = {item.get("viewport") for item in evidence_items}
    missing_viewports = REQUIRED_VIEWPORT_EVIDENCE - viewports
    if missing_viewports:
        raise AssertionError(f"missing required viewport evidence: {sorted(missing_viewports)}")

    ids = [item["evidence_id"] for item in evidence_items]
    if len(ids) != len(set(ids)):
        raise AssertionError("evidence_ids must be unique")

    for item in evidence_items:
        allowed_use = item.get("downstream_allowed_use", {})
        if item.get("quality_level") in {"L1_static_visual_only", "L2_frontend_visual_with_viewport"}:
            if allowed_use.get("validation_claim") != "no":
                raise AssertionError(
                    f"{item['evidence_id']} visual-only evidence must not allow validation claims"
                )
        if not item.get("known_limitations"):
            raise AssertionError(f"{item['evidence_id']} must carry known_limitations")


def validate_breakpoint_policy(packet: dict[str, Any]) -> None:
    bp = packet["breakpoint_inventory"]
    source = bp["source"]
    claim_scope = bp["claim_scope"]
    if source in {"user_declaration", "fallback_default_with_unverified_label"}:
        if claim_scope.get("may_claim_release_ready") is not False:
            raise AssertionError("unverified breakpoint source must not allow release-ready claim")
    if source == "fallback_default_with_unverified_label" and bp.get("confidence") != "low":
        raise AssertionError("fallback breakpoint inventory must carry low confidence")


def validate_privacy_review(packet: dict[str, Any]) -> None:
    review = packet["privacy_review"]
    failed = [key for key, value in review.items() if value is not True]
    if failed:
        raise AssertionError(f"privacy_review must be fully acknowledged: {failed}")


def validate_completion_and_verdict(packet: dict[str, Any]) -> None:
    completion = packet["evidence_complete_definition"]
    incomplete = [key for key, value in completion.items() if value is not True]
    verdict = packet["intake_verdict"]

    if incomplete and verdict.get("pilot_allowed_to_start"):
        raise AssertionError(f"pilot cannot start while completion checks are false: {incomplete}")
    if verdict.get("status") == "allowed" and verdict.get("pilot_allowed_to_start") is not True:
        raise AssertionError("allowed intake verdict must set pilot_allowed_to_start=true")
    if verdict.get("status") == "blocked" and verdict.get("pilot_allowed_to_start") is not False:
        raise AssertionError("blocked intake verdict must set pilot_allowed_to_start=false")
    if verdict.get("status") == "allowed" and verdict.get("missing_required_items"):
        raise AssertionError("allowed intake verdict must not carry missing_required_items")
    if verdict.get("status") == "allowed" and verdict.get("blocker_conflicts"):
        raise AssertionError("allowed intake verdict must not carry blocker_conflicts")


def main() -> int:
    try:
        run_schema_validator()
        packet = load_json(VALID_PACKET)
        validate_desktop_baseline(packet)
        validate_evidence_items(packet)
        validate_breakpoint_policy(packet)
        validate_privacy_review(packet)
        validate_completion_and_verdict(packet)
    except AssertionError as exc:
        print(f"Evidence intake check failed: {exc}", file=sys.stderr)
        return 1
    except Exception:
        print("Evidence intake check crashed unexpectedly:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1

    print("Evidence intake check passed: intake packet is machine-checkable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
