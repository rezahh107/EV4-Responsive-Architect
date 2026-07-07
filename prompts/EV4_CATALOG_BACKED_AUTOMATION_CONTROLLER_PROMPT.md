# EV4 Catalog-Backed Automation Controller Prompt

You are operating inside `rezahh107/EV4-Responsive-Architect`.

## Required preflight

1. Inspect live repository state first:
   - open PRs;
   - latest merged/closed PRs;
   - default branch/head;
   - `.github/workflows/validate.yml`;
   - `STATUS.md`;
   - `planning/EV4_AUTOMATION_CONTROL_STATE.json`;
   - `planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json`.
2. If any open automation PR exists, reconcile it before selecting new catalog work.
3. Do not start a parallel automation PR unless the open PR is proven non-conflicting and the selected Work Package remains reviewable.

## Selection rule

Read the Work Package Catalog first.

Select exactly one of:

```text
one approved selectable Work Package
one approved PR slice under one Work Package ID
```

Never invent new `RTAQ-*` tasks, micro-tasks, guard-only tasks, checkpoint-only tasks, queue-depth reserve tasks, or unrelated objectives outside the catalog.

Stop after one material objective slice.

## Split rule

A Work Package may be large in objective, but each PR must remain reviewable.

If splitting is required, split by implementation layer under the same Work Package ID.

Acceptable:

```text
WP-RESP-001/PR-A: schema and fixtures
WP-RESP-001/PR-B: validators and CI
WP-RESP-001/PR-C: docs, STATUS, and final integration
```

Forbidden:

```text
unrelated RTAQ task invention
checkpoint-only work after every merge
airficial reserve tasks
queue-refresh loops
```

## Required preservation

Preserve existing quality gates and evidence boundaries:

```text
Do not create submitted evidence unless explicitly authorized.
Do not mutate Issue #8 unless explicitly authorized.
Do not run or authorize real pilot execution.
Do not claim production_ready.
Do not claim release_ready.
Do not claim live_render_validated.
Do not claim export_json_validated.
Do not claim accessibility_passed.
Do not claim pixel_perfect.
Do not claim responsive_correctness_validated.
Do not treat CI success as responsive correctness evidence.
Do not treat merged PRs or catalog completion as domain evidence.
```

## Required validation

Run or report why you could not run:

```bash
python validation/e2e/run_automation_control_state_check.py
python validation/e2e/run_automation_work_package_catalog_check.py
python validation/e2e/run_rolling_queue_check.py
python validation/e2e/run_run_ledger_check.py
python validation/e2e/run_task_quality_gate_check.py
```

If the selected slice changes workflow, STATUS, or validators, also run the affected targeted validators.

## Reporting

Report in Persian.

Include:

```text
selected Work Package ID
selected PR slice ID, if any
branch
files changed
tests run and results
tests not run and why
safety/evidence boundaries preserved
open PR reconciliation result
remaining risks
next safe human action
```
