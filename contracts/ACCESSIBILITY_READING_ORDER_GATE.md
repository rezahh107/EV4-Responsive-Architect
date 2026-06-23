# ACCESSIBILITY_READING_ORDER_GATE

Version: 0.1.0
Status: hardening_candidate
Owner stage: `/accessibility-reading-order-gate`
Applies when: responsive repair affects visual order, visibility, focus order, source-order risk, or meaningful content placement

---

## 1. Purpose

Prevent responsive repair from creating visual/source/keyboard/screen-reader order risks.

Responsive repair often uses viewport-specific order, reverse direction, hide/show behavior, overlay simplification, or mobile-specific layout changes. These can make a section look correct while making reading order, keyboard order, or content availability unsafe.

Core rule:

```text
A visually fixed mobile layout is not acceptable if meaningful content becomes hidden, unreachable, or semantically illogical.
```

---

## 2. Non-Purpose

This contract does not:

```text
- perform a full WCAG audit;
- certify accessibility compliance;
- replace human accessibility review;
- force all decorative layers to remain visible;
- forbid Custom Order categorically;
- forbid mobile decoration simplification.
```

It is a gate for responsive repair safety, not a full accessibility certification.

---

## 3. Applies When

```yaml
applies_when:
  - visual_order_changes
  - custom_order_used
  - reverse_direction_used
  - meaningful_content_hidden_or_deferred
  - overlay_interacts_with_meaningful_content
  - duplicate_mobile_section_considered
  - decoration_layer_hidden_near_content
  - CTA_or_interactive_element_position_changes
  - focusable_element_visibility_changes
```

If none of these apply, the stage may emit:

```yaml
gate_status: not_applicable
reason: no_order_visibility_or_focus_risk_detected
```

---

## 4. Required Inputs

```yaml
required_inputs:
  - Responsive_Repair_Selection
  - Repair_Scope_Freeze
  - Repair_Option_Analysis_Payload
  - Build_Tree_Payload.content_editability_map
  - Build_Tree_Payload.overlay_decoration_map
  - Desktop_Baseline_Lock
  - Breakpoint_Inventory_Lock
  - responsive_repair_plan_if_steps_already_written
```

Optional but recommended:

```yaml
optional_inputs:
  - DOM_order_evidence
  - keyboard_navigation_test
  - screen_reader_review
  - frontend_after_screenshot
  - builder_feedback
```

---

## 5. Required Checks

```yaml
required_checks:
  meaningful_content_visibility_preserved:
    description: no meaningful text, CTA, card content, or essential visual content is hidden on any selected viewport

  source_order_risk_recorded:
    description: visual reordering risk is recorded even when DOM order is unknown

  keyboard_order_risk_recorded:
    description: focus and tab order risk is recorded for interactive/focusable elements

  screen_reader_order_risk_recorded:
    description: screen-reader reading order risk is recorded when visual order differs from likely DOM order

  tap_target_risk_recorded:
    description: tappable element size, spacing, and overlap risk is recorded where relevant

  focus_order_risk_recorded:
    description: focus sequence risk is recorded if order or visibility changes touch interactive elements

  decoration_hide_safety_checked:
    description: hidden/simplified items are inherited as decorative and do not carry meaning
```

---

## 6. Risk Triggers

```yaml
risk_triggers:
  custom_order:
    risk: visual_order_may_differ_from_DOM_order
    required_action: record_source_and_keyboard_order_risk

  reverse_direction:
    risk: visual_order_may_reverse_without_source_order_change
    required_action: record_source_order_risk

  hide_on_mobile:
    risk: meaningful_content_may_be_lost
    required_action: verify_hidden_item_is_decoration_or_nonessential_duplicate

  duplicate_mobile_section:
    risk: duplicate_content_and_focus_confusion
    required_action: route_to_architecture_mutation_veto_or_main_pipeline_review

  absolute_or_overlay_positioning:
    risk: visual_position_may_not_match_reading_order
    required_action: verify_overlay_is_decoration_or interaction_is_safe

  connector_simplification:
    risk: connector_may_carry_implied_meaning
    required_action: verify_main_pipeline_classified_connector_as_decorative
```

---

## 7. Gate Schema

```yaml
Accessibility_Reading_Order_Gate:
  schema: ev4-responsive-accessibility-gate@1.0.0
  gate_status:
    enum:
      - not_applicable
      - pass
      - pass_with_visible_risk
      - fail_requires_responsive_repair
      - fail_requires_implementation_repair
      - fail_requires_main_pipeline_rerun
      - blocked_missing_evidence

  applies_because:
    - trigger

  affected_items:
    - node_id:
      structure_label:
      content_role:
        enum:
          - meaningful
          - decorative
          - interactive
          - unknown
      viewport_scope:
      repair_step_ids:

  checks:
    meaningful_content_visibility_preserved: pass|fail|unknown|not_applicable
    source_order_risk_recorded: pass|fail|unknown|not_applicable
    keyboard_order_risk_recorded: pass|fail|unknown|not_applicable
    screen_reader_order_risk_recorded: pass|fail|unknown|not_applicable
    tap_target_risk_recorded: pass|fail|unknown|not_applicable
    focus_order_risk_recorded: pass|fail|unknown|not_applicable
    decoration_hide_safety_checked: pass|fail|unknown|not_applicable

  risk_summary:
    source_order_risk: low|medium|high|unknown|not_applicable
    keyboard_order_risk: low|medium|high|unknown|not_applicable
    screen_reader_order_risk: low|medium|high|unknown|not_applicable
    tap_target_risk: low|medium|high|unknown|not_applicable

  required_follow_up:
    - builder_verification
    - DOM_order_check
    - keyboard_test
    - main_pipeline_rerun
```

---

## 8. Allowed Outcomes

```yaml
allowed_outcomes:
  pass:
    condition:
      - meaningful_content_visibility_preserved
      - no_order_or_focus_risk_detected
      - no unresolved medium_or_higher accessibility risk

  pass_with_visible_risk:
    condition:
      - risk exists but is documented
      - meaningful content is not hidden
      - required verification is listed
      - production_ready_claim_disabled

  fail_requires_responsive_repair:
    condition:
      - repair creates avoidable visibility/order/focus issue that can be fixed responsively

  fail_requires_implementation_repair:
    condition:
      - widget/control mapping creates accessibility risk

  fail_requires_main_pipeline_rerun:
    condition:
      - safe repair requires architecture mutation
      - meaningful/decorative classification appears wrong

  blocked_missing_evidence:
    condition:
      - high-impact order or visibility risk cannot be evaluated
```

---

## 9. Custom Order Policy

```yaml
custom_order_policy:
  allowed_when:
    - meaningful_reading_order_preserved_or_risk_carried
    - no interactive_order_conflict_detected
    - DOM_order_unknown_is_not_claimed_as_safe
    - builder_verification_required_if_risk_unknown

  forbidden_when:
    - custom_order_hides_or_reorders_meaningful_sequence_unsafely
    - keyboard_order_becomes_misleading_for_focusable_elements
    - screen_reader_order_conflict_is_known_and_unresolved
    - custom_order_is_used_to_avoid_build_tree_route
```

Rule:

```text
Custom Order can be a responsive visual repair.
It cannot be used to pretend that DOM/source order has been validated.
```

---

## 10. Hide / Simplify Policy

```yaml
hide_or_simplify_policy:
  allowed_for:
    - decoration_only_connector
    - purely_visual_ornament
    - redundant_nonessential_visual_detail

  forbidden_for:
    - meaningful_text
    - CTA
    - feature_card_content
    - essential_icon_with_no_text_equivalent
    - visual_core_if_it_carries_meaning

  required_if_hiding_decoration:
    - inherited_decoration_classification
    - no_meaning_loss_statement
    - viewport_scope
    - rollback_action
```

---

## 11. Stop Conditions

```yaml
stop_conditions:
  - meaningful_content_would_be_hidden
  - interactive_element_focus_order_high_risk
  - screen_reader_order_known_conflict
  - duplicate_mobile_section_required
  - decoration_classification_unknown_for_hidden_layer
  - source_order_risk_high_and_unverified
  - accessibility_safe_repair_requires_architecture_mutation
```

---

## 12. Repair Routes

```yaml
repair_routes:
  meaningful_content_visibility_failure: /responsive-repair-plan_repair_or_EV4_/build-tree
  decoration_classification_unknown: /decoration-classification-inheritance-check
  duplicate_mobile_section_needed: /architecture-mutation-veto
  custom_order_high_risk: /repair-option-analysis_or_/responsive-repair-selection
  DOM_order_evidence_needed: evidence_request
  widget_mapping_accessibility_issue: EV4_Architect_/implementation
```

---

## 13. Self-Audit

```yaml
self_audit:
  applies_when_checked: pass|fail
  meaningful_content_visibility_checked: pass|fail
  decorative_hide_safety_checked: pass|fail|not_applicable
  custom_order_policy_checked: pass|fail|not_applicable
  source_order_risk_recorded: pass|fail|not_applicable
  keyboard_focus_risk_recorded: pass|fail|not_applicable
  screen_reader_risk_recorded: pass|fail|not_applicable
  production_ready_not_claimed: pass|fail
```

---

## 14. Example

```yaml
Accessibility_Reading_Order_Gate:
  schema: ev4-responsive-accessibility-gate@1.0.0
  gate_status: pass_with_visible_risk
  applies_because:
    - custom_order_used
  affected_items:
    - node_id: smart-home__feature-card-03
      structure_label: Feature Card 03
      content_role: meaningful
      viewport_scope: mobile
      repair_step_ids:
        - RSP-STEP-004
  checks:
    meaningful_content_visibility_preserved: pass
    source_order_risk_recorded: pass
    keyboard_order_risk_recorded: not_applicable
    screen_reader_order_risk_recorded: pass
    tap_target_risk_recorded: not_applicable
    focus_order_risk_recorded: not_applicable
    decoration_hide_safety_checked: not_applicable
  risk_summary:
    source_order_risk: unknown
    keyboard_order_risk: not_applicable
    screen_reader_order_risk: unknown
    tap_target_risk: not_applicable
  required_follow_up:
    - builder_verification
    - DOM_order_check_if_production_claim_is_needed
```
