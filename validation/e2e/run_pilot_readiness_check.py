#!/usr/bin/env python3
"""Gate smart-home pilot start from a validated evidence intake packet.

This runner does not execute the responsive pilot. It decides whether the pilot
is allowed to start in shadow mode from repository-backed intake evidence and
can persist a readiness report for downstream pilot execution.
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from validation.e2e.run_evidence_intake_check import validate_packet  # noqa: E402

DEFAULT_PACKET = ROOT / "validation" / "fixtures" / "valid" / "evidence_intake_packet.valid.json"
READINESS_SCHEMA = ROOT / "schemas" / "ev4-responsive-pilot-readiness.schema.json"
DEFAULT_OUT = ROOT / "examples" / "smart-home-connector" / "readiness" / "PILOT_READINESS_REPORT.generated.json"

FORBIDDEN_CLAIMS = [
    "production_ready",
    "release_ready",
    "live_render_validated",
    "export_json_validated",
    "accessibility_passed",
    "playwright_visual_regression_validated",
]

STATUS_PRIORITY = [
    "blocked_privacy_review_missing",
    "blocked_missing_evidence",
    "blocked_conflicting_evidence",
    "blocked_schema_or_semantic_failure",
]

REASON_STATUS_MAP = {
    "missing_required_evidence": "blocked_missing_evidence",
    "privacy_review_incomplete": "blocked_privacy_review_missing",
    "selected_candidate_conflict": "blocked_conflicting_evidence",
    "schema_or_semantic_failure": "blocked_schema_or_semantic_failure",
    "intake_verdict_does_not_allow_pilot_start": "blocked_schema_or_semantic_failure",
    "breakpoint_claim_scope_allows_release_ready": "blocked_schema_or_semantic_failure",
    "evidence_allows_validation_claim": "blocked_schema_or_semantic_failure",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    data.pop("$schema_file", None)
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def boundary(value: bool, reason: str) -> dict[str, Any]:
    return {"value": value, "reason": reason}


def blocking_reason(reason_code: str, source_ref: str, required_resolution: str) -> dict[str, Any]:
    return {
        "reason_code": reason_code,
        "severity": "blocker",
        "source_ref": source_ref,
        "required_resolution": required_resolution,
    }


def visible_flag(flag_code: str, severity: str, source_ref: str, required_handling: str) -> dict[str, Any]:
    return {
        "flag_code": flag_code,
        "severity": severity,
        "source_ref": source_ref,
        "required_handling": required_handling,
    }


def choose_blocked_status(reasons: list[dict[str, Any]]) -> str:
    mapped = {REASON_STATUS_MAP.get(reason["reason_code"], "blocked_schema_or_semantic_failure") for reason in reasons}
    for status in STATUS_PRIORITY:
        if status in mapped:
            return status
    return "blocked_schema_or_semantic_failure"


def next_action_for_status(status: str) -> str:
    return {
        "ready_for_shadow_mode_pilot": "start_shadow_mode_pilot",
        "partial_ready_with_visible_flags": "start_shadow_mode_pilot_with_visible_flags",
        "blocked_missing_evidence": "request_missing_evidence",
        "blocked_conflicting_evidence": "resolve_conflicting_evidence",
        "blocked_privacy_review_missing": "complete_privacy_review",
        "blocked_schema_or_semantic_failure": "repair_schema_or_semantic_packet",
    }[status]


def build_readiness(packet: dict[str, Any]) -> dict[str, Any]:
    blocking: list[dict[str, Any]] = []
    flags: list[dict[str, Any]] = []

    verdict = packet["intake_verdict"]
    if verdict.get("status") != "allowed" or verdict.get("pilot_allowed_to_start") is not True:
        if verdict.get("missing_required_items"):
            blocking.append(
                blocking_reason(
                    "missing_required_evidence",
                    "intake_verdict.missing_required_items",
                    "Provide all missing intake packet evidence before starting pilot.",
                )
            )
        if verdict.get("blocker_conflicts"):
            blocking.append(
                blocking_reason(
                    "selected_candidate_conflict",
                    "intake_verdict.blocker_conflicts",
                    "Resolve blocker conflicts or route back to the owning EV4 stage.",
                )
            )
        if not verdict.get("missing_required_items") and not verdict.get("blocker_conflicts"):
            blocking.append(
                blocking_reason(
                    "intake_verdict_does_not_allow_pilot_start",
                    "intake_verdict",
                    "Repair the intake verdict so pilot_allowed_to_start is true only when evidence is complete.",
                )
            )

    bp_source = packet["breakpoint_inventory"]["source"]
    if bp_source in {"user_declaration", "fallback_default_with_unverified_label"}:
        flags.append(
            visible_flag(
                "breakpoint_source_not_export_verified",
                "medium",
                "breakpoint_inventory.source",
                "Carry this flag into the pilot report and forbid release-ready claims.",
            )
        )

    if packet["breakpoint_inventory"]["claim_scope"].get("may_claim_release_ready") is not False:
        blocking.append(
            blocking_reason(
                "breakpoint_claim_scope_allows_release_ready",
                "breakpoint_inventory.claim_scope.may_claim_release_ready",
                "Set may_claim_release_ready=false unless project settings/export and release evidence exist.",
            )
        )

    for item in packet["evidence_items"]:
        if item["downstream_allowed_use"].get("validation_claim") != "no":
            blocking.append(
                blocking_reason(
                    "evidence_allows_validation_claim",
                    f"evidence_items.{item['evidence_id']}.downstream_allowed_use.validation_claim",
                    "Visual or limited evidence must not authorize validation claims.",
                )
            )
        if item["quality_level"] in {"L1_static_visual_only", "L2_frontend_visual_with_viewport"}:
            flags.append(
                visible_flag(
                    "visual_only_evidence",
                    "medium",
                    f"evidence_items.{item['evidence_id']}.quality_level",
                    "Carry this flag into observation/failure mapping; do not infer DOM, CSS cause, or accessibility pass.",
                )
            )

    flags.extend(
        [
            visible_flag(
                "no_live_render_evidence",
                "note",
                "validation_boundary.live_elementor_render_validated",
                "Do not claim live Elementor rendering validation.",
            ),
            visible_flag(
                "no_export_json_evidence",
                "note",
                "validation_boundary.export_json_validated",
                "Do not claim export JSON validation.",
            ),
            visible_flag(
                "accessibility_not_validated",
                "note",
                "validation_boundary.accessibility_pass_claimed",
                "Do not claim accessibility pass; run accessibility gate on real DOM if needed.",
            ),
        ]
    )

    if blocking:
        status = choose_blocked_status(blocking)
        authorized = False
        authorization_scope = "not_authorized"
        carry_forward_flags: list[dict[str, Any]] = []
    elif flags:
        status = "partial_ready_with_visible_flags"
        authorized = True
        authorization_scope = "shadow_mode_only_with_visible_flags"
        carry_forward_flags = flags
    else:
        status = "ready_for_shadow_mode_pilot"
        authorized = True
        authorization_scope = "shadow_mode_only"
        carry_forward_flags = []

    return {
        "schema": "ev4-responsive-pilot-readiness@1.0.0",
        "readiness_id": f"{packet['packet_id']}-READINESS",
        "source_packet_id": packet["packet_id"],
        "section_id": packet["section_id"],
        "readiness_status": status,
        "blocking_reasons": blocking,
        "visible_flags": [] if status == "ready_for_shadow_mode_pilot" else flags,
        "required_next_action": next_action_for_status(status),
        "validation_boundary": {
            "live_elementor_render_validated": boundary(False, "no_live_render_evidence"),
            "export_json_validated": boundary(False, "no_export_json_supplied"),
            "playwright_visual_regression_validated": boundary(False, "no_playwright_visual_regression_run"),
            "accessibility_pass_claimed": boundary(False, "accessibility_gate_not_executed_on_real_dom"),
            "production_ready_claimed": boundary(False, "release_gate_evidence_missing"),
        },
        "pilot_start_authorization": {
            "authorized": authorized,
            "authorization_scope": authorization_scope,
            "forbidden_claims": FORBIDDEN_CLAIMS,
            "required_carry_forward_flags": carry_forward_flags,
        },
    }


def validate_readiness_schema(report: dict[str, Any]) -> None:
    try:
        import jsonschema
    except ImportError as exc:
        raise AssertionError("jsonschema package is required") from exc
    schema = load_json(READINESS_SCHEMA)
    jsonschema.Draft202012Validator(schema).validate(report)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and validate an EV4 responsive pilot readiness report.")
    parser.add_argument(
        "--packet",
        type=Path,
        default=DEFAULT_PACKET,
        help="Evidence intake packet JSON. Defaults to the valid fixture.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional output path for the generated readiness report.",
    )
    parser.add_argument(
        "--allow-blocked",
        action="store_true",
        help="Allow blocked readiness reports; useful for negative-path fixtures.",
    )
    parser.add_argument(
        "--skip-schema-suite",
        action="store_true",
        help="Skip full fixture suite when validating a submitted packet.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        packet_path = args.packet if args.packet.is_absolute() else ROOT / args.packet
        out_path = args.out if args.out is None or args.out.is_absolute() else ROOT / args.out
        packet = validate_packet(packet_path, run_full_schema_validator=not args.skip_schema_suite)
        report = build_readiness(packet)
        validate_readiness_schema(report)
        if out_path is not None:
            write_json(out_path, report)
        if report["readiness_status"].startswith("blocked") and not args.allow_blocked:
            raise AssertionError(f"pilot readiness blocked: {report['blocking_reasons']}")
    except AssertionError as exc:
        print(f"Pilot readiness check failed: {exc}", file=sys.stderr)
        return 1
    except Exception:
        print("Pilot readiness check crashed unexpectedly:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1

    print(f"Pilot readiness check passed: {report['readiness_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
