#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
CONTROL = ROOT / "planning" / "EV4_AUTOMATION_CONTROL_STATE.json"
CONTROL_SCHEMA = ROOT / "schemas" / "ev4-automation-control-state.schema.json"
QUEUE = ROOT / "planning" / "EV4_ROLLING_QUEUE.json"
STATUS = ROOT / "STATUS.md"

EXPECTED_CONTROL = {
    "schema": "ev4-automation-control-state@1.0.0",
    "project": "EV4 Responsive Architect",
    "execution_state_source_of_truth": "planning/EV4_AUTOMATION_CONTROL_STATE.json",
    "current_execution_driver": "bounded_material_checkpoint_guard",
    "rolling_queue_authority": "historical_non_authoritative_until_reconciled",
    "rolling_queue_execution_status": "retired_as_execution_driver",
    "rolling_queue_path": "planning/EV4_ROLLING_QUEUE.json",
    "status_path": "STATUS.md",
    "latest_material_checkpoint": "PR #120 RTAQ-0036 pilot readiness Validate chain closure",
    "latest_checkpoint_guard": "PR #113 RTAQ-0030 bounded foundation checkpoint guard",
    "queue_drift_acknowledged": True,
    "queue_reconciliation_required_before_queue_driver": True,
    "checkpoint_only_loop_policy": "bounded_checkpoints_only_not_append_every_merge",
    "next_action_policy": "material_objective_only",
}

REQUIRED_FORBIDDEN_NEXT_ACTIONS = [
    "create_checkpoint_only_pr_for_every_merge",
    "treat_stale_rolling_queue_as_current_driver",
    "invent_rtaq_task_without_planning_contract",
    "upgrade_evidence_pilot_readiness_or_release_claims",
]

REQUIRED_BOUNDARY_CLAIMS = {
    "real_submitted_packet_present": False,
    "pilot_allowed_to_start": False,
    "readiness_claims_upgraded": False,
    "production_ready": False,
    "release_ready": False,
    "responsive_correctness_claim_upgraded": False,
}

EXPECTED_STATUS_CLAIMS = {
    "foundation_checkpoint_policy": "bounded checkpoints only; not append every merged PR",
    "automation_control_state": "planning/EV4_AUTOMATION_CONTROL_STATE.json",
    "execution_state_source_of_truth": "planning/EV4_AUTOMATION_CONTROL_STATE.json",
    "current_execution_driver": "bounded_material_checkpoint_guard",
    "rolling_queue_authority": "historical_non_authoritative_until_reconciled",
    "rolling_queue_execution_status": "retired_as_execution_driver",
    "rolling_queue_reconciliation_required": "true",
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

QUEUE_DRIFT_TASKS = {"RTAQ-0019", "RTAQ-0020", "RTAQ-0021", "RTAQ-0022"}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fail(f"missing required JSON file: {path.relative_to(ROOT)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    return payload


def schema_errors(payload: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    messages: list[str] = []
    for error in sorted(validator.iter_errors(payload), key=lambda item: [str(part) for part in item.path]):
        path = ".".join(str(part) for part in error.path) or "<root>"
        messages.append(f"{path}: {error.message}")
    return messages


def assert_schema_valid(payload: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    errors = schema_errors(payload, schema)
    if errors:
        fail(f"{label} must validate against schema: {errors[0]}")


def assert_schema_invalid(payload: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    if not schema_errors(payload, schema):
        fail(f"malformed payload unexpectedly passed schema validation: {label}")


def task_by_id(queue: dict[str, Any]) -> dict[str, dict[str, Any]]:
    tasks = queue.get("tasks")
    if not isinstance(tasks, list):
        fail("rolling queue tasks must be a list")
    result: dict[str, dict[str, Any]] = {}
    for task in tasks:
        if not isinstance(task, dict):
            fail("rolling queue task must be an object")
        task_id = task.get("task_id")
        if not isinstance(task_id, str):
            fail("rolling queue task is missing string task_id")
        if task_id in result:
            fail(f"duplicate rolling queue task_id: {task_id}")
        result[task_id] = task
    return result


def rolling_queue_has_known_drift(queue: dict[str, Any]) -> bool:
    if queue.get("queue_status") != "active":
        return False
    tasks = task_by_id(queue)
    return all(tasks.get(task_id, {}).get("status") == "pending" for task_id in QUEUE_DRIFT_TASKS)


def assert_control_state(control: dict[str, Any], control_schema: dict[str, Any], queue: dict[str, Any]) -> None:
    assert_schema_valid(control, control_schema, "automation control state")

    for key, expected in EXPECTED_CONTROL.items():
        if control.get(key) != expected:
            fail(f"automation control state mismatch for {key}: {control.get(key)!r} != {expected!r}")

    forbidden = control.get("forbidden_next_actions")
    if forbidden != REQUIRED_FORBIDDEN_NEXT_ACTIONS:
        fail("forbidden_next_actions must exactly match the required execution guard list and order")

    boundary_claims = control.get("boundary_claims")
    if boundary_claims != REQUIRED_BOUNDARY_CLAIMS:
        fail("boundary_claims must exactly preserve evidence, pilot, readiness, production, release, and responsive-correctness boundaries")

    if control["current_execution_driver"] == "rolling_queue":
        fail("rolling queue must not be restored as the current execution driver in this contract")
    if control["rolling_queue_authority"] != "historical_non_authoritative_until_reconciled":
        fail("rolling queue must remain historical and non-authoritative until a deliberate reconciliation PR")
    if control["rolling_queue_execution_status"] != "retired_as_execution_driver":
        fail("rolling queue execution status must remain retired_as_execution_driver")

    active_cycle = queue.get("active_cycle")
    active_cycle_status = active_cycle.get("cycle_status") if isinstance(active_cycle, dict) else None
    if queue.get("queue_status") == "active" or active_cycle_status == "active":
        if control["rolling_queue_execution_status"] != "retired_as_execution_driver":
            fail("historical active queue snapshot requires retired_as_execution_driver control state")
        if control["rolling_queue_authority"] != "historical_non_authoritative_until_reconciled":
            fail("historical active queue snapshot must not regain execution authority")

    if rolling_queue_has_known_drift(queue):
        if control["queue_drift_acknowledged"] is not True:
            fail("known rolling queue drift must remain explicitly acknowledged")
        if control["queue_reconciliation_required_before_queue_driver"] is not True:
            fail("queue reconciliation must be required before restoring queue driver authority")


def normalize_status_value(raw_value: str) -> str:
    value = raw_value.strip()
    if " #" in value:
        value = value.split(" #", 1)[0].strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1].strip()
    value = re.sub(r"\s+", " ", value)
    lowered = value.lower()
    if lowered in {"true", "false", "null"}:
        return lowered
    return value


def parse_yaml_claim_occurrences(status_text: str) -> list[tuple[str, str, int]]:
    occurrences: list[tuple[str, str, int]] = []
    inside_yaml_block = False

    for line_number, raw_line in enumerate(status_text.splitlines(), start=1):
        line = raw_line.strip()
        if line.startswith("```yaml"):
            inside_yaml_block = True
            continue
        if inside_yaml_block and line.startswith("```"):
            inside_yaml_block = False
            continue
        if not inside_yaml_block or not line or line.startswith("#") or line.startswith("-"):
            continue
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        if key:
            occurrences.append((key, normalize_status_value(raw_value), line_number))

    return occurrences


def assert_status_text(status_text: str) -> None:
    claims: dict[str, list[tuple[str, int]]] = {}
    for key, value, line_number in parse_yaml_claim_occurrences(status_text):
        if key in EXPECTED_STATUS_CLAIMS:
            claims.setdefault(key, []).append((value, line_number))

    for key, expected in EXPECTED_STATUS_CLAIMS.items():
        occurrences = claims.get(key, [])
        if not occurrences:
            fail(f"STATUS.md missing automation/boundary key: {key}")
        if len(occurrences) != 1:
            details = ", ".join(f"line {line}: {value!r}" for value, line in occurrences)
            fail(f"STATUS.md contains duplicate automation/boundary key {key}: {details}")
        actual, line_number = occurrences[0]
        if actual != expected:
            fail(
                f"STATUS.md automation/boundary value mismatch for {key} at line {line_number}: "
                f"{actual!r} != {expected!r}"
            )


def status_fixture(extra_claims: list[str] | None = None) -> str:
    lines = [f"{key}: {value}" for key, value in EXPECTED_STATUS_CLAIMS.items()]
    lines.extend(extra_claims or [])
    return "```yaml\n" + "\n".join(lines) + "\n```"


def valid_control() -> dict[str, Any]:
    control = dict(EXPECTED_CONTROL)
    control["forbidden_next_actions"] = list(REQUIRED_FORBIDDEN_NEXT_ACTIONS)
    control["boundary_claims"] = dict(REQUIRED_BOUNDARY_CLAIMS)
    return control


def assert_invalid_control(control: dict[str, Any], schema: dict[str, Any], queue: dict[str, Any], expected_fragment: str) -> None:
    try:
        assert_control_state(control, schema, queue)
    except AssertionError as exc:
        if expected_fragment not in str(exc):
            fail(f"self-test failed with unexpected diagnostic: {exc}")
    else:
        fail(f"self-test failed: invalid control state was accepted; expected {expected_fragment!r}")


def assert_invalid_status(status_text: str, expected_fragment: str) -> None:
    try:
        assert_status_text(status_text)
    except AssertionError as exc:
        if expected_fragment not in str(exc):
            fail(f"self-test failed with unexpected diagnostic: {exc}")
    else:
        fail(f"self-test failed: invalid STATUS text was accepted; expected {expected_fragment!r}")


def run_self_tests() -> None:
    schema = load_json(CONTROL_SCHEMA)
    queue_with_drift = {
        "queue_status": "active",
        "active_cycle": {"cycle_status": "active"},
        "tasks": [{"task_id": task_id, "status": "pending"} for task_id in sorted(QUEUE_DRIFT_TASKS)],
    }

    control = valid_control()
    assert_control_state(control, schema, queue_with_drift)
    queue_with_null_cycle = dict(queue_with_drift)
    queue_with_null_cycle["active_cycle"] = None
    assert_control_state(control, schema, queue_with_null_cycle)

    missing_required = dict(control)
    missing_required.pop("execution_state_source_of_truth")
    assert_schema_invalid(missing_required, schema, "missing execution_state_source_of_truth")

    unknown_key = dict(control)
    unknown_key["rolling_queue_driver"] = "active"
    assert_schema_invalid(unknown_key, schema, "unknown execution key")

    rolling_driver = dict(control)
    rolling_driver["current_execution_driver"] = "rolling_queue"
    assert_invalid_control(rolling_driver, schema, queue_with_drift, "current_execution_driver")

    active_queue_status = dict(control)
    active_queue_status["rolling_queue_execution_status"] = "active"
    assert_invalid_control(active_queue_status, schema, queue_with_drift, "rolling_queue_execution_status")

    authoritative_queue = dict(control)
    authoritative_queue["rolling_queue_authority"] = "authoritative"
    assert_invalid_control(authoritative_queue, schema, queue_with_drift, "rolling_queue_authority")

    bad_forbidden = dict(control)
    bad_forbidden["forbidden_next_actions"] = [
        "create_checkpoint_only_pr_for_every_merge",
        "treat_stale_rolling_queue_as_current_driver",
        "upgrade_evidence_pilot_readiness_or_release_claims",
        "invent_rtaq_task_without_planning_contract",
    ]
    assert_invalid_control(bad_forbidden, schema, queue_with_drift, "forbidden_next_actions")

    duplicate_forbidden = dict(control)
    duplicate_forbidden["forbidden_next_actions"] = [
        "create_checkpoint_only_pr_for_every_merge",
        "treat_stale_rolling_queue_as_current_driver",
        "invent_rtaq_task_without_planning_contract",
        "create_checkpoint_only_pr_for_every_merge",
    ]
    assert_schema_invalid(duplicate_forbidden, schema, "duplicate forbidden_next_actions")

    valid_status = status_fixture()
    assert_status_text(valid_status)
    assert_invalid_status(status_fixture(["execution_state_source_of_truth: planning/EV4_ROLLING_QUEUE.json"]), "execution_state_source_of_truth")
    assert_invalid_status(status_fixture(["rolling_queue_execution_status: active"]), "rolling_queue_execution_status")
    assert_invalid_status(status_fixture(["current_execution_driver: rolling_queue"]), "current_execution_driver")
    assert_invalid_status(status_fixture().replace("pilot_allowed_to_start: false", "pilot_allowed_to_start: true"), "pilot_allowed_to_start")


def main() -> int:
    run_self_tests()
    control = load_json(CONTROL)
    control_schema = load_json(CONTROL_SCHEMA)
    queue = load_json(QUEUE)
    if not STATUS.is_file():
        fail("missing STATUS.md")
    assert_control_state(control, control_schema, queue)
    assert_status_text(STATUS.read_text(encoding="utf-8"))
    print("automation control state check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
