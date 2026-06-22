# FORBIDDEN_INFERENCE_RULE

## Purpose

Prevent the model from turning visual symptoms into unsupported technical diagnoses.

## Global Rule

```text
A screenshot can show a symptom.
A screenshot alone cannot prove the technical cause.
```

## Forbidden from Static Screenshot Only

```yaml
forbidden_from_static_screenshot_only:
  - exact_dom_order
  - exact_css_property
  - exact_elementor_control
  - exact_breakpoint_value
  - plugin_dependency
  - export_behavior
  - accessibility_pass
  - production_ready_state
```

## Required if Cause is Unclear

```yaml
required_if_cause_unclear:
  cause_status: unknown
  cause_candidates_allowed: true
  repair_must_be_conditional: true
```

## Violation Effect

```yaml
violation_effect:
  severity: blocker
  route_to:
    - /breakpoint-observation
    - /responsive-evidence-ingest-ledger
```
