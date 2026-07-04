# RTAQ-0034 Issue #8 submitted path guard

## Objective

Close an evidence-boundary gap in the evidence-intake fixture matrix: a `real_issue_submission` packet for Issue #8 must not use repository example or template paths as if they were submitted evidence attachments.

## Technical decision

The repository may keep example fixtures for contract validation, but real Issue #8 submissions must reference submitted Issue #8 evidence artifacts. The matrix guard now rejects `examples/` and `template/` references when `packet_origin` is `real_issue_submission`.

## Changed artifacts

- `validation/e2e/run_evidence_intake_fixture_matrix_check.py`
- `validation/fixtures/invalid/evidence_intake_real_example_artifact.invalid.json`

## Boundary

This is a fixture and validator hardening change only. It does not fetch or mutate Issue #8, create submitted evidence, start pilot execution, or upgrade readiness, production, release, accessibility, live-render, export, pixel, or responsive-correctness claims.

## Validation expectation

The primary Validate workflow must pass on the exact PR head before merge. CI success remains repository-check evidence only and does not prove responsive correctness.
