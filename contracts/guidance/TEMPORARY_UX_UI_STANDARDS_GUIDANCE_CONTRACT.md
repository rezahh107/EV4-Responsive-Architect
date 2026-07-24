# Temporary UX/UI Standards Guidance Boundary

## Scope

This contract defines how `EV4 Responsive Architect` may consume temporary UX/UI standards as non-authoritative decision-support guidance.

It does not create repository authority, replace contracts or Stage Anchors, reinterpret Kernel decisions, execute Project Gate transport, create submitted evidence, authorize a pilot, or establish responsive correctness.

## Guidance rule

A standards guidance artifact is eligible for repository-local use only when all of the following are explicit:

1. A stable guidance identity and revision.
2. Source provenance for every guidance item.
3. A bounded applicability scope.
4. Known exceptions and non-applicable conditions.
5. Conflict handling that identifies every higher-authority source, records whether each conflict is resolved or unresolved, and defers to repository contracts, validators, Stage Anchors, Kernel decisions, Project Gate authority, and project-specific evidence.
6. A lifecycle state and review date that prevent stale guidance from silently remaining active.
7. Explicit false evidence, pilot, readiness, production, release, export, accessibility, pixel, and responsive-correctness claims.

Missing provenance, unsupported universal wording, stale lifecycle state, unresolved conflict, authority substitution, or any forbidden claim upgrade must fail closed in the validator slice.

## Authority precedence

When guidance conflicts with another source, precedence is:

1. repository contracts, schemas, validators, and Stage Anchors;
2. authoritative Kernel decisions and Project Gate boundaries;
3. project-specific submitted evidence that passed its governing gates;
4. this non-authoritative guidance artifact.

Guidance may narrow its own applicability. It may not broaden repository authority, bypass a validator, or convert a recommendation into a correctness claim.

## Machine-readable conflict disposition

Each conflict entry must include:

- a stable conflict identity;
- the higher-authority class and a concrete reference;
- a disposition of `resolved` or `unresolved`;
- a bounded rationale; and
- a non-empty resolution reference when the disposition is `resolved`.

An `unresolved` conflict must use a null resolution reference and remain fail-closed and non-selectable. A `resolved` conflict is eligible only when its resolution reference identifies the higher-authority basis for the disposition. An empty conflict list means that no known conflict is declared; it does not permit a validator to ignore a conflict detected from repository truth.

## Machine-readable artifact

The schema is:

`contracts/guidance/temporary-ux-ui-standards-guidance.v1.schema.json`

The schema requires:

- guidance identity, revision, lifecycle, and review date;
- item-level provenance and source classification;
- applicability and exception rules;
- machine-readable conflict identity, authority reference, disposition, and resolution evidence;
- non-authoritative usage semantics; and
- false boundary claims.

## Required negative coverage for WP-RESP-017/PR-B

The validator slice must reject at least:

- missing or unverifiable provenance;
- unsupported universal applicability;
- missing exceptions;
- stale or expired guidance presented as active;
- a conflict missing its higher-authority reference or disposition;
- a resolved conflict without a non-empty resolution reference;
- an unresolved conflict represented as selectable;
- guidance replacing a contract, validator, Stage Anchor, Kernel decision, or Project Gate authority;
- standards conformance represented as responsive-correctness evidence; and
- any submitted-evidence, pilot, readiness, production, release, export, accessibility, pixel, or responsive-correctness upgrade.

## Preserved boundaries

This contract does not prove or create:

- submitted evidence;
- Issue #8 mutation;
- pilot authorization or execution;
- production or release readiness;
- live-render or export validation;
- accessibility conformance;
- pixel-perfect output; or
- responsive correctness.

Schema validity and CI success remain repository-check evidence only.
