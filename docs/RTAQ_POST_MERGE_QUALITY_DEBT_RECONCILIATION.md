# RTAQ post-merge quality debt reconciliation

Status: active reconciliation record  
Scope: known automation-quality debt accumulated through PR #135 plus WP-RESP-003 fixture coverage closure  
Runtime behavior changed: no  
Responsive-correctness claim changed: no

## Purpose

This document records a bounded reconciliation of automation-quality debt found after recent post-queue hardening PRs. It is not a feature document, not submitted evidence, not a pilot/readiness artifact, and not proof of responsive correctness.

## QD-001 — malformed-hash fixture contradiction

Status: resolved.

PR #134 added `validation/fixtures/invalid/builder_responsive_input_malformed_hash.invalid.json` as a malformed-hash negative fixture. The fixture reason said a malformed Project Gate digest must deny Builder to Responsive intake eligibility, but `responsive_intake_decision.intake_allowed` was `true`.

Resolution in this reconciliation:

- `responsive_intake_decision.intake_allowed` is set to `false` for the malformed-hash fixture.
- Builder invalid fixtures that describe denied intake are semantically fail-closed.
- `validation/e2e/run_builder_responsive_input_boundary_check.py` now checks invalid fixture semantic consistency before/alongside expected schema failure.
- Legacy invalid fixture filenames are preserved to avoid rename churn; the fixture payloads now carry fail-closed intake decisions.

## QD-002 — duplicate RTAQ-0049 traceability

Status: resolved as bounded traceability clarification.

The visible ordinal `RTAQ-0049` appeared in three merged PR titles. Git history and merged PR titles are not rewritten by this reconciliation.

Traceability map:

| PR | Visible ordinal | Actual bounded slice |
| --- | --- | --- |
| #133 | RTAQ-0049 | real submitted example artifact guard |
| #134 | RTAQ-0049 | Builder digest boundary hardening |
| #135 | RTAQ-0049 | submitted payload hash format guard |

These are three post-queue hardening slices sharing a visible ordinal. They are not three separate queue tasks, and they do not authorize submitted evidence, pilot execution, readiness upgrade, release readiness, production readiness, live-render validation, export validation, accessibility pass, pixel matching, or responsive-correctness claims.

## QD-003 — stale RTAQ-0011 state-sync tooling

Status: resolved.

The current control-state model says rolling queue execution is retired as an execution driver, with bounded checkpoint-only policy. The archived rolling queue shows RTAQ-0010 merged and RTAQ-0011 superseded, and `STATUS.md` records `rolling_queue_reconciliation_required: false`.

Resolution in this reconciliation:

- `validation/e2e/run_rtaq_0011_state_sync_plan_check.py` accepts the current archive/retired/superseded state.
- `tools/rtaq_0011_state_sync_applier.py` exits cleanly as a no-op in that state, including when invoked with `--write`.
- This reconciliation does not fabricate `LEDGER-0021` and does not revive rolling queue execution authority.

## QD-004 — delayed review-window / post-merge review debt

Status: resolved for the known actionable item; fast-merge timing remains historical bounded debt.

The automation quality gate declares a delayed-review policy with a minimum 10-minute wait before merge. Some recent PRs were merged quickly, and PR #134 received an actionable Gemini review comment after merge.

Resolution in this reconciliation:

- The actionable PR #134 review item is resolved by QD-001.
- The incident is recorded here and in `planning/EV4_POST_MERGE_QUALITY_DEBT_REGISTER.json`.
- The existing Builder boundary validator now validates that all P1 quality-debt register items are resolved or explicitly bounded, so known post-merge actionable review debt cannot remain silent in repository checks.

This does not pretend that local CI can enforce GitHub elapsed merge time without network state.

## QD-005 — quality-debt register negative fixture coverage

Status: resolved.

The quality-debt register was checked by the Builder boundary validator, but the validator did not require named negative fixtures proving that unresolved P1 debt or forbidden boundary-claim upgrades fail closed.

Resolution in this reconciliation:

- `validation/fixtures/invalid/quality_debt_register_unresolved_p1.invalid.json` proves unresolved P1 quality debt is rejected.
- `validation/fixtures/invalid/quality_debt_register_boundary_upgrade.invalid.json` proves forbidden boundary upgrades are rejected.
- `validation/e2e/run_builder_responsive_input_boundary_check.py` now requires exactly those quality-debt negative fixtures and asserts they cannot satisfy the live register guard.

This remains repository quality-gate evidence only. It does not create submitted evidence, mutate Issue #8, authorize pilot execution, or upgrade readiness or responsive-correctness claims.

## Boundary

This reconciliation does not create submitted evidence, does not mutate Issue #8, does not run or authorize a pilot, and does not upgrade readiness, production, release, live-render, export, accessibility, pixel, or responsive-correctness claims. CI success remains repository-check evidence only.
