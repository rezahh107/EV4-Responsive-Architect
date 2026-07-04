# RTAQ-0032 — Rolling Queue Driver Retirement

## Purpose

This document records the execution-control boundary after the automation control-state guard was introduced.

The rolling queue remains a preserved historical planning artifact. It is not the current execution driver.

## Current execution source of truth

```yaml
execution_state_source_of_truth: planning/EV4_AUTOMATION_CONTROL_STATE.json
current_execution_driver: bounded_material_checkpoint_guard
rolling_queue_authority: historical_non_authoritative_until_reconciled
rolling_queue_execution_status: retired_as_execution_driver
```

## Decision

`planning/EV4_ROLLING_QUEUE.json` must not be treated as the live automation driver while it still contains stale historical queue state.

The control state is now schema-backed by:

```text
schemas/ev4-automation-control-state.schema.json
```

and guarded by:

```text
validation/e2e/run_automation_control_state_check.py
```

## Non-goals

This change does not:

- rewrite rolling-queue history;
- invent new RTAQ tasks;
- backfill the run ledger;
- create submitted evidence;
- mutate Issue #8;
- start or authorize a real pilot;
- upgrade readiness, production, release, live-render, export, accessibility, pixel, or responsive-correctness claims.

## Required invariant

Any future change that restores the rolling queue as an execution driver must first perform a deliberate queue reconciliation and update the control-state schema, control-state file, STATUS markers, and validators in the same PR.

Until then, material-objective PRs may proceed through the bounded material checkpoint guard without treating stale rolling-queue state as current execution authority.
