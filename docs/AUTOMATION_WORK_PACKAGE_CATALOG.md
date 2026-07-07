# Automation Work Package Catalog

## Purpose

`planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json` is the approved source for future automation objective selection.

The catalog replaces the old queue-driven execution habit:

```text
old: micro task → tiny PR → CI/review → queue/ledger/status sync → refresh queue
new: approved Work Package Catalog → one material Work Package or PR slice → reviewable PR → preserved gates → recorded outcome
```

Planning remains automatic. The controller must inspect repository state and decide whether to reconcile an open PR, continue an active Work Package, select the next ready Work Package, or prepare state-driven catalog replenishment when policy allows it.

## Why the rolling-queue model was retired as the driver

The rolling queue preserved history and auditability, but it encouraged very small tasks, frequent queue refreshes, checkpoint/status PRs, and high PR/CI/review overhead for minor changes.

The queue is still retained as a reconciled archive:

```text
planning/EV4_ROLLING_QUEUE.json = historical_reconciled_archive
```

It is not the current execution driver.

## Current execution driver

```yaml
current_execution_driver: work_package_catalog_guard
catalog: planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json
schema: schemas/ev4-automation-work-package-catalog.schema.json
validator: validation/e2e/run_automation_work_package_catalog_check.py
```

Future automation must select exactly one approved Work Package, or exactly one approved PR slice under a Work Package, from the catalog.

It must not invent arbitrary `RTAQ-*` tasks, micro-tasks, checkpoint-only tasks, guard-only tasks, or artificial reserve tasks outside the catalog.

## Three execution layers

```text
Work Package = capability objective
PR = reviewable implementation slice under one Work Package ID
Automation Run = bounded attempt to advance or reconcile the active objective
```

A Work Package can be capability-sized. A PR must remain reviewable. An automation run must not expand into unrelated work.

## Automatic planning and replenishment

Catalog replenishment is automatic but state-driven. It is not a fixed ordinal refresh.

Allowed replenishment triggers are repository-state changes such as:

```text
ready Work Package depth below threshold
active Work Package completed and project state changed
material blocker changed priorities
core contract or architecture changed
no executable Work Package exists and a real project gap is detected
```

Forbidden refresh triggers are:

```text
every fifth task
after four tasks create the next four tasks
refresh because a fixed count was reached
checkpoint-only refresh
bookkeeping-only refresh
artificial reserve work
```

## Active execution takes priority

Catalog replenishment must not block active execution.

If an active Work Package or active PR exists, the controller must prioritize continuing or reconciling that work. It may still inspect catalog depth and report that replenishment is needed, but mutation is limited by the single-active-mutation-PR policy.

## Single-active-mutation-PR policy

When an active mutation PR exists, the controller may:

```text
detect catalog depth
report replenishment needed
prepare a non-mutating replenishment plan
update the catalog only if the catalog change is in-scope for the same active PR
```

It must not:

```text
create a parallel catalog PR
interrupt the active Work Package
start unrelated catalog mutation
create checkpoint-only or bookkeeping-only catalog refresh PRs
```

When no active mutation PR exists, the controller may continue an active Work Package, select the next ready Work Package, or create a catalog replenishment PR only when ready depth is below threshold and the replenishment is state-driven, schema-backed, CI-validated, and reviewable.

## Reviewable PR slices

When splitting is necessary, split by implementation layer under the same Work Package ID.

Acceptable examples:

```text
WP-RESP-001/PR-A: schema and fixtures
WP-RESP-001/PR-B: validators and CI
WP-RESP-001/PR-C: docs, STATUS, and final integration
```

Forbidden examples:

```text
invent unrelated RTAQ tasks
create guard-only work that does not unblock a named Work Package
add checkpoint-only PRs after every merge
create artificial reserve tasks to keep task count high
restore rolling_queue as the driver by implication
refresh because a fixed ordinal was reached
```

## Work Package quality requirements

Each Work Package must have measurable current state, measurable target state, a capability-level outcome, truth boundaries, acceptance gates, and negative fixture coverage when applicable.

Any estimated percentage is reporting-only. It is not evidence validation, readiness proof, or completion proof.

## Safety gates remain mandatory

Catalog selection does not weaken existing gates. A PR slice must preserve:

```text
CI validation
reviewability
schema-backed contracts
validator-backed checks
STATUS/workflow parity when touched
run-ledger and quality-gate discipline where applicable
```

CI success remains repository-check evidence only. It is not responsive correctness evidence.

## Evidence, pilot, readiness, and production boundary

The catalog does not authorize:

```text
submitted evidence creation
Issue #8 mutation
real pilot execution
production_ready
release_ready
live_render_validated
export_json_validated
accessibility_passed
pixel_perfect
responsive_correctness_validated
```

A completed catalog Work Package is not evidence validation. Real submitted evidence and readiness gates must pass before any stronger claim can be made.
