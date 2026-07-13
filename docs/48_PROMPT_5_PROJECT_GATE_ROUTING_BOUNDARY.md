# Prompt 5 Project Gate Routing Boundary

Work Package: `WP-RESP-013`  
Slice: `WP-RESP-013/PR-C`

## Implemented local boundary

Responsive now owns a deterministic, repository-local validation boundary for Prompt 5 routing envelopes. The implementation consists of:

- contract: `contracts/project-gate/PROMPT_5_ROUTING_BOUNDARY.md`;
- schema: `contracts/project-gate/prompt-5-routing-envelope.v1.schema.json`;
- validator: `validation/e2e/run_prompt_5_routing_envelope_check.py`;
- positive fixtures: `validation/fixtures/prompt05/valid/*.valid.json`;
- negative fixtures: `validation/fixtures/prompt05/invalid/*.invalid.json`;
- CI path: `.github/workflows/validate.yml`.

The validator checks Draft 2020-12 schema conformance plus explicit policy semantics for route/reject coupling, diagnostic behavior, transport eligibility, authority ownership, exact boundary-claim registry, and all-false boundary values.

## Authority boundary

Responsive may decide only whether a locally produced routing envelope is eligible or rejected. Responsive does not execute transport, mutate EV4 Project Gate runtime state, replace Project Gate decisions, or authorize downstream progression. EV4 Project Gate remains the transport and downstream gate authority.

## Fail-closed behavior

The routing boundary rejects, at minimum:

- missing or incomplete source lineage;
- unsupported routing targets;
- authority substitution or Responsive-owned transport execution;
- inconsistent route/reject and `transport_eligible` states;
- forbidden submitted-evidence, pilot, production, release, live-render, export, accessibility, pixel-perfect, or responsive-correctness upgrades.

## Current limitations

This repository-local implementation does not prove that external Project Gate transport is deployed, exercised, or accepted. It does not create submitted evidence, satisfy Issue #8, run a pilot, validate a live render or export, or establish responsive correctness. Exact-head CI success is repository-check evidence only.

## Validation

```bash
python validation/e2e/run_prompt_5_routing_envelope_check.py
```

The command is also part of the primary `Validate` workflow. Its success must not be interpreted as production readiness, release readiness, transport execution, or domain evidence.
