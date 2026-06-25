# Review Artifact Path

This directory contains machine-checkable request and review-record artifacts for sensitive EV4 automation tasks.

## Required generated paths

```text
planning/reviews/TQR-{TASK_REF}.cross-review.json
planning/reviews/CRR-{TASK_REF}.cross-review-request.md
```

## Contract

Sensitive automation tasks may not be completed by self-critique alone. A separate strict reviewer must produce a review record that validates against `ev4-responsive-task-quality-review@1.0.0`.

The review record must:

```text
- use reviewer_role=strict_pessimistic_reviewer
- preserve prompt_separation=true
- use temperature_policy=temperature_0_1_recommended
- set cross_critique.status=completed before completion is allowed
- include deterministic checks, findings, and boundary assertions
```

## Boundary

These artifacts are quality-control records only. They are not responsive evidence, real pilot evidence, production validation, release validation, export validation, live-render validation, or accessibility validation.
