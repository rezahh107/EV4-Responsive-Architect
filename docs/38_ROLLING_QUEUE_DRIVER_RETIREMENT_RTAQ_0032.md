# RTAQ-0032 — Rolling Queue Driver Retirement

## Purpose

This document records the execution-control boundary after the automation control-state guard was introduced and later refactored to a catalog-backed Work Package model.

The rolling queue remains a preserved historical planning artifact. It is not the current execution driver.

## Current execution source of truth

```yaml
execution_state_source_of_truth: planning/EV4_AUTOMATION_CONTROL_STATE.json
current_execution_driver: work_package_catalog_guard
work_package_catalog: planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json
catalog_authority: approved_material_objective_source
rolling_queue_authority: historical_reconciled_archive
rolling_queue_execution_status: retired_as_execution_driver
```

## Decision

`planning/EV4_ROLLING_QUEUE.json` must not be treated as the live automation driver. It is a reconciled archive of historical queue work.

Future automation must select material objectives only from:

```text
planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json
```

The catalog is schema-backed by:

```text
schemas/ev4-automation-work-package-catalog.schema.json
```

and guarded by:

```text
validation/e2e/run_automation_work_package_catalog_check.py
```

The control state is schema-backed by:

```text
schemas/ev4-automation-control-state.schema.json
```

and guarded by:

```text
validation/e2e/run_automation_control_state_check.py
```

## Non-goals

This change does not:

- restore rolling queue execution authority;
- rewrite rolling-queue history;
- invent new `RTAQ-*` tasks;
- backfill the run ledger;
- create submitted evidence;
- mutate Issue #8;
- start or authorize a real pilot;
- upgrade readiness, production, release, live-render, export, accessibility, pixel, or responsive-correctness claims.

## Required invariant

Any future change that restores the rolling queue as an execution driver must first perform a deliberate queue reconciliation and update the control-state schema, control-state file, STATUS markers, validators, and CI in the same PR.

Until then, material-objective PRs must proceed through the Work Package Catalog guard and must not treat rolling-queue archive state as current execution authority.
