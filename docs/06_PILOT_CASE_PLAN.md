# 06 — Pilot Case Plan

## Purpose

Run a vertical-slice pilot before building heavy automation.

```yaml
pilot_case_v0_1:
  section: smart_home_connector
  mode: shadow_mode_manual
  production_ready: false
```

## Why This Pilot Exists

E2E-001 proves contract and fixture validation only. The pilot tests a more practical question:

```text
Can a builder actually follow the responsive repair workflow without the model redesigning the section?
```

## Run Only

```yaml
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
```

## Skip for Pilot

```yaml
skip_for_pilot:
  - Playwright_automation
  - multi_run_convergence
  - full_handoff_export
  - production_release_gate
  - export_import_roundtrip
```

Schema validation remains allowed for supplied pilot JSON artifacts.

## Required Pilot Files

```yaml
required_pilot_files:
  - examples/smart-home-connector/PILOT_CASE_V0_1.md
  - examples/smart-home-connector/PILOT_MANIFEST.json
  - examples/smart-home-connector/evidence/EVIDENCE_MANIFEST.template.json
  - examples/smart-home-connector/templates/RESPONSIVE_FAILURE_MAP.template.md
  - examples/smart-home-connector/templates/REPAIR_OPTION_ANALYSIS.template.md
  - examples/smart-home-connector/builder/BUILDER_REPAIR_CHECKLIST.template.md
  - examples/smart-home-connector/audits/FINAL_AUDIT_LITE.template.md
  - prompts/PILOT_SMART_HOME_CONNECTOR_STARTER.md
```

## Required User Evidence Before Diagnosis

```yaml
required_user_evidence_before_diagnosis:
  - completed_main_EV4_handoff_or_authorized_payload_excerpt
  - desktop_baseline_screenshot_or_declared_equivalent
  - tablet_screenshot_or_declared_equivalent
  - mobile_screenshot_or_declared_equivalent
  - breakpoint_inventory_source_or_user_declaration
```

If these inputs are missing, the pilot must output a missing-input checklist instead of diagnosing.

## Success Criteria

```yaml
pilot_success_criteria:
  - builder_can_follow_steps_without_extra_interpretation
  - each_step_has_rollback
  - desktop_regression_check_is_clear
  - no_architecture_mutation_occurs
  - unknowns_are_visible
  - repair_option_analysis_prevents_premature_selection
  - connector_decoration_status_is_inherited_from_main_pipeline
```

## Failure Criteria

```yaml
pilot_failure_criteria:
  - architecture_mutation_veto_triggered_without_route
  - screenshot_only_claims_exact_css_or_dom_cause
  - builder_step_lacks_rollback
  - meaningful_content_hidden_to_fit_mobile
  - desktop_regression_not_checked
  - repair_selection_occurs_without_option_analysis
```

## Validation Boundary

```text
The pilot validates builder usability and workflow discipline only.
It does not validate production readiness, live Elementor rendering, export JSON, Playwright visual regression, exact pixel matching, or full accessibility.
```
