# Pilot Evidence Intake Guide

Version: 0.1.1
Status: machine_checkable_intake_ready
Scope: smart-home connector pilot evidence collection

## Purpose

This guide defines the evidence required before running the smart-home connector responsive pilot.

The pilot must not start from memory, screenshots alone, or an unselected architecture candidate.

## Intake Rule

```text
No responsive pilot execution without a machine-checkable evidence intake packet.
```

The packet schema is:

```text
ev4-responsive-evidence-intake-packet@1.0.0
```

Validator:

```text
python validation/e2e/run_evidence_intake_check.py
```

## Required Evidence Packet

```yaml
required_evidence_packet:
  main_ev4_handoff:
    required: true
    must_include:
      - selected_candidate_id
      - Build_Tree_Payload_or_equivalent
      - Implementation_Payload_or_builder_notes
      - Final_Audit_Payload_or_final_audit_status
      - Handoff_Payload_or_equivalent
      - overlay_decoration_map
      - content_editability_map
      - responsive_structure_contract
      - carried_unknowns
      - audit_flags

  desktop_baseline:
    required: true
    must_include:
      - evidence_id
      - desktop_screenshot_or_declared_equivalent
      - viewport_label_or_width
      - root_section_identity_or_root_class
      - known_acceptable_desktop_issues
      - minimum_must_not_regress_items

  tablet_evidence:
    required: true
    must_include:
      - evidence_id
      - screenshot_or_declared_equivalent
      - viewport_label_or_width
      - visible_section_state
      - per_item_evidence_quality

  mobile_evidence:
    required: true
    must_include:
      - evidence_id
      - screenshot_or_declared_equivalent
      - viewport_label_or_width
      - visible_section_state
      - per_item_evidence_quality

  breakpoint_inventory:
    required: true
    must_include:
      - source
      - confidence
      - claim_scope
      - breakpoint_records
```

## Evidence File Naming Convention

Use predictable names so the pilot can cite evidence without ambiguity:

```text
main-ev4-handoff.md
desktop-baseline-[width].png
tablet-[width].png
mobile-[width].png
breakpoint-inventory.json
```

## Per-Item Evidence Quality

Every evidence item must carry quality metadata:

```yaml
evidence_quality:
  quality_level:
    - L1_static_visual_only
    - L2_frontend_visual_with_viewport
    - L3_resize_sweep_or_video
    - L4_dom_or_export_structure
    - L5_live_render_plus_dom_plus_visual
  confidence_cap:
    - low
    - medium
    - high
    - high_for_structure_medium_for_visual
  downstream_allowed_use:
    observation: true
    diagnosis: no | limited | yes
    repair_selection: no | limited | yes
    validation_claim: no | limited | yes
```

## Screenshot Evidence Rule

```yaml
screenshot_can_support:
  - visible_collision
  - visible_clipping
  - visible_overflow_symptom
  - visible_order_symptom
  - viewport_specific_visual_state

screenshot_cannot_support:
  - exact_DOM_order
  - exact_CSS_cause
  - exact_Elementor_control
  - exact_breakpoint_value
  - accessibility_pass
  - production_ready_claim
```

## Minimum Desktop Must-Not-Regress Items

```yaml
minimum_desktop_must_not_regress:
  - meaningful_text_visibility
  - feature_card_group_integrity
  - visual_core_presence
  - connector_layer_containment
  - no_horizontal_overflow
```

## Breakpoint Source Claim Scope

```yaml
breakpoint_inventory_policy:
  project_settings_or_export_json:
    may_observe: true
    may_plan_repair: true
    may_handoff_controlled: true
    may_claim_release_ready: only_with_other_release_evidence

  user_declaration:
    may_observe: true
    may_plan_repair: true
    may_handoff_controlled: true_with_flag
    may_claim_release_ready: false

  fallback_default_with_unverified_label:
    may_observe: true
    may_plan_repair: limited
    may_handoff_controlled: only_with_visible_flag
    may_claim_release_ready: false
```

## Privacy Review

Evidence may contain private site or client data. Before submitting evidence:

```yaml
privacy_review_required:
  - credentials_and_access_tokens_removed
  - private_user_data_removed
  - emails_form_data_and_client_identifiers_removed
  - screenshots_reviewed_for_private_urls
  - export_like_evidence_reviewed_for_private_identifiers
```

## Evidence Complete Definition

```yaml
evidence_complete_definition:
  complete_when:
    - intake_packet_validates_against_schema
    - all_required_evidence_ids_are_present
    - each_required_evidence_item_has_source_viewport_quality_and_limitations
    - desktop_baseline_has_minimum_must_not_regress_list
    - breakpoint_inventory_has_confidence_and_claim_scope
    - privacy_review_acknowledged
    - no_blocker_conflicts_exist
```

## Optional Evidence

```yaml
optional_evidence:
  - Elementor_export_json
  - resize_sweep_video
  - browser_devtools_dom_notes
  - computed_style_notes
  - Playwright_screenshot_set
  - before_after_visual_diff
  - builder_feedback_after_repair
```

## Forbidden Intake Sources

```text
- unselected architecture candidate
- memory of prior chat without current payload
- raw screenshot as architecture authority
- undocumented user preference as validation evidence
- case memory as current evidence
```

## Intake Output

The intake process must produce:

```yaml
intake_output:
  - input_authorization_record
  - evidence_intake_packet
  - evidence_manifest
  - breakpoint_inventory_record
  - desktop_baseline_record
  - unresolved_unknowns_before_pilot
  - pilot_start_decision
```

## Pilot Start Decision

```yaml
pilot_start_decision:
  allowed:
    condition:
      - selected_candidate_id_present
      - main_handoff_minimum_fields_present
      - desktop_baseline_present
      - tablet_and_mobile_evidence_present
      - breakpoint_inventory_present_or_flagged
      - privacy_review_acknowledged
      - no_blocker_input_conflict

  blocked:
    condition:
      - evidence_intake_packet_missing_or_invalid
      - missing_main_ev4_handoff
      - missing_desktop_baseline
      - missing_tablet_or_mobile_evidence
      - selected_candidate_identity_conflict
      - privacy_review_incomplete
      - architecture_mutation_required_before_pilot
```

## Production Boundary

This intake does not prove:

```text
- live Elementor render validation
- export JSON validation
- accessibility pass
- Playwright visual regression
- production readiness
```

It only determines whether the responsive pilot may start.
