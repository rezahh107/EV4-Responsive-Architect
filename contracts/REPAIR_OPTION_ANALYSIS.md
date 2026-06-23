# REPAIR_OPTION_ANALYSIS

Version: 0.1.0
Status: hardening_candidate
Owner stage: `/repair-option-analysis`
Applies before: `/responsive-repair-selection`

---

## 1. Purpose

Require option analysis before repair selection.

This contract prevents the model from jumping directly from failure mapping to a preferred repair. It forces each eligible failure to have at least one analyzed option, a rejected-option ledger when alternatives exist, and explicit evidence/risk state before repair selection.

Core rule:

```text
No repair selection without an option ledger.
No CSS option without native/control-based option review.
No selected option without carried risks and verification requirements.
```

---

## 2. Non-Purpose

This contract does not:

```text
- write builder steps;
- freeze repair scope;
- override repair ownership routing;
- bypass unknown budget gate;
- bypass architecture mutation veto;
- produce final handoff;
- guarantee that a selected option will work in Elementor.
```

---

## 3. Required Inputs

```yaml
required_inputs:
  - Responsive_Failure_Map
  - Repair_Ownership_Routing_Payload
  - Unknown_Budget_Gate_Result
  - Architecture_Mutation_Veto_Report
  - Breakpoint_Inventory_Lock
  - Desktop_Baseline_Lock
  - Cross_Viewport_Cascade_Dependency_Map_if_available
  - Accessibility_Gate_Precheck_if_order_or_visibility_risk_exists
```

---

## 4. Allowed Work

`/repair-option-analysis` may:

```text
- enumerate candidate repair options;
- map each option to a repair owner;
- compare native controls, design-system variable adjustment, scoped CSS, decoration simplification, asset adjustment, evidence request, or main-pipeline route;
- record why an option is rejected;
- carry desktop, cascade, accessibility, CSS, and evidence risks;
- block selection if no option is supportable.
```

---

## 5. Forbidden Work

`/repair-option-analysis` must not:

```text
- select the winning repair bundle;
- write step-by-step builder instructions;
- introduce new failure IDs without routing;
- alter selected_candidate_id;
- change build tree node identity;
- promote screenshot-only symptoms into confirmed causes;
- use hidden recommendation language;
- choose CSS before reviewing native options;
- ignore architecture mutation veto.
```

---

## 6. Repair Option Types

```yaml
repair_option_types:
  elementor_native_control:
    description: repair using viewport-specific Elementor controls
    examples:
      - Direction
      - Width
      - Min Height
      - Gap
      - Padding
      - Margin
      - Typography
      - Custom Order with accessibility gate

  design_system_variable:
    description: adjust approved class/variable/token without changing architecture
    examples:
      - spacing variable
      - typography variable
      - radius variable

  scoped_css:
    description: local CSS patch under project root and target node class
    requires:
      - CSS_SELECTOR_SAFETY
      - breakpoint source
      - rollback

  decoration_hide_or_simplify:
    description: hide or simplify decoration-only layer on responsive viewport
    requires:
      - decoration inherited as decorative from main pipeline

  asset_media_adjustment:
    description: adjust responsive media sizing/cropping behavior while preserving asset role

  evidence_request:
    description: stop and request evidence before repair can be selected

  build_tree_route:
    description: route to EV4 Architect /build-tree or earlier stage
    requires:
      - Architecture_Mutation_Veto_Report
```

---

## 7. Option Analysis Schema

```yaml
Repair_Option_Analysis_Payload:
  schema: ev4-responsive-repair-option-analysis@1.0.0
  analysis_status:
    enum:
      - complete
      - partial_blocked_by_unknowns
      - blocked_by_veto
      - blocked_missing_inputs

  failure_option_groups:
    - failure_id:
      failure_type:
      affected_node_id:
      viewport_scope:
      repair_owner_from_routing:
      option_set_status:
        enum:
          - eligible_options_available
          - only_evidence_request_available
          - only_main_pipeline_route_available
          - blocked
      options:
        - option_id:
          repair_owner:
          repair_type:
            enum:
              - elementor_native_control
              - design_system_variable
              - scoped_css
              - decoration_hide_or_simplify
              - asset_media_adjustment
              - evidence_request
              - build_tree_route
          target_node_id:
          viewport_scope:
          native_control_possible:
            enum: yes|no|unknown
          scoped_css_needed:
            enum: yes|no|unknown
          desktop_regression_risk:
            enum: low|medium|high|unknown
          cascade_risk:
            enum: low|medium|high|unknown
          accessibility_risk:
            enum: low|medium|high|unknown
          architecture_mutation_risk:
            enum: none|potential|triggered|unknown
          evidence_support:
            enum:
              - SUPPORTED_EVIDENCE
              - PARTIALLY_SUPPORTED_EVIDENCE
              - INFERRED_EVIDENCE
              - ABSENT_EVIDENCE
              - CONTRADICTED_EVIDENCE
              - UNRESOLVED_CONFLICT
          required_prechecks:
          verification_required:
          rollback_feasibility:
            enum: clear|partial|unknown|not_applicable
          selection_eligibility:
            enum: eligible|defer|blocked|route_to_main_pipeline
          rejection_reason_if_not_selected:
```

---

## 8. Decision Order

Options should be analyzed in this order unless evidence justifies skipping a category:

```yaml
repair_decision_order:
  1: elementor_native_control
  2: design_system_variable
  3: scoped_css
  4: decoration_hide_or_simplify
  5: asset_media_adjustment
  6: evidence_request
  7: build_tree_route
```

Rule:

```text
Native controls are preferred, not magically sufficient.
If native controls are insufficient, record why before considering CSS or route escalation.
```

---

## 9. CSS Option Gate

A scoped CSS option is eligible only when:

```yaml
css_option_gate:
  required:
    - native_option_reviewed_or_not_applicable
    - project_root_class_known
    - target_node_class_known
    - breakpoint_source_available_or_flagged
    - selector_safety_possible
    - rollback_possible
  forbidden_when:
    - global_selector_required
    - meaningful_content_would_be_hidden
    - CSS_would_reconstruct_architecture
    - exact_breakpoint_invented
    - target_node_class_unknown
```

---

## 10. Architecture Route Gate

A build-tree route or main-pipeline route is required when:

```yaml
architecture_route_gate:
  route_required_when:
    - architecture_mutation_veto_triggered
    - repair_requires_node_identity_change
    - repair_requires_major_wrapper_change
    - repair_requires_meaningful_content_hide_or_flatten
    - repair_requires_decoration_role_change
    - responsive_repair_would_break_desktop_baseline_by_design
```

---

## 11. Accessibility Gate Precheck

If an option changes visual order, source order risk, visibility, focus order, or meaningful content placement:

```yaml
accessibility_precheck_required:
  - custom_order_used
  - reverse_direction_used
  - hide_or_simplify_layer_near_meaningful_content
  - duplicate_mobile_section_considered
  - overlay_interacts_with_meaningful_content
```

The option may remain eligible only as:

```yaml
eligibility_with_accessibility_risk:
  low_risk: eligible_with_post_check
  medium_risk: eligible_with_visible_risk_and_required_verification
  high_risk: blocked_or_route
  unknown: defer_until_accessibility_gate
```

---

## 12. Selection Readiness Rules

An option may be passed to `/responsive-repair-selection` only when:

```yaml
selection_readiness:
  - failure_id_exists
  - repair_owner_matches_routing_or_route_change_is_explained
  - architecture_mutation_veto_not_triggered
  - desktop_regression_risk_not_high_unrouted
  - high_impact_unknowns_resolved_or_selection_blocked
  - CSS_selector_safety_possible_if_css_option
  - accessibility_gate_precheck_complete_if_needed
  - rollback_feasibility_not_unknown_for_builder_action
```

---

## 13. Stop Conditions

```yaml
stop_conditions:
  - no_option_can_preserve_architecture
  - only_option_hides_meaningful_content
  - only_option_requires_global_css
  - selected_candidate_identity_conflict
  - repair_owner_unknown_for_high_or_blocker_failure
  - unknown_budget_gate_failed
  - architecture_mutation_veto_triggered
```

---

## 14. Self-Audit

```yaml
self_audit:
  all_selected_failures_have_options: pass|fail
  native_options_reviewed_before_css: pass|fail|not_applicable
  rejected_options_recorded: pass|fail
  desktop_regression_risk_recorded: pass|fail
  cascade_risk_recorded: pass|fail
  accessibility_risk_recorded: pass|fail
  mutation_veto_checked: pass|fail
  no_repair_steps_written: pass|fail
  no_selection_leaked: pass|fail
```

---

## 15. Example

```yaml
Repair_Option_Analysis_Payload:
  schema: ev4-responsive-repair-option-analysis@1.0.0
  analysis_status: complete
  failure_option_groups:
    - failure_id: RSP-F-002
      failure_type: overflow_x
      affected_node_id: smart-home__feature-grid
      viewport_scope: mobile
      repair_owner_from_routing: responsive_repair
      option_set_status: eligible_options_available
      options:
        - option_id: RSP-OPT-001
          repair_owner: responsive_repair
          repair_type: elementor_native_control
          target_node_id: smart-home__feature-grid
          viewport_scope: mobile
          native_control_possible: yes
          scoped_css_needed: no
          desktop_regression_risk: low
          cascade_risk: low
          accessibility_risk: low
          architecture_mutation_risk: none
          evidence_support: PARTIALLY_SUPPORTED_EVIDENCE
          required_prechecks:
            - verify_mobile_viewport_active
            - verify_target_container_selected
          verification_required:
            - no_horizontal_scroll_after_step
            - desktop_baseline_recheck
          rollback_feasibility: clear
          selection_eligibility: eligible
          rejection_reason_if_not_selected: null

        - option_id: RSP-OPT-002
          repair_owner: responsive_repair
          repair_type: scoped_css
          target_node_id: smart-home__feature-grid
          viewport_scope: mobile
          native_control_possible: yes
          scoped_css_needed: unknown
          desktop_regression_risk: medium
          cascade_risk: low
          accessibility_risk: low
          architecture_mutation_risk: none
          evidence_support: INFERRED_EVIDENCE
          required_prechecks:
            - native_control_option_reviewed_first
            - CSS_SELECTOR_SAFETY
          verification_required:
            - computed_style_or_frontend_screenshot
          rollback_feasibility: clear
          selection_eligibility: defer
          rejection_reason_if_not_selected: native option should be tested before CSS fallback
```
