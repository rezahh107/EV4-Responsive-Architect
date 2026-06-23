# EV4 Rolling Queue Controller

Version: 1.0.0
Status: active

## Purpose

The rolling queue keeps the EV4 Responsive Architect project moving without losing state between hourly automation runs.

The queue is stored in:

```text
planning/EV4_ROLLING_QUEUE.json
```

The queue is validated by:

```bash
python validation/e2e/run_rolling_queue_check.py
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

## Status Values

```text
pending
in_progress
merged
blocked
skipped
superseded
```

Blocked tasks must include a blocker reason.

## Task Types

```text
repo_sync
evidence_bridge
validator_hardening
pilot_preparation
real_evidence_execution
queue_refresh
```

`real_evidence_execution` tasks must explicitly require real evidence.

## Current Initial Cycle

```text
RQ-0001: Sync STATUS and Issue 8
RQ-0002: Define Issue-to-Packet bridge
RQ-0003: Add conflict summary to readiness path
RQ-0004: Prepare real pilot artifact slots
RQ-0005: Refresh rolling queue
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
