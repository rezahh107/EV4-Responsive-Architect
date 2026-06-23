# 00 — Overview

`EV4 Responsive Architect` is a post-build responsive repair and validation system for Elementor V4 sections already architected by EV4 Architect.

## System Boundary

```text
EV4 Architect = architecture selection + build tree + implementation handoff.
EV4 Responsive Architect = responsive evidence audit + repair ownership + atomic repair plan + validation handoff.
```

## Main Principle

```text
Repair responsive behavior without silently changing architecture.
```

## Repository Layers

```text
1. docs/       Human-readable overview and roadmap
2. contracts/  Normative rules and gates
3. stages/     Stage protocols
4. schemas/    Machine-readable schemas
5. state/      State as Code JSON files
6. validation/ Programmatic validators and fixtures
7. examples/   Pilot and E2E cases
8. prompts/    Run prompts and builder session starters
```

## First Supported Workflow

```text
completed EV4 handoff
→ responsive evidence ingest
→ desktop baseline lock
→ breakpoint inventory lock
→ breakpoint observation
→ failure map
→ repair ownership routing
→ repair option analysis
→ repair selection
→ repair scope freeze
→ atomic repair plan
→ final audit
```
