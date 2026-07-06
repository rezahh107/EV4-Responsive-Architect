#!/usr/bin/env python3
"""Validate EV4 responsive evidence intake packets."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "validation" / "schema_validator" / "validate_schemas.py"
DEFAULT_PACKET = ROOT / "validation" / "fixtures" / "valid" / "evidence_intake_packet.valid.json"
ISSUE_8_NUMBER = 8
ISSUE_8_REF_SHORTHAND = "#8"
ISSUE_8_REF_URL = "https://github.com/rezahh107/EV4-Responsive-Architect/issues/8"
ISSUE_8_ALLOWED_REFS = {ISSUE_8_REF_SHORTHAND, ISSUE_8_REF_URL}
MINIMUM_DESKTOP_MUST_NOT_REGRESS = {"meaningful_text_visibility", "feature_card_group_integrity", "visual_core_presence", "connector_layer_containment", "no_horizontal_overflow"}
REQUIRED_VIEWPORT_EVIDENCE = {"desktop", "tablet", "mobile"}
SAMPLE_MARKERS = ("SAMPLE", "sample", ".sample", "placeholder")
SCREENSHOT_CAPABILITIES = {"visible_viewport_state", "visible_collision", "visible_overflow_symptom", "visible_clipping", "visible_spacing_issue", "visible_alignment_issue", "visible_order_symptom", "visible_content_visibility_state", "visible_connector_position_symptom"}
VISUAL_ONLY_TYPES = {"frontend_screenshot", "editor_screenshot"}
VISUAL_MUST_NOT_SUPPORT = {"computed_css_value", "dom_structure_observation", "exported_widget_structure", "exported_control_value", "declared_breakpoint_value"}
VISUAL_REQUIRED_CANNOT_SUPPORT = {"exact_css_cause", "dom_reading_order", "accessibility_pass", "production_ready_claim"}
REAL_ELIGIBLE_STATUSES = {"submitted", "validated"}
REAL_SHADOW_SCOPE = "real_shadow_mode_only"
GENERATED_ARTIFACT_MARKERS = (
    ".generated.",
    "/generated/",
    "generated/",
    "/readiness/",
    "readiness/",
    "/planning/",
    "planning/",
    "/reports/",
    "reports/",
    "pilot_readiness_report",
    "pilot_dry_run_record",
    "risk_priority_assessment.generated",
    "ev4_run_ledger",
    "ev4_rolling_queue",
    "status.md",
)
REPOSITORY_EXAMPLE_OR_TEMPLATE_MARKERS = (
    "examples/",
    "/examples/",
    "template/",
    "/template/",
)
SUBMITTED_ARTIFACT_ALLOWED_PREFIXES = (
    "issues/8/",
    "issue-8/",
    "evidence/issue-8/",
)
SUBMITTED_ARTIFACT_ALLOWED_BASENAMES = {
    "main-ev4-handoff.md",
    "breakpoint-inventory.json",
    "evidence_intake_packet.submitted.json",
}
SUBMITTED_SCREENSHOT_BASENAME_PREFIXES = (
    "desktop-baseline-",
    "desktop-",
    "tablet-",
    "mobile-",
)
SUBMITTED_SCREENSHOT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    payload.pop("$schema_file", None)
    return payload


def run_schema_validator() -> None:
    result = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise AssertionError(f"schema validator failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")


def _has_sample_marker(value: Any) -> bool:
    return isinstance(value, str) and any(marker in value for marker in SAMPLE_MARKERS)


def _repo_relative_path(path: Path) -> str | None:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return None


def _normalize_artifact_ref(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.replace("\\", "/").strip()
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _has_generated_artifact_marker(path_ref: str) -> bool:
    lowered = path_ref.lower()
    return any(marker in lowered for marker in GENERATED_ARTIFACT_MARKERS)


def _has_repository_example_or_template_marker(path_ref: str) -> bool:
    lowered = path_ref.lower()
    return any(marker in lowered for marker in REPOSITORY_EXAMPLE_OR_TEMPLATE_MARKERS)


def _submitted_artifact_basename_allowed(basename: str) -> bool:
    lowered = basename.lower()
    if lowered in SUBMITTED_ARTIFACT_ALLOWED_BASENAMES:
        return True
    return (
        any(lowered.startswith(prefix) for prefix in SUBMITTED_SCREENSHOT_BASENAME_PREFIXES)
        and Path(lowered).suffix in SUBMITTED_SCREENSHOT_EXTENSIONS
    )


def _is_allowed_submitted_artifact_path(path_ref: str) -> bool:
    normalized = _normalize_artifact_ref(path_ref)
    if normalized is None or normalized.startswith("../") or "/../" in normalized or normalized.startswith("/"):
        return False
    basename = normalized.rsplit("/", 1)[-1]
    if not _submitted_artifact_basename_allowed(basename):
        return False
    return "/" not in normalized or any(normalized.startswith(prefix) for prefix in SUBMITTED_ARTIFACT_ALLOWED_PREFIXES)


def submitted_source_artifact_refs(packet: dict[str, Any], packet_path: Path | None = None) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    if packet_path is not None:
        packet_ref = _repo_relative_path(packet_path)
        if packet_ref is not None:
            refs.append(("packet_path", packet_ref))
    handoff = packet.get("main_ev4_handoff")
    handoff_ref = _normalize_artifact_ref(handoff.get("source_ref")) if isinstance(handoff, dict) else None
    if handoff_ref is not None:
        refs.append(("main_ev4_handoff.source_ref", handoff_ref))
    evidence_items = packet.get("evidence_items")
    if not isinstance(evidence_items, list):
        return refs
    for index, item in enumerate(evidence_items):
        if not isinstance(item, dict):
            continue
        item_id = item.get("evidence_id", f"index_{index}")
        file_name = _normalize_artifact_ref(item.get("file_name"))
        if file_name is not None:
            refs.append((f"evidence_items.{item_id}.file_name", file_name))
    return refs


def validate_submitted_packet_artifact_path_allowlist(packet: dict[str, Any], packet_path: Path | None = None) -> None:
    """Ensure real submitted evidence does not point at generated reports or repo bookkeeping."""
    if packet.get("packet_origin") != "real_issue_submission":
        return

    rejected: list[str] = []
    for field, path_ref in submitted_source_artifact_refs(packet, packet_path):
        if _has_generated_artifact_marker(path_ref):
            rejected.append(f"{field}={path_ref} uses generated/report/bookkeeping artifact path")
            continue
        if _has_repository_example_or_template_marker(path_ref):
            rejected.append(f"{field}={path_ref} uses repository examples/templates instead of submitted Issue #8 attachments")
            continue
        if not _is_allowed_submitted_artifact_path(path_ref):
            rejected.append(f"{field}={path_ref} is outside the submitted evidence artifact allowlist")

    if rejected:
        raise AssertionError(f"real_issue_submission source artifacts must use submitted evidence paths only: {rejected}")


def sample_indicators(packet: dict[str, Any], packet_path: Path | None = None) -> list[str]:
    indicators: list[str] = []
    if packet_path is not None and _has_sample_marker(str(packet_path)):
        indicators.append("packet_path")
    if _has_sample_marker(packet.get("packet_id")):
        indicators.append("packet_id")
    handoff = packet.get("main_ev4_handoff", {})
    if _has_sample_marker(handoff.get("source_ref")):
        indicators.append("main_ev4_handoff.source_ref")
    if _has_sample_marker(handoff.get("payload_identity_hash")):
        indicators.append("main_ev4_handoff.payload_identity_hash")
    for item in packet.get("evidence_items", []):
        item_id = item.get("evidence_id", "<unknown>")
        if _has_sample_marker(item.get("evidence_id")):
            indicators.append(f"evidence_items.{item_id}.evidence_id")
        if _has_sample_marker(item.get("file_name")):
            indicators.append(f"evidence_items.{item_id}.file_name")
    return indicators


def validate_submitted_mode(packet: dict[str, Any], packet_path: Path) -> None:
    if packet_path == DEFAULT_PACKET:
        raise AssertionError("submitted mode requires an explicit non-default --packet path")
    if packet.get("packet_origin") != "real_issue_submission":
        raise AssertionError("submitted mode only accepts packet_origin=real_issue_submission")
    indicators = sample_indicators(packet, packet_path)
    if indicators:
        raise AssertionError(f"submitted mode rejects sample or placeholder markers: {indicators}")


def validate_issue_8_reference_lock(issue_reference: Any, label: str) -> None:
    """Require Issue #8 identity to be consistent by number and URL/ref."""
    if not isinstance(issue_reference, dict):
        raise AssertionError(f"{label} requires structured issue_reference")
    if issue_reference.get("issue_number") != ISSUE_8_NUMBER:
        raise AssertionError(f"{label} is locked to Issue #8 evidence submission")
    ref = issue_reference.get("issue_url_or_ref")
    if not isinstance(ref, str) or ref not in ISSUE_8_ALLOWED_REFS:
        raise AssertionError(f"{label} issue_url_or_ref must point to Issue #8")


def validate_submitted_packet_source_kind_lock(packet: dict[str, Any]) -> None:
    """Require real shadow-mode eligibility to come from an actual submitted issue packet."""
    origin = packet.get("packet_origin")
    packet_status = packet.get("packet_status")
    issue_reference = packet.get("issue_reference")
    verdict = packet.get("intake_verdict")
    if not isinstance(verdict, dict):
        verdict = {}

    real_eligible_requested = (
        verdict.get("allowed_scope") == REAL_SHADOW_SCOPE
        or verdict.get("real_pilot_allowed_to_start") is True
        or (verdict.get("pilot_allowed_to_start") is True and verdict.get("sample_dry_run_allowed") is not True)
    )
    if not real_eligible_requested:
        return

    if origin != "real_issue_submission":
        raise AssertionError("real shadow-mode eligibility requires packet_origin=real_issue_submission")
    if packet_status not in REAL_ELIGIBLE_STATUSES:
        raise AssertionError("real shadow-mode eligibility requires packet_status=submitted or validated")
    validate_issue_8_reference_lock(issue_reference, "real shadow-mode eligibility")
    if issue_reference.get("evidence_submission_status") not in REAL_ELIGIBLE_STATUSES:
        raise AssertionError("real shadow-mode eligibility requires issue_reference.evidence_submission_status=submitted or validated")
    if verdict.get("real_pilot_allowed_to_start") is not True:
        raise AssertionError("real shadow-mode eligibility requires real_pilot_allowed_to_start=true")


def validate_packet_origin(packet: dict[str, Any], packet_path: Path) -> None:
    origin = packet["packet_origin"]
    issue_reference = packet["issue_reference"]
    verdict = packet["intake_verdict"]
    if origin in {"sample_contract_fixture", "fixture_contract_validation"} and issue_reference is not None:
        raise AssertionError(f"{origin} must not carry a real issue_reference")
    if origin == "sample_contract_fixture":
        if not sample_indicators(packet, packet_path):
            raise AssertionError("sample_contract_fixture must carry visible sample markers")
        if verdict.get("sample_dry_run_allowed") is not True or verdict.get("real_pilot_allowed_to_start") is not False:
            raise AssertionError("sample_contract_fixture must be dry-run-only and never real-pilot authorized")
        if verdict.get("allowed_scope") != "sample_dry_run_only":
            raise AssertionError("sample_contract_fixture must use allowed_scope=sample_dry_run_only")
    if origin == "fixture_contract_validation":
        if verdict.get("real_pilot_allowed_to_start") is not False:
            raise AssertionError("contract fixtures must not allow real pilot start")
        if verdict.get("allowed_scope") not in {"contract_fixture_only", "not_allowed"}:
            raise AssertionError("contract fixtures must use contract_fixture_only or not_allowed scope")
    if origin == "real_issue_submission":
        validate_issue_8_reference_lock(issue_reference, "real_issue_submission")
        indicators = sample_indicators(packet, packet_path)
        if indicators:
            raise AssertionError(f"real_issue_submission must not carry sample markers: {indicators}")
        if verdict.get("allowed_scope") not in {"real_shadow_mode_only", "not_allowed"}:
            raise AssertionError("real_issue_submission must use real_shadow_mode_only or not_allowed scope")
        if verdict.get("pilot_allowed_to_start") is True and verdict.get("real_pilot_allowed_to_start") is not True:
            raise AssertionError("real allowed packet must set real_pilot_allowed_to_start=true")
    if verdict.get("real_pilot_allowed_to_start") is True and origin != "real_issue_submission":
        raise AssertionError("only real_issue_submission may set real_pilot_allowed_to_start=true")


def validate_desktop_baseline(packet: dict[str, Any]) -> None:
    missing = MINIMUM_DESKTOP_MUST_NOT_REGRESS - set(packet["desktop_baseline"].get("must_not_regress", []))
    if missing:
        raise AssertionError(f"desktop must_not_regress missing required items: {sorted(missing)}")


def validate_evidence_capabilities(item: dict[str, Any]) -> None:
    evidence_type = item.get("evidence_type")
    can_support = set(item.get("can_support", []))
    cannot_support = set(item.get("cannot_support", []))
    if evidence_type in VISUAL_ONLY_TYPES:
        illegal = sorted(can_support & VISUAL_MUST_NOT_SUPPORT)
        if illegal:
            raise AssertionError(f"{item['evidence_id']} visual evidence claims unsupported capabilities: {illegal}")
        if not can_support <= SCREENSHOT_CAPABILITIES:
            raise AssertionError(f"{item['evidence_id']} visual evidence can_support must use screenshot capability enum")
        missing = sorted(VISUAL_REQUIRED_CANNOT_SUPPORT - cannot_support)
        if missing:
            raise AssertionError(f"{item['evidence_id']} visual evidence missing cannot_support limits: {missing}")


def validate_evidence_items(packet: dict[str, Any]) -> None:
    items = packet["evidence_items"]
    missing_viewports = REQUIRED_VIEWPORT_EVIDENCE - {item.get("viewport") for item in items}
    if missing_viewports:
        raise AssertionError(f"missing required viewport evidence: {sorted(missing_viewports)}")
    ids = [item["evidence_id"] for item in items]
    if len(ids) != len(set(ids)):
        raise AssertionError("evidence_ids must be unique")
    for item in items:
        validate_evidence_capabilities(item)
        if item.get("quality_level") in {"L1_static_visual_only", "L2_frontend_visual_with_viewport"} and item.get("downstream_allowed_use", {}).get("validation_claim") != "no":
            raise AssertionError(f"{item['evidence_id']} visual-only evidence must not allow validation claims")
        if not item.get("known_limitations"):
            raise AssertionError(f"{item['evidence_id']} must carry known_limitations")


def validate_breakpoint_policy(packet: dict[str, Any]) -> None:
    bp = packet["breakpoint_inventory"]
    if bp["source"] in {"user_declaration", "fallback_default_with_unverified_label"} and bp["claim_scope"].get("may_claim_release_ready") is not False:
        raise AssertionError("unverified breakpoint source must not allow release-ready claim")
    if bp["source"] == "fallback_default_with_unverified_label" and bp.get("confidence") != "low":
        raise AssertionError("fallback breakpoint inventory must carry low confidence")


def validate_privacy_review(packet: dict[str, Any]) -> None:
    failed = [key for key, value in packet["privacy_review"].items() if value is not True]
    if failed:
        raise AssertionError(f"privacy_review must be fully acknowledged: {failed}")


def validate_completion_and_verdict(packet: dict[str, Any]) -> None:
    incomplete = [key for key, value in packet["evidence_complete_definition"].items() if value is not True]
    verdict = packet["intake_verdict"]
    if incomplete and verdict.get("pilot_allowed_to_start"):
        raise AssertionError(f"pilot cannot start while completion checks are false: {incomplete}")
    if verdict.get("status") == "allowed" and verdict.get("pilot_allowed_to_start") is not True:
        raise AssertionError("allowed intake verdict must set pilot_allowed_to_start=true")
    if verdict.get("status") == "blocked" and verdict.get("pilot_allowed_to_start") is not False:
        raise AssertionError("blocked intake verdict must set pilot_allowed_to_start=false")
    if verdict.get("status") == "allowed" and (verdict.get("missing_required_items") or verdict.get("blocker_conflicts")):
        raise AssertionError("allowed intake verdict must not carry missing_required_items or blocker_conflicts")
    if verdict.get("allowed_scope") == "not_allowed" and verdict.get("pilot_allowed_to_start") is True:
        raise AssertionError("not_allowed scope must not allow pilot start")
    if verdict.get("allowed_scope") == "real_shadow_mode_only" and verdict.get("real_pilot_allowed_to_start") is not True:
        raise AssertionError("real_shadow_mode_only must set real_pilot_allowed_to_start=true")


def validate_packet(packet_path: Path, *, run_full_schema_validator: bool = True, submitted_mode: bool = False) -> dict[str, Any]:
    if run_full_schema_validator:
        run_schema_validator()
    packet = load_json(packet_path)
    if submitted_mode:
        validate_submitted_mode(packet, packet_path)
    validate_packet_origin(packet, packet_path)
    validate_submitted_packet_source_kind_lock(packet)
    validate_submitted_packet_artifact_path_allowlist(packet, packet_path)
    validate_desktop_baseline(packet)
    validate_evidence_items(packet)
    validate_breakpoint_policy(packet)
    validate_privacy_review(packet)
    validate_completion_and_verdict(packet)
    return packet


def _real_issue_submission_probe(issue_number: int) -> dict[str, Any]:
    packet = load_json(DEFAULT_PACKET)
    packet["packet_id"] = "issue-8-submission-probe"
    packet["packet_status"] = "blocked"
    packet["packet_origin"] = "real_issue_submission"
    packet["issue_reference"] = {
        "issue_number": issue_number,
        "issue_url_or_ref": f"https://github.com/rezahh107/EV4-Responsive-Architect/issues/{issue_number}",
        "evidence_submission_status": "blocked",
    }
    packet["main_ev4_handoff"]["source_ref"] = f"issue-{issue_number}/main-ev4-handoff.md"
    packet["intake_verdict"] = {
        "status": "blocked",
        "missing_required_items": ["real submitted packet not validated in self-test"],
        "blocker_conflicts": [],
        "evidence_quality_summary": "Self-test probe only; not submitted evidence.",
        "pilot_allowed_to_start": False,
        "sample_dry_run_allowed": False,
        "real_pilot_allowed_to_start": False,
        "allowed_scope": "not_allowed",
    }
    return packet


def assert_rejected(label: str, callback: Any, expected_fragment: str) -> None:
    try:
        callback()
    except AssertionError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"{label} rejection must cite {expected_fragment!r}, got: {exc}") from exc
    else:
        raise AssertionError(f"{label} must be rejected")


def _mark_probe_real_shadow_requested(packet: dict[str, Any]) -> None:
    packet["intake_verdict"] = {
        "status": "allowed",
        "missing_required_items": [],
        "blocker_conflicts": [],
        "evidence_quality_summary": "Self-test probe only; not submitted evidence.",
        "pilot_allowed_to_start": True,
        "sample_dry_run_allowed": False,
        "real_pilot_allowed_to_start": True,
        "allowed_scope": REAL_SHADOW_SCOPE,
    }


def run_self_test() -> None:
    issue_8_path = ROOT / "issue-8/evidence_intake_packet.submitted.json"
    valid_issue_8_probe = _real_issue_submission_probe(ISSUE_8_NUMBER)
    validate_packet_origin(valid_issue_8_probe, issue_8_path)
    validate_submitted_packet_source_kind_lock(valid_issue_8_probe)
    validate_submitted_packet_artifact_path_allowlist(valid_issue_8_probe, issue_8_path)

    assert_rejected(
        "wrong issue boundary",
        lambda: validate_packet_origin(_real_issue_submission_probe(9), ROOT / "issue-9/evidence_intake_packet.submitted.json"),
        "Issue #8",
    )

    conflicting_ref_probe = _real_issue_submission_probe(ISSUE_8_NUMBER)
    conflicting_ref_probe["issue_reference"]["issue_url_or_ref"] = "https://github.com/rezahh107/EV4-Responsive-Architect/issues/9"
    assert_rejected(
        "wrong issue reference url",
        lambda: validate_packet_origin(conflicting_ref_probe, issue_8_path),
        "issue_url_or_ref",
    )

    malformed_ref_probe = _real_issue_submission_probe(ISSUE_8_NUMBER)
    malformed_ref_probe["issue_reference"]["issue_url_or_ref"] = [ISSUE_8_REF_URL]
    assert_rejected(
        "malformed issue reference url",
        lambda: validate_packet_origin(malformed_ref_probe, issue_8_path),
        "issue_url_or_ref",
    )

    draft_real_shadow_probe = _real_issue_submission_probe(ISSUE_8_NUMBER)
    _mark_probe_real_shadow_requested(draft_real_shadow_probe)
    assert_rejected(
        "unsubmitted real shadow probe",
        lambda: validate_submitted_packet_source_kind_lock(draft_real_shadow_probe),
        "packet_status=submitted or validated",
    )

    generated_artifact_probe = _real_issue_submission_probe(ISSUE_8_NUMBER)
    generated_artifact_probe["main_ev4_handoff"]["source_ref"] = "examples/smart-home-connector/readiness/PILOT_READINESS_REPORT.generated.json"
    assert_rejected(
        "generated artifact source",
        lambda: validate_submitted_packet_artifact_path_allowlist(generated_artifact_probe, issue_8_path),
        "generated/report/bookkeeping artifact path",
    )

    example_artifact_probe = _real_issue_submission_probe(ISSUE_8_NUMBER)
    example_artifact_probe["main_ev4_handoff"]["source_ref"] = "examples/smart-home-connector/evidence/main-ev4-handoff.md"
    assert_rejected(
        "repository example artifact source",
        lambda: validate_submitted_packet_artifact_path_allowlist(example_artifact_probe, issue_8_path),
        "repository examples/templates",
    )

    disallowed_artifact_probe = _real_issue_submission_probe(ISSUE_8_NUMBER)
    disallowed_artifact_probe["evidence_items"][0]["file_name"] = "exports/mobile-390.png"
    assert_rejected(
        "disallowed artifact source",
        lambda: validate_submitted_packet_artifact_path_allowlist(disallowed_artifact_probe, issue_8_path),
        "outside the submitted evidence artifact allowlist",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an EV4 responsive evidence intake packet.")
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET, help="Path to the evidence intake packet JSON. Defaults to the valid fixture.")
    parser.add_argument("--skip-schema-suite", action="store_true", help="Skip the full schema/fixture suite and validate only the submitted packet semantics.")
    parser.add_argument("--submitted-mode", action="store_true", help="Require an explicit real_issue_submission packet and reject sample, fixture, template, and placeholder evidence.")
    parser.add_argument("--self-test", action="store_true", help="Run evidence-intake semantic boundary self-tests without treating probes as submitted evidence.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.self_test:
            run_self_test()
            print("Evidence intake self-tests passed")
            return 0
        packet_path = args.packet if args.packet.is_absolute() else ROOT / args.packet
        validate_packet(packet_path, run_full_schema_validator=not args.skip_schema_suite, submitted_mode=args.submitted_mode)
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
