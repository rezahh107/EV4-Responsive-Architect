#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
CONTROL = ROOT / "planning" / "EV4_AUTOMATION_CONTROL_STATE.json"
SCHEMA = ROOT / "schemas" / "ev4-automation-control-state.schema.json"
QUEUE = ROOT / "planning" / "EV4_ROLLING_QUEUE.json"
STATUS = ROOT / "STATUS.md"

EXPECTED_CONTROL = {
    "schema": "ev4-automation-control-state@1.0.0",
    "project": "EV4 Responsive Architect",
    "execution_state_source_of_truth": "planning/EV4_AUTOMATION_CONTROL_STATE.json",
    "current_execution_driver": "bounded_material_checkpoint_guard",
    "rolling_queue_authority": "historical_reconciled_archive",
    "rolling_queue_execution_status": "retired_as_execution_driver",
    "rolling_queue_path": "planning/EV4_ROLLING_QUEUE.json",
    "status_path": "STATUS.md",
    "latest_material_checkpoint": "PR #122 RTAQ-0038 rolling queue archive reconciliation",
    "latest_checkpoint_guard": "PR #113 RTAQ-0030 bounded foundation checkpoint guard",
    "queue_drift_acknowledged": False,
    "queue_reconciliation_required_before_queue_driver": False,
    "checkpoint_only_loop_policy": "bounded_checkpoints_only_not_append_every_merge",
    "next_action_policy": "material_objective_only",
}

FORBIDDEN_NEXT_ACTIONS = [
    "create_checkpoint_only_pr_for_every_merge",
    "treat_stale_rolling_queue_as_current_driver",
    "invent_rtaq_task_without_planning_contract",
    "upgrade_evidence_pilot_readiness_or_release_claims",
]

BOUNDARY_CLAIMS = {
    "real_submitted_packet_present": False,
    "pilot_allowed_to_start": False,
    "readiness_claims_upgraded": False,
    "production_ready": False,
    "release_ready": False,
    "responsive_correctness_claim_upgraded": False,
}

STATUS_CLAIMS = {
    "foundation_checkpoint_policy": "bounded checkpoints only; not append every merged PR",
    "automation_control_state": "planning/EV4_AUTOMATION_CONTROL_STATE.json",
    "execution_state_source_of_truth": "planning/EV4_AUTOMATION_CONTROL_STATE.json",
    "current_execution_driver": "bounded_material_checkpoint_guard",
    "rolling_queue_authority": "historical_reconciled_archive",
    "rolling_queue_execution_status": "retired_as_execution_driver",
    "rolling_queue_reconciliation_required": "false",
    "latest_material_checkpoint": "PR #122 RTAQ-0038 rolling queue archive reconciliation",
    "checkpoint_only_loop_policy": "bounded checkpoints only; not append every merged PR",
    "next_action_policy": "material objectives only; checkpoint refresh only when material checkpoint changes",
    "automation_control_validator": "validation/e2e/run_automation_control_state_check.py",
    "real_submitted_packet_present": "false",
    "pilot_allowed_to_start": "false",
    "readiness_claims_upgraded": "false",
    "production_ready": "false",
    "prompt_pack_release_ready": "false",
    "pilot_execution_scope": "not_allowed",
}

TERMINAL_TASK_STATUSES = {"merged", "superseded", "complete", "retired", "archived"}
DRIFT_TASKS = {"RTAQ-0019", "RTAQ-0020", "RTAQ-0021", "RTAQ-0022"}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    return payload


def schema_error_messages(payload: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    return [f"{'.'.join(str(p) for p in error.path) or '<root>'}: {error.message}" for error in validator.iter_errors(payload)]


def assert_schema_valid(payload: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    errors = schema_error_messages(payload, schema)
    if errors:
        fail(f"{label} must validate against schema: {errors[0]}")


def assert_schema_invalid(payload: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    if not schema_error_messages(payload, schema):
        fail(f"invalid payload unexpectedly passed schema validation: {label}")


def tasks_by_id(queue: dict[str, Any]) -> dict[str, dict[str, Any]]:
    tasks = queue.get("tasks")
    if not isinstance(tasks, list):
        fail("rolling queue tasks must be a list")
    result = {}
    for task in tasks:
        if not isinstance(task, dict) or not isinstance(task.get("task_id"), str):
            fail("rolling queue task must be an object with task_id")
        if task["task_id"] in result:
            fail(f"duplicate rolling queue task_id: {task['task_id']}")
        result[task["task_id"]] = task
    return result


def queue_has_old_drift(queue: dict[str, Any]) -> bool:
    if queue.get("queue_status") != "active":
        return False
    tasks = tasks_by_id(queue)
    return all(tasks.get(task_id, {}).get("status") == "pending" for task_id in DRIFT_TASKS)


def queue_is_complete_archive(queue: dict[str, Any]) -> bool:
    cycle = queue.get("active_cycle")
    if queue.get("queue_status") != "complete" or not isinstance(cycle, dict) or cycle.get("cycle_status") != "complete":
        return False
    tasks = queue.get("tasks")
    return isinstance(tasks, list) and bool(tasks) and all(isinstance(task, dict) and task.get("status") in TERMINAL_TASK_STATUSES for task in tasks)


def assert_control_state(control: dict[str, Any], schema: dict[str, Any], queue: dict[str, Any]) -> None:
    assert_schema_valid(control, schema, "automation control state")
    for key, expected in EXPECTED_CONTROL.items():
        if control.get(key) != expected:
            fail(f"automation control state mismatch for {key}: {control.get(key)!r} != {expected!r}")
    if control.get("forbidden_next_actions") != FORBIDDEN_NEXT_ACTIONS:
        fail("forbidden_next_actions must exactly match the required guard list")
    if control.get("boundary_claims") != BOUNDARY_CLAIMS:
        fail("boundary_claims must preserve evidence and readiness boundaries")
    if control["current_execution_driver"] == "rolling_queue":
        fail("rolling queue must not be restored as current execution driver")
    if queue_has_old_drift(queue):
        fail("active known-drift queue cannot use reconciled archive control state")
    if not queue_is_complete_archive(queue):
        fail("reconciled archive control state requires complete terminal rolling queue history")


def normalize_status_value(raw_value: str) -> str:
    value = raw_value.strip()
    if " #" in value:
        value = value.split(" #", 1)[0].strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'\"', "'"}:
        value = value[1:-1].strip()
    value = re.sub(r"\s+", " ", value)
    return value.lower() if value.lower() in {"true", "false", "null"} else value


def parse_status_claims(text: str) -> dict[str, list[tuple[str, int]]]:
    claims: dict[str, list[tuple[str, int]]] = {}
    in_yaml = False
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if line.startswith("```yaml"):
            in_yaml = True
            continue
        if in_yaml and line.startswith("```"):
            in_yaml = False
            continue
        if not in_yaml or not line or line.startswith("#") or line.startswith("-") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key in STATUS_CLAIMS:
            claims.setdefault(key, []).append((normalize_status_value(value), line_number))
    return claims


def assert_status_text(text: str) -> None:
    claims = parse_status_claims(text)
    for key, expected in STATUS_CLAIMS.items():
        occurrences = claims.get(key, [])
        if not occurrences:
            fail(f"STATUS.md missing automation/boundary key: {key}")
        if len(occurrences) != 1:
            fail(f"STATUS.md contains duplicate automation/boundary key: {key}")
        actual, line_number = occurrences[0]
        if actual != expected:
            fail(f"STATUS.md value mismatch for {key} at line {line_number}: {actual!r} != {expected!r}")


def status_fixture(extra: list[str] | None = None) -> str:
    lines = [f"{key}: {value}" for key, value in STATUS_CLAIMS.items()]
    lines.extend(extra or [])
    return "```yaml\n" + "\n".join(lines) + "\n```"


def valid_control() -> dict[str, Any]:
    control = dict(EXPECTED_CONTROL)
    control["forbidden_next_actions"] = list(FORBIDDEN_NEXT_ACTIONS)
    control["boundary_claims"] = dict(BOUNDARY_CLAIMS)
    return control


def complete_queue_fixture() -> dict[str, Any]:
    return {"queue_status": "complete", "active_cycle": {"cycle_status": "complete"}, "tasks": [{"task_id": "RTAQ-0001", "status": "merged"}, {"task_id": "RTAQ-0011", "status": "superseded"}]}


def drift_queue_fixture() -> dict[str, Any]:
    return {"queue_status": "active", "active_cycle": {"cycle_status": "active"}, "tasks": [{"task_id": task_id, "status": "pending"} for task_id in sorted(DRIFT_TASKS)]}


def assert_invalid_control(control: dict[str, Any], schema: dict[str, Any], queue: dict[str, Any], expected: str) -> None:
    try:
        assert_control_state(control, schema, queue)
    except AssertionError as exc:
        if expected not in str(exc):
            fail(f"self-test produced unexpected diagnostic: {exc}")
    else:
        fail(f"invalid control state was accepted: {expected}")


def assert_invalid_status(text: str, expected: str) -> None:
    try:
        assert_status_text(text)
    except AssertionError as exc:
        if expected not in str(exc):
            fail(f"self-test produced unexpected diagnostic: {exc}")
    else:
        fail(f"invalid STATUS text was accepted: {expected}")


def run_self_tests() -> None:
    schema = load_json(SCHEMA)
    control = valid_control()
    queue = complete_queue_fixture()
    assert_control_state(control, schema, queue)
    missing_required = dict(control)
    missing_required.pop("execution_state_source_of_truth")
    assert_schema_invalid(missing_required, schema, "missing execution_state_source_of_truth")
    old_control = dict(control)
    old_control["rolling_queue_authority"] = "historical_non_authoritative_until_reconciled"
    assert_schema_invalid(old_control, schema, "old queue authority")
    bad_driver = dict(control)
    bad_driver["current_execution_driver"] = "rolling_queue"
    assert_invalid_control(bad_driver, schema, queue, "current_execution_driver")
    bad_order = dict(control)
    bad_order["forbidden_next_actions"] = list(reversed(FORBIDDEN_NEXT_ACTIONS))
    assert_invalid_control(bad_order, schema, queue, "forbidden_next_actions")
    assert_invalid_control(control, schema, drift_queue_fixture(), "active known-drift queue")
    incomplete_queue = {"queue_status": "complete", "active_cycle": {"cycle_status": "complete"}, "tasks": [{"task_id": "RTAQ-0001", "status": "pending"}]}
    assert_invalid_control(control, schema, incomplete_queue, "complete terminal rolling queue history")
    assert_status_text(status_fixture())
    assert_invalid_status(status_fixture(["current_execution_driver: rolling_queue"]), "current_execution_driver")
    assert_invalid_status(status_fixture().replace("rolling_queue_reconciliation_required: false", "rolling_queue_reconciliation_required: true"), "rolling_queue_reconciliation_required")
    assert_invalid_status(status_fixture().replace("pilot_allowed_to_start: false", "pilot_allowed_to_start: true"), "pilot_allowed_to_start")


def main() -> int:
    run_self_tests()
    control = load_json(CONTROL)
    schema = load_json(SCHEMA)
    queue = load_json(QUEUE)
    assert_control_state(control, schema, queue)
    assert_status_text(STATUS.read_text(encoding="utf-8"))
    print("automation control state check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
