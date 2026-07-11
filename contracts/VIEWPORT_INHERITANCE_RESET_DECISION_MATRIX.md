# Viewport Inheritance and Reset Decision Matrix

Status: proposed_v0.1.0
Work Package: `WP-RESP-007`
PR slice: `WP-RESP-007/PR-A`
Related contract: `contracts/EV4_VIEWPORT_DISPLAY_CONTRACT.md`

## Purpose

Define deterministic repository-level rules for deciding whether a node's responsive state at `tablet` or `mobile` is explicitly set, inherited from a wider viewport, reset to a neutral/default state, intentionally inactive, or unresolved.

This contract is an input and strategy boundary. It does not prove live rendering, pixel accuracy, accessibility, export validity, production readiness, release readiness, or responsive correctness.

## Non-Purpose

This contract does not:

- infer behavior from screenshots or desktop-only evidence;
- authorize browser, Elementor, pilot, or production execution;
- define CSS cascade behavior outside the declared EV4 responsive payload;
- convert CI success into domain evidence;
- claim `live_render_validated`, `export_json_validated`, `accessibility_passed`, `pixel_perfect`, or `responsive_correctness_validated`.

## Required Inputs

A decision requires:

1. a canonical `node_ref`;
2. a canonical viewport in `desktop | tablet | mobile`;
3. the wider-viewport state, when inheritance is considered;
4. an explicit source signal describing set, reset, inactive, or unknown state;
5. a reason and source reference for every non-explicit decision.

Missing or contradictory inputs produce `unknown`; they must not be guessed.

## Canonical Decision States

- `explicit`: the current viewport contains an authoritative value or state.
- `inherited`: no current-viewport override exists and the contract permits use of the nearest wider viewport state.
- `reset`: an explicit reset marker removes or neutralizes the inherited value for the current viewport.
- `inactive`: the node is explicitly inactive for the current viewport.
- `unknown`: available evidence is missing, contradictory, non-canonical, or insufficient.

`reset` is not equivalent to `inherited`, `inactive`, or absence. A reset must be represented by an explicit reset signal.

## Decision Matrix

| Current viewport signal | Wider viewport state | Decision | Required behavior |
|---|---|---|---|
| canonical explicit value/state | any | `explicit` | Use the current viewport declaration and record its source. |
| canonical reset marker | any | `reset` | Do not inherit the wider value; record the reset source and target property/state. |
| canonical inactive marker | any | `inactive` | Mark the node inactive at this viewport; do not reinterpret as reset. |
| no override | `explicit` or `inherited` | `inherited` | Use the nearest wider authoritative state only when inheritance is allowed for the field. |
| no override | `reset` | `reset` | Preserve the wider reset for the current viewport. |
| no override | `inactive` | `inactive` | Preserve inactivity for the current viewport. |
| no override | `unknown` | `unknown` | Stop inheritance; unresolved wider state cannot become authoritative. |
| contradictory explicit/reset/inactive signals | any | `unknown` | Fail closed and report the conflicting sources. |
| non-canonical viewport or property path | any | `unknown` | Reject routing until canonicalized by an owning contract. |
| screenshot-only or visual inference | any | `unknown` | Record as observation only; do not convert to a contract decision. |

## Inheritance Order

The only permitted wider-to-narrower lookup order is:

```text
desktop -> tablet -> mobile
```

- `tablet` may inherit from `desktop`.
- `mobile` may inherit from `tablet`; tablet may itself inherit from desktop when it has no override.
- Wider viewports never inherit from narrower viewports.
- An `unknown` state blocks further inference through that path.

## Reset Rules

A valid reset decision must identify:

- `node_ref`;
- `viewport`;
- affected property or state path;
- canonical reset marker or owning source;
- reason.

A missing value, empty object, `null`, or omitted key is not automatically a reset. The owning schema or contract must explicitly define it as a reset marker.

## Allowed Work

- Document canonical inheritance and reset decisions.
- Add focused fixtures for explicit, inherited, reset, inactive, conflict, and unknown states.
- Add validator diagnostics that enforce this matrix.
- Align STATUS and validation indexes only when a validator or workflow becomes active.

## Forbidden Work

- Do not infer mobile or tablet behavior from desktop-only evidence.
- Do not turn omission into reset without an owning contract.
- Do not bypass an `unknown` state by falling back to a wider viewport.
- Do not treat repository validation as live responsive evidence.
- Do not create submitted evidence, mutate Issue #8, or authorize a real pilot.
- Do not upgrade any evidence, readiness, production, release, export, accessibility, pixel, or responsive-correctness claim.

## Payload Shape

```yaml
viewport_decision:
  node_ref: string
  viewport: desktop | tablet | mobile
  property_path: string
  decision: explicit | inherited | reset | inactive | unknown
  source_viewport: desktop | tablet | mobile | null
  source_ref: string | null
  reason: string
  conflicts: [string]
```

## Gate Rules

A decision passes repository-level validation only when:

1. viewport and decision values are canonical;
2. `explicit`, `reset`, and `inactive` decisions have a non-empty `source_ref`;
3. `inherited` identifies a valid wider `source_viewport` and does not cross an `unknown` state;
4. `unknown` records the unresolved or conflicting reason;
5. no forbidden evidence or readiness claim is upgraded.

## Stop Conditions

Stop and return `unknown` when:

- the viewport, node, or property path is non-canonical;
- the wider source is unknown;
- explicit, reset, and inactive signals conflict;
- inheritance permission for the field is absent or ambiguous;
- the only support is screenshot, visual observation, or desktop-only evidence.

## Repair Routes

- Canonicalize the viewport or property path through its owning schema.
- Supply the missing authoritative source reference.
- Resolve conflicting explicit/reset/inactive declarations.
- Add a focused fixture and validator diagnostic under `WP-RESP-007/PR-B`.
- Preserve `unknown` when ambiguity cannot be resolved safely.

## Self-Audit

- [ ] Every decision uses a canonical state.
- [ ] Every inherited decision points only to a wider viewport.
- [ ] No inheritance crosses an unknown state.
- [ ] Reset is backed by an explicit canonical reset marker.
- [ ] Omission is not treated as reset by default.
- [ ] Screenshot-only evidence remains observational.
- [ ] All evidence and readiness boundary claims remain false.

## Example

```yaml
viewport_decision:
  node_ref: connector-card-01
  viewport: mobile
  property_path: layout.display
  decision: inherited
  source_viewport: tablet
  source_ref: responsive_payload.viewport_rules[3].tablet
  reason: mobile has no override and tablet contains the nearest authoritative state
  conflicts: []
```
