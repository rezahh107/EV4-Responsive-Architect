# Responsive Reference Family Linkage Contract

Status: active_patch_1_role_alignment  
Schema: `ev4-responsive-reference-family@1.0.0`  
Purpose: prevent mobile/tablet reference behavior from being inferred from raw screenshots or desktop-only references.

---

## Rule

Raw screenshots are evidence only, never baseline authority.

A desktop screenshot does not prove mobile/tablet behavior.

Responsive reference behavior requires scoped reference authorization when a responsive route depends on visual-reference behavior.

---

## Required Fields

When a responsive packet uses a visual reference for tablet or mobile behavior, it must carry:

```yaml
golden_reference_id:
golden_reference_version:
golden_reference_scope: desktop | tablet | mobile | global
golden_reference_family:
parent_reference_id:
adaptation_type: same_tree_adaptation | viewport_specific_adaptation | hybrid_adaptation | none
per_viewport_reference_authorization:
  desktop: authorized | not_authorized | not_applicable
  tablet: authorized | not_authorized | not_applicable
  mobile: authorized | not_authorized | not_applicable
reference_supersedes:
superseded_by:
```

`reference_supersedes` and `superseded_by` may be null when no supersession relationship exists.

---

## Failure Rules

Responsive validation must fail when:

```text
- mobile/tablet behavior is inferred from desktop screenshot only
- raw screenshot is used as authority
- scoped reference behavior lacks golden_reference_id/version/scope/family
- per_viewport_reference_authorization does not authorize the viewport being evaluated
```

---

## Ownership

Responsive owns scoped reference-family validation.

CE owns or carries the locked Golden Reference contract before Builder execution.

Architect may register design-level source evidence but does not authorize mobile/tablet reference-family behavior.
