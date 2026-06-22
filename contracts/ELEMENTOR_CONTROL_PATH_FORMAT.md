# ELEMENTOR_CONTROL_PATH_FORMAT

## Purpose

Make builder instructions executable in Elementor UI language.

## Required Shape

```yaml
elementor_control_path:
  schema: ev4-elementor-control-path@1.0.0
  target_node_id:
  structure_label:
  class_name:
  editor_area:
    enum:
      - Content
      - Layout
      - Style
      - Advanced
      - MotionEffects
      - CustomCSS
      - Unknown
  control_group:
  control_name:
  viewport_scope:
  value_policy:
    enum:
      - exact_value_from_evidence
      - relative_adjustment
      - builder_select_best_fit
      - verify_current_then_apply
      - unknown_do_not_apply
  value_source:
    enum:
      - breakpoint_inventory_lock
      - design_system_variable
      - user_declaration
      - frontend_evidence
      - builder_verification_required
  fallback_semantic_instruction:
  rollback_instruction:
```

## Builder Instruction Must Include

```yaml
builder_instruction_must_include:
  - node
  - active_class
  - viewport
  - tab_or_panel
  - control
  - value_policy
  - validation_check
  - rollback
```
