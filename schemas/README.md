# Schemas

Machine-readable JSON Schemas for EV4 Responsive Architect payloads.

## Policy

- Every schema must include `$schema`, `$id`, `title`, `type`, `required`, and an explicit `additionalProperties` policy.
- Top-level object schemas must require a `schema` discriminator.
- Critical enums must be closed, especially `evidence_label`, `severity`, viewport labels, gate outcomes, and repair ownership values.
- Fixtures must include valid and invalid samples for critical schemas.
- CI must validate schema files, fixture payloads, and v0.1 semantic gates.

## Hardened v0.1 Core Targets

```text
ev4-responsive-stage-anchor.schema.json
ev4-responsive-main-input.schema.json
ev4-responsive-payload-identity.schema.json
ev4-responsive-evidence-ingest.schema.json
ev4-responsive-repair-option-analysis.schema.json
ev4-responsive-repair-plan.schema.json
ev4-responsive-accessibility-gate.schema.json
ev4-responsive-css-selector-safety.schema.json
```

## Validation Layers

```text
Layer 1: JSON syntax validation
Layer 2: JSON Schema Draft 2020-12 validation
Layer 3: fixture pass/fail validation
Layer 4: EV4 semantic checks where JSON Schema alone is not enough
```

The current semantic checks include CSS selector safety gates for global selector leakage and missing project root / target node scope.
