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
- `receipt_id`, a deterministic repository-local identity for the concrete receipt object being correlated;
- `receipt_identity_scheme` = `rfc8785-sha256-receipt-object-v1`;
- `receipt_sha256`, the lowercase SHA-256 digest of the canonical receipt object defined below;
- `routing_schema` = `prompt-5-routing-envelope.v1`;
- `receipt_schema` = `ev4-responsive-kernel-decision-receipt.schema.json`;
- `pipeline_id` and `run_id` from Prompt 5 lineage;
- `producer_export_id`, `producer_export_schema`, and `producer_export_sha256` from Prompt 5 lineage;
- `decision_card_ref` and `decision_family` from downstream `decision_lineage`;
- routing `decision` and receipt `receipt_state`.

A correlation is invalid when any pinned identity or lineage value cannot be resolved from the referenced source objects or diverges from them.

## Deterministic receipt identity

Receipt identity MUST be derived from the concrete receipt object rather than authored independently.

- When the canonical receipt input is a direct receipt object, the identity source is that receipt object.
- When the canonical receipt input is the trace-backed envelope form, the identity source is the nested `kernel_decision_receipt` object only. The fixture wrapper and `decision_lineage` are not part of the receipt digest because lineage is pinned separately by this correlation contract.
- Serialize the identity-source receipt object with RFC 8785 JSON Canonicalization Scheme (JCS), UTF-8 encode the canonical JSON bytes, and compute SHA-256 over those bytes.
- `receipt_sha256` MUST equal the resulting lowercase 64-hex digest.
- `receipt_id` MUST equal `sha256:<receipt_sha256>` exactly.

The next-slice validator MUST recompute this digest from the referenced canonical receipt input and fail closed when the digest, identity scheme, or derived `receipt_id` differs. An arbitrary non-empty `receipt_id` is not valid identity evidence.

## Outcome compatibility

The correlation layer does not invent a new decision. It checks compatibility between an existing route outcome and an existing receipt state.

- `route` is compatible only with a trace-backed downstream receipt whose `receipt_state` is `success` or `insufficient_evidence` and whose machine-readable lineage remains available.
- `reject` is compatible only with a non-success receipt state (`insufficient_evidence` or `runtime_mismatch_warning`) and MUST retain the Prompt 5 diagnostic codes that caused rejection.
- `reject` correlated with a `success` receipt is invalid.
- Human-readable success text MUST NOT override a machine-readable reject outcome, missing trace, or divergent lineage.

The validator for the next slice MUST fail closed on route/receipt outcome mismatch rather than normalize or reinterpret either source artifact.

## Receipt identity and duplicate handling

`receipt_id` identifies one concrete downstream receipt object by its deterministic canonical-content digest. Duplicate `receipt_id` values are valid only when recomputation from each referenced receipt produces the same `receipt_sha256`; otherwise the validator MUST reject the correlation as identity divergence or ambiguity. Distinct receipt content cannot share an authored alias to bypass duplicate detection.

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
- the receipt identity scheme is unsupported;
- `receipt_sha256` cannot be recomputed from the canonical receipt object or diverges;
- `receipt_id` is not exactly derived as `sha256:<receipt_sha256>`;
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
