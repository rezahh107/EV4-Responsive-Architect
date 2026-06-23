# Builder Repair Checklist — Template

Pilot: smart-home-connector-v0.1  
Status: template_waiting_for_selected_repair

## Builder Rule

Apply one atomic step at a time. After each step, check desktop before continuing.

Do not apply any step if:

```text
- the target node cannot be found;
- the active class is missing;
- the viewport control is not available;
- desktop changes unexpectedly;
- the step would hide meaningful content;
- the step requires changing the approved build tree.
```

## Step Format

```yaml
repair_steps:
  - step_id: RSP-STEP-001
    failure_id: RSP-F-001
    selected_option_id: RSP-OPT-001A
    target_node_id: TODO_NODE_ID
    target_structure_label: TODO_LABEL
    active_class_name: TODO_CLASS_WITHOUT_DOT
    viewport_scope: mobile
    single_repair_intent: TODO_ONE_INTENT_ONLY
    elementor_control_path:
      editor_area: TODO_Content_Layout_Style_Advanced_CustomCSS
      control_group: TODO_GROUP
      control_name: TODO_CONTROL
      value_policy: verify_current_then_apply
      value_source: builder_verification_required
    before_state_description: TODO
    expected_after_state: TODO
    rollback_action: TODO_REVERT_THIS_STEP_ONLY
    desktop_check_required: true
    cascade_check_required: true
    validation_evidence_required:
      - frontend_or_editor_screenshot_after
      - builder_confirmation_sentence
```

## Confirmation Sentence

After executing a checkpoint, builder must reply with:

```text
Executed RSP-STEP-___, desktop checked, no unexpected regression, evidence attached.
```

If there is unexpected behavior:

```text
Executed RSP-STEP-___, unexpected behavior found: ___, rollback needed: yes/no.
```

## Desktop Regression Check

```yaml
desktop_regression_check:
  meaningful_text_visibility: TODO_pass_fail_unknown
  feature_card_group_integrity: TODO_pass_fail_unknown
  visual_core_presence: TODO_pass_fail_unknown
  connector_layer_containment: TODO_pass_fail_unknown
  horizontal_overflow: TODO_none_present_unknown
  unexpected_desktop_reflow: TODO_yes_no_unknown
```
