# RTAQ-0037 Control Checkpoint Reconciliation

## Objective

Reconcile the automation control checkpoint after the merged validation-chain work through PR #120 without restoring the retired rolling queue as an execution driver.

## Technical decision

The active execution source remains `planning/EV4_AUTOMATION_CONTROL_STATE.json`. The rolling queue is preserved as historical execution intent until a separate material reconciliation updates it. This PR updates the enforced automation-control schema constant and control-state file to the latest material checkpoint, rather than creating a status-only or merge-final bookkeeping PR.

## Changes

- Update `planning/EV4_AUTOMATION_CONTROL_STATE.json` so `latest_material_checkpoint` reflects PR #120.
- Update `schemas/ev4-automation-control-state.schema.json` so the validator enforces the reconciled checkpoint value.
- Update `STATUS.md` to expose the same checkpoint and this reconciliation artifact.

## Boundary

- Does not create submitted evidence.
- Does not mutate Issue #8.
- Does not restore the rolling queue as the execution driver.
- Does not start or authorize pilot execution.
- Does not upgrade readiness, production, release, accessibility, live-render, export, pixel, or responsive-correctness claims.

## Validation expectation

The primary Validate workflow must pass on the exact PR head before merge. CI success remains repository-check evidence only and is not responsive correctness evidence.
