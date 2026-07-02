# MAIN_PIPELINE_HANDOFF_INPUT_CONTRACT

Version: 0.2.0  
Status: production_handoff_provenance_required  
Owner stage: `/main-pipeline-handoff-ingest`  
Applies to: every production EV4 Responsive Architect run

---

## 1. Purpose

Define the exact payload package that may enter `EV4 Responsive Architect` from the completed production EV4 pipeline.

The production path is:

```text
Architect → CE → Builder → Responsive
```

Responsive does not consume raw Architect output directly in production. Architect output reaches Responsive only as inherited baseline/provenance after CE constructability review, Builder execution, and Builder evidence packaging.

Core rule:

```text
Responsive repair can only operate on an authorized Builder handoff with preserved CE/Builder provenance.
A raw screenshot is evidence; it is not a baseline authority.
A direct Architect packet is preflight/debug only, never production Responsive intake.
```

---

## 2. Non-Purpose

This contract does not:

```text
- choose or re-rank architecture candidates;
- reinterpret the original section screenshot;
- prove constructability;
- execute Builder actions;
- repair responsive failures;
- validate live frontend rendering;
- prove production readiness;
- replace upstream Architect, CE, or Builder contracts.
```

---

## 3. Required Inputs

```yaml
required_payloads:
  - Builder_Output_Payload
  - Builder_Build_Evidence
  - CE_Builder_Executable_Package_Provenance
  - Builder_Context_Package_Provenance
  - Golden_Reference_Contract_Provenance
  - Spatial_Lexicon_Version_Used
  - Visual_Tolerance_Policy_Ref
  - Build_Intent_Brief_Ref
  - EV4_DEBUG_TRACE
```

Legacy Architect main-pipeline payloads may remain as inherited baseline references, but they are not sufficient to authorize Responsive production intake by themselves.

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

## 5. Required Upstream Provenance

`ev4-responsive-main-input@1.0.0` must include `upstream_provenance`.

```yaml
upstream_provenance:
  production_handoff_source: builder_output_and_build_evidence

  builder_provenance:
    builder_package_schema: ev4-builder-context-package@1.0.0
    builder_output_ref: string
    builder_input_authorization_digest: sha256:<64-hex>
    build_evidence_refs: []

  ce_provenance:
    ce_package_schema: ev4-builder-executable-package@1.0.0
    ce_package_ref: string
    constructability_status: executable_ready
    builder_decisions_required: 0
    blocking_dependencies_count: 0

  visual_governance_provenance:
    golden_reference_contract_id: string
    golden_reference_contract_hash: sha256:<64-hex>
    spatial_lexicon_version_used: string
    visual_tolerance_policy_ref: string
    build_intent_brief_ref: string
    reference_paradigm_lock_ref: string
    paradigm_to_structure_map_ref: string

  builder_validation_claims:
    builder_runtime_intake_authorized: true
    visual_reference_prerequisites_present: true
    build_completed: true|false
    live_render_validated: true|false
    export_validated: true|false
    production_ready_allowed: false
```

These fields make the Responsive start packet provenance-bearing instead of a direct Architect bypass.

---

## 6. Optional Inputs

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

Optional inputs may improve evidence quality. They do not override locked upstream facts unless they create an explicit contradiction that routes to the owning upstream stage.

---

## 7. Forbidden as Authoritative Baseline

```yaml
forbidden_as_authoritative_baseline:
  - raw_section_screenshot_without_ev4_baseline
  - direct_architect_packet_without_ce_builder_provenance
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

## 8. Payload Identity Requirements

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

  builder_to_responsive_package_consistency:
    required: true
    failure_effect: blocker

  ce_to_builder_package_consistency:
    required: true
    failure_effect: blocker

  golden_reference_identity_consistency:
    required: true
    failure_effect: blocker

  stale_payload_detection:
    required: true
    failure_effect: high_or_blocker_by_dependency
```

---

## 9. Allowed Work

`/main-pipeline-handoff-ingest` may:

```text
- normalize the incoming Builder handoff package;
- assign missing local evidence IDs;
- compute or record payload identity hashes;
- import CE and Builder provenance without silent rewriting;
- copy carried unknowns into the responsive unknown register;
- copy audit flags into the responsive audit flag register;
- determine whether responsive intake may begin;
- route missing or contradicted baseline data to the owning EV4 stage.
```

---

## 10. Forbidden Work

`/main-pipeline-handoff-ingest` must not:

```text
- accept direct Architect output as production Responsive input;
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

## 11. Gate Rules

```yaml
gates:
  GATE_INPUT_COMPLETE:
    pass_when: all_required_builder_and_provenance_payloads_present
    fail_effect: stop_and_route_to_missing_payload_request

  GATE_UPSTREAM_PROVENANCE_PRESENT:
    pass_when: upstream_provenance exists and production_handoff_source is builder_output_and_build_evidence
    fail_effect: stop_and_route_to_project_gate_or_builder_handoff_repair

  GATE_CE_EXECUTABLE_READY:
    pass_when: ce_provenance.constructability_status is executable_ready and builder_decisions_required is 0
    fail_effect: stop_and_route_to_CE

  GATE_BUILDER_AUTHORIZED:
    pass_when: builder_runtime_intake_authorized is true and production_ready_allowed is false
    fail_effect: stop_and_route_to_Builder_or_Project_Gate

  GATE_VISUAL_GOVERNANCE_PRESENT:
    pass_when: golden_reference_contract, spatial_lexicon_version_used, visual_tolerance_policy, and build_intent_brief provenance are present
    fail_effect: stop_and_route_to_CE_or_Builder_handoff_repair

  GATE_SELECTED_CANDIDATE_LOCK:
    pass_when: selected_candidate_id matches across inherited upstream payloads
    fail_effect: stop_and_route_to_EV4_recommend_or_build_tree_owner_stage

  GATE_UNKNOWN_SURVIVAL:
    pass_when: carried_unknowns_are_imported_without_silent_resolution
    fail_effect: stop_and_repair_ingest_payload

  GATE_PRODUCTION_BOUNDARY:
    pass_when: production_ready_claim_is_false_unless real final validation exists
    fail_effect: stop_and_repair_handoff_claims
```

---

## 12. Stop Conditions

```yaml
stop_conditions:
  - missing_required_payload
  - missing_upstream_provenance
  - direct_architect_packet_without_ce_builder_provenance
  - schema_version_unknown_or_incompatible
  - selected_candidate_identity_conflict
  - missing_builder_build_evidence
  - missing_golden_reference_contract_provenance
  - missing_visual_tolerance_policy
  - missing_build_intent_brief
  - Handoff_Payload_claims_production_ready_without_evidence
  - upstream_payload_hash_changed_after_downstream_handoff
  - user_supplied_only_raw_screenshot_without_EV4_baseline
```

---

## 13. Repair Routes

```yaml
repair_routes:
  missing_or_invalid_builder_evidence: EV4_Builder
  missing_or_invalid_ce_provenance: EV4_CE
  missing_visual_governance_provenance: EV4_CE_or_Builder_handoff_repair
  selected_candidate_identity_conflict: EV4_Architect_/recommend_or_/build-tree
  missing_build_tree: EV4_Architect_/build-tree
  missing_implementation_mapping: EV4_Architect_/implementation
  visual_role_conflict: EV4_Architect_/decompose_or_/build-tree
  platform_capability_conflict: EV4_Architect_/research
  production_claim_conflict: EV4_Builder_or_final_Project_Gate
```

---

## 14. Output Payload

```yaml
Main_Pipeline_Handoff_Ingest_Payload:
  schema: ev4-responsive-main-input@1.0.0
  upstream_provenance:
    production_handoff_source: builder_output_and_build_evidence
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

## 15. Self-Audit

```yaml
self_audit:
  required_payloads_checked: pass|fail
  upstream_provenance_checked: pass|fail
  ce_executable_ready_checked: pass|fail
  builder_authorization_checked: pass|fail
  visual_governance_checked: pass|fail
  selected_candidate_lock_checked: pass|fail
  unknowns_preserved: pass|fail
  audit_flags_preserved: pass|fail
  production_boundary_preserved: pass|fail
  no_responsive_repair_attempted: pass|fail
  no_architecture_mutation_attempted: pass|fail
```

---

## 16. Example Payload

```yaml
Main_Pipeline_Handoff_Ingest_Payload:
  schema: ev4-responsive-main-input@1.0.0
  input_authorization_status: authorized
  selected_candidate_id: ARCH-FAM-C
  selected_candidate_family: connector_stage_normal_flow_cards
  upstream_provenance:
    production_handoff_source: builder_output_and_build_evidence
    builder_provenance:
      builder_package_schema: ev4-builder-context-package@1.0.0
      builder_output_ref: builder-output://BUILD-001
      builder_input_authorization_digest: sha256:<64-hex>
      build_evidence_refs:
        - builder-evidence://checkpoint-001
    ce_provenance:
      ce_package_schema: ev4-builder-executable-package@1.0.0
      ce_package_ref: ce-package://CE-BEP-SMART-HOME-001
      constructability_status: executable_ready
      builder_decisions_required: 0
      blocking_dependencies_count: 0
    visual_governance_provenance:
      golden_reference_contract_id: golden-smart-home-desktop
      golden_reference_contract_hash: sha256:<64-hex>
      spatial_lexicon_version_used: v1.fa
      visual_tolerance_policy_ref: ce-package://CE-BEP-SMART-HOME-001.visual_tolerance_policy
      build_intent_brief_ref: ce-package://CE-BEP-SMART-HOME-001.build_intent_brief
      reference_paradigm_lock_ref: builder-package://BCTX-001.reference_paradigm_lock
      paradigm_to_structure_map_ref: builder-package://BCTX-001.paradigm_to_structure_map
    builder_validation_claims:
      builder_runtime_intake_authorized: true
      visual_reference_prerequisites_present: true
      build_completed: true
      live_render_validated: false
      export_validated: false
      production_ready_allowed: false
  responsive_pipeline_allowed_to_start: true
  stop_reason_if_blocked: null
```
