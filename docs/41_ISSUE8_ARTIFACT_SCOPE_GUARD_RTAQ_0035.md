# RTAQ-0035 Issue #8 artifact scope guard

## Objective

Close the remaining evidence-intake matrix gap where a `real_issue_submission` packet could be locked to Issue #8 while its artifact references pointed at another issue or an unscoped submitted path.

## Technical decision

For real Issue #8 submissions, the fixture matrix now requires every submitted handoff and evidence attachment reference to carry an Issue #8-scoped marker such as `issues/8/`, `issue-8`, or `issue_8`. This is a repository-side intake guard only; it does not fetch Issue #8 or convert any attachment into submitted evidence.

## Changed artifacts

- `validation/e2e/run_evidence_intake_fixture_matrix_check.py`
- `validation/fixtures/invalid/evidence_intake_real_wrong_issue_artifact.invalid.json`

## Boundary

This change only hardens fixture validation. It does not create submitted evidence, mutate Issue #8, start pilot execution, or upgrade readiness, production, release, accessibility, live-render, export, pixel, or responsive-correctness claims.

## Validation expectation

The primary Validate workflow must pass on the exact PR head before merge. CI success remains repository-check evidence only and does not prove responsive correctness.
