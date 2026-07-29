# EV4 Prompt 5 Cross-Contract Compatibility Contract

## Identity

- Contract ID: `prompt-5-cross-contract-compatibility.v1`
- Contract version: `1.0.0`
- Work Package: `WP-RESP-014`
- Slice: `WP-RESP-014/PR-A`
- Usage class: repository-local compatibility control

## Purpose

This contract defines the repository-local manifest that pins the Prompt 5 routing envelope to the producer-gate export and vendored Project Gate common-contract surfaces on which that routing envelope depends.

The manifest is a compatibility record only. It does not execute Project Gate transport, replace Project Gate authority, reinterpret Kernel decisions, create submitted evidence, authorize a pilot, or establish production, release, live-render, export, accessibility, pixel-perfect, or responsive-correctness evidence.

## Required pinned surfaces

A conforming manifest MUST identify exactly these dependency roles:

1. `prompt_5_routing_envelope`
2. `producer_gate_export_schema`
3. `project_gate_common_contract_lock`

Each dependency MUST pin:

- repository path;
- contract identifier;
- contract version;
- Git blob SHA;
- SHA-256 digest of the complete file bytes.

A dependency identity is compatible only when every pinned value matches the repository object being evaluated. A matching path or version without matching hashes is insufficient.

## Lineage compatibility

The manifest MUST declare the compatible producer-export schema expected by the Prompt 5 routing envelope. The following relationship is normative for version 1:

- Prompt 5 routing envelope: `prompt-5-routing-envelope.v1`
- producer export schema: `producer-gate-export.v1`
- route target: `ev4-project-gate`
- producer stage: `responsive`

The compatibility record MUST fail closed when identifiers, versions, route target, producer stage, or producer-export lineage disagree.

## Authority boundary

The only routing-decision owner represented by this manifest is `responsive`. The only transport-execution owner represented by this manifest is `ev4-project-gate`.

The following claims MUST remain false:

- Responsive executes Project Gate transport.
- Responsive substitutes a Project Gate decision.
- Compatibility proves submitted evidence, pilot authorization, production readiness, release readiness, live-render validation, export validation, accessibility, pixel-perfect output, or responsive correctness.

## Fail-closed conditions for PR-B

The validator and fixtures delivered by `WP-RESP-014/PR-B` MUST reject at least:

- missing required dependency role;
- duplicate dependency role;
- unsupported manifest or dependency version;
- path, contract ID, or contract-version drift;
- Git blob SHA drift;
- file SHA-256 drift;
- producer-stage, route-target, or producer-export lineage mismatch;
- Responsive transport-execution or Project Gate authority substitution;
- any evidence, pilot, readiness, export, accessibility, pixel, or responsive-correctness boundary upgrade.

## Evidence and readiness boundary

Schema validity, hash parity, validator success, CI success, review completion, mergeability, or merge establish repository-check evidence only. They do not establish any domain-evidence or readiness claim.
