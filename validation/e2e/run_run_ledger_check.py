#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "planning" / "EV4_RUN_LEDGER.json"
LEDGER_SCHEMA = ROOT / "schemas" / "ev4-responsive-run-ledger.schema.json"
QUEUE = ROOT / "planning" / "EV4_ROLLING_QUEUE.json"

REQUIRED_BOUNDARIES = {
    "no_real_evidence_created",
    "no_real_pilot_run",
    "no_production_claim",
    "no_release_claim",
    "no_live_render_claim",
    "no_export_validation_claim",
    "no_accessibility_pass_claim",
    "sample_not_used_as_real",
}


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fail(message: str) -> None:
    raise AssertionError(message)


def validate_schema(payload: dict[str, Any], schema: dict[str, Any]) -> None:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda e: [str(p) for p in e.path])
    if errors:
        fail(f"run ledger schema validation failed: {errors[0].message}")


def main() -> None:
    ledger = load(LEDGER)
    schema = load(LEDGER_SCHEMA)
    queue = load(QUEUE)

    validate_schema(ledger, schema)

    task_by_id = {task["task_id"]: task for task in queue["tasks"]}
    record_ids = [record["record_id"] for record in ledger["ledger_records"]]
    if len(record_ids) != len(set(record_ids)):
        fail("run ledger record IDs must be unique")

    cutoff_task = ledger["imported_history"]["cutoff_task"]
    if cutoff_task not in task_by_id:
        fail("run ledger cutoff task must exist in rolling queue")
    if task_by_id[cutoff_task]["status"] not in {"completed", "merged", "skipped", "superseded", "cancelled"}:
        fail("run ledger cutoff task must be terminal in rolling queue")

    latest_record_task = None
    for record in ledger["ledger_records"]:
        task_ref = record["task_ref"]
        if task_ref is not None:
            if task_ref not in task_by_id:
                fail(f"ledger record references unknown task {task_ref}")
            if task_by_id[task_ref]["status"] not in {"completed", "merged"}:
                fail(f"ledger record references non-completed task {task_ref}")
            latest_record_task = task_ref

        if record["status"] == "merged":
            if not record["pr_number"] or not record["merge_sha"]:
                fail("merged ledger record must include PR number and merge SHA")
            if record["ci_conclusion"] != "success":
                fail("merged ledger record must have successful CI conclusion")

        boundaries = set(record["boundary_assertions"])
        missing_boundaries = REQUIRED_BOUNDARIES - boundaries
        if missing_boundaries:
            fail(f"ledger record missing boundary assertions: {sorted(missing_boundaries)}")

        artifact_paths = [artifact["path"] for artifact in record["artifacts"]]
        if any(path == "Merged PR artifacts" for path in artifact_paths):
            fail("ledger artifacts must name concrete files, not generic merged artifacts")
        if not record["critique_summary"]:
            fail("ledger record must include critique summary")

    if latest_record_task is None:
        fail("run ledger must include at least one task-linked record")

    print("Run ledger validation passed")


if __name__ == "__main__":
    main()
