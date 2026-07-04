# RTAQ-0033 Primary Validation Chain Closure

## Objective

Promote queue and run-ledger validation from delegated repository checks into the primary `Validate` workflow so shared execution-state invariants fail at the same exact PR head as the responsive, evidence, pilot, STATUS, and automation-control guards.

## Technical decision

The rolling queue remains a historical, non-authoritative execution artifact under `planning/EV4_AUTOMATION_CONTROL_STATE.json`. Because it is still a shared truth-boundary file and the run ledger still references queue task history, their validators must run automatically in the primary validation chain rather than relying on manual or delegated execution.

## Changes

- Add `python validation/e2e/run_rolling_queue_check.py` to `.github/workflows/validate.yml`.
- Add `python validation/e2e/run_run_ledger_check.py` to `.github/workflows/validate.yml`.
- Add deterministic diagnostics for both guard files.
- Update `STATUS.md` so `active_validation` and `automatic_check` match the primary validation chain and `delegated_repository_checks` is empty.

## Boundaries preserved

- No rolling queue history is rewritten.
- No run ledger history is backfilled.
- No submitted evidence is created.
- Issue #8 is not mutated.
- No real pilot is started or authorized.
- No readiness, production, release, live-render, export, accessibility, pixel, or responsive-correctness claim is upgraded.

## Validation expectation

GitHub Actions `Validate` must pass on the configured Python matrix for the exact PR head before merge. CI success remains repository-check evidence only and is not responsive correctness evidence.
