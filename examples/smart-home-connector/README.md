# Smart Home Connector — Pilot Example

This directory will host the first shadow-mode pilot case for EV4 Responsive Architect.

## Purpose

Validate whether the responsive repair plan is builder-usable before investing in heavy automation.

## Expected Inputs

```yaml
expected_inputs:
  - completed_main_EV4_handoff
  - desktop_baseline_screenshot
  - tablet_screenshot
  - mobile_screenshot
  - breakpoint_inventory_lock
```

## Expected Outputs

```yaml
expected_outputs:
  - responsive_failure_map
  - repair_ownership_routing
  - repair_option_analysis
  - responsive_repair_plan
  - final_audit_lite
```

## Boundary

This example must not claim live Elementor validation or production readiness unless real evidence is added.
