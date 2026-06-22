# EV4 Responsive Architect — Master Project Specification

Version: 0.1.0-final-draft  
Status: repository_initialization_ready  
Production status: not_production_ready  
Language: Persian reports, English technical identifiers  
Primary owner: Reza  
Project family: EV4 Architect / EV4 Responsive Architect  
Target platform: Elementor V4  
Execution model: LLM-guided, audit-first, builder-in-the-loop, validation-ready, repository-backed

---

## 0. Executive Summary

`EV4 Responsive Architect` is a responsive repair, validation, and handoff system built on top of the completed `EV4 Architect` section architecture pipeline.

`EV4 Architect` answers:

```text
What is the safest, editable, Elementor-native architecture for this section?
```

`EV4 Responsive Architect` answers:

```text
After the section is built, what breaks across real viewports, why does it break, who owns the repair, what is safe to change, how do we repair atomically, and how do we prove that we did not break another viewport?
```

Core rule:

```text
Responsive Architect may repair responsive behavior.
Responsive Architect may not silently re-architect the section.
```

If a responsive failure cannot be repaired without changing the approved architecture, the system must stop and route back to the earliest owning EV4 Architect stage.

---

## 1. Purpose

The purpose of `EV4 Responsive Architect` is to provide a controlled, evidence-bound responsive repair workflow for Elementor V4 sections that have already passed through EV4 Architect.

The project produces:

```text
- responsive audit reports;
- responsive failure maps;
- repair ownership routes;
- repair option analysis;
- atomic builder repair plans;
- partial repair handoffs;
- controlled responsive handoffs;
- validation-ready state snapshots.
```

The project must not produce:

```text
- hidden architecture changes;
- unscoped CSS patches;
- production-ready claims without real evidence;
- exact breakpoint or pixel claims without verified source;
- meaningful content flattened into image, SVG, or hard-coded HTML.
```

---

## 2. Core Philosophy

```text
Evidence before decision.
Input contract before diagnosis.
Structure before styling.
Meaningful content before decoration.
Normal flow before absolute positioning.
Inheritance before reclassification.
Observation before diagnosis.
Repair ownership before repair action.
Option analysis before repair selection.
Atomic repair before bulk repair.
Rollback before handoff.
Frontend validation before release claim.
Partial truth before over-claiming.
Programmatic validation before trusting model-generated schemas.
State as Code before conversational memory.
```

Guiding sentence:

```text
Run only as much pipeline as the risk requires,
but never less evidence than the claim requires.
```

---

## 3. Relationship to EV4 Architect

`EV4 Responsive Architect` is an add-on system in the EV4 ecosystem. It depends on completed EV4 Architect payloads and must respect the selected architecture unless a routed partial rerun explicitly returns to the correct EV4 stage.

Required main pipeline inputs:

```yaml
required_main_pipeline_inputs:
  - Recommendation_Payload
  - Build_Tree_Payload
  - Implementation_Payload
  - Final_Audit_Payload
  - Handoff_Payload
  - EV4_DEBUG_TRACE
  - selected_candidate_id
  - selected_candidate_family
  - structure_tree
  - naming_map
  - class_map
  - overlay_decoration_map
  - content_editability_map
  - responsive_structure_contract
  - asset_accessibility_map
  - carried_unknowns
  - audit_flags
  - repair_routes
```

Locked facts:

```yaml
locked_main_pipeline_facts:
  - selected_candidate_id
  - selected_candidate_family
  - build_tree_node_identity
  - meaningful_content_classification
  - decorative_content_classification
  - overlay_decoration_map
  - responsive_structure_contract
  - content_editability_map
  - carried_unknowns
  - audit_flags
```

Forbidden main-pipeline reinterpretation:

```text
- re-score architecture candidates;
- re-run /recommend;
- select a different architecture;
- reinterpret the original screenshot as new architecture evidence;
- reclassify decorative elements as meaningful;
- reclassify meaningful elements as decorative;
- convert a responsive repair into hidden build-tree mutation.
```

---

## 4. Non-Negotiable Boundaries

The system must not:

```text
- change the selected architecture without routed EV4 partial rerun;
- redesign during responsive repair;
- re-score architecture candidates;
- re-run architecture recommendation;
- reinterpret the original screenshot as new architecture evidence;
- flatten meaningful text into SVG, image, or hard-coded HTML;
- classify decorative connector lines as meaningful if the main Build_Tree_Payload classified them as decorative;
- hide meaningful content on any viewport;
- assume cards are clickable;
- assume Dynamic Loop from repeated items alone;
- assume mobile connector behavior without evidence;
- invent exact breakpoints, colors, typography, spacing, coordinates, or asset dimensions;
- write unscoped global CSS;
- claim live Elementor rendering unless live rendering evidence exists;
- claim export JSON or EDIS validation unless real export evidence exists;
- claim exact pixel matching unless measured and validated;
- claim production readiness without release-gate evidence.
```

---

## 5. Source-of-Truth Hierarchy

```yaml
platform_capability_source_priority:
  1: real_elementor_runtime_or_export_evidence
  2: current_elementor_editor_ui_evidence
  3: official_elementor_documentation
  4: project_contracts
  5: workbook_or_internal_methodology
  6: model_inference

current_implementation_state_priority:
  1: latest_user_explicit_statement
  2: latest_frontend_screenshot
  3: latest_editor_screenshot
  4: diagnostic_output
  5: current_state_payload
  6: older_notes_or_screenshots

responsive_repair_authority:
  1: Main_EV4_Build_Tree_Payload
  2: Main_EV4_Implementation_Payload
  3: Main_EV4_Handoff_Payload
  4: Main_EV4_Final_Audit_Payload
  5: Desktop_Baseline_Lock
  6: Breakpoint_Inventory_Lock
  7: Breakpoint_Observation_Evidence
  8: Responsive_Evidence_Ledger
  9: Builder_Feedback_Loop_Evidence
```

If sources conflict, the conflict must be reported before continuing.

---

## 6. Evidence Labels

Use this closed evidence set:

```yaml
evidence_labels:
  - SUPPORTED_EVIDENCE
  - PARTIALLY_SUPPORTED_EVIDENCE
  - INFERRED_EVIDENCE
  - ABSENT_EVIDENCE
  - CONTRADICTED_EVIDENCE
  - UNRESOLVED_CONFLICT
  - NON_APPLICABLE
```

Rules:

```text
ABSENT_EVIDENCE is not contradiction.
CONTRADICTED_EVIDENCE is not unknown.
NON_APPLICABLE is not a good score.
Unknowns must survive until explicitly resolved by named evidence.
A screenshot may prove a visible symptom; it does not prove DOM, CSS cause, Elementor setting, exact breakpoint, or accessibility pass.
```

---

## 7. Project Architecture

The repository is organized around five layers:

```text
1. Human-readable contracts
2. Machine-readable schemas
3. Stage protocols
4. State and validation tooling
5. E2E and fixture evidence
```

Recommended top-level directories:

```text
docs/
stages/
contracts/
schemas/
state/
validation/
examples/
prompts/
.github/workflows/
```

---

## 8. Execution Model

The contract model keeps all stages available. The execution model may choose shorter paths based on risk.

```yaml
execution_modes:
  full_protocol_mode:
    use_when:
      - formal audit
      - E2E validation
      - complex responsive failure
      - cascade risk is high
      - architecture mutation veto is possible
      - CSS repair is required

  triage_fast_path:
    use_when:
      - trivial repair
      - low cascade risk
      - no meaningful content order change
      - no overlay or connector risk
      - no CSS required
    required_gates:
      - main_pipeline_input_contract
      - desktop_baseline_lock
      - breakpoint_inventory_lock
      - architecture_mutation_veto_check
      - cascade_check_lite
      - atomic_repair_plan
      - builder_feedback
      - final_audit_lite

  interactive_builder_mode:
    use_when:
      - builder is inside Elementor
      - user wants step-by-step execution
      - repair is being applied manually
    output_style:
      - small reversible actions
      - exact node and control path
      - confirmation sentence after checkpoint
      - rollback before next step
```

Fast-path guard:

```yaml
triage_fast_path_guard:
  fast_path_may_reduce_number_of_stages: true
  fast_path_must_not_reduce_evidence_requirements_for_claims: true
  fast_path_must_not_skip:
    - input_contract_validation
    - architecture_mutation_veto_check
    - desktop_baseline_lock
    - breakpoint_inventory_lock
    - unknown_budget_gate_for_high_impact_unknowns
    - accessibility_gate_if_order_or_visibility_changes
    - final_audit
```

---

## 9. Responsive Pipeline

Full stage order:

```text
/main-pipeline-handoff-ingest
/responsive-intake
/context-budget-check
/responsive-evidence-ingest-ledger
/repair-triage
/desktop-baseline-lock
/breakpoint-inventory-lock
/breakpoint-observation
/responsive-observation-evidence-ledger
/responsive-failure-map
/decoration-classification-inheritance-check
/cross-viewport-cascade-dependency-map
/failure-priority-ordering
/unknown-budget-gate
/repair-ownership-routing
/repair-option-analysis
/responsive-repair-selection
/repair-scope-freeze
/responsive-repair-plan
/css-selector-safety-check
/accessibility-reading-order-gate
/builder-feedback-loop
/multi-run-convergence-gate
/partial-repair-state
/responsive-final-audit
/responsive-handoff-export
```

Conditional stages:

```yaml
conditional_stages:
  css-selector-safety-check:
    runs_when:
      - selected_repair_uses_custom_css

  accessibility-reading-order-gate:
    runs_when:
      - visual_order_changes
      - custom_order_used
      - reverse_direction_used
      - meaningful_content_visibility_changes
      - overlay_interacts_with_meaningful_content

  multi-run-convergence-gate:
    runs_when:
      - repair_iteration_count_greater_than_1
      - builder_feedback_introduces_new_failure
      - repeated repair_attempts_occur
```

---

## 10. Key Stage Contracts

### 10.1 `/main-pipeline-handoff-ingest`

Purpose: load, verify, normalize, and hash main EV4 handoff payloads before responsive work begins.

Output:

```yaml
Main_Pipeline_Handoff_Ingest_Payload:
  schema: ev4-responsive-main-input@1.0.0
  selected_candidate_id:
  selected_candidate_family:
  payload_identity_hashes:
  inherited_structure_tree:
  inherited_class_map:
  inherited_content_editability_map:
  inherited_overlay_decoration_map:
  inherited_responsive_structure_contract:
  inherited_unknowns:
  inherited_audit_flags:
  inherited_repair_routes:
  input_authorization_status:
```

Forbidden: redesign, responsive diagnosis, new architecture evidence, payload identity changes.

### 10.2 `/responsive-evidence-ingest-ledger`

Purpose: record raw input evidence before deriving observations.

Evidence quality levels:

```yaml
evidence_quality_levels:
  - L1_static_visual_only
  - L2_frontend_visual_with_viewport
  - L3_resize_sweep_or_video
  - L4_dom_or_export_structure
  - L5_live_render_plus_dom_plus_visual
```

A raw screenshot may support visible symptoms, not exact cause or release claims.

### 10.3 `/breakpoint-inventory-lock`

Purpose: lock actual project breakpoints before observation and repair planning.

```yaml
source_priority:
  1: live_elementor_project_settings_or_export_json
  2: user_declaration
  3: existing_builder_context_or_editor_screenshot
  4: build_tree_responsive_contract
  5: elementor_default_fallback_with_unverified_label
```

Fallback may observe and produce controlled repair with visible flags, but cannot support release-ready claims.

### 10.4 `/responsive-failure-map`

Closed failure taxonomy:

```yaml
failure_taxonomy:
  - overflow_x
  - overflow_y
  - collision
  - clipping
  - wrapping_break
  - unreadable_text
  - bad_visual_order
  - bad_dom_order_risk
  - tap_target_risk
  - overlay_escape
  - connector_noise
  - connector_collision
  - visual_core_scale_failure
  - asset_aspect_ratio_failure
  - duplicate_content_risk
  - hidden_meaningful_content
  - spacing_collapse
  - excessive_blank_space
  - z_index_overlap
  - other_requires_taxonomy_extension
```

### 10.5 `/repair-option-analysis`

Purpose: analyze possible repair options before selecting a repair bundle.

Required for each eligible failure:

```yaml
repair_option_analysis:
  for_each_failure:
    failure_id:
    options:
      - option_id
        repair_owner:
        repair_type:
        native_control_possible:
        scoped_css_needed:
        desktop_regression_risk:
        cascade_risk:
        accessibility_risk:
        evidence_support:
        rejected_reason_if_not_selected:
        verification_required:
```

Forbidden: selection without option ledger, CSS option before native option is evaluated.

### 10.6 `/responsive-repair-plan`

Purpose: produce atomic, reversible builder steps for selected failures only.

Each step requires:

```yaml
repair_atomic_step:
  step_id:
  failure_id:
  selected_option_id:
  target_node_id:
  target_structure_label:
  active_class_name:
  viewport_scope:
  single_repair_intent:
  elementor_control_path:
  before_state_description:
  expected_after_state:
  rollback_action:
  desktop_check_required:
  cascade_check_required:
  validation_evidence_required:
```

---

## 11. Architecture Mutation Veto

`Architecture Mutation Veto` is a global gate. Every stage after `/responsive-failure-map` must check it.

Triggers:

```yaml
architecture_mutation_veto_triggers:
  - selected_candidate_identity_change
  - selected_candidate_family_change
  - meaningful_content_must_be_hidden_to_fit
  - decorative_element_must_become_meaningful
  - connector_layer_requires_semantic_role_change
  - normal_flow_content_requires_absolute_positioning_without_prior_approval
  - tree_node_identity_change_required
  - major_wrapper_addition_or_removal_required
  - duplicate_mobile_section_required
  - Build_Tree_Payload_contradiction
  - Implementation_Payload_contradiction
  - Handoff_Payload_contradiction
```

Action:

```yaml
architecture_mutation_veto_action:
  - stop_current_responsive_stage
  - emit_architecture_mutation_veto_report
  - preserve_all_responsive_evidence
  - route_to_earliest_owning_main_pipeline_stage
```

Forbidden:

```text
No self-authorized build-tree change.
No silent selected-candidate change.
No hiding architecture mutation inside CSS.
No proceeding to handoff after veto.
```

---

## 12. Forbidden Inference Rule

```text
A screenshot can show a symptom.
A screenshot alone cannot prove the technical cause.
```

Forbidden from static screenshot only:

```yaml
forbidden_from_static_screenshot_only:
  - exact_dom_order
  - exact_css_property
  - exact_elementor_control
  - exact_breakpoint_value
  - plugin_dependency
  - export_behavior
  - accessibility_pass
  - production_ready_state
```

If cause is unclear:

```yaml
required_if_cause_unclear:
  cause_status: unknown
  cause_candidates_allowed: true
  repair_must_be_conditional: true
```

---

## 13. Elementor Control Path Format

Builder instructions must use Elementor-native UI language.

Required shape:

```yaml
elementor_control_path:
  schema: ev4-elementor-control-path@1.0.0
  target_node_id:
  structure_label:
  class_name:
  editor_area:
  control_group:
  control_name:
  viewport_scope:
  value_policy:
  value_source:
  fallback_semantic_instruction:
  rollback_instruction:
```

Builder instruction must include node, active class, viewport, tab/panel, control, value policy, validation check, and rollback.

---

## 14. Context Budget and Truncation Ban

Compression is allowed. Blind truncation is forbidden.

Forbidden:

```yaml
context_compression_forbidden:
  - blind_truncation
  - drop_oldest_messages_strategy
  - remove_stage_anchor_fields
  - remove_unknowns_to_save_space
  - remove_veto_triggers
  - remove_payload_hashes
  - remove_repair_routes
```

Must preserve exactly:

```yaml
must_preserve_exactly:
  - selected_candidate_id
  - payload_identity_hashes
  - breakpoint_inventory_lock
  - desktop_baseline_lock
  - architecture_mutation_veto_state
  - unknown_budget_gate_state
  - repair_scope_freeze
  - partial_repair_state
```

---

## 15. Payload Identity Hashing

Every payload must have a stable identity record.

```yaml
payload_identity:
  schema: ev4-responsive-payload-identity@1.0.0
  payload_id:
  schema_version:
  source_stage:
  content_hash:
  created_at:
  supersedes:
  depends_on:
  source_files_or_evidence_ids:
```

If an upstream payload hash changes:

```yaml
if_upstream_payload_hash_changes:
  - mark_downstream_payloads_stale
  - rerun_from_earliest_dependent_stage
  - do_not_reuse_stale_handoff
```

---

## 16. State as Code

Authoritative state should be versioned JSON in Git. SQLite may be used only as an optional index.

```yaml
state_strategy:
  authoritative_state:
    format: versioned_json_in_git
    purpose:
      - audit
      - diff
      - rollback
      - CI validation
      - convergence tracking

  optional_index:
    format: sqlite
    purpose:
      - fast_lookup
      - local_querying
      - evidence_registry_index
    authoritative: false
```

Do not commit private production data or large binaries without artifact policy review.

---

## 17. Programmatic Validation Strategy

LLM-generated payloads must not be trusted as structurally valid solely because the LLM says they are valid.

```yaml
validation_responsibilities:
  LLM:
    - semantic reasoning
    - architecture judgment
    - evidence interpretation
    - repair planning
    - audit explanation

  Programmatic_Validator:
    - JSON Schema validation
    - required field validation
    - enum validation
    - payload identity check
    - schema version check
    - anchor compatibility check
    - duplicate ID detection
    - forbidden field detection
    - stale payload detection
```

Initial validator targets:

```yaml
validator_targets_v0_1:
  - ev4-responsive-stage-anchor@1.0.0
  - ev4-responsive-main-input@1.0.0
  - ev4-responsive-breakpoint-inventory@1.0.0
  - ev4-responsive-evidence-ingest@1.0.0
  - ev4-responsive-repair-plan@1.0.0
```

Recommended tools:

```text
Python: jsonschema
Node.js: ajv
CI: GitHub Actions
```

---

## 18. Visual Regression Policy

Visual regression is recommended for v0.1 and required for stable release claims.

```yaml
visual_regression_policy:
  v0_1:
    status: optional_recommended
    use_for:
      - manual_comparison
      - before_after_desktop_regression_check
      - pilot_evidence_review

  v0_2:
    status: recommended
    use_for:
      - E2E_002
      - responsive_screenshot_set
      - desktop_before_after_regression

  stable_release:
    status: required_for_release_claim
    required_tools:
      - Playwright_screenshot_capture
      - baseline_screenshot_set
      - diff_threshold_policy
      - human_review_for_false_positives
```

Visual regression must not be the only validation source. It should be combined with breakpoint inventory, DOM/export evidence where available, builder feedback, accessibility checks, and scoped validation claims.

---

## 19. Accessibility Reading Order Gate

Runs when visual order changes, custom order is used, reverse direction is used, meaningful content visibility changes, or overlays interact with meaningful content.

Required checks:

```yaml
accessibility_reading_order_gate:
  schema: ev4-responsive-accessibility-gate@1.0.0
  required_checks:
    - meaningful_content_visibility_preserved
    - source_order_risk_recorded
    - keyboard_order_risk_recorded
    - screen_reader_order_risk_recorded
    - tap_target_risk_recorded
    - focus_order_risk_recorded
```

Allowed outcomes: `pass`, `pass_with_visible_risk`, `fail_requires_repair`, `fail_requires_main_pipeline_rerun`.

---

## 20. Severity Model

Use this closed severity set:

```yaml
severity_levels:
  blocker:
    effect: must_stop_current_stage
  high:
    effect: must_halt_repair_selection_unless_explicitly_routed
  medium:
    effect: may_proceed_if_carried_forward_and_budget_allows
  minor:
    effect: may_proceed_with_visible_flag
  note:
    effect: informational_only
```

Do not use `major` as severity in this project. Use `high` instead.

---

## 21. Handoff and Production Boundary

Allowed handoff states:

```yaml
handoff_states:
  clean_responsive_handoff:
    allowed_when:
      - final_status: pass
      - no_medium_or_higher_flags
      - unknowns_do_not_affect_responsive_repair

  controlled_handoff_with_flags:
    allowed_when:
      - final_status: pass_with_minor_flags or pass_with_medium_flags
      - flags_are_visible
      - no_blocker_or_high_unresolved

  partial_repair_handoff:
    allowed_when:
      - partial_repair_state_documented
      - remaining_failures_are_explicit
      - repair_routes_are_present

  blocked_handoff:
    required_when:
      - blocker_exists
      - high_unresolved_exists
      - schema_mismatch_exists
      - selected_candidate_identity_conflict_exists
      - production_boundary_would_be_violated
```

The project must not claim `production_ready`, `release_ready`, `pixel_perfect`, `export_validated`, `live_render_validated`, or `accessibility_passed` unless evidence exists for the claim.

---

## 22. Builder Interaction Policy

```text
- Use small reversible steps.
- Normally provide up to five small related actions per response in interactive builder mode.
- Always identify selected element, active class, control path, viewport, and value source.
- Do not combine unrelated structure, styling, responsive, CSS, and asset work in one step.
- Ask for exact confirmation sentence after each checkpoint.
- Do not proceed after unexpected desktop change.
- Do not force full pipeline rerun for one local step failure.
- Do not over-explain official documentation in builder-step responses unless requested.
```

Example confirmation:

```text
Root and Relative Stage are created, classes applied without dots.
```

---

## 23. E2E and Validation Roadmap

### E2E-001 — Textual Fixture Contract Validation

Goal: validate prompt-pack and contract flow with controlled textual fixtures. Not sufficient for real screenshot validation, live Elementor rendering, export JSON validation, exact pixel matching, or production readiness.

### E2E-002 — Real Builder Responsive Test

Required evidence:

```yaml
E2E_002_required_evidence:
  - original_reference_screenshot
  - completed_main_EV4_handoff
  - desktop_baseline_frontend_screenshot
  - breakpoint_inventory_lock
  - tablet_frontend_screenshot
  - mobile_frontend_screenshot
  - builder_feedback_after_repair
  - final_frontend_screenshots
  - responsive_final_audit
```

Optional recommended evidence: Elementor export JSON, EDIS evidence, Playwright screenshot set, browser/device matrix, visual diff report.

### E2E-003 — Export / Import / JSON Roundtrip

Required evidence: Build_Tree_Payload, generated Elementor JSON skeleton, import test result, exported Elementor JSON after import, roundtrip comparison, live render screenshot, Playwright screenshot set.

---

## 24. Pilot Case Plan

Before building full automation, run a vertical-slice pilot.

```yaml
pilot_case_v0_1:
  section: smart_home_connector
  mode: shadow_mode_manual

  run_only:
    - main-pipeline-handoff-ingest
    - responsive-evidence-ingest-ledger
    - desktop-baseline-lock
    - breakpoint-inventory-lock
    - breakpoint-observation
    - responsive-failure-map
    - failure-priority-ordering
    - repair-ownership-routing
    - repair-option-analysis
    - responsive-repair-selection
    - repair-scope-freeze
    - responsive-repair-plan
    - responsive-final-audit-lite

  skip_for_pilot:
    - full_schema_validator
    - Playwright_automation
    - multi_run_convergence
    - full_handoff_export
```

Pilot success criteria:

```yaml
pilot_success_criteria:
  - builder_can_follow_steps_without_extra_interpretation
  - each_step_has_rollback
  - desktop_regression_check_is_clear
  - no_architecture_mutation_occurs
  - unknowns_are_visible
  - repair_option_analysis_prevents_premature_selection
```

---

## 25. Initial Milestone Checklist

```yaml
milestone_v0_1_required:
  docs:
    - PROJECT_MASTER_SPEC.md
    - STATUS.md
    - README.md
    - CHANGELOG.md
    - docs/00_OVERVIEW.md
    - docs/05_VALIDATION_ROADMAP.md
    - docs/06_PILOT_CASE_PLAN.md

  contracts:
    - MAIN_PIPELINE_HANDOFF_INPUT_CONTRACT
    - ARCHITECTURE_MUTATION_VETO
    - RESPONSIVE_EVIDENCE_CONTRACT
    - FORBIDDEN_INFERENCE_RULE
    - REPAIR_TRIAGE_ROUTING
    - DESKTOP_BASELINE_LOCK
    - BREAKPOINT_INVENTORY_LOCK
    - CROSS_VIEWPORT_CASCADE_DEPENDENCY
    - REPAIR_OPTION_ANALYSIS
    - REPAIR_ATOMICITY
    - ELEMENTOR_CONTROL_PATH_FORMAT
    - ACCESSIBILITY_READING_ORDER_GATE
    - CSS_SELECTOR_SAFETY
    - PAYLOAD_IDENTITY_HASHING
    - STATE_AS_CODE
    - PRODUCTION_BOUNDARY

  schemas:
    - stage_anchor_schema_stub
    - main_input_schema_stub
    - evidence_ingest_schema_stub
    - breakpoint_inventory_schema_stub
    - repair_option_analysis_schema_stub
    - repair_plan_schema_stub
    - accessibility_gate_schema_stub
    - handoff_schema_stub

  validation:
    - schema_validator_prototype
    - sample_valid_payload
    - sample_invalid_payload
    - payload_identity_hash_check

  examples:
    - smart_home_connector_shadow_mode_example
```

---

## 26. Current Project Verdict

```yaml
project_status:
  ev4_core_pipeline: mature_for_controlled_handoff
  responsive_extension: repository_initialization_ready
  production_ready: false
  prompt_pack_release_ready: false
  next_phase: repo_initialization_contract_split_schema_stubs_and_pilot_case
```

The next correct move is:

```text
Commit the master spec.
Split contracts.
Version schemas.
Create validators.
Run a pilot case.
Then run real E2E evidence.
```

---

## 27. Reference Baseline

This specification is aligned with these external method families:

```text
- Elementor responsive editing and container workflow
- WCAG 2.2 Reflow and content preservation requirements
- CSS responsive design practices: media queries, container queries, and normal-flow behavior
- JSON Schema / Ajv validation for machine-readable payloads
- Playwright visual comparison for regression checks
- Git-based State as Code for auditability and rollback
```
