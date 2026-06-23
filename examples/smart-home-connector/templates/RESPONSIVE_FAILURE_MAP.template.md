# Responsive Failure Map — Template

Pilot: smart-home-connector-v0.1  
Status: template_waiting_for_real_evidence

## Input Authorization

```yaml
main_pipeline_handoff_verified: false
selected_candidate_id: ARCH-FAM-C
selected_candidate_identity_status: TODO_verified_or_conflict
breakpoint_inventory_status: TODO_locked_or_fallback
architecture_mutation_veto_checked: false
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
    evidence_scope: symptom_only
    user_visible_symptom: TODO_VISIBLE_SYMPTOM_ONLY
    cause_status: unknown
    cause_candidates:
      - TODO_candidate_only_not_claim
    owner_status: owner_candidate_only
    owner_candidate: TODO_responsive_repair_evidence_request_build_tree_route
    repair_allowed_now: TODO_yes_no
    repair_blockers:
      - TODO_or_empty
    unknowns:
      - RSP-U-001
```

## Owner Status Rule

```yaml
owner_status_allowed_values:
  - not_routed_yet
  - owner_candidate_only
  - routed_by_repair_ownership_stage

failure_map_rule:
  suspected_owner_is_not_final_route: true
  final_owner_requires_stage: repair-ownership-routing
```

## Forbidden Inference Check

```yaml
forbidden_inference_check:
  exact_dom_order_claimed_from_screenshot_only: false
  exact_css_cause_claimed_from_screenshot_only: false
  exact_elementor_control_claimed_from_screenshot_only: false
  exact_breakpoint_claimed_from_screenshot_only: false
  accessibility_pass_claimed_from_visual_only: false
  production_ready_claimed: false
```

## Unknown Register

```yaml
unknowns:
  - unknown_id: RSP-U-001
    description: TODO
    severity: TODO_blocker_high_medium_low
    required_to_select_repair: TODO_yes_no
    evidence_needed: TODO
    current_status: unresolved
```

## Unknown Gate Lite

```yaml
unknown_gate_lite:
  unresolved_required_unknowns:
    - TODO_or_empty
  repair_selection_allowed: false
  rule: if_any_unknown_required_to_select_repair_is_yes_then_repair_selection_allowed_false
  required_action_if_blocked:
    - request_evidence
    - route_to_main_pipeline_if_architecture_related
    - defer_failure
```
