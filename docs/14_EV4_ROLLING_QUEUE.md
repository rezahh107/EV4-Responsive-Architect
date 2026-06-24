# EV4 Rolling Queue Controller

Version: 1.1.0
Status: active_with_run_ledger

## Purpose

The rolling queue keeps the EV4 Responsive Architect project moving without losing state between hourly automation runs.

The active queue is stored in:

```text
planning/EV4_ROLLING_QUEUE.json
```

The run ledger is stored in:

```text
planning/EV4_RUN_LEDGER.json
```

The queue is validated by:

```bash
python validation/e2e/run_rolling_queue_check.py
```

The run ledger is validated by:

```bash
python validation/e2e/run_run_ledger_check.py
```

## Operating Model

Each automation run must execute exactly one bounded task from the queue.

After the task is complete, the same run must critique that task. Small fixes are allowed only when they are inside the same task scope.

The fifth task in each active cycle is always a queue-refresh task. It audits the previous four tasks and writes the next four bounded tasks plus the next refresh task.

## Queue Rules

```text
- one task per automation run
- same-task critique required
- at least four pending tasks while queue_status is active
- every fifth active-cycle task must be queue_refresh
- CI is required for repo changes
- real pilot execution is blocked until real submitted evidence and readiness gates pass
```

## Run Ledger Rules

Each completed controller run that changes repo state should have a run-ledger record.

A ledger record must include:

```text
- task_ref when the run maps to a queue task
- PR number when repo files changed
- merge SHA when merged
- CI conclusion
- concrete artifact paths
- critique summary
- boundary assertions
- next queue effect
```

The ledger is not a replacement for the queue. It is an audit companion that prevents completed tasks from being recorded only as generic merged artifacts.

## Status Values

```text
pending
in_progress
completed
merged
blocked
skipped
superseded
cancelled
stale_in_progress
```

Blocked tasks must include a blocker reason.

## Task Types

```text
repo_sync
evidence_bridge
validator_hardening
schema_hardening
pilot_preparation
real_evidence_execution
queue_refresh
```

`real_evidence_execution` tasks must explicitly require real evidence.

## Live Queue Source

Do not copy the current task list into this document. The live cycle changes as automation runs.

Read the current queue from:

```text
planning/EV4_ROLLING_QUEUE.json
```

Read completed-run audit records from:

```text
planning/EV4_RUN_LEDGER.json
```

## Boundary

This queue does not authorize these claims:

```text
production_ready
release_ready
pixel_perfect
live_render_validated
export_json_validated
accessibility_passed
sample packet used as real evidence
numeric score overriding a hard gate
```

## Completion Definition

The project is not complete because the queue says so. The project reaches handoff readiness only when real evidence exists, the submitted evidence packet validates, readiness passes, the shadow-mode pilot produces controlled artifacts, and the final audit allows controlled handoff.
