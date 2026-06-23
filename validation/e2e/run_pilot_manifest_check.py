#!/usr/bin/env python3
"""Validate the smart-home connector pilot harness.

This check is intentionally repository-local. It validates the pilot manifest,
required file references, stage routing metadata, placeholder policy, and release
claim boundaries. It does not validate real Elementor rendering, export JSON,
Playwright screenshots, or production readiness.
"""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "examples" / "smart-home-connector" / "PILOT_MANIFEST.json"
SCHEMA_PATH = ROOT / "schemas" / "ev4-responsive-pilot-manifest.schema.json"

REQUIRED_STAGES = {
    "main-pipeline-handoff-ingest",
    "responsive-evidence-ingest-ledger",
    "desktop-baseline-lock",
    "breakpoint-inventory-lock",
    "breakpoint-observation",
    "responsive-failure-map",
    "failure-priority-ordering",
    "unknown-budget-gate-lite",
    "repair-ownership-routing",
    "repair-option-analysis",
    "responsive-repair-selection",
    "repair-scope-freeze",
    "responsive-repair-plan",
    "responsive-final-audit-lite",
}

REQUIRED_CONDITIONAL_OR_SKIPPED = {
    "repair-triage",
    "responsive-observation-evidence-ledger",
    "css-selector-safety-check",
    "accessibility-reading-order-gate",
    "builder-feedback-loop",
    "multi-run-convergence-gate",
    "partial-repair-state",
}

REQUIRED_LITE_GATES = {
    "main_pipeline_input_authorization",
    "desktop_baseline_lock",
    "breakpoint_inventory_lock",
    "forbidden_inference_check",
    "unknown_gate_lite",
    "architecture_mutation_veto_check",
    "repair_option_analysis_before_selection",
    "repair_scope_freeze_before_steps",
    "final_audit_lite_verdict",
}

REQUIRED_STOP_CONDITIONS = {
    "missing_main_ev4_handoff",
    "selected_candidate_identity_conflict",
    "desktop_baseline_missing",
    "breakpoint_inventory_missing_or_unusable",
    "unknown_required_to_select_repair_unresolved",
    "architecture_mutation_veto_triggered",
    "meaningful_content_must_be_hidden_to_fit",
    "builder_reports_unexpected_desktop_regression",
}

REQUIRED_FORBIDDEN_CLAIMS = {
    "production_ready",
    "live_render_validated",
    "export_validated",
    "pixel_perfect",
    "accessibility_passed",
    "Playwright_validated",
}

REQUIRED_FILE_KEYS = {
    "runbook",
    "evidence_manifest_template",
    "evidence_manifest_valid_example",
    "input_authorization_record_template",
    "breakpoint_observation_notes_template",
    "failure_map_template",
    "repair_option_template",
    "repair_selection_record_template",
    "remaining_unknowns_template",
    "builder_checklist_template",
    "final_audit_lite_template",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return data


def assert_subset(name: str, required: set[str], actual: set[str]) -> None:
    missing = sorted(required - actual)
    if missing:
        raise AssertionError(f"{name} missing required values: {missing}")


def validate_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("schema") != "ev4-responsive-pilot-manifest@0.1.0":
        raise AssertionError("pilot manifest schema discriminator mismatch")
    if manifest.get("production_ready") is not False:
        raise AssertionError("pilot manifest must not be production_ready")
    if manifest.get("mode") != "shadow_mode_manual":
        raise AssertionError("pilot manifest must remain shadow_mode_manual")

    sequence = manifest.get("required_sequence")
    if not isinstance(sequence, list):
        raise AssertionError("required_sequence must be a list")
    assert_subset("required_sequence", REQUIRED_STAGES, set(sequence))

    skipped = manifest.get("skipped_or_conditional_stages")
    if not isinstance(skipped, dict):
        raise AssertionError("skipped_or_conditional_stages must be an object")
    assert_subset("skipped_or_conditional_stages", REQUIRED_CONDITIONAL_OR_SKIPPED, set(skipped))
    for stage, meta in skipped.items():
        if not isinstance(meta, dict) or "status" not in meta:
            raise AssertionError(f"skipped/conditional stage {stage} must include status")
        status = meta["status"]
        if status == "conditional" and not meta.get("runs_when"):
            raise AssertionError(f"conditional stage {stage} must include runs_when")
        if status != "conditional" and not meta.get("reason"):
            raise AssertionError(f"non-conditional stage {stage} must include reason")

    lite_gates = manifest.get("required_lite_gates")
    if not isinstance(lite_gates, list):
        raise AssertionError("required_lite_gates must be a list")
    assert_subset("required_lite_gates", REQUIRED_LITE_GATES, set(lite_gates))

    stop_conditions = manifest.get("stop_conditions")
    if not isinstance(stop_conditions, list):
        raise AssertionError("stop_conditions must be a list")
    assert_subset("stop_conditions", REQUIRED_STOP_CONDITIONS, set(stop_conditions))

    forbidden_claims = manifest.get("forbidden_claims")
    if not isinstance(forbidden_claims, list):
        raise AssertionError("forbidden_claims must be a list")
    assert_subset("forbidden_claims", REQUIRED_FORBIDDEN_CLAIMS, set(forbidden_claims))

    policy = manifest.get("template_placeholder_policy")
    if not isinstance(policy, dict):
        raise AssertionError("template_placeholder_policy must be an object")
    if policy.get("template_files_may_contain_TODO") is not True:
        raise AssertionError("templates must explicitly allow TODO placeholders")
    if policy.get("executable_pilot_files_must_not_contain_TODO") is not True:
        raise AssertionError("executable pilot files must ban TODO placeholders")
    if policy.get("executable_pilot_files_must_not_contain_null_for_required_claims") is not True:
        raise AssertionError("executable pilot files must ban null required claims")

    files = manifest.get("pilot_files")
    if not isinstance(files, dict):
        raise AssertionError("pilot_files must be an object")
    assert_subset("pilot_files", REQUIRED_FILE_KEYS, set(files))
    for key, relative_path in files.items():
        if not isinstance(relative_path, str) or not relative_path:
            raise AssertionError(f"pilot_files.{key} must be a non-empty string")
        if not (ROOT / relative_path).exists():
            raise AssertionError(f"pilot file does not exist: {relative_path}")


def validate_schema_file_exists() -> None:
    schema = load_json(SCHEMA_PATH)
    if schema.get("title") != "EV4 Responsive Pilot Manifest":
        raise AssertionError("pilot manifest schema title mismatch")


def main() -> int:
    try:
        validate_schema_file_exists()
        validate_manifest(load_json(MANIFEST_PATH))
    except AssertionError as exc:
        print(f"Pilot manifest check failed: {exc}", file=sys.stderr)
        return 1
    except Exception:  # noqa: BLE001
        print("Pilot manifest check failed with an unexpected error:", file=sys.stderr)
        traceback.print_exc()
        return 1
    print("Pilot manifest check passed: smart-home connector pilot harness is structurally valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
