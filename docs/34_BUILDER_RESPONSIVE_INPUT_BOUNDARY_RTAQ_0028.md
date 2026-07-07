# RTAQ-0028 Builder → Responsive input boundary

## Objective

Close the Builder → Responsive intake gap that was still marked `not_implemented` by adding a schema-bound, non-executing Responsive intake eligibility package.

WP-RESP-002/PR-A extends that boundary by making the future Builder → Project Gate → Responsive transition path operationally explicit while preserving the same non-executing, evidence-bound scope.

## Technical decision

The package validates only the shape and evidence references of a future Builder handoff. It deliberately stops before Project Gate execution, pilot execution, readiness generation, or any responsive-correctness claim.

Responsive owns only local intake eligibility checks. Builder remains responsible for Builder-owned output and execution evidence, and Project Gate remains responsible for verified transport of Builder-owned artifacts when that route exists. Responsive must not copy upstream schemas as canonical truth, fabricate missing evidence, or infer viewport correctness from transport.

## Added boundary artifacts

```yaml
schema: schemas/ev4-builder-responsive-input.schema.json
validator: validation/e2e/run_builder_responsive_input_boundary_check.py
valid_fixture:
  - validation/fixtures/valid/builder_responsive_input.valid.json
invalid_fixture:
  - validation/fixtures/invalid/builder_responsive_input_missing_mobile_evidence.invalid.json
  - validation/fixtures/invalid/builder_responsive_input_blocked_project_gate_allows_intake.invalid.json
  - validation/fixtures/invalid/builder_responsive_input_blocked_viewport_allows_intake.invalid.json
  - validation/fixtures/invalid/builder_responsive_input_forbidden_claim_subset.invalid.json
  - validation/fixtures/invalid/builder_responsive_input_malformed_hash.invalid.json
workflow_gate: .github/workflows/validate.yml
contract: contracts/BUILDER_TO_RESPONSIVE_INPUT_BOUNDARY.md
claim_boundary: input eligibility only; not responsive correctness evidence
```

## Project Gate transition interpretation

```yaml
future_transition_path:
  builder_output_and_build_evidence: Builder-owned
  project_gate_verification_transport: Project Gate-owned
  responsive_intake_eligibility: Responsive-owned

responsive_allowed_to_validate:
  - Project Gate reference is verified rather than blocked
  - Project Gate and Builder artifact digests match sha256:<64 lowercase hexadecimal characters>
  - Builder action, execution, layout, and completion evidence references are present
  - desktop, tablet, and mobile evidence slots are explicit and provided when intake is allowed
  - the intake decision preserves the canonical claim boundary

responsive_forbidden_to_claim:
  - production_ready
  - release_ready
  - live_render_validated
  - export_json_validated
  - accessibility_passed
  - pixel_perfect
  - responsive_correctness_validated
  - ci_success_as_frontend_evidence
```

## Acceptance boundary

- Required Builder evidence references are explicit.
- Desktop, tablet, and mobile evidence slots are explicit.
- Missing mobile evidence is rejected by a negative fixture.
- Blocked/non-verified Project Gate state is intake-blocking.
- Malformed Project Gate or Builder artifact digests are intake-blocking.
- Repository checks cannot become frontend, viewport, export, accessibility, release, production, or pilot evidence.

## Non-goals

- No Project Gate implementation.
- No Builder implementation.
- No Issue #8 mutation.
- No submitted evidence creation.
- No pilot execution or authorization.
- No readiness, production, release, live-render, export, accessibility, pixel, or responsive-correctness claim upgrade.

## Work Package trace

```yaml
work_package_id: WP-RESP-002
pr_slice_id: WP-RESP-002/PR-A
slice_title: contract and schema boundary
execution_driver: work_package_catalog_guard
catalog_source: planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json
rolling_queue_role: historical_reconciled_archive_only
```
