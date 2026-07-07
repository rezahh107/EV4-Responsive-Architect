# EV4 Responsive Architect — Master Project Specification

Version: 0.3.0-responsive-tree-architecture-active  
Status: responsive_tree_architecture_active_on_main  
Production status: not_production_ready  
Language: Persian reports, English technical identifiers  
Target platform: Elementor V4  
Execution model: classification-first, route-gated, builder-handoff-oriented, catalog-backed, evidence-bounded

---

## 0. Executive Summary

`EV4 Responsive Architect` is now a responsive-tree architecture system on `main`.

Primary mode:

```text
Primary mode: design_to_responsive_tree
Secondary mode: responsive_repair
```

The system runs after the main `EV4 Architect` pipeline has produced an approved desktop/section architecture and build tree. Its job is to classify the relationship between desktop and responsive evidence, choose a safe Elementor route, produce a builder handoff, and plan validation without overstating evidence.

Automation objective selection is controlled by the Work Package Catalog, not by the retired rolling queue execution driver.

---

## 1. Active Source of Truth

```yaml
active_refactor_doc:
  - docs/RESPONSIVE_TREE_ARCHITECTURE_REFACTOR_v0.3.0.md
active_contracts:
  - contracts/MAIN_PIPELINE_HANDOFF_INPUT_CONTRACT.md
  - contracts/BUILDER_TO_RESPONSIVE_INPUT_BOUNDARY.md
  - contracts/EV4_RESPONSIVE_TREE_ARCHITECTURE_CONTRACT.md
  - contracts/EV4_VIEWPORT_RELATIONSHIP_CLASSIFICATION_CONTRACT.md
  - contracts/EV4_RESPONSIVE_STRATEGY_ROUTING_CONTRACT.md
  - contracts/EV4_VIEWPORT_DISPLAY_CONTRACT.md
  - contracts/EV4_RESPONSIVE_HANDOFF_EXPORT_CONTRACT.md
active_schema:
  - schemas/ev4-responsive-output.schema.json
  - schemas/ev4-builder-responsive-input.schema.json
  - schemas/ev4-automation-control-state.schema.json
  - schemas/ev4-automation-work-package-catalog.schema.json
active_validation:
  - validation/e2e/run_responsive_tree_architecture_refactor_check.py
  - validation/e2e/run_submitted_packet_eligibility_gate_check.py
  - validation/e2e/run_submitted_packet_readiness_dry_run.py
  - validation/e2e/run_evidence_intake_check.py
  - validation/e2e/run_evidence_intake_submitted_mode_path_check.py
  - validation/e2e/run_evidence_intake_submitted_payload_hash_check.py
  - validation/e2e/run_evidence_intake_fixture_matrix_check.py
  - validation/e2e/run_pilot_readiness_check.py
  - validation/e2e/run_pilot_readiness_boundary_check.py
  - validation/e2e/run_issue_8_preflight_boundary_check.py
  - validation/e2e/run_issue_to_packet_bridge_check.py
  - validation/e2e/run_builder_responsive_input_boundary_check.py
  - validation/e2e/run_task_quality_gate_check.py
  - validation/e2e/run_rtaq_ssot_guard_check.py
  - validation/e2e/run_status_merged_foundation_guard_check.py
  - validation/e2e/run_automation_control_state_check.py
  - validation/e2e/run_automation_work_package_catalog_check.py
automation_control_state:
  - planning/EV4_AUTOMATION_CONTROL_STATE.json
work_package_catalog:
  - planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json
historical_rolling_queue_archive:
  - planning/EV4_ROLLING_QUEUE.json
active_run_ledger:
  - planning/EV4_RUN_LEDGER.json
primary_validate_chain_index:
  - docs/17_VALIDATION_COMMAND_INDEX.md
active_contract_schema_validator_index:
  - docs/20_ACTIVE_CONTRACT_SCHEMA_VALIDATOR_INDEX.md
```

---

## 2. Evidence Boundary

```text
- The upstream EV4 packet route seed is advisory.
- Desktop-only evidence must not be treated as tablet/mobile evidence.
- Meaningful content must not be removed from a viewport without explicit authorization.
- Route selection is planning evidence, not validation evidence.
- CI success or a merged PR is repository evidence only, not responsive correctness evidence.
- Catalog completion or Work Package completion is not evidence validation.
- Higher-readiness claims remain blocked without matching real evidence.
- Issue #8 remains evidence-pending until a real submitted packet validates.
- The real pilot remains blocked until submitted packet and readiness gates pass.
```

---

## 3. Required Inputs

```yaml
required_inputs:
  ev4_responsive_start_packet:
    schema: ev4-responsive-start-packet@1.0.0
    required: true
  approved_desktop_tree:
    required: true
  responsive_design_evidence:
    mobile_mockup: required_or_explicitly_absent
    tablet_mockup: required_or_explicitly_absent
  target_breakpoint_scope:
    required: true
  viewport_policy:
    required_if_variant_possible: true
```

---

## 4. Classification and Routing

```yaml
section_relationship:
  classification:
    - same_section_adaptation
    - viewport_specific_variant
    - hybrid_split
    - unresolved_requires_designer_input

responsive_strategy_route:
  - same_tree_responsive_overrides
  - viewport_specific_variant_tree
  - hybrid_split_architecture
  - blocked_pending_input
```

Route mapping:

```yaml
same_section_adaptation: same_tree_responsive_overrides
viewport_specific_variant: viewport_specific_variant_tree
hybrid_split: hybrid_split_architecture
unresolved_requires_designer_input: blocked_pending_input
```

---

## 5. Responsive Pipeline

```text
/responsive-start-packet-ingest
/responsive-design-intake
/viewport-source-ledger
/section-relationship-classification
/elementor-strategy-routing
/responsive-tree-ownership-contract
/same-tree-responsive-derivation
/viewport-tree-architecture
/composite-responsive-plan
/display-and-breakpoint-contract
/content-accessibility-duplication-gate
/responsive-builder-handoff
/responsive-validation-plan
/responsive-final-review
/responsive-output-package
```

---

## 6. Current Machine-Checked Chain

The automatic workflow installs validation dependencies and runs the primary Validate chain listed in:

```text
docs/17_VALIDATION_COMMAND_INDEX.md
docs/20_ACTIVE_CONTRACT_SCHEMA_VALIDATOR_INDEX.md
```

The checker coverage includes:

```text
required responsive-tree docs/contracts/stages
required route vocabulary terms
ev4-responsive-output@0.3.0 schema validity
valid route fixture acceptance
invalid fixture rejection
builder handoff step integrity
Builder/Project Gate to Responsive intake boundary checks
submitted-packet eligibility failure modes
submitted packet dry-run readiness behavior
submitted-mode path, payload-hash, fixture-matrix, and Issue #8 bridge guards
pilot readiness and pilot boundary guards
catalog-backed Work Package selection discipline
retired rolling-queue archive discipline
run-ledger, task-quality, RTAQ SSOT, STATUS, and automation-control checks
```

All active validators harden repository contracts, submitted-packet eligibility, task quality-gate structure, catalog-selection discipline, queue archive discipline, ledger discipline, boundary docs, and STATUS/workflow parity. They do not prove live render correctness, export validation, accessibility pass, pixel accuracy, production readiness, or release readiness.

The legacy run-ledger workflow is manual-only during this refactor path.

---

## 7. Merged Foundation

```yaml
merged_foundation:
  - PR #59 bookkeeping sync
  - PR #60 responsive tree architecture refactor
  - PR #61 responsive output schema and route fixtures
  - PR #62 responsive output negative validation fixtures
  - PR #63 validator hardening and restored coverage checks
  - PR #65 post-refactor active queue reset
  - PR #67 submitted packet eligibility gate hardening
  - PR #69 controlled-use readiness snapshot and first-run guide
  - PR #71 guarded handoff pack and drift audit
  - PR #73 queue refresh audit and next bounded task plan
  - PR #75 master spec and status drift closure
  - PR #77 validator and command index hardening
```

---

## 8. Final Master Rule

```text
Classify first.
Route second.
Generate tree or overrides third.
Package builder handoff fourth.
Plan validation without claiming validation fifth.
Select automation work only from the Work Package Catalog.
```
