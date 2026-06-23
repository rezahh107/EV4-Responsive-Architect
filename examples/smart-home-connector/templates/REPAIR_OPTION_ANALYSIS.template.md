# Repair Option Analysis — Template

Pilot: smart-home-connector-v0.1  
Status: template_waiting_for_failure_map

## Rule

No repair selection is allowed until each eligible failure has at least one option analysis record and rejected alternatives are documented.

## Option Ledger

```yaml
repair_option_analysis:
  - failure_id: RSP-F-001
    options:
      - option_id: RSP-OPT-001A
        repair_owner: elementor_native_control
        repair_type: elementor_native_control
        native_control_possible: unknown
        scoped_css_needed: unknown
        desktop_regression_risk: unknown
        cascade_risk: unknown
        accessibility_risk: unknown
        evidence_support: PARTIALLY_SUPPORTED_EVIDENCE
        expected_effect: TODO
        verification_required:
          - desktop_baseline_recheck
          - affected_viewport_recheck
        rejected_reason_if_not_selected: null

      - option_id: RSP-OPT-001B
        repair_owner: scoped_css
        repair_type: scoped_css
        native_control_possible: unknown
        scoped_css_needed: yes
        desktop_regression_risk: unknown
        cascade_risk: unknown
        accessibility_risk: unknown
        evidence_support: INFERRED_EVIDENCE
        expected_effect: TODO
        verification_required:
          - css_selector_safety_check
          - desktop_baseline_recheck
          - frontend_screenshot_after
        rejected_reason_if_not_selected: TODO_if_rejected
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
```
