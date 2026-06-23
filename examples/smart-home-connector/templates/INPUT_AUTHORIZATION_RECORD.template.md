# Input Authorization Record — Template

Pilot: smart-home-connector-v0.1  
Status: template_waiting_for_main_handoff

## Authorization Summary

```yaml
input_authorization:
  selected_candidate_id: ARCH-FAM-C
  selected_candidate_identity_status: TODO_verified_conflict_missing
  main_pipeline_handoff_status: TODO_verified_missing_stale
  build_tree_payload_status: TODO_available_missing_stale
  implementation_payload_status: TODO_available_missing_stale
  final_audit_payload_status: TODO_available_missing_stale
  handoff_payload_status: TODO_available_missing_stale
  responsive_pipeline_allowed_to_start: TODO_yes_no
  stop_reason_if_blocked: TODO_or_none
```

## Payload Identity

```yaml
payload_identity:
  build_tree_payload_hash: TODO
  implementation_payload_hash: TODO
  handoff_payload_hash: TODO
  source_ref: TODO
```

## Gate

```yaml
block_pilot_when:
  - missing_main_ev4_handoff
  - selected_candidate_identity_conflict
  - build_tree_payload_missing
  - architecture_mutation_veto_already_triggered
```
