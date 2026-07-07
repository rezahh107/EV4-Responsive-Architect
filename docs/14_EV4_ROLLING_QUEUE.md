# EV4 Rolling Queue Controller

Version: 1.4.0  
Status: historical_reconciled_archive_retired_as_execution_driver

## Purpose

The rolling queue previously kept the EV4 Responsive Architect project moving between automation or manual-controller runs.

It is no longer the current execution driver.

The current driver is:

```text
work_package_catalog_guard
```

The approved material-objective source is:

```text
planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json
```

## Current live files

The historical queue archive is stored in:

```text
planning/EV4_ROLLING_QUEUE.json
```

The automation control state is stored in:

```text
planning/EV4_AUTOMATION_CONTROL_STATE.json
```

The Work Package Catalog is stored in:

```text
planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json
```

The run ledger is stored in:

```text
planning/EV4_RUN_LEDGER.json
```

The queue and archive discipline are still validated by:

```bash
python validation/e2e/run_rolling_queue_check.py
```

The run ledger is validated by:

```bash
python validation/e2e/run_run_ledger_check.py
```

The catalog-backed execution model is validated by:

```bash
python validation/e2e/run_automation_control_state_check.py
python validation/e2e/run_automation_work_package_catalog_check.py
```

## Boundary

The queue remains useful as an audit artifact. It is not an evidence authority and not an execution authority.

```text
Queue task completion != evidence validation
CI success != responsive validation
Merged PR != authoritative evidence
Run ledger record != production readiness
Catalog completion != evidence validation
```

## Retired operating model

The old rolling-queue model used small bounded tasks and queue refreshes. It created useful audit history but encouraged micro-task execution, checkpoint/status work, and frequent PR/CI/review overhead.

The current model is:

```text
approved Work Package Catalog → one material Work Package or reviewable PR slice → preserved gates → recorded outcome
```

## Forbidden under the current model

```text
rolling_queue as current_execution_driver
new arbitrary RTAQ task invention
checkpoint-only PR after every merge
artificial reserve task to keep queue depth high
queue-refresh loop as execution driver
guard-only task that does not unblock a named Work Package
```

## Status values preserved in history

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

Historical blocked tasks must include a blocker reason.

## Historical task types

```text
repo_sync
evidence_bridge
validator_hardening
schema_hardening
pilot_preparation
real_evidence_execution
queue_refresh
evidence_boundary
```

`real_evidence_execution` tasks must explicitly require real evidence.

## Completion definition

The project is not complete because the queue says so, and it is not complete because the catalog says so. The project reaches handoff readiness only when real evidence exists, the submitted evidence packet validates, readiness passes, the shadow-mode pilot produces controlled artifacts, and the final audit allows controlled handoff.
