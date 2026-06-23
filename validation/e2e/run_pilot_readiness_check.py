#!/usr/bin/env python3
"""Gate smart-home pilot start from a validated evidence intake packet.

This runner does not execute the responsive pilot. It decides whether the pilot
is allowed to start in shadow mode from repository-backed intake evidence.
"""

from __future__ import annotations

import json
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
INTAKE_CHECK = ROOT / "validation" / "e2e" / "run_evidence_intake_check.py"
VALID_PACKET = ROOT / "validation" / "fixtures" / "valid" / "evidence_intake_packet.valid.json"
READINESS_SCHEMA = ROOT / "schemas" / "ev4-responsive-pilot-readiness.schema.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    data.pop("$schema_file", None)
    return data


def run_intake_check() -> None:
    result = subprocess.run(
        [sys.executable, str(INTAKE_CHECK)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            "evidence intake check must pass before pilot readiness\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def build_readiness(packet: dict[str, Any]) -> dict[str, Any]:
    blocking: list[str] = []
    flags: list[str] = []

    verdict = packet["intake_verdict"]
    if verdict.get("status") != "allowed" or verdict.get("pilot_allowed_to_start") is not True:
        blocking.append("intake_verdict_does_not_allow_pilot_start")

    bp_source = packet["breakpoint_inventory"]["source"]
    if bp_source in {"user_declaration", "fallback_default_with_unverified_label"}:
        flags.append(f"breakpoint_source_not_export_verified:{bp_source}")

    if packet["breakpoint_inventory"]["claim_scope"].get("may_claim_release_ready") is not False:
        blocking.append("breakpoint_claim_scope_allows_release_ready")

    for item in packet["evidence_items"]:
        if item["downstream_allowed_use"].get("validation_claim") != "no":
            blocking.append(f"evidence_allows_validation_claim:{item['evidence_id']}")
        if item["quality_level"] in {"L1_static_visual_only", "L2_frontend_visual_with_viewport"}:
            flags.append(f"visual_only_evidence:{item['evidence_id']}")

    if blocking:
        status = "blocked_schema_or_semantic_failure"
        next_action = "Resolve blocking intake issues before starting pilot."
    elif flags:
        status = "partial_ready_with_visible_flags"
        next_action = "Pilot may start in shadow mode only; keep visible flags and forbid release-ready claims."
    else:
        status = "ready_for_shadow_mode_pilot"
        next_action = "Start shadow-mode pilot."

    return {
        "schema": "ev4-responsive-pilot-readiness@1.0.0",
        "readiness_id": "SHP-READINESS-001",
        "source_packet_id": packet["packet_id"],
        "section_id": packet["section_id"],
        "readiness_status": status,
        "blocking_reasons": blocking,
        "visible_flags": flags,
        "required_next_action": next_action,
        "validation_boundary": {
            "live_elementor_render_validated": False,
            "export_json_validated": False,
            "playwright_visual_regression_validated": False,
            "accessibility_pass_claimed": False,
            "production_ready_claimed": False,
        },
    }


def validate_readiness_schema(report: dict[str, Any]) -> None:
    try:
        import jsonschema
    except ImportError as exc:
        raise AssertionError("jsonschema package is required") from exc
    schema = load_json(READINESS_SCHEMA)
    jsonschema.Draft202012Validator(schema).validate(report)


def main() -> int:
    try:
        run_intake_check()
        packet = load_json(VALID_PACKET)
        report = build_readiness(packet)
        validate_readiness_schema(report)
        if report["readiness_status"].startswith("blocked"):
            raise AssertionError(f"pilot readiness blocked: {report['blocking_reasons']}")
    except AssertionError as exc:
        print(f"Pilot readiness check failed: {exc}", file=sys.stderr)
        return 1
    except Exception:
        print("Pilot readiness check crashed unexpectedly:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1

    print("Pilot readiness check passed: shadow-mode pilot may start with visible flags")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
