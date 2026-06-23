# EV4 Responsive Architect — Master Project Specification

Version: 0.2.1-p0-system-hardening  
Status: p0_system_hardening_in_pull_request  
Production status: not_production_ready  
Language: Persian reports, English technical identifiers  
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

```yaml
completed_layers:
  contract_hardening: merged
  schema_hardening: merged_to_main
  E2E_001_textual_validation: merged
  smart_home_connector_pilot_package: merged
  pilot_harness_hardening: merged
  evidence_intake_validation: merged
  pilot_readiness_engine: merged
  pilot_dry_run_execution_layer: merged
  sample_vs_real_safety_hardening: merged
  risk_priority_assessment_engine: merged
  master_spec_sync: merged

active_layer:
  p0_system_hardening:
    status: in_pull_request
    purpose:
      - close evidence capability enums
      - add conflict resolution protocol
      - add responsive failure-map validator
      - add responsive final-audit validator
      - add handoff ingest failure policy
      - add fast-path eligibility checklist
```

The system is ready to receive real smart-home connector evidence only after the P0 hardening layer is merged. It is not production-ready and must not claim real Elementor validation until real runtime/export evidence exists.

---

## 2. Non-Negotiable Boundaries

The system must not:

```text
- change the selected architecture without routed EV4 partial rerun
- redesign during responsive repair
- re-score architecture candidates
- re-run architecture recommendation
- hide meaningful content on any viewport
- assume cards are clickable
- assume Dynamic Loop from repeated items alone
- assume mobile connector behavior without evidence
- invent exact breakpoints, colors, typography, spacing, coordinates, or asset dimensions
- write unscoped global CSS
- claim live Elementor rendering unless live rendering evidence exists
- claim export JSON or EDIS validation unless real export evidence exists
- claim exact pixel matching unless measured and validated
- claim accessibility pass unless accessibility validation evidence exists
- claim production readiness without release-gate evidence
- treat sample submitted packets as real submitted evidence
- use numeric score, average score, or readiness score to override any hard gate
- let screenshot evidence claim CSS cause, DOM structure, computed style, accessibility pass, or production readiness
```

---

## 3. Source-of-Truth Hierarchy

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
  11: Conflict_Resolution_Record
  12: Risk_Priority_Assessment
  13: Builder_Feedback_Loop_Evidence
```

If sources conflict, the conflict must be reported before continuing. Unresolved conflicts must block downstream execution unless a degraded-mode policy explicitly allows continuation with visible flags.

---

## 4. Evidence Discipline

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

Evidence items must carry closed capability fields:

```yaml
evidence_item_required_shape:
  evidence_id:
  evidence_type:
  capture_source:
  viewport:
  viewport_width:
  quality_level:
  confidence_cap:
  can_support: closed_enum
  cannot_support: closed_enum
  downstream_allowed_use:
  known_limitations:
```

Visual screenshot evidence may support only visible symptoms such as visible collision, visible overflow, visible clipping, visible spacing/alignment/order symptoms, and viewport-specific visual state. It must not claim computed CSS, DOM structure, exported structure, exported control value, exact breakpoint value, accessibility pass, or production readiness.

---

## 5. Conflict Resolution Protocol

Conflict records use:

```text
ev4-responsive-conflict-resolution@1.0.0
```

Unresolved conflicts must use:

```yaml
conflict_status: unresolved_blocking
resolution_action: block_downstream_until_resolved
downstream_effect: blocked
```

Resolved conflicts must select the highest-priority available source from the source-of-truth hierarchy and record the losing source references.

---

## 6. Execution Modes and Fast Path

Fast-path is allowed only if `ev4-responsive-fast-path-eligibility@1.0.0` returns `eligible`.

```yaml
fast_path_eligibility_criteria:
  affected_viewport_count: <= 1
  custom_css_required: false
  meaningful_visibility_change: false
  content_order_change: false
  overlay_or_connector_risk: false
  architecture_mutation_risk: false
  cascade_risk: low
  unknowns_required_for_repair: false
  accessibility_gate_triggered: false
```

Fast-path may reduce the number of stages; it must not reduce evidence requirements for claims.

---

## 7. Responsive Pipeline

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

Conditional stages must define dependency triggers and cannot be silently skipped.

---

## 8. Current Machine-Checked Chain

Current CI commands:

```bash
python validation/schema_validator/validate_schemas.py
python validation/e2e/run_e2e_001.py
python validation/e2e/run_pilot_manifest_check.py
python validation/e2e/run_evidence_intake_check.py
python validation/e2e/run_pilot_readiness_check.py
python validation/e2e/run_pilot_dry_run_check.py
python validation/e2e/run_risk_priority_check.py
python validation/e2e/run_p0_system_hardening_check.py
```

Required negative paths include:

```text
- invalid JSON schema payloads must fail
- invalid CSS selector safety payloads must fail
- screenshot evidence claiming CSS/DOM/computed support must fail
- unresolved conflict continuing downstream must fail
- unresolved repair-critical unknown in failure map must fail
- final audit handoff with blockers must fail
- schema-failed handoff continuing silently must fail
- non-trivial repair marked fast-path eligible must fail
- sample packet in submitted-shadow-mode must fail
- blocked intake packet must not produce authorized run record
- numeric score fields must fail
- hard gate failure with ready verdict must fail
- blocker failure with ready verdict must fail
- unknown evidence or failure refs must fail
- high repair risk without mitigation must fail
```

---

## 9. Active Schema Inventory

```yaml
active_schemas:
  ev4-responsive-stage-anchor: stage transition authorization
  ev4-responsive-main-input: main EV4 handoff normalization and authorization
  ev4-responsive-handoff-ingest-decision: handoff ingest failure/block/degraded-mode decision
  ev4-responsive-payload-identity: payload hash and source identity tracking
  ev4-responsive-evidence-ingest: raw evidence ledger payloads
  ev4-responsive-evidence-intake-packet: submitted evidence packet with closed evidence capability enums
  ev4-responsive-conflict-resolution: source conflict decision and downstream block/continue behavior
  ev4-responsive-pilot-manifest: pilot sequence, files, conditional stages, lite gates, and stop conditions
  ev4-responsive-pilot-readiness: readiness verdict, visible flags, blocking reasons, validation boundary, and pilot authorization
  ev4-responsive-pilot-run-record: dry-run or submitted shadow-mode run record with hashes and artifact traceability
  ev4-responsive-fast-path-eligibility: machine-checkable triage fast-path decision
  ev4-responsive-failure-map: responsive failure mapping, unknown gate, and mutation risk route
  ev4-responsive-repair-option-analysis: candidate repair option comparison, rejection reasons, and selection status
  ev4-responsive-repair-plan: atomic repair plan and rollback-safe builder steps
  ev4-responsive-css-selector-safety: scoped CSS selector safety and semantic selector checks
  ev4-responsive-accessibility-gate: accessibility reading-order and visibility gate
  ev4-responsive-final-audit: final responsive audit and controlled handoff gate
  ev4-responsive-risk-priority-assessment: categorical risk, priority, confidence, hard-gate, and mitigation assessment without numeric scoring
```

---

## 10. Handoff Ingest Failure Policy

Handoff ingest uses:

```text
ev4-responsive-handoff-ingest-decision@1.0.0
```

Allowed routes:

```yaml
accepted:
  downstream_allowed: true
  required_next_action: start_responsive_intake
blocked_missing_payload:
  downstream_allowed: false
  required_next_action: request_complete_main_handoff
blocked_schema_failure:
  downstream_allowed: false
  required_next_action: request_complete_main_handoff
continue_degraded_with_visible_flags:
  downstream_allowed: true
  visible_flags: required
  required_next_action: continue_degraded_with_flags
routed_to_main_pipeline:
  downstream_allowed: false
  required_next_action: route_back_to_main_pipeline
```

No invalid handoff may silently continue.

---

## 11. Failure Map and Final Audit

Failure map uses:

```text
ev4-responsive-failure-map@1.0.0
```

It must block when repair-critical unknowns are unresolved and must route back to the main pipeline when architecture mutation risk is high.

Final audit uses:

```text
ev4-responsive-final-audit@1.0.0
```

A controlled handoff requires all audit checks to pass and no blocking reasons.

---

## 12. Evidence Intake, Readiness, Run Record, and Risk

A real responsive pilot must begin with `ev4-responsive-evidence-intake-packet@1.1.0`.

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

Readiness must include readiness status, visible flags, blocking reasons, validation boundary, and pilot authorization. Pilot run records must include packet hash, readiness hash, manifest check result, generator command, generated timestamp, git ref, and artifact hashes. Risk-priority assessment must remain categorical and must not generate numeric scores.

---

## 13. Builder Repair Contract

Builder-facing repair steps must be atomic and reversible.

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

---

## 14. Release Boundary

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
- P0 system hardening validation
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
- screenshot evidence claiming CSS cause, DOM structure, computed style, accessibility pass, or production readiness
```

---

## 15. Immediate Next Work

```yaml
must_do_next_after_p0_merge:
  - collect real smart-home connector evidence in Issue #8
  - create EVIDENCE_INTAKE_PACKET.submitted.json with packet_origin=real_issue_submission
  - run submitted-shadow-mode only after sample marker and issue reference gates pass
  - start shadow-mode pilot only when readiness is ready or partial_ready_with_visible_flags
  - generate failure map, final audit, and risk-priority assessment from real artifacts
```

---

## 16. Final Master Rule

```text
Never let a convenient repair hide an architecture mutation.
Never let a visual symptom become a CSS cause without evidence.
Never let sample evidence become real submitted evidence.
Never let a numeric score override a blocker.
Never let a responsive fix break desktop silently.
Never claim more than the evidence proves.
```
