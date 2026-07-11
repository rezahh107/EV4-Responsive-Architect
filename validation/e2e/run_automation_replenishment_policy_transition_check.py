#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "planning" / "EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json"
SCHEMA = ROOT / "schemas" / "ev4-automation-work-package-catalog.schema.json"

LEGACY_POLICY = {
    "ready_work_package_target": 3,
    "refresh_when_ready_below": 2,
    "max_ready_work_packages": 5,
}
PREFERRED_POLICY = {
    "ready_work_package_target": 4,
    "refresh_when_ready_below": 4,
    "max_ready_work_packages": 5,
}

EXPECTED_STATE_DRIVEN_TRIGGERS = [
    "ready_work_package_depth_below_threshold",
    "active_work_package_completed_and_project_state_changed",
    "material_blocker_changed_priorities",
    "core_contract_or_architecture_changed",
    "no_executable_work_package_exists_and_real_project_gap_detected",
]
EXPECTED_FORBIDDEN_REFRESH_TRIGGERS = [
    "fixed_task_ordinal_reached",
    "every_fifth_task",
    "after_four_tasks_create_next_four",
    "fixed_count_reached",
    "checkpoint_only_refresh",
    "bookkeeping_only_refresh",
]
EXPECTED_ACTIVE_PR_ALLOWED = [
    "detect_catalog_depth",
    "report_replenishment_needed",
    "prepare_non_mutating_replenishment_plan",
    "update_catalog_only_if_in_scope_for_same_active_pr",
]
EXPECTED_ACTIVE_PR_FORBIDDEN = [
    "create_parallel_catalog_pr",
    "interrupt_active_work_package",
    "start_unrelated_catalog_mutation",
    "create_checkpoint_only_catalog_refresh_pr",
]
EXPECTED_NO_ACTIVE_PR_ALLOWED = [
    "continue_active_work_package",
    "select_next_ready_work_package",
    "create_catalog_replenishment_pr_if_ready_depth_below_threshold",
    "update_catalog_as_part_of_same_material_work_package_if_in_scope",
]


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    return payload


def assert_schema_valid(catalog: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    errors = sorted(
        Draft202012Validator(schema).iter_errors(catalog),
        key=lambda error: [str(part) for part in error.path],
    )
    if errors:
        path = ".".join(str(part) for part in errors[0].path) or "<root>"
        fail(f"{label} must validate against schema: {path}: {errors[0].message}")


def get_policy(catalog: dict[str, Any]) -> dict[str, Any]:
    policy = catalog.get("catalog_replenishment_policy")
    if not isinstance(policy, dict):
        fail("catalog_replenishment_policy must be an object")
    return policy


def policy_projection(catalog: dict[str, Any]) -> dict[str, int]:
    policy = get_policy(catalog)
    projection: dict[str, int] = {}
    for key in PREFERRED_POLICY:
        value = policy.get(key)
        if not isinstance(value, int) or isinstance(value, bool):
            fail(f"catalog_replenishment_policy.{key} must be an integer")
        projection[key] = value
    return projection


def assert_relational_invariants(policy: dict[str, int], label: str) -> None:
    target = policy["ready_work_package_target"]
    threshold = policy["refresh_when_ready_below"]
    maximum = policy["max_ready_work_packages"]
    if threshold > target:
        fail(f"{label}: refresh_when_ready_below must not exceed ready_work_package_target")
    if target > maximum:
        fail(f"{label}: ready_work_package_target must not exceed max_ready_work_packages")


def assert_policy_steps_integrity(policy: dict[str, Any], label: str) -> None:
    if policy.get("state_driven_triggers") != EXPECTED_STATE_DRIVEN_TRIGGERS:
        fail(f"{label}: state_driven_triggers does not match expected list or order")
    if policy.get("forbidden_refresh_triggers") != EXPECTED_FORBIDDEN_REFRESH_TRIGGERS:
        fail(f"{label}: forbidden_refresh_triggers does not match expected list or order")

    active_pr = policy.get("when_active_pr_exists")
    if not isinstance(active_pr, dict):
        fail(f"{label}: when_active_pr_exists must be an object")
    if active_pr.get("allowed") != EXPECTED_ACTIVE_PR_ALLOWED:
        fail(f"{label}: when_active_pr_exists.allowed does not match expected list or order")
    if active_pr.get("forbidden") != EXPECTED_ACTIVE_PR_FORBIDDEN:
        fail(f"{label}: when_active_pr_exists.forbidden does not match expected list or order")

    no_active_pr = policy.get("when_no_active_pr_exists")
    if not isinstance(no_active_pr, dict):
        fail(f"{label}: when_no_active_pr_exists must be an object")
    if no_active_pr.get("allowed") != EXPECTED_NO_ACTIVE_PR_ALLOWED:
        fail(f"{label}: when_no_active_pr_exists.allowed does not match expected list or order")


def run_self_tests(catalog: dict[str, Any], schema: dict[str, Any]) -> None:
    preferred = copy.deepcopy(catalog)
    preferred["catalog_replenishment_policy"].update(PREFERRED_POLICY)
    assert_schema_valid(preferred, schema, "preferred 4/4/5 policy")
    assert_policy_steps_integrity(
        get_policy(preferred), "preferred 4/4/5 policy"
    )
    assert_relational_invariants(policy_projection(preferred), "preferred 4/4/5 policy")

    threshold_above_target = copy.deepcopy(preferred)
    threshold_above_target["catalog_replenishment_policy"].update(
        {"ready_work_package_target": 3, "refresh_when_ready_below": 4}
    )
    try:
        assert_relational_invariants(
            policy_projection(threshold_above_target), "threshold-above-target fixture"
        )
    except AssertionError as exc:
        if "must not exceed ready_work_package_target" not in str(exc):
            fail(f"unexpected threshold-above-target diagnostic: {exc}")
    else:
        fail("threshold-above-target fixture was accepted")

    target_above_maximum = copy.deepcopy(preferred)
    target_above_maximum["catalog_replenishment_policy"].update(
        {"ready_work_package_target": 6, "max_ready_work_packages": 5}
    )
    errors = list(Draft202012Validator(schema).iter_errors(target_above_maximum))
    if not errors:
        fail("target-above-maximum fixture unexpectedly passed schema validation")
    try:
        assert_relational_invariants(
            policy_projection(target_above_maximum), "target-above-maximum fixture"
        )
    except AssertionError as exc:
        if "must not exceed max_ready_work_packages" not in str(exc):
            fail(f"unexpected target-above-maximum diagnostic: {exc}")
    else:
        fail("target-above-maximum fixture was accepted by relational invariants")

    reordered_triggers = copy.deepcopy(preferred)
    triggers = reordered_triggers["catalog_replenishment_policy"]["state_driven_triggers"]
    triggers[0], triggers[1] = triggers[1], triggers[0]
    try:
        assert_policy_steps_integrity(
            get_policy(reordered_triggers), "reordered-trigger fixture"
        )
    except AssertionError as exc:
        if "state_driven_triggers does not match expected list or order" not in str(exc):
            fail(f"unexpected reordered-trigger diagnostic: {exc}")
    else:
        fail("reordered-trigger fixture was accepted")


def main() -> int:
    catalog = load_json(CATALOG)
    schema = load_json(SCHEMA)
    assert_schema_valid(catalog, schema, "live automation work package catalog")
    assert_policy_steps_integrity(get_policy(catalog), "live policy")
    live_policy = policy_projection(catalog)
    assert_relational_invariants(live_policy, "live policy")
    if live_policy not in (LEGACY_POLICY, PREFERRED_POLICY):
        fail(
            "live replenishment policy must be either the legacy 3/2/5 transition state "
            "or the preferred 4/4/5 state"
        )
    run_self_tests(catalog, schema)
    state = "preferred" if live_policy == PREFERRED_POLICY else "legacy_transition"
    print(f"automation replenishment policy transition check passed ({state})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
