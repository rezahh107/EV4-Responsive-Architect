# EV4 Responsive Architect — Master Project Specification

Version: 0.2.0-current-system-sync  
Status: risk_priority_engine_hardened  
Production status: not_production_ready  
Language: Persian reports, English technical identifiers  
Primary owner: Reza  
Project family: EV4 Architect / EV4 Responsive Architect  
Target platform: Elementor V4  
Execution model: LLM-guided, audit-first, builder-in-the-loop, validation-ready, repository-backed

---

## 0. Executive Summary

`EV4 Responsive Architect` is the responsive repair, validation, and handoff system that runs after a section has already passed through the main `EV4 Architect` architecture pipeline.

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

If a responsive failure cannot be repaired without changing the approved architecture, the system must stop and route back to the owning EV4 Architect stage.

---

## 1. Current Repository State

This master specification reflects the repository state after the following merged hardening layers:

```yaml
completed_layers:
  contract_hardening:
    status: merged
    purpose: harden the main handoff, mutation veto, evidence, repair option, accessibility, and CSS selector contracts

  schema_hardening:
    status: merged_to_main
    purpose: convert core payloads into machine-checkable JSON schemas with valid and invalid fixtures

  E2E_001_textual_validation:
    status: merged
    purpose: validate the minimum textual payload chain from intake to repair and gates

  smart_home_connector_pilot_package:
    status: merged
    purpose: provide shadow-mode pilot runbook, manifest, templates, and starter prompt

  pilot_harness_hardening:
    status: merged
    purpose: validate pilot manifest, conditional stages, lite gates, placeholder policy, and output templates

  evidence_intake_validation:
    status: merged
    purpose: turn human intake into a machine-checkable evidence intake packet

  pilot_readiness_engine:
    status: merged
    purpose: emit persistent readiness reports for submitted packets with visible flags, blocking reasons, and authorization scope

  pilot_dry_run_execution_layer:
    status: merged
    purpose: dry-run the chain from sample submitted packet to readiness report, manifest check, and pilot run record

  sample_vs_real_safety_hardening:
    status: merged
    purpose: prevent sample packets from being treated as real submitted evidence

  risk_priority_assessment_engine:
    status: merged
    purpose: validate and emit categorical risk-priority assessments without numeric scoring and without allowing gate override
```

The system is now ready to receive real smart-home connector evidence, but it is not production-ready and must not claim real Elementor validation until real runtime/export evidence exists.

---

## 2. Purpose

The purpose of `EV4 Responsive Architect` is to provide a controlled, evidence-bound responsive repair workflow for Elementor V4 sections that have already passed through EV4 Architect.

The project produces:

```text
- evidence intake packets;
- pilot readiness reports;
- responsive audit reports;
- responsive failure maps;
- risk-priority assessments;
- repair ownership routes;
- repair option analysis;
- atomic Elementor repair plans;
- builder repair checklists;
- partial repair handoffs;
- controlled responsive handoffs;
- validation-ready state snapshots.
```

The project must not produce:

```text
- hidden architecture changes;
- unscoped CSS patches;
- numeric readiness scores;
- average scores used to override hard gates;
- production-ready claims without real evidence;
- exact breakpoint or pixel claims without verified source;
- meaningful content flattened into image, SVG, or hard-coded HTML.
```

---

## 3. Non-Negotiable Boundaries

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
- claim accessibility pass unless accessibility validation evidence exists;
- claim production readiness without release-gate evidence;
- treat sample submitted packets as real submitted evidence;
- use numeric score, average score, or readiness score to override any hard gate.
```

---

## 4. Source-of-Truth Hierarchy

```yaml
platform_capability_source_priority:
  1: real_elementor_runtime_or_export_evidence
  2: current_elementor_editor_ui_evidence
  3: official_elementor_documentation
  4: project_contracts
  5: workbook_or_internal_methodology
  6: model_inference

current_implementation_state_priority:
  1: real_submitted_evidence_packet
  2: latest_user_explicit_statement
  3: latest_frontend_screenshot
  4: latest_editor_screenshot
  5: diagnostic_output
  6: current_state_payload
  7: older_notes_or_screenshots

responsive_repair_authority:
  1: Main_EV4_Build_Tree_Payload
  2: Main_EV4_Implementation_Payload
  3: Main_EV4_Handoff_Payload
  4: Main_EV4_Final_Audit_Payload
  5: Evidence_Intake_Packet
  6: Pilot_Readiness_Report
  7: Desktop_Baseline_Lock
  8: Breakpoint_Inventory_Lock
  9: Breakpoint_Observation_Evidence
  10: Responsive_Evidence_Ledger
  11: Risk_Priority_Assessment
  12: Builder_Feedback_Loop_Evidence
```

If sources conflict, the conflict must be reported before continuing.

---

## 5. Evidence Discipline

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
NON_APPLICABLE is not a score.
Unknowns must survive until explicitly resolved by named evidence.
A screenshot may prove a visible symptom; it does not prove DOM, CSS cause, Elementor setting, exact breakpoint, or accessibility pass.
```

Evidence items must carry quality and downstream-use limits:

```yaml
evidence_item_required_shape:
  evidence_id:
  evidence_type:
  capture_source:
  viewport:
  viewport_width:
  quality_level:
  confidence_cap:
  can_support:
  cannot_support:
  downstream_allowed_use:
  known_limitations:
```

---

## 6. Repository Architecture

The repository is organized around these layers:

```text
1. Human-readable contracts
2. Machine-readable schemas
3. Stage and pilot protocols
4. Validation tooling
5. Valid and invalid fixtures
6. Pilot examples and templates
7. GitHub issue intake layer
8. CI workflow enforcement
```

Top-level directories:

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
.github/ISSUE_TEMPLATE/
```

---

## 7. Execution Modes

```yaml
execution_modes:
  full_protocol_mode:
    use_when:
      - formal audit
      - real evidence pilot
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

  shadow_mode_manual_pilot:
    use_when:
      - real evidence is available but no live Elementor automation is available
      - the system must produce a controlled repair report without release claims

  sample_submitted_packet_dry_run:
    use_when:
      - proving artifact chain and CI behavior before real evidence exists
    forbidden_use:
      - real pilot authorization
      - production or release claims
      - treating sample evidence as submitted project evidence
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

## 8. Responsive Pipeline

Full protocol stage order remains:

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
      - repeated_repair_attempts_occur
```

---

## 9. Current Machine-Checked Chain

The current machine-checked chain is:

```text
Schema Suite
→ E2E-001 Textual Fixture Validation
→ Pilot Manifest Check
→ Evidence Intake Packet Validation
→ Pilot Readiness Report Validation
→ Pilot Dry-Run Execution Validation
→ Risk-Priority Assessment Validation
```

Current CI commands:

```bash
python validation/schema_validator/validate_schemas.py
python validation/e2e/run_e2e_001.py
python validation/e2e/run_pilot_manifest_check.py
python validation/e2e/run_evidence_intake_check.py
python validation/e2e/run_pilot_readiness_check.py
python validation/e2e/run_pilot_dry_run_check.py
python validation/e2e/run_risk_priority_check.py
```

Required negative paths include:

```text
- invalid JSON schema payloads must fail;
- invalid CSS selector safety payloads must fail;
- sample packet in submitted-shadow-mode must fail;
- blocked intake packet must not produce authorized run record;
- numeric score fields must fail;
- hard gate failure with ready verdict must fail;
- blocker failure with ready verdict must fail;
- unknown evidence or failure refs must fail;
- high repair risk without mitigation must fail.
```

---

## 10. Active Schema Inventory

```yaml
active_schemas:
  ev4-responsive-stage-anchor:
    purpose: stage transition authorization

  ev4-responsive-main-input:
    purpose: main EV4 handoff normalization and authorization

  ev4-responsive-payload-identity:
    purpose: payload hash and source identity tracking

  ev4-responsive-evidence-ingest:
    purpose: raw evidence ledger payloads

  ev4-responsive-evidence-intake-packet:
    purpose: submitted evidence packet for real pilot intake

  ev4-responsive-pilot-manifest:
    purpose: pilot sequence, files, conditional stages, lite gates, and stop conditions

  ev4-responsive-pilot-readiness:
    purpose: readiness verdict, visible flags, blocking reasons, validation boundary, and pilot authorization

  ev4-responsive-pilot-run-record:
    purpose: dry-run or submitted shadow-mode run record with hashes and artifact traceability

  ev4-responsive-repair-option-analysis:
    purpose: candidate repair option comparison, rejection reasons, and selection status

  ev4-responsive-repair-plan:
    purpose: atomic repair plan and rollback-safe builder steps

  ev4-responsive-css-selector-safety:
    purpose: scoped CSS selector safety and semantic selector checks

  ev4-responsive-accessibility-gate:
    purpose: accessibility reading-order and visibility gate

  ev4-responsive-risk-priority-assessment:
    purpose: categorical risk, priority, confidence, hard-gate, and mitigation assessment without numeric scoring
```

All object schemas should prefer:

```yaml
schema_hardening_defaults:
  additionalProperties: false
  explicit_schema_discriminator: required
  closed_enums_for_statuses: required
  production_claims_forbidden_without_evidence: required
  generated_report_traceability: required_where_applicable
```

---

## 11. Evidence Intake Contract

A real responsive pilot must begin with a machine-checkable evidence intake packet.

Minimum required evidence:

```yaml
required_real_evidence_packet:
  selected_candidate_id: required
  main_ev4_handoff: required
  desktop_baseline: required
  tablet_evidence: required
  mobile_evidence: required
  breakpoint_inventory: required_or_flagged
  privacy_review: required
  packet_origin: real_issue_submission
  issue_reference: required
```

Sample packet safety:

```yaml
sample_packet_rules:
  packet_origin: sample_contract_fixture
  allowed_scope: sample_dry_run_only
  real_pilot_allowed_to_start: false
  may_run_submitted_shadow_mode: false
  sample_markers_must_block_real_mode:
    - SAMPLE in packet_id
    - .sample in file names
    - sample in source refs
    - sha256-sample-placeholder
```

Real submitted mode preflight:

```yaml
real_submitted_preflight:
  packet_origin: real_issue_submission
  issue_reference: required
  packet_id_must_not_contain_sample_marker: true
  source_refs_must_not_contain_sample_marker: true
  payload_identity_hash_must_not_be_placeholder: true
  evidence_file_names_must_not_contain_sample_marker: true
  privacy_review_acknowledged: true
  real_pilot_allowed_to_start: true
  allowed_scope: real_shadow_mode_only
```

---

## 12. Pilot Readiness Contract

Pilot readiness produces one of these statuses:

```text
ready_for_shadow_mode_pilot
partial_ready_with_visible_flags
blocked_missing_evidence
blocked_conflicting_evidence
blocked_privacy_review_missing
blocked_schema_or_semantic_failure
```

Readiness must include:

```yaml
pilot_readiness_report_required_parts:
  readiness_status:
  visible_flags:
  blocking_reasons:
  required_next_action:
  validation_boundary:
  pilot_start_authorization:
```

Rules:

```text
ready_for_shadow_mode_pilot cannot have blocking_reasons.
partial_ready_with_visible_flags must have at least one visible flag and no blocking reasons.
blocked statuses must have at least one blocking reason.
Pilot authorization scope must be shadow_mode_only, shadow_mode_only_with_visible_flags, or not_authorized.
Production, release, live render, export, accessibility pass, and Playwright claims remain false without real evidence.
```

---

## 13. Pilot Run Record Contract

A pilot run record links packet, readiness report, manifest check, and generated artifacts.

Required traceability:

```yaml
pilot_run_record_traceability:
  source_packet_sha256: required
  source_readiness_sha256: required
  generated_at_utc: required
  generator_command: required
  git_ref_or_commit: required
  manifest_check_result: required
  generated_artifacts:
    - artifact_path
    - artifact_type
    - status
    - artifact_sha256
```

Runtime generated files must use `.generated.json` and must not be treated as committed examples.

---

## 14. Risk & Priority Assessment Contract

This project must not use numeric scoring. It uses categorical risk, gate, priority, and verdict logic.

Forbidden:

```text
score
numeric_score
responsive_score
readiness_score
average_score
numeric_score_claimed
average_score_used_to_override_gate
```

Required dimensions:

```yaml
risk_priority_dimensions:
  hard_gates:
    status: pass | fail | not_triggered
    blocking_if_failed: true | false
    gate_weight: hard_blocker | soft_warning

  failure_items:
    severity: blocker | high | medium | minor | note
    priority: P0 | P1 | P2 | P3
    repair_urgency: immediate | next | later | monitor
    evidence_confidence: high | medium | low
    selected_for_repair: true | false
    owner_route:

  repair_risks:
    risk_level: high | medium | low
    desktop_regression_risk: high | medium | low
    accessibility_risk: high | medium | low | not_triggered
    architecture_mutation_risk: high | medium | low
    mitigation_checks:

  aggregate_verdict:
    status:
    required_next_action:
```

Semantic rules:

```text
Hard gate failure cannot produce ready verdict.
Blocker failure cannot produce ready verdict.
Blocker failure must be P0 and immediate.
Blocker failure cannot route to no_action_note.
High architecture mutation risk must route back to main EV4 pipeline.
Low-confidence failure cannot be selected for repair and must request evidence.
Repair risks must reference real failure IDs.
Failure evidence refs must reference known evidence IDs.
High repair risk requires rollback_plan_required.
High desktop regression risk requires desktop_recheck_each_step.
High accessibility risk requires accessibility_gate_required.
High architecture mutation repair risk requires route_back_to_main_pipeline_required.
Sample packet assessments cannot be marked as submitted evidence assessments.
```

---

## 15. CSS Selector Safety Contract

Scoped Custom CSS is allowed only when practical and controlled.

CSS safety rules:

```text
Root section class required.
Target class required.
No unscoped global selector.
No real ID selector unless explicitly justified.
No universal selector unless explicitly justified.
No broad html/body selector.
No unjustified !important.
No production-ready claim from CSS safety alone.
```

Selector parser must not false-positive on:

```text
- class names containing body/html;
- attribute selectors containing # or *;
- literal characters inside attribute values.
```

---

## 16. Accessibility Reading-Order Contract

Accessibility gate runs when order, visibility, or meaningful-content relationships change.

Gate outputs:

```yaml
accessibility_gate_required_parts:
  gate_status:
  applies_because:
  affected_items:
  checks:
  risk_summary:
  required_follow_up:
```

Forbidden:

```text
accessibility_passed claim without validation evidence
hiding meaningful content on mobile
visual-only order changes treated as DOM reading-order pass
```

---

## 17. Builder Repair Contract

Builder-facing repair steps must be atomic and reversible.

Required step shape:

```yaml
builder_repair_step:
  step_id:
  target_node:
  viewport:
  precheck:
    target_node_found:
    active_class_present:
    viewport_selected:
    current_value_recorded:
  action:
    elementor_control_path:
    value_policy:
  postcheck:
    expected_after_state_observed:
    desktop_regression_check_done:
    affected_viewport_rechecked:
  rollback:
    rollback_action:
    rollback_verified:
  validation_evidence_required:
```

Rules:

```text
One atomic action per step.
Desktop must be checked after risky viewport changes.
Rollback must be known before execution.
No bulk repair without convergence gate.
No CSS patch before CSS selector safety check.
```

---

## 18. Smart-Home Connector Pilot

The current pilot target is the smart-home connector section.

Pilot status:

```yaml
smart_home_connector_pilot:
  package: merged
  harness: merged
  intake_issue: Issue #8
  evidence_status: pending_real_evidence
  dry_run: available
  real_shadow_mode: blocked_until_real_submitted_packet
```

Pilot files include:

```text
examples/smart-home-connector/PILOT_CASE_V0_1.md
examples/smart-home-connector/PILOT_MANIFEST.json
examples/smart-home-connector/evidence/EVIDENCE_MANIFEST.template.json
examples/smart-home-connector/intake/SMART_HOME_EVIDENCE_INTAKE_CHECKLIST.md
examples/smart-home-connector/intake/EVIDENCE_INTAKE_PACKET.sample-submitted.json
examples/smart-home-connector/readiness/PILOT_READINESS_REPORT.template.json
examples/smart-home-connector/runs/PILOT_RUN_RECORD.example.json
examples/smart-home-connector/templates/
examples/smart-home-connector/builder/
examples/smart-home-connector/audits/
```

Real pilot cannot start until:

```text
- Issue #8 contains real evidence;
- EVIDENCE_INTAKE_PACKET.submitted.json exists;
- packet_origin is real_issue_submission;
- privacy review is acknowledged;
- sample markers are absent;
- readiness status is ready_for_shadow_mode_pilot or partial_ready_with_visible_flags;
- pilot_start_authorization is not_authorized = false;
- risk-priority assessment can be generated from real artifacts.
```

---

## 19. Release Boundary

Allowed now:

```text
- controlled_builder_handoff
- responsive_repair_plan
- partial_repair_handoff
- validation_ready_state
- contract_validation_only fixtures
- E2E-001 textual fixture validation
- shadow-mode manual pilot package
- machine-checkable evidence intake packet
- pilot readiness gate with visible flags
- persistent pilot readiness report
- pilot dry-run execution record
- sample-vs-real submitted packet safety checks
- risk and priority rubric for repair planning
- parameterized risk-priority assessment validation
- generated risk-priority assessment report
```

Forbidden now:

```text
- production_ready claim
- release_ready claim
- pixel_perfect claim
- export_validated claim
- live_render_validated claim
- accessibility_passed claim
- treating sample submitted packet as real submitted evidence
- numeric score used as readiness evidence
- average score used to override a hard gate
- ready verdict while blocker failure exists
- repair risk without required mitigation checks
```

---

## 20. Immediate Next Work

```yaml
must_do_next:
  - collect real smart-home connector evidence in Issue #8
  - create EVIDENCE_INTAKE_PACKET.submitted.json with packet_origin=real_issue_submission
  - run submitted-shadow-mode only after sample marker and issue reference gates pass
  - start shadow-mode pilot only when readiness is ready or partial_ready_with_visible_flags
  - generate risk-priority assessment only after readiness report and pilot run record exist
```

Optional hardening after real evidence begins:

```yaml
post_real_evidence_hardening:
  - add submitted evidence fixtures derived from real Issue #8 packet with private data removed
  - add pilot execution report template generated from real failure map
  - add builder feedback loop fixture after first manual repair step
  - add visual regression plan if Playwright screenshots become available
  - add export JSON validation plan if Elementor export evidence becomes available
```

---

## 21. Handoff Rule

Final responsive outputs must state their claim level.

Allowed claim levels:

```text
contract_validated
fixture_validated
sample_dry_run_validated
submitted_packet_validated
shadow_mode_pilot_ready
shadow_mode_pilot_completed
builder_feedback_validated
live_render_validated
export_validated
release_candidate
```

A higher claim level may not be used unless the required evidence exists.

---

## 22. Final Master Rule

```text
Never let a convenient repair hide an architecture mutation.
Never let a visual symptom become a CSS cause without evidence.
Never let sample evidence become real submitted evidence.
Never let a numeric score override a blocker.
Never let a responsive fix break desktop silently.
Never claim more than the evidence proves.
```
