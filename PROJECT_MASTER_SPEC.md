# EV4 Responsive Architect — Master Project Specification

Version: 0.3.0-responsive-tree-architect-refactor  
Status: responsive_tree_architecture_refactor_in_pull_request  
Production status: not_production_ready  
Language: Persian reports, English technical identifiers  
Target platform: Elementor V4  
Execution model: classification-first, route-gated, builder-handoff-oriented, evidence-bounded

---

## 0. Executive Summary

`EV4 Responsive Architect` is now a responsive-tree architecture system.

It runs after the main `EV4 Architect` pipeline has produced an approved desktop/section architecture and build tree. The primary job is to decide how a responsive design should be represented in Elementor.

```text
Primary mode: design_to_responsive_tree
Secondary mode: responsive_repair
```

Repair mode is used only when a responsive implementation already exists and evidence shows a real problem.

---

## 1. Active Refactor Source of Truth

```yaml
active_refactor_doc:
  - docs/RESPONSIVE_TREE_ARCHITECTURE_REFACTOR_v0.3.0.md
active_contracts:
  - contracts/EV4_RESPONSIVE_TREE_ARCHITECTURE_CONTRACT.md
  - contracts/EV4_VIEWPORT_RELATIONSHIP_CLASSIFICATION_CONTRACT.md
  - contracts/EV4_RESPONSIVE_STRATEGY_ROUTING_CONTRACT.md
  - contracts/EV4_VIEWPORT_DISPLAY_CONTRACT.md
  - contracts/EV4_RESPONSIVE_HANDOFF_EXPORT_CONTRACT.md
active_validation:
  - validation/e2e/run_responsive_tree_architecture_refactor_check.py
```

---

## 2. Non-Negotiable Boundaries

```text
- The upstream EV4 packet route seed is advisory.
- Desktop-only evidence must not be treated as tablet/mobile evidence.
- Meaningful content must not be removed from a viewport without explicit authorization.
- Route selection is planning evidence, not validation evidence.
- CI success or a merged PR is not responsive correctness evidence.
- No production, release, live render, export, pixel, or accessibility validation claim is allowed without matching real evidence.
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

## 4. Relationship Classification

```yaml
section_relationship:
  classification:
    - same_section_adaptation
    - viewport_specific_variant
    - hybrid_split
    - unresolved_requires_designer_input
```

---

## 5. Responsive Strategy Routes

```yaml
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

## 6. Responsive Pipeline

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

## 7. Output Families

```yaml
outputs:
  responsive_strategy_decision:
  same_tree_responsive_derivation:
  viewport_tree_architecture:
  composite_responsive_plan:
  display_and_breakpoint_contract:
  content_accessibility_duplication_gate:
  responsive_builder_handoff:
  responsive_validation_plan:
  responsive_final_review:
  responsive_output_package:
```

---

## 8. Current Machine-Checked Chain

The automatic workflow now runs:

```bash
python validation/schema_validator/validate_schemas.py
python validation/e2e/run_responsive_tree_architecture_refactor_check.py
```

The legacy run-ledger workflow is manual-only during this refactor.

---

## 9. Final Master Rule

```text
Classify first.
Route second.
Generate tree or overrides third.
Package builder handoff fourth.
Plan validation without claiming validation fifth.
```
