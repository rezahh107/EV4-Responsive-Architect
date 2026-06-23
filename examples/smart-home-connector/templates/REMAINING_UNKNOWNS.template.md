# Remaining Unknowns — Template

Pilot: smart-home-connector-v0.1  
Status: template_waiting_for_audit

## Unknown Register

```yaml
remaining_unknowns:
  - unknown_id: TODO
    source_stage: TODO
    description: TODO
    severity: TODO_blocker_high_medium_low
    affects_repair_selection: TODO_yes_no
    affects_handoff: TODO_yes_no
    evidence_needed: TODO
    route:
      enum:
        - request_more_evidence
        - defer_to_next_responsive_run
        - route_to_main_pipeline
        - carry_forward_visible_flag
```

## Gate

```yaml
handoff_blocked_if:
  - blocker_unknown_exists
  - high_unknown_affects_repair_selection
  - selected_candidate_identity_unknown
  - meaningful_content_visibility_unknown
```
