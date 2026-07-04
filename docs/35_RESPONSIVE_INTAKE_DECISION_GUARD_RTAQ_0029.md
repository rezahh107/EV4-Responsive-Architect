# RTAQ-0029 Responsive Intake Decision Guard

## Objective

Close the Builder → Responsive intake gap where an allowed intake decision could be expressed beside blocked Project Gate or viewport evidence states.

## Technical decision

The Builder → Responsive input schema now treats `responsive_intake_decision.intake_allowed: true` as a gated state. A true intake decision requires:

- `project_gate_ref.gate_status: verified`
- `viewport_evidence.desktop.evidence_status: provided`
- `viewport_evidence.tablet.evidence_status: provided`
- `viewport_evidence.mobile.evidence_status: provided`
- the complete canonical forbidden-claim set

This is a repository contract and fixture boundary only. It proves structural intake eligibility; it does not prove responsive correctness or authorize execution.

## Validation coverage

`validation/e2e/run_builder_responsive_input_boundary_check.py` now includes negative fixtures for:

- blocked Project Gate with intake allowed
- blocked viewport evidence with intake allowed
- incomplete forbidden-claim inventory
- missing mobile evidence

## Truth boundary

This task does not create submitted evidence, mutate Issue #8, start a real pilot, implement Project Gate, or upgrade readiness, production, release, live-render, export, accessibility, pixel, or responsive-correctness claims.

CI success remains repository-check evidence only.
