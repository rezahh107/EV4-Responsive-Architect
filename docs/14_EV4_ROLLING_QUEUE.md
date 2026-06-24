# EV4 Rolling Queue Controller

Version: 1.2.0
Status: active_with_control_plane_and_run_ledger

## Purpose

The rolling queue keeps the EV4 Responsive Architect project moving without losing state between hourly automation runs.

The queue is an execution-control tool. It is not an evidence authority.

```text
Queue task completion != evidence validation
CI success != responsive validation
Merged PR != authoritative evidence
Run ledger record != production readiness
```

## Live Files

The active queue is stored in:

```text
planning/EV4_ROLLING_QUEUE.json
```

The queue control-plane policy is stored in:

```text
planning/EV4_QUEUE_CONTROL_PLANE.json
```

The run ledger is stored in:

```text
planning/EV4_RUN_LEDGER.json
```

The queue and control plane are validated by:

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

## Control-Plane Boundary

The queue control plane records rules that the automation must obey before executing a task:

```text
- the queue cannot create or upgrade evidence truth
- the queue cannot mark anything production-ready
- real pilot execution requires a validated real submitted packet and readiness pass
- current runtime state remains on main for now
- control/rolling-queue is a future migration candidate, not current runtime truth
```

This step intentionally does not move runtime queue state to a dedicated branch. A branch split requires a later migration task with lease recovery and optimistic locking tested.

## Queue Rules

```text
- one task per automation run
- same-task critique required
- at least four pending tasks while queue_status is active
- every fifth active-cycle task must be queue_refresh
- CI is required for repo changes
- real pilot execution is blocked until real submitted evidence and readiness gates pass
```

## Lease and Transition Policy

The control plane defines the intended lease and transition model:

```text
pending -> leased -> executing
executing -> awaiting_external | needs_review | blocked | completed
blocked -> pending | superseded | cancelled
```

Forbidden transitions include:

```text
pending -> completed
awaiting_external -> completed
blocked -> completed
```

The current implementation validates this policy as contract. Full write-mode leasing is a later hardening task.

## Diagnostics

The control plane defines diagnostics such as:

```text
RQ_SCHEMA_INVALID
RQ_ILLEGAL_TRANSITION
RQ_LEASE_CONFLICT
RQ_PR_STATE_DRIFT
RQ_CI_ACTION_REQUIRED
RQ_EVIDENCE_STATE_MISMATCH
```

A diagnostic must block or route work rather than silently repairing drift.

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
