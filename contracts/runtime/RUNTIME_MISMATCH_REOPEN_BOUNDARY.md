# Runtime Mismatch Reopen Boundary

## Purpose

This contract defines a bounded, repository-local package for reporting a runtime observation that conflicts with a prior authoritative decision. The package requests authoritative review; it does not replace, amend, reinterpret, or supersede the prior decision.

Canonical schema:

`contracts/runtime/runtime-mismatch-reopen-package.v1.schema.json`

## Authority model

Responsive may observe runtime behavior, record deterministic mismatch facts, preserve lineage, and request reopening. Responsive must not author a replacement Kernel decision, silently reinterpret the prior decision, approve transport, authorize a pilot, or convert repository checks into domain evidence.

An accepted package therefore requires:

- exact prior-decision identity and schema;
- repository, commit, and artifact hash lineage;
- an explicit consumer stage;
- a timestamped runtime observation with expected and observed states;
- at least one immutable evidence reference;
- one enumerated reopen reason;
- `requested_action: reopen_for_authoritative_review`;
- `responsive_may_replace_decision: false`;
- `authoritative_redecision_required: true`.

## Fail-closed rejection conditions

A consumer must reject a reopen package when any of the following applies:

- prior decision lineage is missing, partial, malformed, or not hash-pinned;
- the observation omits the consumer stage, timestamp, environment, mismatch code, expected state, or observed state;
- no evidence reference is supplied;
- the package requests a replacement decision or implies Responsive-side redesign authority;
- the reopen reason is not one of the schema-defined reasons;
- any submitted-evidence, pilot, production, release, live-render, export, accessibility, pixel, or responsive-correctness boundary is upgraded.

## Evidence and readiness boundaries

This package is a routing and review-request artifact only. Its existence, schema validity, validator success, CI success, review approval, or merge does not establish runtime correctness, responsive correctness, submitted evidence, pilot authorization, production readiness, release readiness, export validation, accessibility, or pixel-perfect output.

All boundary claims are required and fixed to `false` by schema.

## Deferred implementation

This PR slice defines only the contract and schema. Fixtures, deterministic diagnostics, validator behavior, CI wiring, command-index entries, and any directly affected STATUS parity remain assigned to `WP-RESP-012/PR-B`.
