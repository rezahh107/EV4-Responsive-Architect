# Smart-Home Connector — Evidence Intake Checklist

Version: 0.1.1
Status: machine_checkable_intake_ready

Use this checklist before starting the responsive pilot.

## A. Machine-Readable Intake Packet

- [ ] `EVIDENCE_INTAKE_PACKET` is provided.
- [ ] Packet schema is `ev4-responsive-evidence-intake-packet@1.0.0`.
- [ ] Packet validates against `schemas/ev4-responsive-evidence-intake-packet.schema.json`.
- [ ] `validation/e2e/run_evidence_intake_check.py` passes.

Blocked if:

```text
evidence intake packet is missing, malformed, or fails semantic checks.
```

## B. Main EV4 Handoff

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

## C. Desktop Baseline

- [ ] Desktop screenshot is provided.
- [ ] Screenshot source is identified: `frontend` or `editor`.
- [ ] Viewport width or label is provided.
- [ ] Root section identity or root class is provided.
- [ ] Known acceptable desktop issues are listed.
- [ ] Minimum must-not-regress list is present:
  - [ ] `meaningful_text_visibility`
  - [ ] `feature_card_group_integrity`
  - [ ] `visual_core_presence`
  - [ ] `connector_layer_containment`
  - [ ] `no_horizontal_overflow`

Blocked if:

```text
desktop state cannot be locked or minimum must-not-regress list is missing.
```

## D. Tablet Evidence

- [ ] Tablet screenshot is provided.
- [ ] Screenshot source is identified.
- [ ] Viewport width or label is provided.
- [ ] Visible responsive symptoms are noted, if any.
- [ ] Per-item evidence quality is recorded:
  - [ ] `quality_level`
  - [ ] `confidence_cap`
  - [ ] `can_support`
  - [ ] `cannot_support`
  - [ ] `downstream_allowed_use`
  - [ ] `known_limitations`

## E. Mobile Evidence

- [ ] Mobile screenshot is provided.
- [ ] Screenshot source is identified.
- [ ] Viewport width or label is provided.
- [ ] Visible responsive symptoms are noted, if any.
- [ ] Per-item evidence quality is recorded.

## F. Breakpoint Inventory

Select one and record claim scope:

- [ ] Elementor project settings or export JSON provided.
- [ ] User-declared breakpoint values provided.
- [ ] Elementor default fallback is used with explicit unverified label.

Claim scope must include:

```yaml
may_observe:
may_plan_repair:
may_handoff_controlled:
may_claim_release_ready: false
```

Blocked for release-ready claims if:

```text
breakpoints are user-declared or fallback values without project/export verification.
```

## G. Privacy Review

- [ ] Credentials and access tokens removed.
- [ ] Private user data, emails, form data, and client-identifying data removed.
- [ ] Screenshots/export-like evidence reviewed for private URLs and client identifiers.

Blocked if:

```text
privacy review is incomplete.
```

## H. File Naming Convention

Use predictable names:

```text
main-ev4-handoff.md
desktop-baseline-[width].png
tablet-[width].png
mobile-[width].png
breakpoint-inventory.json
```

## I. Optional Evidence

- [ ] Elementor export JSON.
- [ ] Resize sweep video.
- [ ] Browser DevTools DOM notes.
- [ ] Computed style notes.
- [ ] Playwright screenshots.
- [ ] Visual diff report.

## Intake Verdict Rules

```yaml
allowed_if:
  - intake_packet_validates_against_schema
  - all_required_evidence_ids_present
  - selected_candidate_id_present
  - main_handoff_minimum_fields_present
  - desktop_baseline_present
  - tablet_evidence_present
  - mobile_evidence_present
  - breakpoint_inventory_present_or_flagged
  - privacy_review_acknowledged
  - no_blocker_conflicts

blocked_if:
  - evidence_intake_packet_missing_or_invalid
  - selected_candidate_id_missing
  - main_handoff_missing
  - desktop_baseline_missing
  - tablet_or_mobile_missing
  - selected_candidate_identity_conflict
  - privacy_review_incomplete
  - architecture_mutation_required_before_pilot
```

## Intake Verdict

```yaml
intake_verdict:
  status: allowed | blocked
  missing_required_items: []
  blocker_conflicts: []
  evidence_quality_summary:
  pilot_allowed_to_start: true | false
```
