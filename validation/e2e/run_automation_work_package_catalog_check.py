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

EXPECTED_SCHEMA_ID = "ev4-automation-work-package-catalog@1.0.0"
EXPECTED_DRIVER = "work_package_catalog_guard"
WORK_PACKAGE_ID_RE = re.compile(r"^WP-RESP-[0-9]{3}$")
SLICE_ID_RE = re.compile(r"^(WP-RESP-[0-9]{3})/PR-[A-Z]$")
FORBIDDEN_CLAIMS = {
    "production_ready",
    "release_ready",
    "live_render_validated",
    "export_json_validated",
    "accessibility_passed",
    "pixel_perfect",
    "responsive_correctness_validated",
}
FALSE_GLOBAL_BOUNDARIES = {
    "submitted_evidence_created_by_catalog",
    "issue_8_mutation_allowed_by_catalog",
    "real_pilot_execution_allowed_by_catalog",
    "catalog_completion_is_evidence_validation",
    "ci_success_is_responsive_correctness_evidence",
    *FORBIDDEN_CLAIMS,
}
FALSE_EVIDENCE_BOUNDARIES = {
    "submitted_evidence_created_by_package",
    "issue_8_mutation_allowed",
    "real_pilot_execution_allowed",
    "ci_success_is_domain_evidence",
    "merged_pr_is_domain_evidence",
    "catalog_completion_is_evidence_validation",
}
FALSE_READINESS_BOUNDARIES = {"pilot_allowed_to_start", *FORBIDDEN_CLAIMS}
SELECTION_POLICY_TRUE = {
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
ARTIFICIAL_TERMS = (
    "pending depth reserve",
    "artificial reserve",
    "keep task count",
    "keep queue depth",
    "reserve task",
    "queue refresh loop",
)
BOOKKEEPING_ONLY_TERMS = (
    "checkpoint-only",
    "checkpoint only",
    "bookkeeping-only",
    "bookkeeping only",
    "status-only",
    "status only",
    "merge-final-only",
)
GUARD_ONLY_TERMS = ("guard-only", "guard only")
MATERIAL_CAPABILITY_TERMS = (
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
)
FORBIDDEN_POSITIVE_CLAIM_PATTERNS = (
    r"\bclaim(?:s|ed)?\s+(?:production|release|readiness|responsive correctness|accessibility|pixel|live render|export)",
    r"\bmark(?:s|ed)?\s+(?:production|release|readiness)",
    r"\bauthori[sz]e(?:s|d)?\s+(?:real\s+)?pilot",
    r"\brun(?:s|ning)?\s+(?:the\s+)?(?:real\s+)?pilot",
    r"\bprove(?:s|d)?\s+responsive correctness",
)
REQUIRED_FORBIDDEN_SPLITS = {
    "invent_unrelated_rtaq_tasks",
    "guard_only_task_without_named_work_package_unblock",
    "checkpoint_only_pr_after_every_merge",
    "artificial_reserve_task_to_keep_task_count_high",
}
REQUIRED_QUALITY_GATES = {
    "python validation/e2e/run_automation_work_package_catalog_check.py",
    "python validation/e2e/run_automation_control_state_check.py",
    "python validation/e2e/run_rolling_queue_check.py",
    "python validation/e2e/run_run_ledger_check.py",
    "python validation/e2e/run_task_quality_gate_check.py",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def reject_duplicate_keys_object_pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fail(f"missing JSON file: {path.relative_to(ROOT)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys_object_pairs_hook)
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{path.relative_to(ROOT)} must be a JSON object")
    return payload


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
        fail(f"invalid catalog unexpectedly passed schema validation: {label}")


def text_fields(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            out.extend(text_fields(item))
        return out
    if isinstance(value, dict):
        out: list[str] = []
        for item in value.values():
            out.extend(text_fields(item))
        return out
    return []


def text_blob(value: Any) -> str:
    return "\n".join(text_fields(value)).lower()


def assert_no_positive_forbidden_claims(wp_id: str, wp: dict[str, Any]) -> None:
    scanned = "\n".join(text_fields({"allowed_work": wp["allowed_work"], "must_deliver": wp["must_deliver"]})).lower()
    for pattern in FORBIDDEN_POSITIVE_CLAIM_PATTERNS:
        if re.search(pattern, scanned):
            fail(f"{wp_id} appears to allow a forbidden readiness/evidence claim: {pattern}")


def assert_boundary_objects(wp_id: str, wp: dict[str, Any]) -> None:
    evidence = wp["evidence_boundary"]
    for key in FALSE_EVIDENCE_BOUNDARIES:
        if evidence.get(key) is not False:
            fail(f"{wp_id} evidence boundary must keep {key}=false")
    if evidence.get("claims_require_real_evidence_gates") is not True:
        fail(f"{wp_id} must require real evidence gates for stronger claims")
    if set(evidence.get("forbidden_claims_without_real_evidence", [])) != FORBIDDEN_CLAIMS:
        fail(f"{wp_id} must list every forbidden claim without real evidence")
    readiness = wp["readiness_boundary"]
    for key in FALSE_READINESS_BOUNDARIES:
        if readiness.get(key) is not False:
            fail(f"{wp_id} readiness boundary must keep {key}=false")


def assert_material_delta(wp_id: str, wp: dict[str, Any]) -> None:
    blob = text_blob({
        "title": wp["title"],
        "current_state": wp["current_state"],
        "target_state": wp["target_state"],
        "target_capability": wp["target_capability"],
        "expected_project_delta": wp["expected_project_delta"],
        "allowed_work": wp["allowed_work"],
        "must_deliver": wp["must_deliver"],
    })
    if not wp["target_capability"].get("measurable"):
        fail(f"{wp_id} must declare a measurable target capability")
    if not any(term in blob for term in MATERIAL_CAPABILITY_TERMS):
        fail(f"{wp_id} must have a measurable target capability, not generic prose")
    if any(term in blob for term in ARTIFICIAL_TERMS):
        fail(f"{wp_id} contains artificial reserve/queue-depth language")
    if wp["selectable"] and any(term in blob for term in BOOKKEEPING_ONLY_TERMS):
        fail(f"{wp_id} is selectable but checkpoint/bookkeeping-only")
    if wp["selectable"] and any(term in blob for term in GUARD_ONLY_TERMS):
        fail(f"{wp_id} is selectable but guard-only")


def assert_guard_only_policy(wp_id: str, wp: dict[str, Any]) -> None:
    blob = text_blob(wp)
    is_guard_only = any(term in blob for term in GUARD_ONLY_TERMS)
    if is_guard_only and not wp.get("unblocks_work_package_ids"):
        fail(f"{wp_id} guard-only work must unblock a named Work Package")
    if not wp["selectable"] and wp.get("maintenance_type") != "non_selectable_material_state_change_governance":
        fail(f"{wp_id} non-selectable package must declare non-selectable maintenance governance")


def assert_split_rule(wp_id: str, wp: dict[str, Any]) -> None:
    split_rule = wp["split_rule"]
    if split_rule["split_by"] != "implementation_layer_under_same_work_package_id":
        fail(f"{wp_id} split rule must split by implementation layer under the same Work Package ID")
    forbidden_splits = set(split_rule.get("forbidden_splits", []))
    if REQUIRED_FORBIDDEN_SPLITS - forbidden_splits:
        fail(f"{wp_id} split rule is missing forbidden split examples")
    seen_slices: set[str] = set()
    for slice_item in wp["allowed_pr_slices"]:
        slice_id = slice_item["slice_id"]
        match = SLICE_ID_RE.match(slice_id)
        if not match:
            fail(f"{wp_id} has invalid slice id: {slice_id}")
        if match.group(1) != wp_id:
            fail(f"{wp_id} slice {slice_id} must stay under the same Work Package ID")
        if slice_id in seen_slices:
            fail(f"{wp_id} duplicate slice id: {slice_id}")
        seen_slices.add(slice_id)
    if wp["selectable"] and not seen_slices:
        fail(f"{wp_id} selectable Work Package must define at least one reviewable PR slice")


def assert_quality_gates(wp_id: str, wp: dict[str, Any]) -> None:
    gates = set(wp["quality_gates"])
    missing = REQUIRED_QUALITY_GATES - gates
    if missing:
        fail(f"{wp_id} missing required quality gates: {sorted(missing)[0]}")
    forbidden_blob = text_blob(wp["forbidden_work"])
    required_terms = ["submitted evidence", "issue #8", "pilot", "production_ready", "ci success"]
    for term in required_terms:
        if term not in forbidden_blob:
            fail(f"{wp_id} forbidden_work must explicitly preserve boundary: {term}")


def assert_work_package(wp_id: str, wp: dict[str, Any]) -> None:
    if wp["id"] != wp_id:
        fail(f"Work Package key/id mismatch: {wp_id} != {wp['id']}")
    if not WORK_PACKAGE_ID_RE.match(wp_id):
        fail(f"invalid Work Package ID: {wp_id}")
    assert_material_delta(wp_id, wp)
    assert_guard_only_policy(wp_id, wp)
    assert_boundary_objects(wp_id, wp)
    assert_no_positive_forbidden_claims(wp_id, wp)
    assert_split_rule(wp_id, wp)
    assert_quality_gates(wp_id, wp)
    if len(wp["definition_of_done"]) < 3:
        fail(f"{wp_id} must have material definition_of_done entries")
    if len(wp["completion_record_requirements"]) < 5:
        fail(f"{wp_id} must require completion records")


def assert_catalog(catalog: dict[str, Any], schema: dict[str, Any]) -> None:
    assert_schema_valid(catalog, schema, "automation work package catalog")
    if catalog["execution_driver"] == "rolling_queue":
        fail("rolling_queue must not be restored as execution driver")
    if catalog["execution_driver"] != EXPECTED_DRIVER:
        fail("catalog execution driver mismatch")
    for key in SELECTION_POLICY_TRUE:
        if catalog["selection_policy"].get(key) is not True:
            fail(f"selection policy must keep {key}=true")
    for key in FALSE_GLOBAL_BOUNDARIES:
        if catalog["global_boundaries"].get(key) is not False:
            fail(f"global boundary must keep {key}=false")
    packages = catalog["work_packages"]
    ids = [wp["id"] for wp in packages.values()]
    if len(ids) != len(set(ids)):
        fail("duplicate Work Package IDs are forbidden")
    selectable = [wp_id for wp_id, wp in packages.items() if wp["selectable"]]
    if not selectable:
        fail("catalog must contain at least one selectable material Work Package")
    for wp_id, wp in packages.items():
        assert_work_package(wp_id, wp)


def valid_work_package_fixture(wp_id: str) -> dict[str, Any]:
    return {
        "id": wp_id,
        "title": "Schema Validator Capability Package",
        "capability_area": "validation_chain",
        "current_state": "Validator behavior exists but needs measurable catalog-backed package coverage.",
        "target_state": "Schema, validator, fixture, CI, and documentation coverage are materially improved.",
        "target_capability": {
            "statement": "Schema, validator, fixture, CI, and documentation coverage are materially improved.",
            "measurement": "A deterministic validator and CI command can verify the package behavior.",
            "measurable": True,
        },
        "expected_project_delta": "Adds deterministic validator and CI-visible fixture coverage for a real repository capability area.",
        "selectable": True,
        "priority": 50,
        "allowed_work": ["Add schema, validator, fixture, documentation, and CI wiring for this material capability."],
        "forbidden_work": [
            "Do not create submitted evidence unless explicitly authorized.",
            "Do not mutate Issue #8 or mark Issue #8 evidence as satisfied.",
            "Do not run or authorize real pilot execution.",
            "Do not claim production_ready, release_ready, live_render_validated, export_json_validated, accessibility_passed, pixel_perfect, or responsive_correctness_validated.",
            "Do not treat CI success, merged PRs, catalog completion, or queue completion as domain evidence.",
        ],
        "must_deliver": ["Schema and validator coverage for the material capability."],
        "must_preserve": [
            "Rolling queue remains a historical reconciled archive, not the execution driver.",
            "Controller selection must come only from the catalog.",
            "Quality gates, CI, review, and evidence boundaries remain mandatory.",
            "Technical evidence claims remain false unless real evidence gates pass.",
        ],
        "evidence_boundary": {
            "submitted_evidence_created_by_package": False,
            "issue_8_mutation_allowed": False,
            "real_pilot_execution_allowed": False,
            "ci_success_is_domain_evidence": False,
            "merged_pr_is_domain_evidence": False,
            "catalog_completion_is_evidence_validation": False,
            "claims_require_real_evidence_gates": True,
            "forbidden_claims_without_real_evidence": sorted(FORBIDDEN_CLAIMS),
        },
        "readiness_boundary": {"pilot_allowed_to_start": False, **{key: False for key in sorted(FORBIDDEN_CLAIMS)}},
        "definition_of_done": ["Schema validates.", "Validator passes.", "CI command is listed."],
        "quality_gates": sorted(REQUIRED_QUALITY_GATES),
        "split_rule": {
            "principle": "A Work Package may be large in objective, but each PR must remain reviewable.",
            "split_by": "implementation_layer_under_same_work_package_id",
            "requires_slice_id_prefix": "<WORK_PACKAGE_ID>/PR-",
            "forbidden_splits": sorted(REQUIRED_FORBIDDEN_SPLITS),
        },
        "allowed_pr_slices": [
            {
                "slice_id": f"{wp_id}/PR-A",
                "title": "schema and fixtures",
                "layer": "schema_fixtures",
                "objective": "Add schema and fixture coverage for the material capability.",
                "review_boundary": "One reviewable slice under the same Work Package ID.",
            }
        ],
        "blocked_if": ["Required owner contract is missing or ambiguous."],
        "completion_record_requirements": [
            "Record selected Work Package ID and PR slice ID.",
            "List files changed.",
            "List validators changed.",
            "State commands run and not run.",
            "Restate evidence and pilot boundaries.",
        ],
        "unblocks_work_package_ids": [],
    }


def valid_catalog_fixture() -> dict[str, Any]:
    return {
        "schema": EXPECTED_SCHEMA_ID,
        "project": "EV4 Responsive Architect",
        "catalog_path": "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json",
        "catalog_status": "approved_material_objective_source",
        "execution_driver": EXPECTED_DRIVER,
        "rolling_queue_authority": "historical_reconciled_archive",
        "selection_policy": {key: True for key in sorted(SELECTION_POLICY_TRUE)},
        "global_boundaries": {
            "submitted_evidence_created_by_catalog": False,
            "issue_8_mutation_allowed_by_catalog": False,
            "real_pilot_execution_allowed_by_catalog": False,
            "catalog_completion_is_evidence_validation": False,
            "ci_success_is_responsive_correctness_evidence": False,
            **{key: False for key in sorted(FORBIDDEN_CLAIMS)},
        },
        "work_packages": {"WP-RESP-999": valid_work_package_fixture("WP-RESP-999")},
    }


def assert_catalog_invalid(catalog: dict[str, Any], schema: dict[str, Any], expected: str) -> None:
    try:
        assert_catalog(catalog, schema)
    except AssertionError as exc:
        if expected not in str(exc):
            fail(f"self-test produced unexpected diagnostic: {exc}")
        return
    fail(f"invalid catalog was accepted: {expected}")


def run_self_tests() -> None:
    schema = load_json(SCHEMA)
    valid = valid_catalog_fixture()
    assert_catalog(valid, schema)

    missing_id = copy.deepcopy(valid)
    missing_id["work_packages"]["WP-RESP-999"].pop("id")
    assert_schema_invalid(missing_id, schema, "missing Work Package id")

    duplicate_id = copy.deepcopy(valid)
    duplicate_id["work_packages"]["WP-RESP-998"] = valid_work_package_fixture("WP-RESP-999")
    assert_catalog_invalid(duplicate_id, schema, "duplicate Work Package IDs")

    checkpoint_only = copy.deepcopy(valid)
    checkpoint_only["work_packages"]["WP-RESP-999"]["expected_project_delta"] = "checkpoint-only status-only bookkeeping only without schema, validator, fixture, CI, or handoff delta"
    assert_catalog_invalid(checkpoint_only, schema, "checkpoint/bookkeeping-only")

    artificial_reserve = copy.deepcopy(valid)
    artificial_reserve["work_packages"]["WP-RESP-999"]["allowed_work"] = ["Create an artificial reserve task to keep task count high with schema wording."]
    assert_catalog_invalid(artificial_reserve, schema, "artificial reserve")

    guard_only = copy.deepcopy(valid)
    guard_only["work_packages"]["WP-RESP-999"]["allowed_work"] = ["Add guard-only schema validator work without naming an unblock target."]
    assert_catalog_invalid(guard_only, schema, "guard-only")

    bad_split = copy.deepcopy(valid)
    bad_split["work_packages"]["WP-RESP-999"]["split_rule"]["split_by"] = "unrelated_micro_tasks"
    assert_schema_invalid(bad_split, schema, "bad split_by")

    bad_slice = copy.deepcopy(valid)
    bad_slice["work_packages"]["WP-RESP-999"]["allowed_pr_slices"][0]["slice_id"] = "RTAQ-9999"
    assert_schema_invalid(bad_slice, schema, "bad slice id")

    readiness_claim = copy.deepcopy(valid)
    readiness_claim["work_packages"]["WP-RESP-999"]["readiness_boundary"]["production_ready"] = True
    assert_schema_invalid(readiness_claim, schema, "production_ready true")

    global_claim = copy.deepcopy(valid)
    global_claim["global_boundaries"]["responsive_correctness_validated"] = True
    assert_schema_invalid(global_claim, schema, "global responsive correctness true")

    rolling_queue_driver = copy.deepcopy(valid)
    rolling_queue_driver["execution_driver"] = "rolling_queue"
    assert_schema_invalid(rolling_queue_driver, schema, "rolling queue driver")


def main() -> int:
    run_self_tests()
    schema = load_json(SCHEMA)
    catalog = load_json(CATALOG)
    assert_catalog(catalog, schema)
    print("automation work package catalog check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
