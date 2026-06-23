# Repair Option Analysis — Template

Pilot: smart-home-connector-v0.1  
Status: template_waiting_for_failure_map

## Rule

No repair selection is allowed until each eligible failure has at least one option analysis record, rejected alternatives are documented, and selection status is explicit.

## Option Ledger

```yaml
repair_option_analysis:
  - failure_id: RSP-F-001
    failure_selection_eligibility: TODO_eligible_blocked_deferred
    options:
      - option_id: RSP-OPT-001A
        selection_status: candidate
        repair_owner: elementor_native_control
        repair_type: elementor_native_control
        native_control_possible: unknown
        scoped_css_needed: unknown
        desktop_regression_risk: unknown
        cascade_risk: unknown
        accessibility_risk: unknown
        architecture_mutation_risk: unknown
        evidence_support: PARTIALLY_SUPPORTED_EVIDENCE
        expected_effect: TODO
        verification_required:
          - desktop_baseline_recheck
          - affected_viewport_recheck
        rejection_category: null
        rejected_reason_if_not_selected: null

      - option_id: RSP-OPT-001B
        selection_status: candidate
        repair_owner: scoped_css
        repair_type: scoped_css
        native_control_possible: unknown
        scoped_css_needed: yes
        desktop_regression_risk: unknown
        cascade_risk: unknown
        accessibility_risk: unknown
        architecture_mutation_risk: unknown
        evidence_support: INFERRED_EVIDENCE
        expected_effect: TODO
        verification_required:
          - css_selector_safety_check
          - desktop_baseline_recheck
          - frontend_screenshot_after
        rejection_category: TODO_if_rejected
        rejected_reason_if_not_selected: TODO_if_rejected
```

## Selection Status Values

```yaml
selection_status_allowed_values:
  - candidate
  - selected
  - rejected
  - deferred

rejection_category_allowed_values:
  - insufficient_evidence
  - desktop_regression_risk
  - accessibility_risk
  - architecture_mutation_risk
  - css_scope_risk
  - native_control_unavailable
  - lower_priority_than_selected_option
  - out_of_current_scope
```

## Selection Preconditions

```yaml
selection_preconditions:
  architecture_mutation_veto_checked: false
  unknown_budget_gate_passed: false
  desktop_baseline_locked: false
  breakpoint_inventory_locked: false
  accessibility_gate_required: TODO_yes_no
  css_selector_safety_required: TODO_yes_no
  selected_option_has_rejected_alternative_record: false
```

## Forbidden Selection

```yaml
forbidden:
  - select_option_without_rejected_alternatives
  - select_css_before_native_option_evaluated
  - select_option_with_high_architecture_mutation_risk
  - select_option_with_unresolved_required_unknown
```
