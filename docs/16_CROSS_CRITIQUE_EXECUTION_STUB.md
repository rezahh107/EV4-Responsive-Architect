# Cross-Critique Execution Stub

Status: active stub

This layer prepares the automation quality gate for a separate reviewer step.

## Purpose

Self-critique is required but not sufficient for sensitive tasks. A separate review record must be produced for sensitive automation work.

## Files

```text
prompts/CROSS_CRITIQUE_STRICT_REVIEWER_PROMPT.md
planning/reviews/CROSS_CRITIQUE_REQUEST.template.md
planning/reviews/TQR-RQ-0000.cross-review.example.json
validation/e2e/run_cross_critique_stub_check.py
```

## Current Boundary

This is a validation stub. It does not call an external LLM from GitHub Actions yet.

It enforces that the repository has:

```text
- a separated strict reviewer prompt
- a request template for sensitive task review
- a valid task-quality review record example
- CI validation through the rolling queue check
```

## Required Reviewer Contract

For sensitive tasks:

```text
reviewer_role = strict_pessimistic_reviewer
prompt_separation = true
temperature_policy = temperature_0_1_recommended
cross_critique.status = completed
```

## Next Hardening Step

A later task may add an actual external reviewer runner. Until then, sensitive task completion must still provide a cross-critique record that validates against `ev4-responsive-task-quality-review@1.0.0`.
