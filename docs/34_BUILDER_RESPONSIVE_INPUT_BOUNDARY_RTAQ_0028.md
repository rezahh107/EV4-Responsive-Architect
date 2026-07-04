# RTAQ-0028 Builder → Responsive input boundary

## Objective

Close the Builder → Responsive intake gap that was still marked `not_implemented` by adding a schema-bound, non-executing Responsive intake eligibility package.

## Technical decision

The new package validates only the shape and evidence references of a future Builder handoff. It deliberately stops before Project Gate execution, pilot execution, readiness generation, or any responsive-correctness claim.

## Added boundary artifacts

```yaml
schema: schemas/ev4-builder-responsive-input.schema.json
validator: validation/e2e/run_builder_responsive_input_boundary_check.py
valid_fixture:
  - validation/fixtures/valid/builder_responsive_input.valid.json
invalid_fixture:
  - validation/fixtures/invalid/builder_responsive_input_missing_mobile_evidence.invalid.json
workflow_gate: .github/workflows/validate.yml
claim_boundary: input eligibility only; not responsive correctness evidence
```

## Acceptance boundary

- Required Builder evidence references are explicit.
- Desktop, tablet, and mobile evidence slots are explicit.
- Missing mobile evidence is rejected by a negative fixture.
- Repository checks cannot become frontend, viewport, export, accessibility, release, production, or pilot evidence.

## Non-goals

- No Project Gate implementation.
- No Issue #8 mutation.
- No submitted evidence creation.
- No pilot execution or authorization.
- No readiness, production, release, live-render, export, accessibility, pixel, or responsive-correctness claim upgrade.
