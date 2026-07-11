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


def policy_projection(catalog: dict[str, Any]) -> dict[str, int]:
    policy = catalog.get("catalog_replenishment_policy")
    if not isinstance(policy, dict):
        fail("catalog_replenishment_policy must be an object")
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
    if threshold > maximum:
        fail(f"{label}: refresh_when_ready_below must not exceed max_ready_work_packages")


def run_self_tests(catalog: dict[str, Any], schema: dict[str, Any]) -> None:
    preferred = copy.deepcopy(catalog)
    preferred["catalog_replenishment_policy"].update(PREFERRED_POLICY)
    assert_schema_valid(preferred, schema, "preferred 4/4/5 policy")
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


def main() -> int:
    catalog = load_json(CATALOG)
    schema = load_json(SCHEMA)
    assert_schema_valid(catalog, schema, "live automation work package catalog")
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
