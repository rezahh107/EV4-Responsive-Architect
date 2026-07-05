# RTAQ-0036 Pilot readiness Validate chain closure

## Objective

Close the primary validation-chain gap where the pilot readiness report generator existed in the repository but was not executed by the primary Validate workflow.

## Technical decision

The existing `validation/e2e/run_pilot_readiness_check.py` self-test now runs as a first-class Validate step on the repository-supported Python matrix. This keeps readiness report generation covered before any future submitted packet can be used to request shadow-mode pilot start.

## Changed artifacts

- `.github/workflows/validate.yml`
- `STATUS.md`

## Boundary

This change validates repository readiness-report behavior only. It does not create submitted evidence, mutate Issue #8, generate a real readiness report from submitted evidence, start pilot execution, or upgrade readiness, production, release, accessibility, live-render, export, pixel, or responsive-correctness claims.

## Validation expectation

The primary Validate workflow must pass on the exact PR head before merge. CI success remains repository-check evidence only and does not prove responsive correctness.
