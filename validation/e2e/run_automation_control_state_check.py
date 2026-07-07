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

EXPECTED_DRIVER = "work_package_catalog_guard"
EXPECTED_CATALOG_PATH = "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json"
EXPECTED_CATALOG_AUTHORITY = "approved_material_objective_source"
EXPECTED_ROLLING_AUTHORITY = "historical_reconciled_archive"
EXPECTED_ROLLING_STATUS = "retired_as_execution_driver"
EXPECTED_PLANNING_POLICY = "automatic_state_driven_catalog_replenishment"
EXPECTED_REFRESH_POLICY = "state_driven_non_blocking_single_active_pr"
EXPECTED_STATUS_LINES = {
    "current_execution_driver: work_package_catalog_guard",
    "work_package_catalog: planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json",
    "catalog_authority: approved_material_objective_source",
    "rolling_queue_execution_status: retired_as_execution_driver",
    "rolling_queue_reconciliation_required: false",
    "checkpoint_only_loop_policy: forbidden without material checkpoint change",
    "automation_control_validator: validation/e2e/run_automation_control_state_check.py",
    "automation_work_package_catalog_validator: validation/e2e/run_automation_work_package_catalog_check.py",
}
REQUIRED_NEXT_ACTIONS = [
    "create_checkpoint_only_pr_for_every_merge",
    "treat_stale_rolling_queue_as_current_driver",
    "invent_rtaq_task_without_catalog_work_package",
    "invent_micro_task_outside_catalog",
    "create_artificial_reserve_task_to_keep_task_count_high",
    "create_parallel_catalog_pr_while_active_mutation_pr_exists",
    "refresh_catalog_because_fixed_ordinal_was_reached",
    "upgrade_evidence_pilot_readiness_or_release_claims",
]


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        fail(f"{path.relative_to(ROOT)} must be a JSON object")
    return payload


def assert_schema_valid(payload: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda error: [str(part) for part in error.path])
    if errors:
        fail(f"{label} schema mismatch: {errors[0].message}")


def assert_queue_archive(queue: dict[str, Any]) -> None:
    cycle = queue.get("active_cycle")
    tasks = queue.get("tasks")
    terminal = {"merged", "superseded", "complete", "retired", "archived"}
    if queue.get("queue_status") != "complete" or not isinstance(cycle, dict) or cycle.get("cycle_status") != "complete":
        fail("rolling queue must remain a complete historical archive")
    if not isinstance(tasks, list) or not tasks or any(not isinstance(task, dict) or task.get("status") not in terminal for task in tasks):
        fail("rolling queue archive tasks must all be terminal")


def assert_catalog_policy(control: dict[str, Any], catalog: dict[str, Any]) -> None:
    if catalog.get("execution_driver") != control.get("current_execution_driver"):
        fail("catalog driver must match control driver")
    execution = catalog.get("execution_policy", {})
    if execution.get("active_work_package_limit") != 1:
        fail("execution policy must allow one active Work Package")
    for key in ["continue_active_before_starting_new", "reconcile_open_pr_before_new_mutation", "open_pr_blocks_new_mutation_pr"]:
        if execution.get(key) is not True:
            fail(f"execution policy must keep {key}=true")
    refresh = catalog.get("catalog_replenishment_policy", {})
    for key in ["state_driven_refresh", "fixed_ordinal_refresh_forbidden", "catalog_replenishment_must_not_block_active_execution", "catalog_replenishment_must_respect_single_active_pr_policy"]:
        if refresh.get(key) is not True:
            fail(f"catalog refresh policy must keep {key}=true")
    active_policy = refresh.get("when_active_pr_exists", {})
    if "create_parallel_catalog_pr" in active_policy.get("allowed", []) or "create_parallel_catalog_pr" not in active_policy.get("forbidden", []):
        fail("active PR catalog refresh policy must forbid parallel catalog PR creation")


def assert_control(control: dict[str, Any], schema: dict[str, Any], catalog: dict[str, Any], queue: dict[str, Any]) -> None:
    assert_schema_valid(control, schema, "automation control state")
    expected = {
        "current_execution_driver": EXPECTED_DRIVER,
        "work_package_catalog_path": EXPECTED_CATALOG_PATH,
        "catalog_authority": EXPECTED_CATALOG_AUTHORITY,
        "automatic_planning_policy": EXPECTED_PLANNING_POLICY,
        "catalog_replenishment_policy": EXPECTED_REFRESH_POLICY,
        "rolling_queue_authority": EXPECTED_ROLLING_AUTHORITY,
        "rolling_queue_execution_status": EXPECTED_ROLLING_STATUS,
        "queue_reconciliation_required_before_queue_driver": False,
        "fixed_ordinal_refresh_policy": "forbidden",
        "open_pr_reconciliation_policy": "reconcile_open_automation_pr_before_new_mutation",
    }
    for key, value in expected.items():
        if control.get(key) != value:
            fail(f"control state mismatch for {key}")
    if control.get("forbidden_next_actions") != REQUIRED_NEXT_ACTIONS:
        fail("forbidden_next_actions must match the expected catalog guard list")
    claims = control.get("boundary_claims")
    if not isinstance(claims, dict) or any(value is not False for value in claims.values()):
        fail("all boundary claims must remain false")
    if control.get("current_execution_driver") == "rolling_queue":
        fail("rolling_queue must not be the current execution driver")
    assert_catalog_policy(control, catalog)
    assert_queue_archive(queue)


def assert_status(text: str) -> None:
    normalized = {line.strip() for line in text.splitlines() if ":" in line and not line.strip().startswith("-")}
    missing = sorted(EXPECTED_STATUS_LINES - normalized)
    if missing:
        fail("STATUS.md missing canonical control markers: " + ", ".join(missing))
    if "current_execution_driver: rolling_queue" in normalized:
        fail("STATUS.md must not restore rolling_queue as current driver")


def run_self_tests() -> None:
    good_control = {
        "current_execution_driver": EXPECTED_DRIVER,
        "work_package_catalog_path": EXPECTED_CATALOG_PATH,
        "catalog_authority": EXPECTED_CATALOG_AUTHORITY,
        "automatic_planning_policy": EXPECTED_PLANNING_POLICY,
        "catalog_replenishment_policy": EXPECTED_REFRESH_POLICY,
        "rolling_queue_authority": EXPECTED_ROLLING_AUTHORITY,
        "rolling_queue_execution_status": EXPECTED_ROLLING_STATUS,
        "queue_reconciliation_required_before_queue_driver": False,
        "fixed_ordinal_refresh_policy": "forbidden",
        "open_pr_reconciliation_policy": "reconcile_open_automation_pr_before_new_mutation",
        "forbidden_next_actions": list(REQUIRED_NEXT_ACTIONS),
        "boundary_claims": {"example": False},
    }
    good_catalog = {
        "execution_driver": EXPECTED_DRIVER,
        "execution_policy": {"active_work_package_limit": 1, "continue_active_before_starting_new": True, "reconcile_open_pr_before_new_mutation": True, "open_pr_blocks_new_mutation_pr": True},
        "catalog_replenishment_policy": {"state_driven_refresh": True, "fixed_ordinal_refresh_forbidden": True, "catalog_replenishment_must_not_block_active_execution": True, "catalog_replenishment_must_respect_single_active_pr_policy": True, "when_active_pr_exists": {"allowed": ["detect_catalog_depth"], "forbidden": ["create_parallel_catalog_pr"]}},
    }
    bad_catalog = json.loads(json.dumps(good_catalog))
    bad_catalog["catalog_replenishment_policy"]["when_active_pr_exists"]["allowed"] = ["create_parallel_catalog_pr"]
    try:
        assert_catalog_policy(good_control, bad_catalog)
    except AssertionError as exc:
        if "parallel" not in str(exc):
            raise
    else:
        fail("parallel catalog PR policy must fail")
    bad_control = dict(good_control)
    bad_control["current_execution_driver"] = "rolling_queue"
    try:
        assert_catalog_policy(bad_control, good_catalog)
    except AssertionError:
        pass
    else:
        fail("driver mismatch must fail")
    assert_status("\n".join(EXPECTED_STATUS_LINES))


def main() -> int:
    run_self_tests()
    control = load_json(CONTROL)
    schema = load_json(SCHEMA)
    catalog = load_json(CATALOG)
    queue = load_json(QUEUE)
    assert_control(control, schema, catalog, queue)
    assert_status(STATUS.read_text(encoding="utf-8"))
    print("automation control state check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
