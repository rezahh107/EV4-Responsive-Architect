# Repair Selection Record — Template

Pilot: smart-home-connector-v0.1  
Status: template_waiting_for_option_analysis

## Selection Preconditions

```yaml
selection_preconditions:
  input_authorization_passed: TODO_yes_no
  desktop_baseline_locked: TODO_yes_no
  breakpoint_inventory_locked: TODO_yes_no
  unknown_gate_lite_passed: TODO_yes_no
  architecture_mutation_veto_checked: TODO_yes_no
  repair_option_analysis_complete: TODO_yes_no
```

## Selection Record

```yaml
repair_selection:
  selected_failure_ids:
    - TODO
  selected_option_ids:
    - TODO
  deferred_failure_ids: []
  excluded_failure_ids: []
  selection_reason_ledger:
    - selected_option_id: TODO
      selected_because: TODO
      supported_by_evidence_ids:
        - TODO
      rejected_alternatives:
        - option_id: TODO
          rejection_category: TODO
          reason: TODO
      carried_risks:
        - TODO_or_empty
      verification_required:
        - TODO
```

## Forbidden

```yaml
forbidden:
  - selection_without_option_analysis
  - selection_with_unresolved_required_unknown
  - selection_after_architecture_mutation_veto
  - selection_without_rejected_alternatives_record
```
