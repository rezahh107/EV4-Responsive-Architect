# Pilot Evidence Intake Guide

Version: 0.1.0
Status: controlled_intake_ready
Scope: smart-home connector pilot evidence collection

## Purpose

This guide defines the evidence required before running the smart-home connector responsive pilot.

The pilot must not start from memory, screenshots alone, or an unselected architecture candidate.

## Intake Rule

```text
No responsive pilot execution without an evidence intake packet.
```

## Required Evidence Packet

```yaml
required_evidence_packet:
  main_ev4_handoff:
    required: true
    accepted_forms:
      - Handoff_Payload
      - Build_Tree_Payload
      - Implementation_Payload
      - Final_Audit_Payload
      - selected_candidate_id
      - carried_unknowns
      - audit_flags
    must_include:
      - selected_candidate_id
      - structure_tree_or_node_map
      - overlay_decoration_map
      - content_editability_map
      - responsive_structure_contract

  desktop_baseline:
    required: true
    accepted_forms:
      - frontend_desktop_screenshot
      - editor_desktop_screenshot_with_visible_viewport_label
    must_include:
      - viewport_label_or_width
      - root_section_identity
      - known_acceptable_desktop_issues
      - must_not_regress_items

  tablet_evidence:
    required: true
    accepted_forms:
      - frontend_tablet_screenshot
      - editor_tablet_screenshot_with_visible_viewport_label
    must_include:
      - viewport_label_or_width
      - visible_section_state

  mobile_evidence:
    required: true
    accepted_forms:
      - frontend_mobile_screenshot
      - editor_mobile_screenshot_with_visible_viewport_label
    must_include:
      - viewport_label_or_width
      - visible_section_state

  breakpoint_inventory:
    required: true
    accepted_forms:
      - Elementor_project_settings_screenshot
      - Elementor_export_json
      - user_declaration
      - fallback_default_with_unverified_label
    release_ready_claim_allowed_from_fallback: false
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

## Evidence Quality Rules

```yaml
evidence_quality_rules:
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

## Intake Output

The intake process must produce:

```yaml
intake_output:
  - input_authorization_record
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
      - desktop_baseline_present
      - tablet_and_mobile_evidence_present
      - breakpoint_inventory_present_or_flagged
      - no_blocker_input_conflict

  blocked:
    condition:
      - missing_main_ev4_handoff
      - missing_desktop_baseline
      - missing_tablet_or_mobile_evidence
      - selected_candidate_identity_conflict
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
