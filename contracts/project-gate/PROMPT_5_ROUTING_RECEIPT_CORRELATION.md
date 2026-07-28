# Prompt 5 Routing to Decision Receipt Correlation

## Purpose

This contract defines a repository-local, non-transport correlation boundary between a Prompt 5 routing envelope and a downstream Responsive Kernel decision receipt. It exists to detect missing or divergent identity, lineage, route outcome, receipt state, and authority semantics without executing Project Gate transport or treating human-readable receipt text as Kernel authority.

## Canonical inputs

The correlation record binds:

- a Prompt 5 routing envelope conforming to `contracts/project-gate/prompt-5-routing-envelope.v1.schema.json`;
- a Responsive Kernel decision receipt conforming to `schemas/ev4-responsive-kernel-decision-receipt.schema.json`;
- the machine-readable Responsive `decision_lineage` associated with that receipt.

The route envelope remains the authority for the repository-local routing decision. The receipt remains presentation-layer output derived from machine-readable decision lineage. Neither receipt prose nor this correlation record may replace Kernel decisions, Project Gate transport authority, repository contracts, or project-specific evidence.

## Correlation identity

Each correlation record MUST have a unique non-empty `correlation_id` and MUST pin:

- `routing_id` from the Prompt 5 routing envelope;
- `receipt_id`, a repository-local identity for the receipt instance being correlated;
- `routing_schema` = `prompt-5-routing-envelope.v1`;
- `receipt_schema` = `ev4-responsive-kernel-decision-receipt.schema.json`;
- `pipeline_id` and `run_id` from Prompt 5 lineage;
- `producer_export_id`, `producer_export_schema`, and `producer_export_sha256` from Prompt 5 lineage;
- `decision_card_ref` and `decision_family` from downstream `decision_lineage`;
- routing `decision` and receipt `receipt_state`.

A correlation is invalid when any pinned identity or lineage value cannot be resolved from the referenced source objects or diverges from them.

## Outcome compatibility

The correlation layer does not invent a new decision. It checks compatibility between an existing route outcome and an existing receipt state.

- `route` is compatible only with a trace-backed downstream receipt whose `receipt_state` is `success` or `insufficient_evidence` and whose machine-readable lineage remains available.
- `reject` is compatible only with a non-success receipt state (`insufficient_evidence` or `runtime_mismatch_warning`) and MUST retain the Prompt 5 diagnostic codes that caused rejection.
- `reject` correlated with a `success` receipt is invalid.
- Human-readable success text MUST NOT override a machine-readable reject outcome, missing trace, or divergent lineage.

The validator for the next slice MUST fail closed on route/receipt outcome mismatch rather than normalize or reinterpret either source artifact.

## Receipt identity and duplicate handling

`receipt_id` identifies one concrete downstream receipt instance within the correlation artifact. Duplicate `receipt_id` values for distinct correlation records in the same validation set are invalid unless the records are byte-identical representations of the same correlation identity. The validator MUST reject ambiguous duplicate identities.

## Authority boundary

The correlation record is descriptive and validation-oriented only.

It MUST record all of the following as `false`:

- `responsive_executes_project_gate_transport`;
- `receipt_text_is_kernel_authority`;
- `correlation_replaces_kernel_decision`;
- `correlation_replaces_project_gate_decision`.

The record MUST also preserve these false evidence/readiness claims:

- submitted evidence created;
- Issue #8 mutated;
- pilot authorized;
- production ready;
- release ready;
- live render validated;
- export JSON validated;
- accessibility passed;
- pixel perfect;
- responsive correctness validated.

CI success, schema validity, merge state, correlation completeness, or receipt text do not establish any of those claims.

## Version and drift behavior

The correlation schema version is `prompt-5-routing-receipt-correlation.v1`.

A validator MUST fail closed when:

- an unsupported correlation schema version is supplied;
- the Prompt 5 routing schema is not the pinned v1 identity;
- the receipt schema identity differs from the pinned Responsive Kernel receipt schema;
- producer export schema or hash differs from the routing envelope;
- pipeline/run identity diverges;
- decision lineage fields are absent or divergent;
- route and receipt outcomes are incompatible;
- duplicate receipt identity is ambiguous;
- authority fields or boundary claims attempt an upgrade.

## Non-goals

This contract does not:

- execute or authorize Project Gate transport;
- create a Kernel decision;
- reinterpret a Kernel decision from receipt prose;
- create submitted evidence or mutate Issue #8;
- authorize pilot execution;
- prove production, release, live-render, export, accessibility, pixel-perfect, or responsive correctness.

## Work Package trace

This contract is the contract/schema layer for `WP-RESP-016/PR-A`. Fixtures, deterministic diagnostics, CI wiring, command-index updates, documentation, and STATUS parity belong to later approved slices under the same Work Package.