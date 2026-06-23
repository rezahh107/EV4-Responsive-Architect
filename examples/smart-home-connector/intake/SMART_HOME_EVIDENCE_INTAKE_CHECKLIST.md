# Smart-Home Connector — Evidence Intake Checklist

Version: 0.1.0
Status: ready_for_user_evidence

Use this checklist before starting the responsive pilot.

## A. Main EV4 Handoff

- [ ] `selected_candidate_id` is provided.
- [ ] `Build_Tree_Payload` or equivalent handoff is provided.
- [ ] `Implementation_Payload` or builder implementation notes are provided.
- [ ] `Final_Audit_Payload` or final audit status is provided.
- [ ] `overlay_decoration_map` is available.
- [ ] `content_editability_map` is available.
- [ ] `responsive_structure_contract` is available.
- [ ] carried unknowns and audit flags are visible.

Blocked if:

```text
selected_candidate_id is missing or conflicts with current EV4 handoff.
```

## B. Desktop Baseline

- [ ] Desktop screenshot is provided.
- [ ] Screenshot source is identified: `frontend` or `editor`.
- [ ] Viewport width or label is provided.
- [ ] Root section identity or root class is provided.
- [ ] Must-not-regress items are listed.
- [ ] Known acceptable desktop issues are listed.

Blocked if:

```text
desktop state cannot be locked.
```

## C. Tablet Evidence

- [ ] Tablet screenshot is provided.
- [ ] Screenshot source is identified.
- [ ] Viewport width or label is provided.
- [ ] Visible responsive symptoms are noted, if any.

## D. Mobile Evidence

- [ ] Mobile screenshot is provided.
- [ ] Screenshot source is identified.
- [ ] Viewport width or label is provided.
- [ ] Visible responsive symptoms are noted, if any.

## E. Breakpoint Inventory

Select one:

- [ ] Elementor project settings or export JSON provided.
- [ ] User-declared breakpoint values provided.
- [ ] Elementor default fallback is used with explicit unverified label.

Blocked for release-ready claims if:

```text
breakpoints are only assumed fallback values.
```

## F. Optional Evidence

- [ ] Elementor export JSON.
- [ ] Resize sweep video.
- [ ] Browser DevTools DOM notes.
- [ ] Computed style notes.
- [ ] Playwright screenshots.
- [ ] Visual diff report.

## Intake Verdict

```yaml
intake_verdict:
  status: TODO_allowed | TODO_blocked
  missing_required_items: []
  blocker_conflicts: []
  evidence_quality_summary: TODO
  pilot_allowed_to_start: TODO_yes_no
```
