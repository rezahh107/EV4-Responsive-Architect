# Smart Home Connector — Pilot Case v0.1

Status: shadow_mode_manual
Production status: not_production_ready
Validation boundary: no live Elementor rendering, no export JSON validation, no Playwright visual regression

## Purpose

This pilot validates whether EV4 Responsive Architect can produce builder-usable responsive repair guidance for a connector-heavy Elementor section without mutating the approved EV4 architecture.

The pilot is a vertical slice. It tests the handoff-to-repair workflow before investing in heavier automation.

## Mental Model

```text
The main EV4 pipeline designed the house.
This pilot checks whether the finished house still works when the hallway gets narrow.
If the hallway is too narrow, the pilot may adjust furniture placement.
It may not move load-bearing walls.
```

## Required Inputs

```yaml
required_inputs:
  main_ev4_handoff:
    - Recommendation_Payload
    - Build_Tree_Payload
    - Implementation_Payload
    - Final_Audit_Payload
    - Handoff_Payload
  responsive_evidence:
    - desktop_baseline_screenshot_or_declared_equivalent
    - tablet_screenshot_or_declared_equivalent
    - mobile_screenshot_or_declared_equivalent
    - breakpoint_inventory_source
  section_identity:
    - selected_candidate_id
    - root_class_name
    - target_section_name
```

## Minimum Pilot Chain

```text
/main-pipeline-handoff-ingest
/responsive-evidence-ingest-ledger
/desktop-baseline-lock
/breakpoint-inventory-lock
/breakpoint-observation
/responsive-failure-map
/failure-priority-ordering
/repair-ownership-routing
/repair-option-analysis
/responsive-repair-selection
/repair-scope-freeze
/responsive-repair-plan
/responsive-final-audit-lite
```

## Pilot Success Criteria

```yaml
pilot_success_criteria:
  - builder_can_follow_steps_without_extra_interpretation
  - each_repair_step_has_rollback
  - desktop_regression_check_is_clear
  - no_architecture_mutation_occurs
  - unknowns_are_visible
  - repair_option_analysis_prevents_premature_selection
  - connector_decoration_status_is_inherited_from_main_pipeline
```

## Stop Conditions

```yaml
stop_conditions:
  - missing_main_ev4_handoff
  - selected_candidate_identity_conflict
  - desktop_baseline_missing
  - breakpoint_inventory_missing_and_user_declines_fallback
  - architecture_mutation_veto_triggered
  - meaningful_content_must_be_hidden_to_fit
  - decorative_connector_must_become_meaningful
  - builder_reports_unexpected_desktop_regression
```

## Allowed Claims

```text
- pilot_ready
- shadow_mode_manual
- controlled_repair_plan_candidate
- evidence_required_before_execution
```

## Forbidden Claims

```text
- production_ready
- live_render_validated
- export_validated
- accessibility_passed
- pixel_perfect
- Playwright_validated
```

## Pilot Output Package

```yaml
pilot_outputs:
  - evidence_manifest
  - input_authorization_record
  - breakpoint_observation_notes
  - responsive_failure_map
  - repair_ownership_routing
  - repair_option_analysis
  - repair_selection_record
  - builder_repair_checklist
  - final_audit_lite
  - remaining_unknowns
```
