# CSS_SELECTOR_SAFETY

## Purpose

Validate Custom CSS repair selectors before and after builder application.

## Runs When

```yaml
runs_when:
  - selected_repair_uses_custom_css
```

## Selector Requirements

```yaml
selector_requirements:
  must_include_project_root_class: true
  must_include_target_node_class: true
  must_not_use_global_element_selector: true
  must_not_use_unscoped_elementor_internal_selector: true
  must_not_use_id_selector: true
  must_not_use_important_unless_justified: true
```

## Breakpoint Wrapping

```yaml
breakpoint_wrapping:
  required_if_viewport_specific: true
  breakpoint_source_must_be:
    - breakpoint_inventory_lock
    - elementor_export_json
    - user_declaration
  forbidden:
    - invented_breakpoint
    - assumed_default_without_label
```

## CSS Must Not

```text
- use global html/body rules;
- use broad unscoped Elementor internals;
- generate meaningful text;
- hide meaningful content;
- create card clickability;
- invent connector mobile behavior;
- use !important without justification.
```
