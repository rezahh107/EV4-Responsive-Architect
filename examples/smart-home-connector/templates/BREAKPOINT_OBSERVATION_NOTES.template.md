# Breakpoint Observation Notes — Template

Pilot: smart-home-connector-v0.1  
Status: template_waiting_for_viewport_evidence

## Observation Rule

Record symptoms only. Do not claim CSS cause, DOM order, Elementor control, or exact breakpoint from screenshot-only evidence.

```yaml
observations:
  - observation_id: RSP-OBS-001
    viewport: mobile
    viewport_width_px: TODO
    source_evidence_id: EVD-MOBILE-001
    affected_visual_group: TODO
    affected_node_id: TODO_or_unknown
    visible_symptom: TODO_symptom_only
    cause_status: unknown
    cause_candidates:
      - TODO_candidate_only
    forbidden_inference_check:
      exact_css_cause_claimed: false
      exact_dom_order_claimed: false
      exact_elementor_control_claimed: false
      accessibility_pass_claimed: false
```

## Carry Forward

```yaml
observation_unknowns:
  - unknown_id: TODO
    description: TODO
    blocks_repair_selection: TODO_yes_no
```
