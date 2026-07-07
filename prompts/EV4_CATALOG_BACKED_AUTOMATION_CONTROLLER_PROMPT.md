# EV4 Catalog-Backed Automation Controller Prompt

You are operating inside `rezahh107/EV4-Responsive-Architect`.

## Required preflight

Read live GitHub and repository state first:

```text
open PRs
latest merged/closed PRs
default branch/head
.github/workflows/validate.yml
STATUS.md
planning/EV4_AUTOMATION_CONTROL_STATE.json
planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json
planning/EV4_AUTOMATION_QUALITY_GATE.json
```

If any open automation PR exists, reconcile it before starting any new mutation.

## Controller algorithm

```text
START
1. Read live GitHub/repo state.
2. If an open automation PR exists, reconcile that PR first.
3. If an active Work Package exists and no blocking PR conflict exists, continue the next safe slice of that Work Package.
4. If no active Work Package exists, select the best ready Work Package from the approved catalog.
5. In parallel as non-mutating decision logic, check ready catalog depth.
6. If ready depth is below threshold, prepare or perform catalog replenishment only when single-active-PR policy allows it.
7. Never refresh because of a fixed task ordinal.
8. Never invent micro-tasks outside the catalog.
9. Preserve CI, review, evidence, pilot, readiness, production, release, and responsive-correctness boundaries.
END
```

## Selection rule

Read the Work Package Catalog first.

Select exactly one of:

```text
one approved selectable Work Package
one approved PR slice under one Work Package ID
```

Never invent new `RTAQ-*` tasks, micro-tasks, guard-only tasks, checkpoint-only tasks, queue-depth reserve tasks, or unrelated objectives outside the catalog.

Stop after one material objective slice.

## Catalog replenishment rule

Planning remains automatic. The user does not need to manually ask for the next five tasks.

Catalog replenishment is state-driven, schema-backed, CI-validated, and PR-reviewed.

Allowed replenishment triggers:

```text
ready Work Package depth is below threshold
active Work Package completed and project state changed
material blocker changed priorities
core contract or architecture changed
no executable Work Package exists and a real project gap is detected
```

Forbidden replenishment triggers:

```text
every fifth task
after four tasks create the next four tasks
refresh because a fixed count was reached
checkpoint-only refresh
bookkeeping-only refresh
artificial reserve work
```

If an active mutation PR exists, allowed replenishment behavior is limited to:

```text
detect catalog depth
report replenishment needed
prepare non-mutating replenishment plan
update catalog only if in-scope for the same active PR
```

Forbidden while an active mutation PR exists:

```text
create parallel catalog PR
interrupt active Work Package
start unrelated catalog mutation
create checkpoint-only catalog refresh PR
```

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
artificial reserve tasks
queue-refresh loops
fixed ordinal refresh
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
Do not treat merged PRs, Work Package completion, or catalog completion as domain evidence.
Do not restore rolling_queue as the current execution driver.
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
catalog depth decision
replenishment action or non-action
safety/evidence boundaries preserved
open PR reconciliation result
remaining risks
next safe human action
```
