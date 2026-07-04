# Builder → Responsive Input Boundary

Status: documented boundary only  
Version: 0.1.0  
Runtime behavior changed: no  
Responsive repair behavior changed: no

## Purpose

This contract note clarifies what Responsive may accept from a future Project Gate Builder → Responsive route.

```text
Builder output and build evidence
→ future Project Gate verification
→ Responsive intake
```

This document does not implement the Project Gate transition, does not start a pilot, and does not upgrade any readiness claim.

## Current Responsive intake state

Responsive currently has these active intake and output surfaces:

```yaml
main_pipeline_input:
  contract: contracts/MAIN_PIPELINE_HANDOFF_INPUT_CONTRACT.md
  status: active historical/main-pipeline baseline
  baseline_rule: raw screenshots are evidence only, not baseline authority

submitted_packet_readiness:
  validator: validation/e2e/run_submitted_packet_readiness_dry_run.py
  command: python validation/e2e/run_submitted_packet_readiness_dry_run.py --self-test
  status: pre-pilot dry run only

responsive_output:
  schema: ev4-responsive-output@0.3.0
  schema_file: schemas/ev4-responsive-output.schema.json
  validator: validation/e2e/run_responsive_tree_architecture_refactor_check.py
  positive_fixtures:
    - validation/fixtures/valid/responsive_output_same_tree.valid.json
    - validation/fixtures/valid/responsive_output_viewport_tree.valid.json
    - validation/fixtures/valid/responsive_output_hybrid.valid.json
    - validation/fixtures/valid/responsive_output_blocked.valid.json
  negative_fixtures:
    - validation/fixtures/invalid/responsive_output_missing_forbidden_claims.invalid.json
    - validation/fixtures/invalid/responsive_output_empty_steps.invalid.json
    - validation/fixtures/invalid/responsive_output_duplicate_step_id.invalid.json
    - validation/fixtures/invalid/responsive_output_route_mode_mismatch.invalid.json
    - validation/fixtures/invalid/responsive_output_builder_mode_mismatch.invalid.json
    - validation/fixtures/invalid/responsive_output_noncanonical_breakpoint_scope.invalid.json
    - validation/fixtures/invalid/responsive_output_unresolved_ready_mismatch.invalid.json

responsive_handoff_export:
  contract: contracts/EV4_RESPONSIVE_HANDOFF_EXPORT_CONTRACT.md
  schema_family: ev4-responsive-handoff-export@0.3.0
```

## Builder-specific input status

A formal Builder-specific Responsive input package is not yet implemented in this repository.

```yaml
builder_to_responsive_input_package:
  status: not_implemented
  schema_file: null
  validator: null
  fixture_suite: null
```

Until that package exists, Responsive intake remains fail-closed for Builder→Responsive automation. A future Project Gate transition may verify and transport Builder-owned artifacts, but Responsive must not treat that transport package as a local Responsive schema unless a dedicated Responsive contract is added later.

## Required future Builder evidence classes

A future Builder→Responsive intake route should require explicit evidence references for:

```yaml
required_builder_evidence_classes:
  - Builder action batch or execution record
  - real Elementor execution evidence
  - layout check evidence
  - completion gate evidence
  - viewport-specific evidence items when responsive claims are evaluated
```

Missing or contradictory evidence blocks Responsive intake.

## Baseline authority

```yaml
authoritative_baseline:
  - selected_candidate_id consistency
  - source packet identity/hash
  - approved Builder output/evidence references
  - submitted packet or Project Gate envelope when implemented

evidence_only:
  - raw screenshots
  - user observations
  - browser notes
  - export artifacts until validated by the appropriate validator
```

A raw screenshot is never enough to authorize Responsive repair or claim viewport correctness.

## Forbidden inference

Responsive must not:

```text
- infer mobile or tablet behavior from desktop evidence;
- use screenshots to override approved architecture or Builder facts;
- silently repair upstream Builder, Architect, or CE defects;
- claim frontend, export, pilot, accessibility, pixel, responsive correctness, release, or production readiness without explicit evidence;
- treat CI success as user-submitted frontend evidence.
```

## Project Gate note

Project Gate may later pin and hash this contract note, Responsive output schema, validators, and fixtures. Project Gate must not copy Responsive schemas into itself as canonical contracts, implement Responsive repair semantics, or invent missing viewport evidence.
