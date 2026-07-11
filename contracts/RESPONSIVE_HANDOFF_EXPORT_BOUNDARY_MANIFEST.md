# Responsive Handoff Export Boundary Manifest

Status: proposed_v0.1.0
Work Package: `WP-RESP-008`
PR slice: `WP-RESP-008/PR-A`
Related contract: `contracts/EV4_RESPONSIVE_HANDOFF_EXPORT_CONTRACT.md`

## Purpose

Define a deterministic repository-level manifest for describing whether a responsive handoff package is structurally eligible for export review.

This manifest records contract references, source lineage, expected artifact classes, validation-plan references, unresolved unknowns, and explicit boundary assertions. It is a repository contract only.

## Non-Purpose

This manifest does not:

- prove that a live builder export occurred;
- validate exported JSON from a real build;
- authorize pilot execution, production, or release;
- prove live rendering, accessibility, pixel parity, or responsive correctness;
- replace the canonical responsive handoff payload or Project Gate producer export contract.

## Required Inputs

A manifest must identify:

- the canonical responsive handoff contract version;
- a stable `source_handoff_ref`;
- a stable `source_packet_ref`;
- the selected route and relationship-classification references;
- the expected export artifact classes;
- the repository validators intended to check the package shape;
- unresolved unknowns and blocking conflicts;
- explicit evidence and readiness boundary assertions.

Missing or ambiguous source lineage must fail closed.

## Canonical Manifest Shape

```yaml
responsive_handoff_export_boundary_manifest:
  schema: ev4-responsive-handoff-export-boundary-manifest@0.1.0
  status: proposed
  source_handoff_ref: string
  source_packet_ref: string
  selected_route_ref: string
  relationship_classification_ref: string
  contract_refs:
    responsive_handoff: contracts/EV4_RESPONSIVE_HANDOFF_EXPORT_CONTRACT.md
    viewport_display: contracts/EV4_VIEWPORT_DISPLAY_CONTRACT.md
  expected_artifact_classes:
    - responsive_tree_output
    - breakpoint_overrides
    - viewport_display_contract
    - builder_handoff
    - validation_plan
    - final_review
  validation_plan_refs:
    - string
  unresolved_unknowns:
    - string
  blocking_conflicts:
    - string
  boundary_assertions:
    submitted_evidence_created: false
    issue_8_mutated: false
    pilot_executed_or_authorized: false
    production_ready: false
    release_ready: false
    live_render_validated: false
    export_json_validated: false
    accessibility_passed: false
    pixel_perfect: false
    responsive_correctness_validated: false
    ci_success_treated_as_domain_evidence: false
```

## Eligibility States

The repository-level manifest may report only one of these states:

- `eligible_for_repository_validation`: required references and boundary assertions are structurally complete;
- `blocked_missing_source`: one or more required source references are absent or ambiguous;
- `blocked_contract_conflict`: referenced contracts disagree or a blocking conflict remains unresolved;
- `unknown`: available repository evidence cannot support a deterministic eligibility decision.

`eligible_for_repository_validation` is not equivalent to `export_json_validated` and must never be translated into a live export claim.

## Gate Rules

1. `source_handoff_ref` and `source_packet_ref` must be non-empty and independently traceable.
2. Every `contract_ref` must point to a repository-owned or explicitly vendored canonical contract.
3. `expected_artifact_classes` describes required classes, not proof that artifacts were produced.
4. `validation_plan_refs` must identify deterministic repository validators or planned validators.
5. Any unresolved source ambiguity, contract disagreement, or missing required artifact class must block repository eligibility.
6. All evidence, pilot, readiness, production, release, export, accessibility, pixel, and responsive-correctness assertions must remain `false` unless separate real-evidence gates explicitly authorize an upgrade.
7. CI success, PR merge, or Work Package completion must not be treated as live export or responsive-correctness evidence.

## Allowed Work

- Clarify the boundary manifest shape and lineage requirements.
- Add schema, fixtures, validators, CI wiring, STATUS entries, and indexes in later approved slices.
- Improve deterministic diagnostics for missing lineage, contract conflict, or forbidden boundary upgrades.

## Forbidden Work

- Creating or fabricating a real exported JSON artifact.
- Setting `export_json_validated` to `true` from repository-only checks.
- Mutating Issue #8 or creating submitted evidence.
- Running or authorizing a real pilot.
- Claiming production, release, live-render, accessibility, pixel-perfect, or responsive correctness.

## Stop Conditions

Stop and report a blocker when:

- the canonical handoff or packet source cannot be identified;
- required contracts conflict;
- a requested change would create live export evidence;
- a requested change would upgrade any forbidden boundary claim;
- validation ownership is ambiguous.

## Repair Routes

- Missing lineage: restore explicit source references without inventing artifacts.
- Contract conflict: reconcile the canonical owner before changing the manifest.
- Missing artifact class: record the gap as blocking rather than assuming output exists.
- Boundary upgrade: reset the claim to `false` and require the separate real-evidence gate.

## Self-Audit

Before activation, verify that:

- the manifest remains a repository-level boundary contract;
- required references are explicit and traceable;
- unknowns and conflicts fail closed;
- no live export, readiness, or responsive-correctness claim is implied;
- later schema and validator work remains assigned to an approved Work Package slice.
