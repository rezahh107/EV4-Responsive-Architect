# RESPONSIVE_EVIDENCE_CONTRACT

Version: 0.1.0
Status: hardening_candidate
Owner stages: `/responsive-evidence-ingest-ledger`, `/breakpoint-observation`, `/responsive-observation-evidence-ledger`
Applies to: all responsive observation, failure mapping, repair routing, selection, validation, and handoff claims

---

## 1. Purpose

Separate raw evidence from derived observation evidence and prevent evidence inflation.

This contract defines what each evidence item can support, what it cannot support, and how evidence may be promoted from raw input into observation, failure, diagnosis, repair selection, or validation claim.

Core rule:

```text
Evidence may support only claims that match its quality level.
Weak evidence may create observations and unknowns; it must not become a hard cause, repair, or validation claim.
```

---

## 2. Non-Purpose

This contract does not:

```text
- select repair options;
- rank repair bundles;
- mutate architecture;
- prove production readiness;
- replace frontend validation;
- replace accessibility review;
- treat official docs as project-specific behavior.
```

---

## 3. Evidence Object Model

```yaml
evidence_objects:
  input_evidence_ledger:
    purpose: raw assets, source files, screenshots, exports, user declarations, and builder notes
    stage_owner: /responsive-evidence-ingest-ledger

  evidence_quality_map:
    purpose: define what each evidence item can and cannot support
    stage_owner: /responsive-evidence-ingest-ledger

  breakpoint_observation:
    purpose: evidence-bound visual or structural observation per viewport
    stage_owner: /breakpoint-observation

  observation_evidence_ledger:
    purpose: derived observations that reference input evidence IDs
    stage_owner: /responsive-observation-evidence-ledger
```

The system must preserve the difference between:

```text
raw evidence → observation → failure → cause candidate → confirmed cause → repair option → validation claim
```

---

## 4. Input Evidence Ledger Schema

```yaml
Input_Evidence_Ledger:
  schema: ev4-responsive-evidence-ingest@1.0.0
  evidence_items:
    - evidence_id:
      evidence_type:
        enum:
          - static_screenshot
          - frontend_screenshot
          - editor_screenshot
          - frontend_video
          - resize_sweep
          - elementor_export_json
          - dom_inspector_note
          - computed_style_note
          - browser_console_note
          - user_observation
          - user_declaration
          - builder_feedback
      viewport_label:
        enum:
          - desktop
          - tablet
          - mobile
          - custom
          - unknown
      viewport_width_px:
      viewport_height_px:
      capture_source:
        enum:
          - frontend
          - elementor_editor
          - export
          - browser_devtools
          - user_statement
          - mixed
          - unknown
      source_ref:
      supplied_by:
      timestamp_or_capture_order:
      file_hash_if_available:
      known_limitations:
      privacy_review_required: true|false
```

---

## 5. Evidence Quality Levels

```yaml
evidence_quality_levels:
  L1_static_visual_only:
    description: screenshot or static visual without verified viewport and without DOM/export evidence
    can_support:
      - visible_collision
      - visible_clipping
      - visible_overflow_symptom
      - visible_order_symptom
      - visible_spacing_symptom
      - visible_text_legibility_symptom
    cannot_support:
      - exact_css_cause
      - exact_dom_order
      - exact_elementor_control
      - exact_breakpoint_value
      - accessibility_pass
      - final_frontend_behavior
      - production_ready_claim
    confidence_cap: low

  L2_frontend_visual_with_viewport:
    description: frontend screenshot with declared or captured viewport metadata
    can_support:
      - viewport_specific_visual_state
      - visible_failure_at_viewport
      - desktop_before_after_visual_comparison_if_pair_exists
    cannot_support:
      - exact_elementor_control
      - DOM_source_order
      - project_settings_without_export_or_UI_evidence
      - accessibility_pass
      - production_ready_claim
    confidence_cap: medium

  L3_resize_sweep_or_video:
    description: video or resize sweep showing behavior across widths
    can_support:
      - breakpoint_transition_behavior
      - failure_appears_or_disappears_range
      - cascade_symptom_over_time
    cannot_support:
      - project_specific_elementor_setting_without_inspection
      - exact_css_cause_without_DOM_or_computed_style
      - export_validation
    confidence_cap: medium

  L4_dom_or_export_structure:
    description: DOM notes, export JSON, or structure evidence
    can_support:
      - structure_or_node_identity
      - class_presence
      - possible_control_mapping
      - project_breakpoint_settings_if_export_contains_them
    cannot_support:
      - visual_correctness_without_render
      - visual_regression_status
      - accessibility_pass_without_semantic_review
    confidence_cap: high_for_structure_medium_for_visual

  L5_live_render_plus_dom_plus_visual:
    description: strongest current validation state combining live render, DOM/export, screenshots, and metadata
    can_support:
      - strongest_validation_state
      - frontend_behavior_claims
      - before_after_regression_claims_with_scope
    cannot_support:
      - production_ready_without_full_release_gate
      - accessibility_pass_without_accessibility_gate
    confidence_cap: high
```

---

## 6. Evidence Quality Map Schema

```yaml
Evidence_Quality_Map:
  schema: ev4-responsive-evidence-quality-map@1.0.0
  items:
    - evidence_id:
      quality_level:
        enum:
          - L1_static_visual_only
          - L2_frontend_visual_with_viewport
          - L3_resize_sweep_or_video
          - L4_dom_or_export_structure
          - L5_live_render_plus_dom_plus_visual
      can_support:
      cannot_support:
      confidence_cap:
        enum:
          - low
          - medium
          - high
          - high_for_structure_medium_for_visual
      downstream_allowed_use:
        observation:
          enum: yes|no|limited
        diagnosis:
          enum: yes|no|limited
        repair_selection:
          enum: yes|no|limited
        validation_claim:
          enum: yes|no|limited
      notes:
```

---

## 7. Breakpoint Observation Schema

```yaml
Breakpoint_Observation:
  schema: ev4-responsive-breakpoint-observation@1.0.0
  observation_id:
  viewport:
  viewport_width_px:
  affected_visual_group:
  affected_node_id:
  symptom:
  evidence_ids:
  evidence_label:
    enum:
      - SUPPORTED_EVIDENCE
      - PARTIALLY_SUPPORTED_EVIDENCE
      - INFERRED_EVIDENCE
      - ABSENT_EVIDENCE
      - CONTRADICTED_EVIDENCE
      - UNRESOLVED_CONFLICT
      - NON_APPLICABLE
  confidence:
    enum: low|medium|high
  cause_status:
    enum:
      - unknown
      - partially_supported
      - supported
      - contradicted
  cause_candidates:
  forbidden_diagnoses:
  unknowns_created:
```

Observation must describe what is visible or evidenced. It must not silently diagnose cause.

---

## 8. Observation Evidence Ledger Schema

```yaml
Observation_Evidence_Ledger:
  schema: ev4-responsive-observation-ledger@1.0.0
  observation_evidence_items:
    - observation_evidence_id:
      source_observation_id:
      source_evidence_ids:
      viewport:
      affected_node_id:
      observation_summary:
      claim_scope:
        enum:
          - symptom_only
          - cause_candidate
          - confirmed_cause
          - repair_support
          - validation_result
      evidence_label:
      confidence:
      unknowns:
      downstream_restrictions:
```

---

## 9. Evidence Promotion Rules

```yaml
evidence_promotion_rules:
  raw_to_observation:
    allowed_when:
      - evidence_id_exists
      - quality_level_assigned
      - claim_scope_within_can_support

  observation_to_failure:
    allowed_when:
      - symptom_is_visible_or_supported
      - failure_type_maps_to_closed_taxonomy
      - evidence_ids_preserved

  failure_to_cause_candidate:
    allowed_when:
      - cause_status_not_forced_to_supported
      - cause_candidates_are_marked_as_candidates

  cause_candidate_to_supported_cause:
    allowed_when:
      - DOM_export_computed_style_or_builder_feedback_supports_cause
      - contradiction_check_passes

  evidence_to_repair_selection:
    allowed_when:
      - repair_option_analysis_exists
      - unknown_budget_gate_passes
      - claim_scope_supports_selection

  evidence_to_validation_claim:
    allowed_when:
      - after_repair_evidence_exists
      - validation_scope_is_explicit
      - production_boundary_not_overclaimed
```

---

## 10. Forbidden Evidence Inflation

```yaml
forbidden_evidence_inflation:
  - screenshot_to_exact_css_cause
  - screenshot_to_DOM_order
  - screenshot_to_exact_elementor_control
  - screenshot_to_project_breakpoint_value
  - screenshot_to_accessibility_pass
  - editor_preview_to_frontend_validation_without_flag
  - export_json_to_visual_correctness_without_render
  - official_docs_to_current_project_state
  - lessons_learned_to_current_failure_proof
  - user_memory_to_authoritative_payload
```

Violation effect:

```yaml
violation_effect:
  severity: blocker
  route_to:
    - /responsive-evidence-ingest-ledger
    - /breakpoint-observation
    - /responsive-observation-evidence-ledger
```

---

## 11. Conflict Rules

```yaml
conflict_rules:
  direct_conflict_between_current_evidence_items:
    evidence_label: UNRESOLVED_CONFLICT
    action: stop_or_route_to_evidence_request

  current_frontend_evidence_contradicts_main_handoff:
    evidence_label: CONTRADICTED_EVIDENCE
    action: route_to_owning_EV4_stage_or_architecture_mutation_veto

  older_evidence_conflicts_with_newer_current_evidence:
    action: prefer_latest_current_evidence_if_source_priority_allows
    required: record_superseded_evidence

  absent_evidence:
    evidence_label: ABSENT_EVIDENCE
    action: create_unknown_or_block_if_high_impact
```

---

## 12. Allowed Work

Evidence stages may:

```text
- register evidence items;
- classify evidence quality;
- state can_support and cannot_support;
- create observations with evidence IDs;
- create unknowns;
- identify conflicts;
- restrict downstream claims;
- route missing evidence requests.
```

---

## 13. Forbidden Work

Evidence stages must not:

```text
- select repair options;
- write repair steps;
- recommend CSS;
- claim confirmed root cause from screenshot alone;
- convert unknowns into facts;
- resolve conflicts silently;
- claim production readiness;
- use case memory as current evidence.
```

---

## 14. Self-Audit

```yaml
self_audit:
  raw_and_observation_evidence_separated: pass|fail
  every_observation_has_evidence_id: pass|fail
  evidence_quality_assigned: pass|fail
  can_support_claim_scope_respected: pass|fail
  screenshot_only_diagnosis_avoided: pass|fail
  conflicts_preserved: pass|fail
  unknowns_created_for_absent_evidence: pass|fail
  no_repair_recommendation_leaked: pass|fail
```

---

## 15. Example

```yaml
Input_Evidence_Ledger:
  schema: ev4-responsive-evidence-ingest@1.0.0
  evidence_items:
    - evidence_id: RSP-E-001
      evidence_type: frontend_screenshot
      viewport_label: mobile
      viewport_width_px: 390
      viewport_height_px: 844
      capture_source: frontend
      source_ref: examples/smart-home-connector/mobile-before.png
      supplied_by: user
      known_limitations:
        - no_DOM_order
        - no_computed_style
      privacy_review_required: false

Evidence_Quality_Map:
  items:
    - evidence_id: RSP-E-001
      quality_level: L2_frontend_visual_with_viewport
      can_support:
        - viewport_specific_visual_state
        - visible_failure_at_viewport
      cannot_support:
        - exact_elementor_control
        - DOM_source_order
        - accessibility_pass
      confidence_cap: medium
      downstream_allowed_use:
        observation: yes
        diagnosis: limited
        repair_selection: limited
        validation_claim: no

Breakpoint_Observation:
  schema: ev4-responsive-breakpoint-observation@1.0.0
  observation_id: RSP-O-001
  viewport: mobile
  viewport_width_px: 390
  affected_visual_group: connector_stage
  affected_node_id: smart-home__connector-layer
  symptom: connector line visually collides with feature card text area
  evidence_ids:
    - RSP-E-001
  evidence_label: SUPPORTED_EVIDENCE
  confidence: medium
  cause_status: unknown
  cause_candidates:
    - connector_overlay_geometry
    - mobile_stack_order
    - insufficient_decoration_simplification
  forbidden_diagnoses:
    - exact_css_property
    - exact_elementor_control
  unknowns_created:
    - RSP-U-connector-mobile-cause
```
