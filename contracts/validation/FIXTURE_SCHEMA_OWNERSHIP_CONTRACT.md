# Fixture-to-Schema Ownership Contract

Status: `approved_contract_for_incremental_migration`

Work Package: `WP-RESP-010`

PR slice: `WP-RESP-010/PR-A`

## Purpose

Define one deterministic ownership model for JSON fixtures without weakening focused semantic validators or silently changing whether a fixture is valid or invalid.

This contract is repository-check infrastructure only. It does not create submitted evidence, authorize a pilot, or establish production, release, live-render, export, accessibility, pixel-perfect, or responsive-correctness claims.

## Ownership classes

Every active JSON fixture MUST resolve to exactly one of these ownership classes:

1. `broad_schema_fixture`
   - Location: `validation/fixtures/valid/*.json` or `validation/fixtures/invalid/*.json`.
   - Required metadata: top-level `$schema_file` naming one existing file under `schemas/`.
   - Primary validator: `validation/schema_validator/validate_schemas.py`.
   - Additional semantic validation MAY run after schema validation.

2. `focused_contract_fixture`
   - Location: a focused fixture subtree such as `validation/fixtures/<capability>/...`, `validation/p0/...`, or another validator-owned directory.
   - Required ownership: the focused validator MUST declare the exact schema or contract path and the exact fixture roots or registry it owns.
   - A focused fixture MUST NOT be implicitly absorbed into the broad validator merely because it is JSON.

3. `quality_gate_fixture`
   - Location: a quality-gate-specific tree such as `validation/task_quality/...`.
   - Required ownership: the quality-gate validator and its canonical schema or policy artifact MUST be explicit.
   - These fixtures are not domain evidence and MUST preserve all false readiness and evidence boundaries.

4. `example_or_template_artifact`
   - Location: `examples/`, templates, or documentation examples outside active validation roots.
   - These artifacts MUST NOT be counted as active fixtures unless a validator explicitly registers them.
   - Example or sample content MUST NOT be reclassified as real submitted evidence.

## Deterministic ownership resolution

Ownership MUST be resolved in this order:

1. exact focused-validator registry or explicit fixture-root declaration;
2. broad fixture root plus valid `$schema_file` metadata;
3. explicit quality-gate registry;
4. example/template classification;
5. otherwise fail closed as `unowned_fixture`.

A fixture MUST NOT have more than one primary owner. Secondary validators MAY consume a fixture only when they preserve the primary owner and do not change its expected pass/fail classification.

## Required inventory record

The migration and validator slice MUST produce a deterministic inventory entry for every active fixture with these fields:

```json
{
  "fixture_path": "validation/fixtures/valid/example.valid.json",
  "expected_result": "valid",
  "ownership_class": "broad_schema_fixture",
  "owning_schema_path": "schemas/example.schema.json",
  "primary_validator_path": "validation/schema_validator/validate_schemas.py",
  "secondary_validator_paths": [],
  "ownership_source": "$schema_file",
  "migration_state": "already_compliant"
}
```

Allowed `expected_result` values are `valid` and `invalid`.

Allowed `migration_state` values are:

- `already_compliant`
- `metadata_required`
- `focused_registry_required`
- `wrong_owner_repair_required`
- `unowned_blocking`

## Migration rules

1. Preserve each fixture's current expected valid/invalid classification unless a separate semantic defect is proven and reviewed.
2. Do not add `$schema_file` to a focused fixture when doing so would bypass or duplicate its focused semantic validator.
3. Do not point a fixture at a permissive schema merely to make broad validation pass.
4. Reject missing schemas, unknown schema paths, duplicate primary owners, and ownership that depends only on filename guessing.
5. Preserve canonical UTF-8 JSON formatting and untouched fields when metadata is added.
6. Apply optimistic concurrency to every modified fixture.
7. Require malformed, missing-owner, wrong-owner, and duplicate-owner negative coverage in `WP-RESP-010/PR-B`.
8. Require exact-head CI before merge; CI success remains repository-check evidence only.

## Broad-validator boundary

`validation/schema_validator/validate_schemas.py` currently requires `$schema_file` only for fixtures directly under:

- `validation/fixtures/valid/`
- `validation/fixtures/invalid/`

The migration MUST keep this boundary explicit. Recursive discovery or expansion into focused subtrees requires an explicit registry and review; it MUST NOT be introduced accidentally by changing a glob.

## Fail-closed diagnostics required for the next slice

`WP-RESP-010/PR-B` MUST provide deterministic diagnostics for at least:

- missing ownership metadata;
- referenced schema absent;
- wrong owning schema;
- duplicate primary ownership;
- focused fixture incorrectly routed through the broad validator;
- unregistered active fixture;
- metadata change that silently flips expected valid/invalid behavior.

## Preserved boundaries

The following remain false and MUST NOT be upgraded by this Work Package:

- submitted evidence present or created;
- Issue #8 evidence satisfied or mutated;
- pilot allowed to start;
- production ready;
- release ready;
- live render validated;
- export JSON validated;
- accessibility passed;
- pixel perfect;
- responsive correctness validated.

Schema validity, fixture ownership, validator success, review, and merge are repository-check evidence only.
