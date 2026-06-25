# Cross-Critique Execution Stub

Status: active generation path

This layer prepares the automation quality gate for a separate reviewer step and now defines a machine-checkable request and review-record path.

## Purpose

Self-critique is required but not sufficient for sensitive tasks. A separate review record must be produced for sensitive automation work.

## Files

```text
prompts/CROSS_CRITIQUE_STRICT_REVIEWER_PROMPT.md
planning/reviews/CROSS_CRITIQUE_REQUEST.template.md
planning/reviews/CROSS_REVIEW_RECORD.template.json
planning/reviews/TQR-RQ-0000.cross-review.example.json
planning/reviews/README.md
validation/e2e/run_cross_critique_stub_check.py
validation/e2e/run_cross_review_generation_path_check.py
```

## Generated Artifact Paths

```text
planning/reviews/CRR-{TASK_REF}.cross-review-request.md
planning/reviews/TQR-{TASK_REF}.cross-review.json
```

## Current Boundary

This remains a validation path. It does not call an external LLM from GitHub Actions yet.

It enforces that the repository has:

```text
- a separated strict reviewer prompt
- a request template for sensitive task review
- a blocked review-record template
- a valid completed task-quality review record example
- CI validation through the rolling queue check and cross-review generation path check
```

## Required Reviewer Contract

For sensitive tasks:

```text
reviewer_role = strict_pessimistic_reviewer
prompt_separation = true
temperature_policy = temperature_0_1_recommended
cross_critique.status = completed
review_record_path = planning/reviews/TQR-{TASK_REF}.cross-review.json
```

## Boundary

Cross-review records are automation quality-control artifacts only. They are not real responsive evidence, real pilot evidence, production validation, release validation, export validation, live-render validation, or accessibility validation.

## Next Hardening Step

A later task may add an actual external reviewer runner. Until then, sensitive task completion must still provide a cross-critique record that validates against `ev4-responsive-task-quality-review@1.0.0`.
