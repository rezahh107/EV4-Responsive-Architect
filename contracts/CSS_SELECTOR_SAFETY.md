# CSS_SELECTOR_SAFETY

Version: 0.1.0
Status: hardening_candidate
Owner stage: `/css-selector-safety-check`
Runs when: selected responsive repair uses Custom CSS

---

## 1. Purpose

Validate Custom CSS repair selectors before and after builder application.

This contract prevents scoped responsive repairs from becoming global CSS leaks, hidden architecture mutations, or brittle Elementor-internal selector hacks.

Core rule:

```text
Custom CSS is allowed only as a localized, reversible technical repair.
It must not replace native Elementor controls when native controls are sufficient.
It must not reconstruct layout globally.
```

---

## 2. Non-Purpose

This contract does not:

```text
- encourage CSS-first repair;
- replace Elementor native responsive controls;
- validate complete frontend rendering;
- authorize global CSS;
- authorize meaningful content generation through CSS;
- authorize hiding meaningful content;
- replace architecture mutation veto.
```

---

## 3. Runs When

```yaml
runs_when:
  - selected_repair_uses_custom_css
  - repair_option_analysis_marks_scoped_css_needed
  - builder_feedback_reports_native_control_unavailable_and_CSS_fallback_selected
```

If no Custom CSS is selected:

```yaml
gate_status: not_applicable
reason: no_custom_css_repair_selected
```

---

## 4. Required Inputs

```yaml
required_inputs:
  - Responsive_Repair_Selection
  - Repair_Option_Analysis_Payload
  - Repair_Scope_Freeze
  - Breakpoint_Inventory_Lock
  - Desktop_Baseline_Lock
  - project_root_class
  - target_node_class
  - proposed_css_patch
```

Optional but recommended:

```yaml
optional_inputs:
  - existing_project_css
  - computed_style_before
  - computed_style_after
  - frontend_before_after_screenshots
  - Elementor_export_JSON
  - builder_feedback
```

---

## 5. Selector Requirements

```yaml
selector_requirements:
  must_include_project_root_class: true
  must_include_target_node_class: true
  must_not_use_global_element_selector: true
  must_not_use_unscoped_elementor_internal_selector: true
  must_not_use_id_selector: true
  must_not_use_important_unless_justified: true
  must_not_target_html_body_root: true
  must_not_target_all_widgets_broadly: true
  must_not_depend_on_generated_unstable_ids: true
```

Allowed selector pattern:

```css
.ev4-section-root .ev4-target-node { }
```

Forbidden selector examples:

```css
html { }
body { }
.elementor-widget-container { }
.elementor-section .elementor-container { }
#some-id { }
* { }
```

---

## 6. Breakpoint Wrapping

```yaml
breakpoint_wrapping:
  required_if_viewport_specific: true
  breakpoint_source_must_be:
    - breakpoint_inventory_lock
    - elementor_export_json
    - user_declaration
  source_confidence_must_be_recorded: true
  forbidden:
    - invented_breakpoint
    - assumed_default_without_label
    - release_ready_claim_from_unverified_breakpoint
```

Fallback policy:

```yaml
fallback_breakpoint_policy:
  user_declaration:
    allowed_for_controlled_handoff: true
    release_ready_claim_allowed: false

  assumed_default_with_unverified_label:
    allowed_for_observation: true
    allowed_for_controlled_repair: true_with_visible_flag
    release_ready_claim_allowed: false
```

---

## 7. CSS Patch Schema

```yaml
CSS_Selector_Safety_Payload:
  schema: ev4-responsive-css-selector-safety@1.0.0
  gate_status:
    enum:
      - not_applicable
      - pass
      - pass_with_visible_risk
      - fail_requires_selector_repair
      - fail_requires_native_control_retry
      - fail_requires_architecture_route
      - blocked_missing_inputs

  patch_id:
  repair_step_ids:
  failure_ids:
  target_node_id:
  project_root_class:
  target_node_class:
  selector:
  media_query:
  breakpoint_source:
  breakpoint_source_confidence:
  declarations:
    - property:
      value:
      value_source:
        enum:
          - design_system_variable
          - builder_verified_value
          - relative_adjustment
          - evidence_based_value
          - provisional_flagged_value
  specificity_assessment:
    enum:
      - likely_safe
      - may_be_too_weak
      - may_be_too_strong
      - unknown
  uses_important: true|false
  important_justification:
  rollback_css:
  validation_required:
```

---

## 8. Allowed CSS Uses

```yaml
allowed_css_uses:
  - local_overflow_containment
  - local_responsive_sizing_patch
  - local_decoration_geometry_adjustment
  - local_nonmeaningful_connector_simplification
  - local_media_aspect_ratio_safety
  - local_wrap_or_clamp_safety_when_native_control_insufficient
```

Allowed only if:

```yaml
allowed_only_if:
  - selector_safety_passes
  - rollback_defined
  - breakpoint_source_recorded
  - desktop_baseline_recheck_required
  - no_meaningful_content_hidden
  - no_architecture_mutation_veto_triggered
```

---

## 9. Forbidden CSS Uses

```text
- use global html/body rules;
- use broad unscoped Elementor internals;
- generate meaningful text;
- hide meaningful content;
- create card clickability;
- invent connector mobile behavior;
- use !important without justification;
- change selected architecture through CSS;
- reconstruct approved build tree through CSS;
- override desktop baseline without explicit repair selection;
- use exact breakpoints not present in Breakpoint Inventory Lock;
- use CSS to avoid a required main-pipeline route.
```

---

## 10. Specificity Check

Before emitting CSS:

```yaml
specificity_check_before_emit:
  required:
    - project_root_class_present
    - target_node_class_present
    - no_global_selector
    - no_unscoped_elementor_internal_selector
    - likely_wins_without_global_leakage
    - no_important_or_justified_important
```

If existing CSS is unavailable:

```yaml
if_existing_css_unavailable:
  specificity_assessment: unknown
  gate_status_allowed: pass_with_visible_risk
  production_ready_claim_allowed: false
```

---

## 11. `!important` Policy

```yaml
important_policy:
  default: forbidden
  allowed_only_when:
    - native_control_unavailable_or_insufficient
    - specificity_conflict_confirmed_or_strongly_supported
    - selector_scope_is_local
    - no_broader_selector_can_safely_win
    - justification_recorded
    - rollback_defined
  forbidden_when:
    - used_to_force_global_override
    - used_to_hide_meaningful_content
    - used_to_bypass_architecture_route
```

---

## 12. Validation Requirements

After applying CSS, validation must include at least one of:

```yaml
after_apply_validation:
  required_one_or_more:
    - computed_style_check
    - matching_rule_check
    - frontend_screenshot_check
    - builder_feedback_with_screenshot

  always_required:
    - desktop_baseline_recheck
    - target_viewport_recheck
    - rollback_confirmed_possible
```

For release-ready claims, CSS validation must include:

```yaml
release_claim_css_validation_required:
  - live_frontend_render
  - before_after_screenshots
  - computed_style_or_export_evidence
  - no_desktop_regression
  - no_accessibility_gate_failure
```

---

## 13. Stop Conditions

```yaml
stop_conditions:
  - project_root_class_missing
  - target_node_class_missing
  - only_possible_selector_is_global
  - selector_targets_unscoped_elementor_internal
  - CSS_required_to_hide_meaningful_content
  - CSS_required_to_create_meaningful_content
  - CSS_required_to_mutate_architecture
  - breakpoint_source_missing_for_viewport_specific_patch
  - rollback_not_defined
```

---

## 14. Repair Routes

```yaml
repair_routes:
  root_class_missing: /responsive-repair-plan_repair_or_EV4_/implementation
  target_node_class_missing: EV4_Architect_/build-tree_or_/implementation
  native_control_possible_but_not_reviewed: /repair-option-analysis
  selector_global_only: /architecture-mutation-veto_or_/repair-option-analysis
  breakpoint_source_missing: /breakpoint-inventory-lock
  CSS_architecture_mutation: /architecture-mutation-veto
  validation_failed_after_apply: /builder-feedback-loop_partial_rerun
```

---

## 15. Self-Audit

```yaml
self_audit:
  runs_when_checked: pass|fail
  native_option_reviewed_first: pass|fail|not_applicable
  project_root_class_present: pass|fail
  target_node_class_present: pass|fail
  selector_scope_safe: pass|fail
  breakpoint_source_recorded: pass|fail|not_applicable
  no_global_selector: pass|fail
  no_meaningful_content_hidden: pass|fail
  no_architecture_mutation: pass|fail
  rollback_defined: pass|fail
  validation_required_listed: pass|fail
```

---

## 16. Example — Safe Local CSS Patch

```yaml
CSS_Selector_Safety_Payload:
  schema: ev4-responsive-css-selector-safety@1.0.0
  gate_status: pass_with_visible_risk
  patch_id: RSP-CSS-001
  repair_step_ids:
    - RSP-STEP-007
  failure_ids:
    - RSP-F-004
  target_node_id: smart-home__connector-layer
  project_root_class: ev4-smart-home
  target_node_class: ev4-smart-home__connector-layer
  selector: ".ev4-smart-home .ev4-smart-home__connector-layer"
  media_query: "@media (max-width: 767px)"
  breakpoint_source: user_declaration
  breakpoint_source_confidence: medium
  declarations:
    - property: display
      value: none
      value_source: relative_adjustment
  specificity_assessment: likely_safe
  uses_important: false
  important_justification: null
  rollback_css: remove RSP-CSS-001
  validation_required:
    - mobile_frontend_screenshot_check
    - desktop_baseline_recheck
    - decoration_classification_inherited_as_decorative
```
