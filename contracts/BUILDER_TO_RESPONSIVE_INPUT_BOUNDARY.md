# Builder → Responsive Input Boundary

Status: schema-bound input eligibility package implemented  
Version: 0.2.0  
Runtime behavior changed: no  
Responsive repair behavior changed: no

## Purpose

This contract note clarifies what Responsive may accept from a future Project Gate Builder → Responsive route.

```text
Builder output and build evidence
→ future Project Gate verification
→ Responsive intake eligibility package
```

This document and its schema implement only a repository-controlled Responsive intake eligibility boundary. They do not implement Project Gate, do not start a pilot, and do not upgrade any readiness, production, release, live-render, export, accessibility, pixel, or responsive-correctness claim.

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

builder_to_responsive_input:
  schema: ev4-builder-responsive-input@0.1.0
  schema_file: schemas/ev4-builder-responsive-input.schema.json
  validator: validation/e2e/run_builder_responsive_input_boundary_check.py
  command: python validation/e2e/run_builder_responsive_input_boundary_check.py
  status: input eligibility only; not responsive correctness evidence

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

A Builder-specific Responsive input package is now schema-bound for repository validation, but remains non-executing until a future Project Gate route provides real verified Builder evidence.

```yaml
builder_to_responsive_input_package:
  status: schema_bound_non_executing
  schema_file: schemas/ev4-builder-responsive-input.schema.json
  validator: validation/e2e/run_builder_responsive_input_boundary_check.py
  fixture_suite:
    valid:
      - validation/fixtures/valid/builder_responsive_input.valid.json
    invalid:
      - validation/fixtures/invalid/builder_responsive_input_missing_mobile_evidence.invalid.json
  claim_boundary: input eligibility only; not responsive correctness evidence
```

Until Project Gate exists, Responsive intake remains fail-closed for Builder→Responsive automation. A future Project Gate transition may verify and transport Builder-owned artifacts, but Responsive must not treat transport alone as proof of viewport correctness.

## Required Builder evidence classes

A Builder→Responsive intake package requires explicit evidence references for:

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
