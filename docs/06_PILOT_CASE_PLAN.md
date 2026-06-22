# 06 — Pilot Case Plan

## Purpose

Run a vertical-slice pilot before building heavy automation.

```yaml
pilot_case_v0_1:
  section: smart_home_connector
  mode: shadow_mode_manual
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
  - full_schema_validator
  - Playwright_automation
  - multi_run_convergence
  - full_handoff_export
```

## Success Criteria

```yaml
pilot_success_criteria:
  - builder_can_follow_steps_without_extra_interpretation
  - each_step_has_rollback
  - desktop_regression_check_is_clear
  - no_architecture_mutation_occurs
  - unknowns_are_visible
  - repair_option_analysis_prevents_premature_selection
```
