#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "planning" / "EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json"
SCHEMA = ROOT / "schemas" / "ev4-automation-work-package-catalog.schema.json"

FORBIDDEN_CLAIMS = {
    "production_ready",
    "release_ready",
    "live_render_validated",
    "export_json_validated",
    "accessibility_passed",
    "pixel_perfect",
    "responsive_correctness_validated",
}
REQUIRED_GATES = {
    "python validation/e2e/run_automation_work_package_catalog_check.py",
    "python validation/e2e/run_automation_control_state_check.py",
    "python validation/e2e/run_rolling_queue_check.py",
    "python validation/e2e/run_run_ledger_check.py",
    "python validation/e2e/run_task_quality_gate_check.py",
}
SELECTION_TRUE = {
    "controller_must_select_from_catalog_only",
    "exactly_one_work_package_or_slice_per_run",
    "arbitrary_rtaq_task_invention_forbidden",
    "micro_task_invention_forbidden",
    "checkpoint_only_loop_forbidden",
    "artificial_reserve_tasks_forbidden",
    "guard_only_work_requires_named_work_package_unblock",
    "open_prs_must_be_reconciled_before_new_selection",
    "reviewable_pr_slices_required",
    "split_by_layer_under_same_work_package_id",
}
EXECUTION_EXPECTED = {
    "active_work_package_limit": 1,
    "continue_active_before_starting_new": True,
    "reconcile_open_pr_before_new_mutation": True,
    "complete_same_objective_in_one_run_when_safe": True,
    "open_pr_blocks_new_mutation_pr": True,
}
REPLENISHMENT_EXPECTED = {
    "ready_work_package_target": 3,
    "refresh_when_ready_below": 2,
    "max_ready_work_packages": 5,
    "state_driven_refresh": True,
    "fixed_ordinal_refresh_forbidden": True,
    "artificial_work_packages_forbidden": True,
    "checkpoint_only_work_forbidden": True,
    "bookkeeping_only_work_forbidden": True,
    "catalog_replenishment_must_not_block_active_execution": True,
    "catalog_replenishment_must_respect_single_active_pr_policy": True,
    "catalog_changes_require_schema_validation": True,
    "catalog_changes_require_ci": True,
    "catalog_changes_require_reviewable_pr": True,
}
STATE_TRIGGERS = {
    "ready_work_package_depth_below_threshold",
    "active_work_package_completed_and_project_state_changed",
    "material_blocker_changed_priorities",
    "core_contract_or_architecture_changed",
    "no_executable_work_package_exists_and_real_project_gap_detected",
}
FORBIDDEN_REFRESH = {
    "fixed_task_ordinal_reached",
    "every_fifth_task",
    "after_four_tasks_create_next_four",
    "fixed_count_reached",
    "checkpoint_only_refresh",
    "bookkeeping_only_refresh",
}
ACTIVE_ALLOWED = [
    "detect_catalog_depth",
    "report_replenishment_needed",
    "prepare_non_mutating_replenishment_plan",
    "update_catalog_only_if_in_scope_for_same_active_pr",
]
ACTIVE_FORBIDDEN = [
    "create_parallel_catalog_pr",
    "interrupt_active_work_package",
    "start_unrelated_catalog_mutation",
    "create_checkpoint_only_catalog_refresh_pr",
]
NO_ACTIVE_ALLOWED = [
    "continue_active_work_package",
    "select_next_ready_work_package",
    "create_catalog_replenishment_pr_if_ready_depth_below_threshold",
    "update_catalog_as_part_of_same_material_work_package_if_in_scope",
]
REQUIREMENTS_TRUE = {
    "measurable_current_state_required",
    "measurable_target_state_required",
    "capability_level_outcome_required",
    "truth_boundaries_required",
    "acceptance_gates_required",
    "negative_fixture_coverage_when_applicable",
    "estimated_percentage_is_reporting_only",
}
MATERIAL_TERMS = (
    "schema",
    "validator",
    "ci",
    "fixture",
    "handoff",
    "submitted-mode",
    "boundary",
    "readiness",
    "catalog",
    "evidence",
    "contract",
    "quality",
)
BAD_SELECTABLE_TERMS = (
    "checkpoint-only",
    "checkpoint only",
    "bookkeeping-only",
    "bookkeeping only",
    "status-only",
    "status only",
    "artificial reserve",
    "pending depth reserve",
    "keep task count",
    "keep queue depth",
)
FIXED_TERMS = ("every fifth", "fifth task", "after four tasks", "next four tasks", "fixed ordinal", "fixed count")
REQUIRED_SPLIT_FORBIDDEN = {
    "invent_unrelated_rtaq_tasks",
    "guard_only_task_without_named_work_package_unblock",
    "checkpoint_only_pr_after_every_merge",
    "artificial_reserve_task_to_keep_task_count_high",
    "queue_refresh_loop_as_execution_driver",
    "fixed_ordinal_refresh",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            fail(f"duplicate JSON object key: {key}")
        out[key] = value
    return out


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
    if not isinstance(payload, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    return payload


def assert_canonical_readable_format(path: Path, payload: dict[str, Any]) -> None:
    """Fail when the catalog is compact/minified or lacks the canonical trailing newline."""
    actual = path.read_text(encoding="utf-8")
    expected = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if actual != expected:
        fail(
            f"{path.relative_to(ROOT)} must use canonical readable JSON format "
            "(json.dumps(data, indent=2, ensure_ascii=False) plus one trailing newline)"
        )


def schema_errors(payload: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda error: [str(part) for part in error.path])
    return [f"{'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}" for error in errors]


def assert_schema_valid(payload: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    errors = schema_errors(payload, schema)
    if errors:
        fail(f"{label} must validate against schema: {errors[0]}")


def assert_schema_invalid(payload: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    if not schema_errors(payload, schema):
        fail(f"invalid payload unexpectedly passed schema validation: {label}")


def text_blob(value: Any) -> str:
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, list):
        return "\n".join(text_blob(item) for item in value)
    if isinstance(value, dict):
        return "\n".join(text_blob(item) for item in value.values())
    return ""


def positive_blob(wp: dict[str, Any]) -> str:
    return text_blob(
        {
            "title": wp["title"],
            "current_state": wp["current_state"],
            "target_state": wp["target_state"],
            "measurable_current_state": wp["measurable_current_state"],
            "measurable_target_state": wp["measurable_target_state"],
            "target_capability": wp["target_capability"],
            "expected_project_delta": wp["expected_project_delta"],
            "allowed_work": wp["allowed_work"],
            "must_deliver": wp["must_deliver"],
        }
    )


def assert_policy(catalog: dict[str, Any]) -> None:
    if catalog["execution_driver"] == "rolling_queue":
        fail("rolling_queue must not be restored as execution driver")
    for key in SELECTION_TRUE:
        if catalog["selection_policy"].get(key) is not True:
            fail(f"selection_policy must keep {key}=true")
    if catalog["execution_policy"] != EXECUTION_EXPECTED:
        fail("execution_policy must preserve one active Work Package and single-active-mutation PR discipline")
    repl = catalog["catalog_replenishment_policy"]
    for key, expected in REPLENISHMENT_EXPECTED.items():
        if repl.get(key) != expected:
            fail(f"catalog_replenishment_policy mismatch for {key}")
    if set(repl["state_driven_triggers"]) != STATE_TRIGGERS:
        fail("catalog replenishment must be state-driven by the approved trigger set")
    if set(repl["forbidden_refresh_triggers"]) != FORBIDDEN_REFRESH:
        fail("catalog replenishment must explicitly reject fixed ordinal refresh triggers")
    if repl["when_active_pr_exists"]["allowed"] != ACTIVE_ALLOWED:
        fail("when_active_pr_exists.allowed must be non-mutating or same-PR in-scope only")
    if repl["when_active_pr_exists"]["forbidden"] != ACTIVE_FORBIDDEN:
        fail("when_active_pr_exists.forbidden must block parallel catalog PR and interruptions")
    if repl["when_no_active_pr_exists"]["allowed"] != NO_ACTIVE_ALLOWED:
        fail("when_no_active_pr_exists.allowed must preserve automatic planning without fixed ordinal refresh")
    if "create_parallel_catalog_pr" in repl["when_active_pr_exists"]["allowed"]:
        fail("active PR policy must not allow parallel catalog PR creation")
    for key in REQUIREMENTS_TRUE:
        if catalog["work_package_requirements"].get(key) is not True:
            fail(f"work_package_requirements must keep {key}=true")
    for key, value in catalog["global_boundaries"].items():
        if value is not False:
            fail(f"global boundary must keep {key}=false")


def assert_boundaries(wp_id: str, wp: dict[str, Any]) -> None:
    evidence = wp["evidence_boundary"]
    for key in [
        "submitted_evidence_created_by_package",
        "issue_8_mutation_allowed",
        "real_pilot_execution_allowed",
        "ci_success_is_domain_evidence",
        "merged_pr_is_domain_evidence",
        "catalog_completion_is_evidence_validation",
    ]:
        if evidence.get(key) is not False:
            fail(f"{wp_id} must keep {key}=false")
    if evidence.get("claims_require_real_evidence_gates") is not True:
        fail(f"{wp_id} must require real evidence gates")
    if set(evidence.get("forbidden_claims_without_real_evidence", [])) != FORBIDDEN_CLAIMS:
        fail(f"{wp_id} must list all forbidden stronger claims")
    readiness = wp["readiness_boundary"]
    for key in ["pilot_allowed_to_start", *sorted(FORBIDDEN_CLAIMS)]:
        if readiness.get(key) is not False:
            fail(f"{wp_id} must keep readiness boundary {key}=false")


def assert_work_package(wp_id: str, wp: dict[str, Any]) -> None:
    if wp["id"] != wp_id:
        fail(f"Work Package key/id mismatch: {wp_id}")
    if wp["reporting"].get("estimated_percentage_is_reporting_only") is not True:
        fail(f"{wp_id} estimated percentage must be reporting-only")
    for key in ["measurable_current_state", "measurable_target_state", "target_capability"]:
        if wp[key].get("measurable") is not True:
            fail(f"{wp_id} missing measurable {key}")
    blob = positive_blob(wp)
    if not any(term in blob for term in MATERIAL_TERMS):
        fail(f"{wp_id} must describe a capability-level outcome")
    if wp["selectable"]:
        if wp.get("ready_state") == "governance":
            fail(f"{wp_id} selectable package cannot use governance ready_state")
        for term in BAD_SELECTABLE_TERMS:
            if term in blob:
                fail(f"{wp_id} is selectable but checkpoint/bookkeeping/artificial-only")
        for term in FIXED_TERMS:
            if term in blob:
                fail(f"{wp_id} is selectable but carries fixed ordinal refresh behavior")
    else:
        if wp.get("maintenance_type") != "non_selectable_state_driven_catalog_replenishment_governance":
            fail(f"{wp_id} non-selectable package must be state-driven governance")
        if wp.get("ready_state") != "governance":
            fail(f"{wp_id} non-selectable governance package must use ready_state=governance")
    assert_boundaries(wp_id, wp)
    if REQUIRED_GATES - set(wp["quality_gates"]):
        fail(f"{wp_id} missing required quality gates")
    if REQUIRED_SPLIT_FORBIDDEN - set(wp["split_rule"].get("forbidden_splits", [])):
        fail(f"{wp_id} split rule missing forbidden split examples")
    seen: set[str] = set()
    for item in wp["allowed_pr_slices"]:
        match = re.match(r"^(WP-RESP-[0-9]{3})/PR-[A-Z]$", item["slice_id"])
        if not match or match.group(1) != wp_id:
            fail(f"{wp_id} has invalid or cross-package slice id")
        if item["slice_id"] in seen:
            fail(f"{wp_id} duplicate PR slice")
        seen.add(item["slice_id"])
    forbidden_text = text_blob(wp["forbidden_work"])
    for term in ["submitted evidence", "issue #8", "pilot", "production_ready", "ci success", "catalog completion"]:
        if term not in forbidden_text:
            fail(f"{wp_id} forbidden_work must preserve {term}")


def assert_ready_depth(catalog: dict[str, Any]) -> None:
    policy = catalog["catalog_replenishment_policy"]
    ready = [wp_id for wp_id, wp in catalog["work_packages"].items() if wp["selectable"] and wp.get("ready_state") == "ready"]
    if len(ready) > policy["max_ready_work_packages"]:
        fail("ready depth exceeds max_ready_work_packages")
    if len(ready) < policy["refresh_when_ready_below"] and "WP-RESP-005" not in catalog["work_packages"]:
        fail("ready depth below threshold requires governance package")
    governance = catalog["work_packages"].get("WP-RESP-005")
    if not governance or governance["selectable"] is not False or governance.get("ready_state") != "governance":
        fail("WP-RESP-005 must remain non-selectable state-driven governance")


def assert_catalog(catalog: dict[str, Any], schema: dict[str, Any]) -> None:
    assert_schema_valid(catalog, schema, "automation work package catalog")
    assert_policy(catalog)
    ids = [wp["id"] for wp in catalog["work_packages"].values()]
    if len(ids) != len(set(ids)):
        fail("duplicate Work Package IDs are forbidden")
    for wp_id, wp in catalog["work_packages"].items():
        assert_work_package(wp_id, wp)
    assert_ready_depth(catalog)


def fixture_wp(wp_id: str, selectable: bool = True) -> dict[str, Any]:
    state = "ready" if selectable else "governance"
    wp = {
        "id": wp_id,
        "title": "Schema Validator Capability Package",
        "capability_area": "validation_chain" if selectable else "catalog_governance",
        "current_state": "Validator behavior exists but needs measurable catalog-backed package coverage.",
        "target_state": "Schema, validator, fixture, CI, and documentation coverage are materially improved.",
        "measurable_current_state": {"statement": "Validator behavior exists but needs measurable catalog-backed package coverage.", "measurement": "Measured by schema, validator, fixture, CI, and documentation coverage.", "measurable": True},
        "measurable_target_state": {"statement": "Schema, validator, fixture, CI, and documentation coverage are materially improved.", "measurement": "Measured by deterministic validator and CI command success.", "measurable": True},
        "target_capability": {"statement": "Schema, validator, fixture, CI, and documentation coverage are materially improved.", "measurement": "A deterministic validator and CI command can verify package behavior.", "measurable": True},
        "expected_project_delta": "Adds deterministic validator and CI-visible fixture coverage for a real repository capability area.",
        "selectable": selectable,
        "ready_state": state,
        "priority": 50,
        "reporting": {"estimated_completion_percentage": 10, "estimated_percentage_is_reporting_only": True},
        "allowed_work": ["Add schema, validator, fixture, documentation, and CI wiring for this material capability."],
        "forbidden_work": ["Do not create submitted evidence unless explicitly authorized.", "Do not mutate Issue #8 or mark Issue #8 evidence as satisfied.", "Do not run or authorize real pilot execution.", "Do not claim production_ready, release_ready, live_render_validated, export_json_validated, accessibility_passed, pixel_perfect, or responsive_correctness_validated.", "Do not treat CI success, merged PRs, catalog completion, Work Package completion, or queue completion as domain evidence."],
        "must_deliver": ["Schema and validator coverage for the material capability."],
        "must_preserve": ["Rolling queue remains a historical reconciled archive, not the execution driver.", "Controller selection must come only from the catalog.", "Quality gates, CI, review, and evidence boundaries remain mandatory.", "Technical evidence claims remain false unless real evidence gates pass."],
        "evidence_boundary": {"submitted_evidence_created_by_package": False, "issue_8_mutation_allowed": False, "real_pilot_execution_allowed": False, "ci_success_is_domain_evidence": False, "merged_pr_is_domain_evidence": False, "catalog_completion_is_evidence_validation": False, "claims_require_real_evidence_gates": True, "forbidden_claims_without_real_evidence": sorted(FORBIDDEN_CLAIMS)},
        "readiness_boundary": {"pilot_allowed_to_start": False, **{key: False for key in sorted(FORBIDDEN_CLAIMS)}},
        "definition_of_done": ["Schema validates.", "Validator passes.", "CI command is listed."],
        "quality_gates": sorted(REQUIRED_GATES),
        "split_rule": {"principle": "A Work Package may be large in objective, but each PR must remain reviewable.", "split_by": "implementation_layer_under_same_work_package_id", "requires_slice_id_prefix": "<WORK_PACKAGE_ID>/PR-", "forbidden_splits": sorted(REQUIRED_SPLIT_FORBIDDEN)},
        "allowed_pr_slices": [{"slice_id": f"{wp_id}/PR-A", "title": "schema and fixtures", "layer": "schema_fixtures", "objective": "Add schema and fixture coverage for the material capability.", "review_boundary": "One reviewable slice under the same Work Package ID."}],
        "blocked_if": ["Required owner contract is missing or ambiguous."],
        "completion_record_requirements": ["Record selected Work Package ID and PR slice ID.", "List files changed.", "List validators changed.", "State commands run and not run.", "Restate evidence and pilot boundaries."],
        "unblocks_work_package_ids": [],
    }
    if not selectable:
        wp["maintenance_type"] = "non_selectable_state_driven_catalog_replenishment_governance"
    return wp


def fixture_catalog() -> dict[str, Any]:
    return {
        "schema": "ev4-automation-work-package-catalog@1.0.0",
        "project": "EV4 Responsive Architect",
        "catalog_path": "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json",
        "catalog_status": "approved_material_objective_source",
        "execution_driver": "work_package_catalog_guard",
        "rolling_queue_authority": "historical_reconciled_archive",
        "selection_policy": {key: True for key in sorted(SELECTION_TRUE)},
        "execution_policy": dict(EXECUTION_EXPECTED),
        "catalog_replenishment_policy": {**dict(REPLENISHMENT_EXPECTED), "state_driven_triggers": sorted(STATE_TRIGGERS), "forbidden_refresh_triggers": sorted(FORBIDDEN_REFRESH), "when_active_pr_exists": {"allowed": list(ACTIVE_ALLOWED), "forbidden": list(ACTIVE_FORBIDDEN)}, "when_no_active_pr_exists": {"allowed": list(NO_ACTIVE_ALLOWED)}},
        "work_package_requirements": {key: True for key in sorted(REQUIREMENTS_TRUE)},
        "global_boundaries": {"submitted_evidence_created_by_catalog": False, "issue_8_mutation_allowed_by_catalog": False, "real_pilot_execution_allowed_by_catalog": False, "catalog_completion_is_evidence_validation": False, "ci_success_is_responsive_correctness_evidence": False, **{key: False for key in sorted(FORBIDDEN_CLAIMS)}},
        "work_packages": {"WP-RESP-998": fixture_wp("WP-RESP-998"), "WP-RESP-005": fixture_wp("WP-RESP-005", selectable=False)},
    }


def assert_invalid(catalog: dict[str, Any], schema: dict[str, Any], expected: str) -> None:
    try:
        assert_catalog(catalog, schema)
    except AssertionError as exc:
        if expected not in str(exc):
            fail(f"self-test produced unexpected diagnostic: {exc}")
        return
    fail(f"invalid catalog was accepted: {expected}")


def run_self_tests() -> None:
    schema = load_json(SCHEMA)
    valid = fixture_catalog()
    assert_catalog(valid, schema)
    missing_id = copy.deepcopy(valid); missing_id["work_packages"]["WP-RESP-998"].pop("id")
    assert_schema_invalid(missing_id, schema, "missing Work Package id")
    duplicate_id = copy.deepcopy(valid); duplicate_id["work_packages"]["WP-RESP-997"] = fixture_wp("WP-RESP-998")
    assert_invalid(duplicate_id, schema, "duplicate Work Package IDs")
    fixed_refresh = copy.deepcopy(valid); fixed_refresh["catalog_replenishment_policy"]["fixed_ordinal_refresh_forbidden"] = False
    assert_schema_invalid(fixed_refresh, schema, "invalid fixed ordinal refresh")
    blocks_active = copy.deepcopy(valid); blocks_active["catalog_replenishment_policy"]["catalog_replenishment_must_not_block_active_execution"] = False
    assert_schema_invalid(blocks_active, schema, "invalid catalog replenishment blocks active execution")
    parallel_pr = copy.deepcopy(valid); parallel_pr["catalog_replenishment_policy"]["when_active_pr_exists"]["allowed"][0] = "create_parallel_catalog_pr"
    assert_invalid(parallel_pr, schema, "when_active_pr_exists.allowed")
    checkpoint_only = copy.deepcopy(valid); checkpoint_only["work_packages"]["WP-RESP-998"]["expected_project_delta"] = "checkpoint-only status-only bookkeeping-only schema validator fixture CI placeholder"
    assert_invalid(checkpoint_only, schema, "checkpoint/bookkeeping")
    percentage_without_target = copy.deepcopy(valid); percentage_without_target["work_packages"]["WP-RESP-998"].pop("measurable_target_state")
    assert_schema_invalid(percentage_without_target, schema, "percentage but no measurable target_state")
    governance = copy.deepcopy(valid); governance["work_packages"] = {"WP-RESP-005": fixture_wp("WP-RESP-005", selectable=False), "WP-RESP-998": fixture_wp("WP-RESP-998")}
    assert_catalog(governance, schema)
    bad_governance = copy.deepcopy(valid); bad_governance["work_packages"]["WP-RESP-005"]["selectable"] = True
    assert_invalid(bad_governance, schema, "selectable package cannot use governance")
    rolling_queue_driver = copy.deepcopy(valid); rolling_queue_driver["execution_driver"] = "rolling_queue"
    assert_schema_invalid(rolling_queue_driver, schema, "rolling queue driver")
    compact_text = json.dumps(valid, separators=(",", ":")) + "\n"
    if compact_text == json.dumps(valid, indent=2, ensure_ascii=False) + "\n":
        fail("canonical format self-test fixture is invalid")


def main() -> int:
    run_self_tests()
    schema = load_json(SCHEMA)
    catalog = load_json(CATALOG)
    assert_canonical_readable_format(CATALOG, catalog)
    assert_catalog(catalog, schema)
    print("automation work package catalog check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
