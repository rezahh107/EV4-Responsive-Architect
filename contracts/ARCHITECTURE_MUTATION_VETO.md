# ARCHITECTURE_MUTATION_VETO

Version: 0.1.0
Status: hardening_candidate
Owner stages: global responsive gate after `/responsive-failure-map`
Applies to: every responsive analysis, routing, selection, plan, audit, and handoff stage

---

## 1. Purpose

Prevent responsive repair from becoming hidden re-architecture.

This contract protects the selected EV4 architecture, the approved Build_Tree_Payload, content editability, decorative/meaningful classifications, and desktop baseline from silent mutation during responsive repair.

Core rule:

```text
If a responsive failure cannot be fixed without changing the approved architecture,
EV4 Responsive Architect must stop and route back to the owning EV4 Architect stage.
```

---

## 2. Non-Purpose

This contract does not:

```text
- forbid legitimate responsive settings;
- forbid mobile simplification of decoration-only layers;
- forbid scoped CSS when selector safety passes;
- authorize the responsive pipeline to rewrite Build_Tree_Payload;
- authorize the model to create a new architecture candidate;
- authorize production-ready claims.
```

---

## 3. Global Rule

`Architecture Mutation Veto` is a global gate.

It must be checked by these stages:

```yaml
must_check_in_stages:
  - /responsive-failure-map
  - /decoration-classification-inheritance-check
  - /cross-viewport-cascade-dependency-map
  - /failure-priority-ordering
  - /unknown-budget-gate
  - /repair-ownership-routing
  - /repair-option-analysis
  - /responsive-repair-selection
  - /repair-scope-freeze
  - /responsive-repair-plan
  - /css-selector-safety-check
  - /accessibility-reading-order-gate
  - /builder-feedback-loop
  - /multi-run-convergence-gate
  - /partial-repair-state
  - /responsive-final-audit
  - /responsive-handoff-export
```

---

## 4. Mutation Categories

```yaml
mutation_categories:
  selected_architecture_mutation:
    description: selected architecture identity or family would change

  build_tree_identity_mutation:
    description: approved node identity, grouping, wrapper strategy, or primary flow would change

  content_semantics_mutation:
    description: meaningful content would be hidden, flattened, reordered unsafely, or moved into decoration/overlay

  decoration_role_mutation:
    description: decoration-only layer would become meaningful or carry essential reading order

  implementation_authority_mutation:
    description: responsive repair would override Implementation_Payload instead of routing to implementation repair

  CSS_as_architecture_mutation:
    description: CSS would reconstruct layout globally or replace approved structure
```

---

## 5. Veto Triggers

```yaml
architecture_mutation_veto_triggers:
  selected_architecture:
    - selected_candidate_identity_change
    - selected_candidate_family_change
    - architecture_candidate_reopened
    - architecture_candidate_reranked_inside_responsive_pipeline

  build_tree:
    - tree_node_identity_change_required
    - major_wrapper_addition_or_removal_required
    - primary_normal_flow_grouping_change_required
    - duplicate_mobile_section_required
    - meaningful_content_moved_into_overlay_required
    - Build_Tree_Payload_contradiction

  content:
    - meaningful_content_must_be_hidden_to_fit
    - meaningful_content_must_be_flattened_to_svg_image_or_html
    - meaningful_content_order_requires_unverified_DOM_reorder
    - content_editability_map_contradiction

  decoration:
    - decorative_element_must_become_meaningful
    - connector_layer_requires_semantic_role_change
    - decoration_classification_conflict

  implementation:
    - Implementation_Payload_contradiction
    - Handoff_Payload_contradiction
    - approved_widget_mapping_must_change_structurally

  CSS:
    - global_css_required_to_reconstruct_layout
    - unscoped_selector_required
    - CSS_required_to_create_meaningful_content
    - CSS_required_to_hide_meaningful_content
```

---

## 6. Allowed Responsive Repairs That Are Not Mutations

These are allowed only when evidence and stage gates support them:

```yaml
allowed_non_mutating_repairs:
  elementor_native_control:
    examples:
      - viewport_specific_direction
      - viewport_specific_width_or_flex_basis
      - viewport_specific_gap
      - viewport_specific_padding_or_margin
      - viewport_specific_typography
      - custom_order_if_accessibility_gate_passes_or_risk_carried

  decoration_simplification:
    examples:
      - hide_decoration_only_connector_on_mobile
      - simplify_decoration_only_connector_geometry
      - reduce_decoration_opacity_or_visual_weight
    required_condition: decoration_role_inherited_from_main_pipeline

  scoped_css:
    examples:
      - local_overflow_containment
      - local_responsive_sizing_patch
      - local_connector_decoration_adjustment
    required_condition: CSS_SELECTOR_SAFETY_passes
```

Allowed repair must preserve:

```yaml
must_preserve:
  - selected_candidate_id
  - selected_candidate_family
  - build_tree_node_identity
  - meaningful_content_visibility
  - content_editability_contract
  - decoration_classification
  - desktop_baseline_lock
```

---

## 7. Required Action When Veto Triggers

```yaml
architecture_mutation_veto_action:
  - stop_current_responsive_stage
  - emit_architecture_mutation_veto_report
  - preserve_all_responsive_evidence
  - preserve_failure_map_and_unknown_register
  - mark_current_repair_selection_blocked
  - route_to_earliest_owning_main_pipeline_stage
  - forbid_responsive_handoff_until_route_resolved
```

---

## 8. Route Owner Matrix

```yaml
route_owner_matrix:
  visual_role_or_content_classification_issue:
    route_to: EV4_Architect_/decompose
    examples:
      - current evidence contradicts meaningful/decorative classification
      - original visual grouping appears misread

  platform_capability_issue:
    route_to: EV4_Architect_/research
    examples:
      - required Elementor control capability is uncertain
      - export behavior contradicts assumed capability

  architecture_family_issue:
    route_to: EV4_Architect_/architectures
    examples:
      - selected architecture family cannot support responsive repair

  scoring_or_gate_issue:
    route_to: EV4_Architect_/score-audit
    examples:
      - prior scoring or audit allowed a contradicted architecture

  selected_candidate_issue:
    route_to: EV4_Architect_/recommend
    examples:
      - selected candidate identity conflict
      - winner no longer eligible due to contradiction

  build_tree_structure_issue:
    route_to: EV4_Architect_/build-tree
    examples:
      - missing wrapper boundary
      - connector containment structurally wrong
      - normal-flow grouping insufficient

  implementation_mapping_issue:
    route_to: EV4_Architect_/implementation
    examples:
      - widget mapping or control path wrong
      - scoped CSS plan contradicts approved tree

  final_audit_or_handoff_claim_issue:
    route_to: EV4_Architect_/final-audit_or_/handoff-export
    examples:
      - production boundary over-claimed
      - unresolved unknown silently dropped
```

---

## 9. Veto Report Schema

```yaml
Architecture_Mutation_Veto_Report:
  schema: ev4-responsive-architecture-mutation-veto@1.0.0
  veto_status:
    enum:
      - not_triggered
      - triggered_blocking
      - potential_veto_requires_evidence
      - routed_to_main_pipeline

  trigger_ids:
    - trigger_id

  trigger_details:
    - trigger_id:
      mutation_category:
      affected_payload:
      affected_node_id:
      affected_viewport:
      evidence_ids:
      why_responsive_repair_is_insufficient:
      earliest_owning_stage:
      required_route:

  preserved_state:
    failure_ids:
    evidence_ids:
    unknown_ids:
    audit_flag_ids:

  forbidden_downstream_work:
    - responsive_repair_selection
    - responsive_repair_plan
    - responsive_handoff_export

  allowed_next_work:
    - route_to_main_pipeline
    - request_evidence
    - emit_partial_repair_state_if_other_failures_can_be_safely_separated
```

---

## 10. Stage Gate Checklist

Every downstream stage must answer:

```yaml
architecture_mutation_gate_checklist:
  selected_candidate_id_unchanged: pass|fail|unknown
  selected_candidate_family_unchanged: pass|fail|unknown
  build_tree_node_identity_preserved: pass|fail|unknown
  meaningful_content_visibility_preserved: pass|fail|unknown
  meaningful_content_not_flattened: pass|fail|unknown
  decoration_role_not_reclassified: pass|fail|unknown
  responsive_repair_not_using_global_css_as_structure: pass|fail|unknown
  desktop_baseline_not_sacrificed: pass|fail|unknown
  veto_triggered: yes|no|potential
```

Gate result rules:

```yaml
gate_result_rules:
  any_fail: veto_triggered
  any_unknown_high_impact: stop_or_route_to_unknown_budget_gate
  potential_veto: do_not_select_repair_until_resolved
  all_pass: responsive_stage_may_continue
```

---

## 11. Forbidden Work

```text
No self-authorized build-tree change.
No silent selected-candidate change.
No hiding architecture mutation inside CSS.
No mobile-only duplicate section as repair without main-pipeline route.
No reclassifying connector lines as meaningful.
No hiding meaningful content to pass mobile.
No proceeding to handoff after veto.
No manual override of veto without explicit human architect route and production-ready claim disabled.
```

---

## 12. Stop Conditions

```yaml
stop_conditions:
  - veto_triggered_blocking
  - selected_candidate_identity_conflict
  - build_tree_node_identity_conflict
  - meaningful_content_visibility_requires_hide
  - decoration_role_conflict
  - unscoped_css_required_for_layout
  - duplicate_mobile_section_required
  - desktop_baseline_must_be_broken_to_fix_mobile
```

---

## 13. Self-Audit

```yaml
self_audit:
  global_gate_checked: pass|fail
  all_triggers_evaluated: pass|fail
  selected_candidate_preserved: pass|fail
  build_tree_identity_preserved: pass|fail
  meaningful_content_preserved: pass|fail
  decoration_classification_preserved: pass|fail
  no_css_architecture_mutation: pass|fail
  route_owner_assigned_if_veto: pass|fail|not_applicable
  downstream_handoff_blocked_if_veto: pass|fail|not_applicable
```

---

## 14. Example — Veto Not Triggered

```yaml
Architecture_Mutation_Veto_Report:
  schema: ev4-responsive-architecture-mutation-veto@1.0.0
  veto_status: not_triggered
  trigger_ids: []
  trigger_details: []
  preserved_state:
    failure_ids:
      - RSP-F-002
    evidence_ids:
      - RSP-E-004
    unknown_ids:
      - RSP-U-001
    audit_flag_ids: []
  allowed_next_work:
    - continue_to_repair_option_analysis
```

---

## 15. Example — Veto Triggered

```yaml
Architecture_Mutation_Veto_Report:
  schema: ev4-responsive-architecture-mutation-veto@1.0.0
  veto_status: triggered_blocking
  trigger_ids:
    - VETO-TREE-001
  trigger_details:
    - trigger_id: VETO-TREE-001
      mutation_category: build_tree_identity_mutation
      affected_payload: Build_Tree_Payload
      affected_node_id: smart-home__connector-stage
      affected_viewport: mobile
      evidence_ids:
        - RSP-E-009
      why_responsive_repair_is_insufficient: connector containment requires changing the approved overlay stage boundary
      earliest_owning_stage: EV4_Architect_/build-tree
      required_route: route_to_build_tree_repair
  preserved_state:
    failure_ids:
      - RSP-F-006
    evidence_ids:
      - RSP-E-009
    unknown_ids:
      - RSP-U-004
    audit_flag_ids:
      - RSP-AF-002
  forbidden_downstream_work:
    - responsive_repair_selection
    - responsive_repair_plan
    - responsive_handoff_export
  allowed_next_work:
    - route_to_main_pipeline
```
