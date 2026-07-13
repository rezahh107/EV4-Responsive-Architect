# EV4 Responsive Architect

Status: responsive system active. Project Gate integration is planned. The Project Gate program is not implemented.

## Role

Responsive Architect validates and repairs post-build behavior across real viewports. It does not select the original architecture, prove pre-build constructability, or perform Builder execution.

## Planned Project Gate Flow

```text
Builder output and build evidence
→ EV4 Project Gate
→ Responsive input
→ Responsive output and viewport evidence
→ EV4 Project Gate
→ final evidence result
```

The future user flow is one upload and one check. An accepted Builder handoff supplies the Responsive package. A non-accepted handoff supplies a plain-language package describing what must be corrected. The final gate checks responsive output and evidence before any final status is issued.

Responsive work requires applicable desktop, tablet, mobile, frontend, browser, export, or diagnostic evidence. A screenshot proves only the visible assertions it supports.

Failures that should have been resolved before build, such as missing connector geometry, overlay containment, asset strategy, interaction approval, or Dynamic Loop approval, are not silently normalized as responsive repairs.

This repository remains authoritative for Responsive schemas, validators, fixtures, repair rules, viewport evidence, and responsive semantics. EV4 Project Gate verifies incoming and final handoffs and does not replace Responsive contracts or invent evidence.

```yaml
project_gate_handoff: documented
project_gate_runtime: not_implemented
production_ready: false
```

## Related Repositories

- `rezahh107/EV4-Project-Gate`
- `rezahh107/EV4-Architect-Repo`
- `rezahh107/EV4-Constructability-Engineer-Repo`
- `rezahh107/EV4-Builder-Assistant-Repo`

