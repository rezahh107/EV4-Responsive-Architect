# Schemas

Machine-readable JSON Schemas for EV4 Responsive Architect payloads.

## Policy

- Every schema must include `$schema`, `$id`, `title`, `type`, `required`, and `additionalProperties` policy.
- Schema names must include versioned IDs where practical.
- Fixtures must include at least one valid and one invalid sample per critical schema.
- CI must validate schema files and fixture payloads.

## Initial Targets

```text
ev4-responsive-stage-anchor.schema.json
ev4-responsive-main-input.schema.json
ev4-responsive-evidence-ingest.schema.json
ev4-responsive-breakpoint-inventory.schema.json
ev4-responsive-repair-plan.schema.json
ev4-responsive-accessibility-gate.schema.json
```
