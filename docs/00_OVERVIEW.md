# 00 — Overview

`EV4 Responsive Architect` is a responsive-tree architecture and Elementor handoff system for sections already architected by EV4 Architect.

## System Boundary

```text
EV4 Architect = desktop/section architecture selection + build tree + implementation handoff.
EV4 Responsive Architect = responsive relationship classification + route selection + responsive tree/override generation + builder handoff + validation plan.
```

## Main Principle

```text
Classify first. Route second. Generate responsive tree or overrides third. Validate claims only with matching evidence.
```

## Primary Workflow

```text
EV4_RESPONSIVE_START_PACKET
→ responsive design intake
→ viewport source ledger
→ section relationship classification
→ Elementor strategy routing
→ responsive tree ownership contract
→ same-tree overrides OR viewport tree OR composite plan
→ display and breakpoint contract
→ content/accessibility/duplication gate
→ responsive builder handoff
→ validation plan
→ final review
→ output package
```

## Supported Modes

```yaml
primary_mode: design_to_responsive_tree
secondary_mode: responsive_repair
```

Repair is no longer the primary identity of the system. It remains a fallback when a responsive implementation already exists and real evidence identifies an issue.

## Repository Layers

```text
1. docs/       Human-readable overview and roadmap
2. contracts/  Normative rules and gates
3. stages/     Stage protocols
4. schemas/    Machine-readable schemas
5. planning/   State and queue files
6. validation/ Programmatic validators and fixtures
7. examples/   Pilot and E2E cases
8. prompts/    Run prompts and builder session starters
```
