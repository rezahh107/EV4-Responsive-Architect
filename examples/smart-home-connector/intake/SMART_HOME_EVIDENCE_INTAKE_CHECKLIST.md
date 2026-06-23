# Smart-Home Connector — Evidence Intake Checklist

Version: 0.1.2  
Status: closed_capability_intake_ready

Use this checklist before starting the responsive pilot.

## A. Machine-Readable Intake Packet

- [ ] `EVIDENCE_INTAKE_PACKET` is provided.
- [ ] Packet schema is `ev4-responsive-evidence-intake-packet@1.1.0`.
- [ ] Packet validates against `schemas/ev4-responsive-evidence-intake-packet.schema.json`.
- [ ] `validation/e2e/run_evidence_intake_check.py` passes.

Blocked if:

```text
evidence intake packet is missing, malformed, uses free-text evidence capability claims, or fails semantic checks.
```

## B. Closed Capability Claims

For screenshot evidence:

- [ ] `can_support` uses only visible symptom capability enums.
- [ ] `cannot_support` includes `exact_css_cause`.
- [ ] `cannot_support` includes `dom_reading_order`.
- [ ] `cannot_support` includes `accessibility_pass`.
- [ ] `cannot_support` includes `production_ready_claim`.

Blocked if:

```text
a screenshot claims CSS cause, DOM structure, Elementor control value, computed CSS value, accessibility pass, or production readiness.
```

## C. Main EV4 Handoff

- [ ] `selected_candidate_id` is provided.
- [ ] `Build_Tree_Payload` or equivalent handoff is provided.
- [ ] `Implementation_Payload` or builder implementation notes are provided.
- [ ] `Final_Audit_Payload` or final audit status is provided.
- [ ] `overlay_decoration_map` is available.
- [ ] `content_editability_map` is available.
- [ ] `responsive_structure_contract` is available.
- [ ] carried unknowns and audit flags are visible.

## D. Desktop Baseline

- [ ] Desktop screenshot is provided.
- [ ] Screenshot source is identified.
- [ ] Viewport width or label is provided.
- [ ] Root section identity or root class is provided.
- [ ] Known acceptable desktop issues are listed.
- [ ] Minimum must-not-regress list is present:
  - [ ] `meaningful_text_visibility`
  - [ ] `feature_card_group_integrity`
  - [ ] `visual_core_presence`
  - [ ] `connector_layer_containment`
  - [ ] `no_horizontal_overflow`

## E. Tablet and Mobile Evidence

- [ ] Tablet evidence is provided.
- [ ] Mobile evidence is provided.
- [ ] Each evidence item has `quality_level`.
- [ ] Each evidence item has `confidence_cap`.
- [ ] Each evidence item has closed `can_support`.
- [ ] Each evidence item has closed `cannot_support`.
- [ ] Each evidence item has `downstream_allowed_use`.
- [ ] Each evidence item has `known_limitations`.

## F. Breakpoint Inventory

- [ ] Breakpoint source is recorded.
- [ ] Confidence is recorded.
- [ ] Claim scope is recorded.
- [ ] `may_claim_release_ready` is false unless release evidence exists.

## G. Privacy Review

- [ ] Credentials and access tokens removed.
- [ ] Private user data, emails, form data, and client-identifying data removed.
- [ ] Screenshots/export-like evidence reviewed for private URLs and client identifiers.

## Intake Verdict Rules

```yaml
allowed_if:
  - intake_packet_validates_against_schema
  - all_required_evidence_ids_present
  - selected_candidate_id_present
  - main_handoff_minimum_fields_present
  - desktop_baseline_present
  - tablet_evidence_present
  - mobile_evidence_present
  - breakpoint_inventory_present_or_flagged
  - privacy_review_acknowledged
  - no_blocker_conflicts

blocked_if:
  - evidence_intake_packet_missing_or_invalid
  - selected_candidate_id_missing
  - main_handoff_missing
  - desktop_baseline_missing
  - tablet_or_mobile_missing
  - selected_candidate_identity_conflict
  - privacy_review_incomplete
  - architecture_mutation_required_before_pilot
  - evidence_capability_claim_outside_closed_enum
```
