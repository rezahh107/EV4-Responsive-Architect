# ACCESSIBILITY_READING_ORDER_GATE

## Purpose

Prevent responsive repair from creating visual/source/keyboard/screen-reader order risks.

## Applies When

```yaml
applies_when:
  - visual_order_changes
  - custom_order_used
  - reverse_direction_used
  - meaningful_content_hidden_or_deferred
  - overlay_interacts_with_meaningful_content
  - duplicate_mobile_section_considered
```

## Required Checks

```yaml
required_checks:
  - meaningful_content_visibility_preserved
  - source_order_risk_recorded
  - keyboard_order_risk_recorded
  - screen_reader_order_risk_recorded
  - tap_target_risk_recorded
  - focus_order_risk_recorded
```

## Outcomes

```yaml
allowed_outcomes:
  - pass
  - pass_with_visible_risk
  - fail_requires_repair
  - fail_requires_main_pipeline_rerun
```
