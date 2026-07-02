# Throughput Control Plane Hardening

This document records the bounded control-plane hardening objective that replaces artificial queue churn with primary-objective throughput.

## Verified input state

- `planning/EV4_ROLLING_QUEUE.json` still encoded `one_task_per_run: true` and `refresh_every_nth_task: 5`.
- The active queue still carried artificial reserve placeholders `RTAQ-0011`, `RTAQ-0012`, and `RTAQ-0013`.
- `STATUS.md` recorded PR #84 as merged and `RTAQ-0010` as the latest completed task, while the queue still showed `RTAQ-0010` as pending.
- `.github/workflows/validate.yml` did not expose a same-head `workflow_dispatch` recovery path with exact-SHA verification.

## Hardening decisions

- Runs are scoped to one primary objective, not one tiny task.
- Same-scope diagnosis, implementation, critique fixes, validation, CI recovery, merge, and post-merge verification may be completed together when safe.
- Planning refresh is triggered by actionable depth falling below the configured threshold or material priority change, not task ordinal position.
- Artificial reserve, status-only, keepalive, merge-final-only, and bookkeeping-only work is not executable queue work.
- Same-head CI recovery is supported through `workflow_dispatch` inputs `ref` and `expected_sha`; the workflow checks out the requested ref and fails if `git rev-parse HEAD` differs from `expected_sha`.

## Queue reconciliation

- `RTAQ-0010` is reconciled to merged because PR #84 is merged and `STATUS.md` already recorded it as the latest completed task.
- `RTAQ-0011` through `RTAQ-0013` are marked `superseded` because they only preserved pending depth.
- `RTAQ-0014` through `RTAQ-0017` provide four bounded actionable objectives without starting evidence, pilot, readiness, production, release, live-render, export, accessibility, or pixel claims.

## Boundary

This hardening changes repository control-plane mechanics only. It creates no submitted evidence, does not modify Issue #8, does not run or authorize a real pilot, and does not upgrade readiness, production, release, live-render, export, accessibility, pixel, or responsive-correctness claims.
