# EV4 Responsive Architect — Master Project Specification

Version: 0.3.0-responsive-tree-architecture-active  
Status: responsive_tree_architecture_active_on_main  
Production status: not_production_ready  
Language: Persian reports, English technical identifiers  
Target platform: Elementor V4  
Execution model: classification-first, route-gated, builder-handoff-oriented, evidence-bounded

---

## 0. Executive Summary

`EV4 Responsive Architect` is now a responsive-tree architecture system on `main`.

Primary mode:

```text
Primary mode: design_to_responsive_tree
Secondary mode: responsive_repair
```

The system runs after the main `EV4 Architect` pipeline has produced an approved desktop/section architecture and build tree. Its job is to classify the relationship between desktop and responsive evidence, choose a safe Elementor route, produce a builder handoff, and plan validation without overstating evidence.

---

## 1. Active Source of Truth

```yaml
active_refactor_doc:
  - docs/RESPONSIVE_TREE_ARCHITECTURE_REFACTOR_v0.3.0.md
active_contracts:
  - contracts/EV4_RESPONSIVE_TREE_ARCHITECTURE_CONTRACT.md
  - contracts/EV4_VIEWPORT_RELATIONSHIP_CLASSIFICATION_CONTRACT.md
  - contracts/EV4_RESPONSIVE_STRATEGY_ROUTING_CONTRACT.md
  - contracts/EV4_VIEWPORT_DISPLAY_CONTRACT.md
  - contracts/EV4_RESPONSIVE_HANDOFF_EXPORT_CONTRACT.md
active_schema:
  - schemas/ev4-responsive-output.schema.json
active_validation:
  - validation/e2e/run_responsive_tree_architecture_refactor_check.py
  - validation/e2e/run_submitted_packet_eligibility_gate_check.py
  - validation/e2e/run_task_quality_gate_check.py
controlled_use_docs:
  - docs/15_CONTROLLED_USE_READINESS_SNAPSHOT.md
  - docs/16_CONTROLLED_MANUAL_FIRST_RUN_GUIDE.md
  - docs/17_VALIDATION_COMMAND_INDEX.md
  - docs/18_GUARDED_HANDOFF_PACK.md
  - docs/19_REPOSITORY_DRIFT_AUDIT_RTAQ_0004.md
  - docs/20_ACTIVE_CONTRACT_SCHEMA_VALIDATOR_INDEX.md
  - docs/21_QUEUE_REFRESH_AUDIT_RTAQ_0005.md
  - docs/22_MASTER_STATUS_DRIFT_CLOSURE_RTAQ_0006.md
  - docs/23_EVIDENCE_BOUND_DOCUMENTATION_GUARD_RTAQ_0008.md
  - docs/24_AUTOMATION_QUALITY_GATE_ENFORCEMENT_AUDIT_RTAQ_0009.md
active_queue:
  - planning/EV4_ROLLING_QUEUE.json
active_run_ledger:
  - planning/EV4_RUN_LEDGER.json
```

---

## 2. Evidence Boundary

```text
- The upstream EV4 packet route seed is advisory.
- Desktop-only evidence must not be treated as tablet/mobile evidence.
- Meaningful content must not be removed from a viewport without explicit authorization.
- Route selection is planning evidence, not validation evidence.
- CI success or a merged PR is repository evidence only, not responsive correctness evidence.
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

The automatic workflow installs validation dependencies and runs:

```bash
python validation/e2e/run_responsive_tree_architecture_refactor_check.py
```

The checker covers:

```text
required responsive-tree docs/contracts/stages
required route vocabulary terms
ev4-responsive-output@0.3.0 schema validity
valid route fixture acceptance
invalid fixture rejection
builder handoff step integrity
route/mode consistency
delegated RTAQ queue, ledger, task-quality, and submitted-packet eligibility checks
```

Additional repository-check validators are active in the bounded RTAQ path:

```bash
python validation/e2e/run_submitted_packet_eligibility_gate_check.py
python validation/e2e/run_task_quality_gate_check.py
```

The responsive-tree checker also delegates these queue-control validators:

```bash
python validation/e2e/run_rolling_queue_check.py
python validation/e2e/run_run_ledger_check.py
```

All of these active and delegated validators harden repository contracts, submitted-packet eligibility, task quality-gate structure, queue discipline, and ledger discipline. They do not prove live render correctness, export validation, accessibility pass, pixel accuracy, production readiness, or release readiness.

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
```
