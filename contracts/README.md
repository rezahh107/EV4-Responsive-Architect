# Contracts

This directory contains normative rules and gates for EV4 Responsive Architect.

Each contract file should include:

- Purpose
- Non-Purpose
- Required Inputs
- Allowed Work
- Forbidden Work
- Payload Schema
- Gate Rules
- Stop Conditions
- Repair Routes
- Self-Audit
- Example Payload

Core v0.1 contracts include input handoff, architecture mutation veto, evidence discipline, repair triage, breakpoint lock, repair option analysis, Elementor control path, accessibility gate, CSS selector safety, payload identity hashing, state as code, and production boundary.

## Responsive decision contracts

- `EV4_VIEWPORT_DISPLAY_CONTRACT.md` — canonical viewport display output shape.
- `VIEWPORT_INHERITANCE_RESET_DECISION_MATRIX.md` — proposed deterministic explicit, inherited, reset, inactive, and unknown routing across desktop, tablet, and mobile; repository-check evidence only until validator/index activation.
