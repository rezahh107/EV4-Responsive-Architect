# Prompt 5 Project Gate Routing Boundary

## Status

- Contract ID: `prompt-5-routing-envelope.v1`
- Work Package: `WP-RESP-013`
- Slice: `WP-RESP-013/PR-A`
- Authority model: Responsive decides only whether a validated local producer artifact is eligible to be routed; EV4 Project Gate owns transport execution and downstream gate decisions.

## Purpose

This contract defines the local, fail-closed envelope used by EV4 Responsive Architect to describe a Prompt 5 routing decision for EV4 Project Gate.

It does not execute transport, mutate EV4 Project Gate, authorize a pilot, create submitted evidence, or upgrade any production, release, export, accessibility, pixel, or responsive-correctness claim.

## Inputs

The envelope requires:

1. a Responsive producer identity pinned to repository, ref, commit SHA, artifact ID, and artifact SHA-256;
2. complete pipeline and run lineage;
3. a pinned `producer-gate-export.v1` export identity and SHA-256;
4. an explicit route decision of `route` or `reject`;
5. explicit authority and boundary-claim objects.

Missing or malformed lineage is invalid and must not silently degrade to inferred routing.

## Routing semantics

### `route`

A `route` decision means only that the local artifact is structurally eligible for handoff to EV4 Project Gate.

Required invariants:

- `target` is exactly `ev4-project-gate`;
- `transport_eligible` is `true`;
- `diagnostic_codes` is empty;
- Responsive still does not execute transport;
- EV4 Project Gate remains the transport execution owner.

### `reject`

A `reject` decision means the artifact must not be routed.

Required invariants:

- `transport_eligible` is `false`;
- at least one deterministic diagnostic code is present;
- diagnostic codes use the `P5R-*` namespace.

The validator slice is expected to define stable codes for at least:

- missing or inconsistent lineage;
- unsupported target or route state;
- authority substitution;
- forbidden evidence or readiness upgrades.

## Authority boundary

Responsive may:

- validate local schema and semantic prerequisites;
- produce a deterministic route or reject decision;
- package the decision and its lineage for EV4 Project Gate.

Responsive may not:

- execute Project Gate transport;
- replace or pre-empt Project Gate decisions;
- mutate an external Project Gate repository or runtime;
- create submitted evidence or mutate Issue #8;
- authorize real pilot execution;
- claim production or release readiness;
- claim live-render, export, accessibility, pixel-perfect, or responsive-correctness validation.

## Evidence boundary

Schema validity, validator success, CI success, PR merge, catalog parity, or Work Package completion are repository-check evidence only. They are not responsive-correctness or production evidence.

All boundary fields in `boundary_claims` are required and fixed to `false`.

## Fail-closed requirements

Consumers must reject an envelope when:

- required source identity or lineage is absent;
- a SHA does not match the required format;
- the target differs from `ev4-project-gate`;
- route and transport eligibility disagree;
- a rejected route has no diagnostic code;
- Responsive is declared as transport execution owner;
- any forbidden evidence or readiness claim is upgraded.

No silent fallback, inferred lineage, or authority substitution is permitted.

## Schema

The normative schema is:

`contracts/project-gate/prompt-5-routing-envelope.v1.schema.json`

Fixtures, deterministic diagnostics, validator wiring, command-index integration, CI wiring, and STATUS parity belong to the approved follow-on slices `WP-RESP-013/PR-B` and `WP-RESP-013/PR-C`.
