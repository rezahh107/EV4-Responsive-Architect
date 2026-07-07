# Builder → Responsive Input Boundary

Status: schema-bound input eligibility package implemented  
Version: 0.2.1  
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

## Operational Project Gate → Builder → Responsive transition boundary

This boundary is intentionally non-executing until Project Gate supplies a verified Builder transition packet. Responsive may validate the shape of a Builder→Responsive package, but it must not infer that Project Gate exists, that Builder execution was real, or that viewport behavior is correct.

```yaml
project_gate_transition:
  status: future_verified_transport_required
  responsive_role: validate intake eligibility only
  project_gate_role: verify and transport Builder-owned artifacts
  builder_role: produce Builder-owned output and evidence artifacts
  allowed_responsive_action:
    - accept schema-valid Builder package only after Project Gate status is verified
    - preserve artifact references and sha256 digests for traceability
    - classify missing, blocked, malformed, or contradictory evidence as intake-blocking
  forbidden_responsive_action:
    - implement Project Gate verification semantics
    - copy Project Gate or Builder schemas as Responsive canonical truth
    - repair upstream Builder, Architect, CE, or Project Gate defects
    - fabricate missing Builder output, viewport evidence, or submitted evidence
    - treat transport, CI, fixture success, or merged PRs as responsive correctness evidence
```

The transition is operationally clear but still evidence-bound: Responsive can say whether the package is eligible for intake under the local schema and validators; Responsive cannot claim frontend correctness, export validity, accessibility, pixel accuracy, release readiness, production readiness, or pilot readiness from that intake decision.

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
      - validation/fixtures/invalid/builder_responsive_input_blocked_project_gate_allows_intake.invalid.json
      - validation/fixtures/invalid/builder_responsive_input_blocked_viewport_allows_intake.invalid.json
      - validation/fixtures/invalid/builder_responsive_input_forbidden_claim_subset.invalid.json
      - validation/fixtures/invalid/builder_responsive_input_malformed_hash.invalid.json
  required_digest_format:
    gate_hash: sha256:<64 lowercase hexadecimal characters>
    artifact_hash: sha256:<64 lowercase hexadecimal characters>
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

Missing or contradictory evidence blocks Responsive intake. Malformed Project Gate or Builder artifact digests also block intake; repository validators only accept explicit `sha256:` digests with 64 lowercase hexadecimal characters for `gate_hash` and `artifact_hash`.

## Eligibility decision matrix

```yaml
allow_intake_only_when:
  project_gate_ref.gate_status: verified
  project_gate_ref.gate_hash: sha256:<64 lowercase hexadecimal characters>
  builder_output_ref.artifact_hash: sha256:<64 lowercase hexadecimal characters>
  builder_evidence:
    action_batch_ref: present
    execution_evidence_ref: present
    layout_check_ref: present
    completion_gate_ref: present
  viewport_evidence:
    desktop: provided
    tablet: provided
    mobile: provided
  responsive_intake_decision.claim_boundary: input eligibility only; not responsive correctness evidence

block_intake_when:
  - Project Gate is blocked, missing, non-verified, malformed, or ambiguous
  - Builder output artifact hash is malformed or absent
  - Builder execution, layout, completion, or action-batch evidence is absent
  - any required viewport evidence is missing or blocked
  - forbidden claims are incomplete, duplicated, expanded into readiness claims, or contradicted by the intake decision
```

An allowed intake decision is only a local eligibility result. It does not authorize Responsive repair, does not imply live-render/export/accessibility/pixel validation, and does not bypass submitted-packet or pilot gates.

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

## Work Package trace

```yaml
work_package_id: WP-RESP-002
pr_slice_id: WP-RESP-002/PR-A
slice_title: contract and schema boundary
catalog_source: planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json
boundary_result: operational handoff path clarified; no execution, evidence creation, Issue #8 mutation, pilot authorization, readiness upgrade, release claim, production claim, or responsive-correctness claim
```
