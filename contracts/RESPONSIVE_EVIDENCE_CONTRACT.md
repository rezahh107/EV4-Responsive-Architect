# RESPONSIVE_EVIDENCE_CONTRACT

## Purpose

Separate raw evidence from derived observation evidence and prevent evidence inflation.

## Evidence Objects

```yaml
evidence_objects:
  input_evidence_ledger:
    purpose: raw assets and sources
  observation_evidence_ledger:
    purpose: derived observations bound to evidence IDs
  evidence_quality_map:
    purpose: define what each evidence item can and cannot support
```

## Evidence Quality Levels

```yaml
evidence_quality_levels:
  L1_static_visual_only:
    can_support:
      - visible_collision
      - visible_clipping
      - visible_overflow_symptom
    cannot_support:
      - exact_css_cause
      - exact_dom_order
      - accessibility_pass

  L2_frontend_visual_with_viewport:
    can_support:
      - viewport_specific_visual_state
    cannot_support:
      - exact_elementor_control

  L3_resize_sweep_or_video:
    can_support:
      - breakpoint_transition_behavior
    cannot_support:
      - project_specific_elementor_setting_without_inspection

  L4_dom_or_export_structure:
    can_support:
      - structure_or_node_identity
    cannot_support:
      - visual_correctness_without_render

  L5_live_render_plus_dom_plus_visual:
    can_support:
      - strongest_validation_state
```

## Rule

A screenshot may support symptoms. It must not be promoted into cause, DOM order, exact setting, or production validation without stronger evidence.
