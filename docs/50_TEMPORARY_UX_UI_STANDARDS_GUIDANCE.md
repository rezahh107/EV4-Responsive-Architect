# Temporary UX/UI Standards Guidance

## Purpose

This document records the operator-facing use boundary for the temporary UX/UI standards guidance capability delivered under `WP-RESP-017`.

The guidance is non-authoritative decision support. It may help a Responsive decision identify relevant UX/UI considerations, but it does not replace repository contracts, schemas, validators, Stage Anchors, Kernel decisions, Project Gate authority, or project-specific evidence.

## Canonical surfaces

- Contract: `contracts/guidance/TEMPORARY_UX_UI_STANDARDS_GUIDANCE_CONTRACT.md`
- Schema: `contracts/guidance/temporary-ux-ui-standards-guidance.v1.schema.json`
- Validator: `validation/e2e/run_temporary_ux_ui_standards_guidance_check.py`
- Fixtures: `validation/fixtures/temporary_ux_ui_standards_guidance/`

## Eligible guidance

A guidance artifact is eligible for repository-local use only when its identity, revision, item-level provenance, applicability, exceptions, conflicts, lifecycle state, and review date satisfy the canonical contract and schema.

Guidance must remain bounded to the source and applicability it can actually support. It may narrow its own scope. It may not promote a recommendation into a universal rule or a Responsive correctness decision.

## Conflict handling

Repository authority wins over guidance. When a guidance item conflicts with a higher-authority source, the artifact must identify the conflict and higher-authority reference and must record a machine-readable disposition.

Unresolved conflicts remain fail-closed and non-selectable. Resolved conflicts require a concrete resolution reference that identifies the higher-authority basis for the resolution. A missing conflict declaration does not authorize ignoring a conflict detected from repository truth.

## Lifecycle and provenance

Active guidance must remain review-current. Expired guidance or active guidance whose required review date is stale is non-selectable until it is re-evaluated through the governing contract.

Repository-local provenance must resolve to the concrete repository object required by the validator. Provenance metadata is not a substitute for project-specific evidence and does not establish runtime manifestation.

## Responsive use boundary

Responsive may use valid guidance only as bounded decision support. A downstream decision must continue to derive authority from the governing Responsive contracts and evidence chain, not from the guidance artifact itself.

The guidance capability does not create or prove:

- submitted evidence;
- Issue #8 mutation;
- pilot authorization or execution;
- production readiness;
- release readiness;
- live-render validation;
- export JSON validation;
- accessibility conformance;
- pixel-perfect output; or
- responsive correctness.

Schema validity, fixture validity, validator success, CI success, review, merge, catalog completion, and standards conformance remain repository-check or decision-support evidence only.

## Operational checks

Primary validation includes:

```bash
python validation/e2e/run_temporary_ux_ui_standards_guidance_check.py
```

The validator provides positive and diagnostic-specific negative coverage for provenance, applicability, lifecycle, conflicts, authority substitution, and forbidden evidence/readiness/correctness upgrades.

The primary `Validate` workflow must continue to execute this validator. Command indexes and `STATUS.md` must remain consistent with the active contract/schema/validator surfaces.

## Work Package trace

This documentation is the `WP-RESP-017/PR-C` documentation and STATUS-parity slice. `WP-RESP-017` must not be marked complete merely because this document exists; completion still requires the slice to satisfy exact-head CI, review, delayed-review, STATUS parity, and all repository quality gates.
