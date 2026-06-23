# MAIN_PIPELINE_HANDOFF_INPUT_CONTRACT

Version: 0.1.0
Status: hardening_candidate
Owner stage: `/main-pipeline-handoff-ingest`
Applies to: every EV4 Responsive Architect run

---

## 1. Purpose

Define the exact payload package that may enter `EV4 Responsive Architect` from the completed `EV4 Architect` pipeline.

This contract prevents responsive repair from starting with weak, stale, partial, or unselected architecture evidence.

Core rule:

```text
Responsive repair can only operate on an authorized EV4 baseline.
A raw screenshot is evidence; it is not a baseline authority.
```

---

## 2. Non-Purpose

This contract does not:

```text
- choose or re-rank architecture candidates;
- reinterpret the original section screenshot;
- repair responsive failures;
- validate live frontend rendering;
- prove production readiness;
- replace EV4 Architect stage anchors.
```

---

## 3. Required Inputs

```yaml
required_payloads:
  - ev4-stage-anchor@1.1.0
  - Recommendation_Payload
  - Build_Tree_Payload
  - Implementation_Payload
  - Final_Audit_Payload
  - Handoff_Payload
  - EV4_DEBUG_TRACE
```

The handoff is valid only when the payload set points to the same selected architecture identity.

---

## 4. Required Inherited Fields

```yaml
required_inherited_fields:
  selected_architecture:
    - selected_candidate_id
    - selected_candidate_family
    - recommendation_status

  build_tree_baseline:
    - structure_tree
    - node_id_map
    - class_map
    - content_editability_map
    - overlay_decoration_map
    - responsive_structure_contract
    - design_system_hook_map
    - carried_forward_unknowns

  implementation_baseline:
    - widget_mapping
    - control_path_map
    - responsive_implementation_plan
    - scoped_css_plan_if_any
    - asset_accessibility_map
    - builder_verification_items

  audit_baseline:
    - final_audit_status
    - audit_flags
    - unresolved_findings
    - repair_routes
    - production_boundary_status

  handoff_baseline:
    - handoff_state
    - validation_claims
    - unknown_register
    - required_user_confirmations
    - next_allowed_actions
```

---

## 5. Optional Inputs

```yaml
optional_inputs:
  - elementor_export_json
  - editor_screenshot_desktop
  - editor_screenshot_tablet
  - editor_screenshot_mobile
  - frontend_screenshot_desktop
  - frontend_screenshot_tablet
  - frontend_screenshot_mobile
  - frontend_video_resize_sweep
  - browser_dom_or_computed_style_notes
  - builder_feedback_notes
  - user_declared_breakpoints
```

Optional inputs may improve evidence quality. They do not override locked main-pipeline facts unless they create an explicit contradiction that routes to the owning EV4 stage.

---

## 6. Forbidden as Authoritative Baseline

```yaml
forbidden_as_authoritative_baseline:
  - raw_section_screenshot_without_ev4_baseline
  - unselected_architecture_candidate
  - rejected_candidate
  - previous_conversation_memory_without_current_payload
  - lessons_learned_as_current_evidence
  - official_docs_as_project_specific_behavior
  - workbook_or_methodology_note_as_current_implementation_state
  - old_payload_without_identity_match
  - stale_handoff_after_upstream_payload_hash_change
```

Allowed but not authoritative:

```yaml
allowed_as_evidence_only:
  - current_responsive_screenshot
  - current_builder_note
  - user_observation
  - visual_reference
```

---

## 7. Payload Identity Requirements

Every input payload must carry or be assigned a payload identity record.

```yaml
payload_identity_required_fields:
  - payload_id
  - schema_version
  - source_stage
  - content_hash
  - created_at_or_supplied_order
  - depends_on
```

Minimum identity checks:

```yaml
identity_checks:
  selected_candidate_consistency:
    required: true
    failure_effect: blocker

  build_tree_to_implementation_consistency:
    required: true
    failure_effect: blocker

  implementation_to_handoff_consistency:
    required: true
    failure_effect: high

  anchor_schema_compatibility:
    required: true
    failure_effect: blocker

  stale_payload_detection:
    required: true
    failure_effect: high_or_blocker_by_dependency
```

---

## 8. Allowed Work

`/main-pipeline-handoff-ingest` may:

```text
- normalize the incoming payload package;
- assign missing local evidence IDs;
- compute or record payload identity hashes;
- produce Source Payload Ledger;
- copy carried unknowns into the responsive unknown register;
- copy audit flags into the responsive audit flag register;
- determine whether responsive intake may begin;
- route missing or contradicted baseline data to the owning EV4 stage.
```

---

## 9. Forbidden Work

`/main-pipeline-handoff-ingest` must not:

```text
- repair any responsive failure;
- infer mobile behavior;
- change selected_candidate_id;
- add, remove, or rename build-tree nodes;
- reclassify meaningful/decorative content;
- convert unknowns into facts;
- use current screenshots to override the approved architecture;
- claim frontend, export, or production validation.
```

---

## 10. Gate Rules

```yaml
gates:
  GATE_INPUT_COMPLETE:
    pass_when: all_required_payloads_present
    fail_effect: stop_and_route_to_missing_payload_request

  GATE_ANCHOR_COMPATIBLE:
    pass_when: ev4-stage-anchor@1.1.0_fields_present_and_not_contradicted
    fail_effect: stop_and_request_repair_anchor

  GATE_SELECTED_CANDIDATE_LOCK:
    pass_when: selected_candidate_id_matches_across_payloads
    fail_effect: stop_and_route_to_EV4_recommend_or_build_tree_owner_stage

  GATE_BUILD_TREE_IDENTITY:
    pass_when: node_id_map_and_structure_tree_are_present
    fail_effect: stop_and_route_to_EV4_build_tree

  GATE_CONTENT_CLASSIFICATION:
    pass_when: content_editability_map_and_overlay_decoration_map_are_present
    fail_effect: stop_and_route_to_EV4_build_tree_or_final_audit

  GATE_UNKNOWN_SURVIVAL:
    pass_when: carried_unknowns_are_imported_without_silent_resolution
    fail_effect: stop_and_repair_ingest_payload

  GATE_PRODUCTION_BOUNDARY:
    pass_when: production_ready_claim_is_false_unless_real_validation_exists
    fail_effect: stop_and_repair_handoff_claims
```

---

## 11. Stop Conditions

```yaml
stop_conditions:
  - missing_required_payload
  - schema_version_unknown_or_incompatible
  - selected_candidate_identity_conflict
  - Build_Tree_Payload_missing_structure_tree
  - Implementation_Payload_missing_mapping
  - Final_Audit_Payload_missing_unresolved_findings_state
  - Handoff_Payload_claims_production_ready_without_evidence
  - upstream_payload_hash_changed_after_downstream_handoff
  - user_supplied_only_raw_screenshot_without_EV4_baseline
```

---

## 12. Repair Routes

```yaml
repair_routes:
  missing_or_invalid_anchor: request_repair_anchor
  selected_candidate_identity_conflict: EV4_Architect_/recommend_or_/build-tree
  missing_build_tree: EV4_Architect_/build-tree
  missing_implementation_mapping: EV4_Architect_/implementation
  missing_final_audit: EV4_Architect_/final-audit
  missing_handoff: EV4_Architect_/handoff-export
  visual_role_conflict: EV4_Architect_/decompose_or_/build-tree
  platform_capability_conflict: EV4_Architect_/research
  production_claim_conflict: EV4_Architect_/final-audit
```

---

## 13. Output Payload

```yaml
Main_Pipeline_Handoff_Ingest_Payload:
  schema: ev4-responsive-main-input@1.0.0
  input_authorization_status:
    enum:
      - authorized
      - blocked_missing_payload
      - blocked_schema_mismatch
      - blocked_identity_conflict
      - blocked_stale_payload
      - routed_to_main_pipeline

  selected_candidate_id:
  selected_candidate_family:
  payload_identity_hashes:
    Recommendation_Payload:
    Build_Tree_Payload:
    Implementation_Payload:
    Final_Audit_Payload:
    Handoff_Payload:

  inherited_baseline:
    structure_tree_ref:
    node_id_map_ref:
    class_map_ref:
    content_editability_map_ref:
    overlay_decoration_map_ref:
    responsive_structure_contract_ref:

  inherited_unknowns:
  inherited_audit_flags:
  inherited_repair_routes:
  validation_claims_imported:
  responsive_pipeline_allowed_to_start: true|false
  stop_reason_if_blocked:
```

---

## 14. Self-Audit

```yaml
self_audit:
  required_payloads_checked: pass|fail
  anchor_compatibility_checked: pass|fail
  selected_candidate_lock_checked: pass|fail
  build_tree_identity_checked: pass|fail
  unknowns_preserved: pass|fail
  audit_flags_preserved: pass|fail
  production_boundary_preserved: pass|fail
  no_responsive_repair_attempted: pass|fail
  no_architecture_mutation_attempted: pass|fail
```

---

## 15. Example Payload

```yaml
Main_Pipeline_Handoff_Ingest_Payload:
  schema: ev4-responsive-main-input@1.0.0
  input_authorization_status: authorized
  selected_candidate_id: ARCH-FAM-C
  selected_candidate_family: connector_stage_normal_flow_cards
  payload_identity_hashes:
    Build_Tree_Payload: sha256:example-build-tree
    Implementation_Payload: sha256:example-implementation
    Handoff_Payload: sha256:example-handoff
  inherited_baseline:
    structure_tree_ref: payload://Build_Tree_Payload.structure_tree
    node_id_map_ref: payload://Build_Tree_Payload.node_id_map
    class_map_ref: payload://Build_Tree_Payload.class_map
    content_editability_map_ref: payload://Build_Tree_Payload.content_editability_map
    overlay_decoration_map_ref: payload://Build_Tree_Payload.overlay_decoration_map
    responsive_structure_contract_ref: payload://Build_Tree_Payload.responsive_structure_contract
  inherited_unknowns:
    - mobile_connector_behavior_unknown
    - exact_breakpoints_not_project_verified
  inherited_audit_flags:
    - controlled_builder_handoff_with_visible_medium_flags
  inherited_repair_routes: []
  validation_claims_imported:
    production_ready: false
    live_render_validated: false
    export_validated: false
  responsive_pipeline_allowed_to_start: true
  stop_reason_if_blocked: null
```
