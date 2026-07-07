#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
CONTROL = ROOT / "planning" / "EV4_AUTOMATION_CONTROL_STATE.json"
CATALOG = ROOT / "planning" / "EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json"
SCHEMA = ROOT / "schemas" / "ev4-automation-control-state.schema.json"
QUEUE = ROOT / "planning" / "EV4_ROLLING_QUEUE.json"
STATUS = ROOT / "STATUS.md"

EXPECTED = {
    "schema": "ev4-automation-control-state@1.0.0",
    "project": "EV4 Responsive Architect",
    "execution_state_source_of_truth": "planning/EV4_AUTOMATION_CONTROL_STATE.json",
    "current_execution_driver": "work_package_catalog_guard",
    "work_package_catalog_path": "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json",
    "catalog_authority": "approved_material_objective_source",
    "catalog_selection_policy": "select_from_catalog_only_one_work_package_or_reviewable_slice",
    "automatic_planning_policy": "automatic_state_driven_catalog_replenishment",
    "catalog_replenishment_policy": "state_driven_non_blocking_single_active_pr",
    "rolling_queue_authority": "historical_reconciled_archive",
    "rolling_queue_execution_status": "retired_as_execution_driver",
    "rolling_queue_path": "planning/EV4_ROLLING_QUEUE.json",
    "status_path": "STATUS.md",
    "queue_drift_acknowledged": False,
    "queue_reconciliation_required_before_queue_driver": False,
    "arbitrary_task_invention_policy": "forbidden_outside_work_package_catalog",
    "checkpoint_only_loop_policy": "forbidden_without_material_checkpoint_change",
    "fixed_ordinal_refresh_policy": "forbidden",
    "next_action_policy": "catalog_material_objective_or_state_driven_replenishment",
    "open_pr_reconciliation_policy": "reconcile_open_automation_pr_before_new_mutation",
}
FORBIDDEN_NEXT_ACTIONS = [
    "create_checkpoint_only_pr_for_every_merge",
    "treat_stale_rolling_queue_as_current_driver",
    "invent_rtaq_task_without_catalog_work_package",
    "invent_micro_task_outside_catalog",
    "create_artificial_reserve_task_to_keep_task_count_high",
    "create_parallel_catalog_pr_while_active_mutation_pr_exists",
    "refresh_catalog_because_fixed_ordinal_was_reached",
    "upgrade_evidence_pilot_readiness_or_release_claims",
]
STATUS_REQUIRED = {
    "current_execution_driver: work_package_catalog_guard",
    "work_package_catalog: planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json",
    "catalog_authority: approved_material_objective_source",
    "rolling_queue_execution_status: retired_as_execution_driver",
    "rolling_queue_reconciliation_required: false",
    "checkpoint_only_loop_policy: forbidden without material checkpoint change",
    "automation_control_validator: validation/e2e/run_automation_control_state_check.py",
    "automation_work_package_catalog_validator: validation/e2e/run_automation_work_package_catalog_check.py",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    return payload


def schema_errors(payload: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    return [error.message for error in sorted(validator.iter_errors(payload), key=lambda item: [str(part) for part in item.path])]


def assert_schema_valid(payload: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    errors = schema_errors(payload, schema)
    if errors:
        fail(f"{label} must validate against schema: {errors[0]}")


def assert_schema_invalid(payload: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    if not schema_errors(payload, schema):
        fail(f"invalid payload unexpectedly passed schema validation: {label}")


def queue_is_complete_archive(queue: dict[str, Any]) -> bool:
    cycle = queue.get("active_cycle")
    tasks = queue.get("tasks")
    terminal = {"merged", "superseded", "complete", "retired", "archived"}
    return queue.get("queue_status") == "complete" and isinstance(cycle, dict) and cycle.get("cycle_status") == "complete" and isinstance(tasks, list) and bool(tasks) and all(isinstance(task, dict) and task.get("status") in terminal for task in tasks)


def assert_catalog_policy(control: dict[str, Any], catalog: dict[str, Any]) -> None:
    if catalog.get("execution_driver") != control["current_execution_driver"]:
        fail("catalog execution driver must match control state")
    execution = catalog.get("execution_policy", {})
    if execution.get("active_work_package_limit") != 1 or execution.get("continue_active_before_starting_new") is not True or execution.get("open_pr_blocks_new_mutation_pr") is not True:
        fail("catalog execution policy must enforce one active Work Package and one active mutation PR")
    repl = catalog.get("catalog_replenishment_policy", {})
    for key in ["state_driven_refresh", "fixed_ordinal_refresh_forbidden", "catalog_replenishment_must_not_block_active_execution", "catalog_replenishment_must_respect_single_active_pr_policy"]:
        if repl.get(key) is not True:
            fail(f"catalog replenishment policy must keep {key}=true")
    active = repl.get("when_active_pr_exists", {})
    if "create_parallel_catalog_pr" in active.get("allowed", []) or "create_parallel_catalog_pr" not in active.get("forbidden", []):
        fail("active PR policy must forbid parallel catalog PR creation")


def assert_control_state(control: dict[str, Any], schema: dict[str, Any], queue: dict[str, Any], catalog: dict[str, Any]) -> None:
    assert_schema_valid(control, schema, "automation control state")
    for key, expected in EXPECTED.items():
        if control.get(key) != expected:
            fail(f"automation control state mismatch for {key}")
    for key in ["latest_material_checkpoint", "latest_checkpoint_guard"]:
        if not isinstance(control.get(key), str) or not control[key].startswith("PR #"):
            fail(f"automation control state must keep {key} as a PR checkpoint string")
    if control.get("forbidden_next_actions") != FORBIDDEN_NEXT_ACTIONS:
        fail("forbidden_next_actions must exactly match the required catalog guard list")
    claims = control.get("boundary_claims")
    if not isinstance(claims, dict) or len(claims) < 8 or any(value is not False for value in claims.values()):
        fail("boundary_claims must remain explicitly false")
    if control["current_execution_driver"] == "rolling_queue":
        fail("rolling queue must not be restored as current execution driver")
    assert_catalog_policy(control, catalog)
    if not queue_is_complete_archive(queue):
        fail("reconciled archive control state requires complete terminal rolling queue history")


def assert_status_text(text: str) -> None:
    normalized = {line.strip() for line in text.splitlines() if ":" in line and not line.strip().startswith("-")}
    for required in STATUS_REQUIRED:
        if required not in normalized:
            fail(f"STATUS.md missing canonical automation key: {required}")
    if "current_execution_driver: rolling_queue" in normalized:
        fail("STATUS.md must not restore rolling_queue as current driver")


def valid_control() -> dict[str, Any]:
    control = dict(EXPECTED)
    control["latest_material_checkpoint"] = "PR #122 RTAQ-0038 rolling queue archive reconciliation"
    control["latest_checkpoint_guard"] = "PR #113 RTAQ-0030 bounded foundation checkpoint guard"
    control["forbidden_next_actions"] = list(FORBIDDEN_NEXT_ACTIONS)
    control["boundary_claims"] = {f"claim_{index}": False for index in range(8)}
    return control


def valid_catalog() -> dict[str, Any]:
    return {"execution_driver": "work_package_catalog_guard", "execution_policy": {"active_work_package_limit": 1, "continue_active_before_starting_new": True, "open_pr_blocks_new_mutation_pr": True}, "catalog_replenishment_policy": {"state_driven_refresh": True, "fixed_ordinal_refresh_forbidden": True, "catalog_replenishment_must_not_block_active_execution": True, "catalog_replenishment_must_respect_single_active_pr_policy": True, "when_active_pr_exists": {"allowed": ["detect_catalog_depth"], "forbidden": ["create_parallel_catalog_pr"]}}}


def complete_queue() -> dict[str, Any]:
    return {"queue_status": "complete", "active_cycle": {"cycle_status": "complete"}, "tasks": [{"task_id": "RTAQ-0001", "status": "merged"}]}


def assert_invalid_control(control: dict[str, Any], schema: dict[str, Any], queue: dict[str, Any], catalog: dict[str, Any], expected: str) -> None:
    try:
        assert_control_state(control, schema, queue, catalog)
    except AssertionError as exc:
        if expected not in str(exc):
            fail(f"self-test produced unexpected diagnostic: {exc}")
        return
    fail(f"invalid control state was accepted: {expected}")


def run_self_tests() -> None:
    schema = load_json(SCHEMA)
    control = valid_control()
    queue = complete_queue()
    catalog = valid_catalog()
    assert_control_state(control, schema, queue, catalog)
    missing = dict(control); missing.pop("automatic_planning_policy")
    assert_schema_invalid(missing, schema, "missing automatic planning")
    bad_driver = dict(control); bad_driver["current_execution_driver"] = "rolling_queue"
    assert_invalid_control(bad_driver, schema, queue, catalog, "current_execution_driver")
    bad_catalog = valid_catalog(); bad_catalog["catalog_replenishment_policy"]["fixed_ordinal_refresh_forbidden"] = False
    assert_invalid_control(control, schema, queue, bad_catalog, "fixed_ordinal_refresh_forbidden")
    parallel = valid_catalog(); parallel["catalog_replenishment_policy"]["when_active_pr_exists"]["allowed"] = ["create_parallel_catalog_pr"]
    assert_invalid_control(control, schema, queue, parallel, "parallel catalog PR")
    assert_status_text("\n".join(sorted(STATUS_REQUIRED)))


def main() -> int:
    run_self_tests()
    control = load_json(CONTROL)
    schema = load_json(SCHEMA)
    queue = load_json(QUEUE)
    catalog = load_json(CATALOG)
    assert_control_state(control, schema, queue, catalog)
    assert_status_text(STATUS.read_text(encoding="utf-8"))
    print("automation control state check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
