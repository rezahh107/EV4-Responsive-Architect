# Automation Work Package Catalog

## Purpose

`planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json` is the approved source for future automation objective selection.

The catalog replaces the old queue-driven execution habit:

```text
old: micro task → tiny PR → CI/review → queue/ledger/status sync → refresh queue
new: approved Work Package Catalog → one material Work Package or PR slice → reviewable PR → preserved gates → recorded outcome
```

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

## How selection works

Before selecting new work, automation must:

1. inspect open PRs and reconcile any open automation PR first;
2. read `planning/EV4_AUTOMATION_CONTROL_STATE.json`;
3. read `planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json`;
4. choose one selectable Work Package or one allowed PR slice under that Work Package;
5. stop after one material objective slice.

A non-selectable maintenance Work Package may be edited only when a material catalog state changed. It must not become a recurring queue-refresh loop.

## Reviewable PR slices

A Work Package may be larger than a single tiny task, but each PR must remain reviewable.

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
```

## Safety gates remain mandatory

Catalog selection does not weaken existing gates. A PR slice must preserve:

```text
CI validation
reviewability
schema-backed contracts
validator-backed checks
STATUS/workflow parity
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
