# Responsive Failure Map — Template

Pilot: smart-home-connector-v0.1  
Status: template_waiting_for_real_evidence

## Input Authorization

```yaml
main_pipeline_handoff_verified: false
selected_candidate_id: ARCH-FAM-C
selected_candidate_identity_status: TODO_verified_or_conflict
breakpoint_inventory_status: TODO_locked_or_fallback
```

## Failure Map

Use only the closed taxonomy from `RESPONSIVE_EVIDENCE_CONTRACT` and `PROJECT_MASTER_SPEC`.

```yaml
failures:
  - failure_id: RSP-F-001
    viewport: mobile
    affected_node_id: TODO_NODE_ID
    failure_type: TODO_overflow_x_collision_connector_noise_etc
    severity: TODO_blocker_high_medium_minor_note
    evidence_ids:
      - EVD-MOBILE-001
    user_visible_symptom: TODO_VISIBLE_SYMPTOM_ONLY
    cause_status: unknown
    cause_candidates:
      - TODO_candidate_only_not_claim
    suspected_owner: TODO_responsive_repair_or_evidence_request
    repair_allowed_now: TODO_yes_no
    unknowns:
      - TODO_UNKNOWN
```

## Forbidden Inference Check

```yaml
forbidden_inference_check:
  exact_dom_order_claimed_from_screenshot_only: false
  exact_css_cause_claimed_from_screenshot_only: false
  exact_elementor_control_claimed_from_screenshot_only: false
  exact_breakpoint_claimed_from_screenshot_only: false
```

## Unknown Register

```yaml
unknowns:
  - unknown_id: RSP-U-001
    description: TODO
    severity: TODO_high_medium_low
    required_to_select_repair: TODO_yes_no
    evidence_needed: TODO
```
