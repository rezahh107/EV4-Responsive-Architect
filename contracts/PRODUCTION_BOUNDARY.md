# PRODUCTION_BOUNDARY

## Purpose

Prevent over-claiming validation that has not occurred.

## Allowed Outputs

```text
controlled_builder_handoff
responsive_repair_plan
partial_repair_handoff
audited_responsive_handoff
validation_ready_state
```

## Forbidden Claims Without Matching Evidence

```text
production_ready
release_ready
pixel_perfect
export_validated
live_render_validated
accessibility_passed
```

## Required Evidence for Production-Ready Claim

```yaml
production_readiness_required_evidence:
  - live_elementor_rendering
  - real_elementor_export_json_or_EDIS_validation
  - browser_device_QA
  - responsive_QA_across_locked_breakpoints
  - accepted_visual_tolerance_or_exact_pixel_matching
  - accessibility_semantics_decisions
  - keyboard_or_focus_order_review_when_order_changes
  - no_blocker_or_high_unresolved_findings
```
