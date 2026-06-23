# Pilot Evidence Intake Guide

Version: 0.1.2  
Status: machine_checkable_intake_ready_with_closed_capabilities  
Scope: smart-home connector pilot evidence collection

## Intake Rule

```text
No responsive pilot execution without a machine-checkable evidence intake packet.
```

The packet schema is:

```text
ev4-responsive-evidence-intake-packet@1.1.0
```

Validator:

```bash
python validation/e2e/run_evidence_intake_check.py
```

## Required Evidence Packet

```yaml
required_evidence_packet:
  main_ev4_handoff: required
  desktop_baseline: required
  tablet_evidence: required
  mobile_evidence: required
  breakpoint_inventory: required
  privacy_review: required
  packet_origin: real_issue_submission
  issue_reference: required
```

## Closed Evidence Capability Enums

`can_support` and `cannot_support` must use closed capability values. Free text is not allowed.

Visual screenshot evidence may support:

```text
visible_viewport_state
visible_collision
visible_overflow_symptom
visible_clipping
visible_spacing_issue
visible_alignment_issue
visible_order_symptom
visible_content_visibility_state
visible_connector_position_symptom
```

Visual screenshot evidence must not claim support for:

```text
computed_css_value
dom_structure_observation
exported_widget_structure
exported_control_value
declared_breakpoint_value
```

Visual screenshot evidence must explicitly include these limitations in `cannot_support`:

```text
exact_css_cause
dom_reading_order
accessibility_pass
production_ready_claim
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
    - each_required_evidence_item_has_source_viewport_quality_limitations_and_closed_capabilities
    - desktop_baseline_has_minimum_must_not_regress_list
    - breakpoint_inventory_has_confidence_and_claim_scope
    - privacy_review_acknowledged
    - no_blocker_conflicts_exist
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
