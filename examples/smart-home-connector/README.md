# Smart Home Connector — Pilot Example

Status: shadow_mode_manual_pilot_pack
Production status: not_production_ready

This directory hosts the first vertical-slice pilot case for EV4 Responsive Architect.

## Purpose

Validate whether the responsive repair plan is builder-usable before investing in heavy automation.

The pilot does not prove live Elementor rendering, export JSON validation, Playwright visual regression, accessibility pass, exact pixel matching, or production readiness.

## Files

```text
PILOT_CASE_V0_1.md
PILOT_MANIFEST.json
evidence/EVIDENCE_MANIFEST.template.json
templates/RESPONSIVE_FAILURE_MAP.template.md
templates/REPAIR_OPTION_ANALYSIS.template.md
builder/BUILDER_REPAIR_CHECKLIST.template.md
audits/FINAL_AUDIT_LITE.template.md
```

## Expected Inputs

```yaml
expected_inputs:
  - completed_main_EV4_handoff
  - desktop_baseline_screenshot_or_declared_equivalent
  - tablet_screenshot_or_declared_equivalent
  - mobile_screenshot_or_declared_equivalent
  - breakpoint_inventory_lock_or_user_declaration
```

## Expected Outputs

```yaml
expected_outputs:
  - evidence_manifest
  - responsive_failure_map
  - repair_ownership_routing
  - repair_option_analysis
  - responsive_repair_selection
  - builder_repair_checklist
  - final_audit_lite
```

## Pilot Boundary

```text
This example is a shadow-mode manual pilot.
It must not claim live Elementor validation or production readiness unless real evidence is added later.
```

## Start Prompt

Use:

```text
prompts/PILOT_SMART_HOME_CONNECTOR_STARTER.md
```
