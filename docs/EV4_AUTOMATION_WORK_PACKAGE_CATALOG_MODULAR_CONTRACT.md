# EV4 Automation Work Package Catalog Modular Contract

Status: proposed contract for `WP-RESP-009/PR-A`.

## Purpose

This contract defines a deterministic modular representation for the Work Package Catalog without creating a second execution authority. It does not migrate package records; migration, reassembly validation, parity checks, and negative fixtures belong to `WP-RESP-009/PR-B`.

## Authority model

The approved objective source remains:

```text
planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json
```

Only one authority mode may be active:

1. `monolith_canonical_modular_shadow`
   - The monolithic catalog remains canonical.
   - Index and package files, when introduced, are generated or checked shadow artifacts.
   - Controllers must not select work directly from modular files.
2. `modular_canonical_monolith_generated`
   - This mode is permitted only after `WP-RESP-009/PR-B` provides deterministic reassembly, parity validation, negative fixtures, CI wiring, controller-path updates, documentation, and STATUS parity.
   - The canonical public path remains the monolithic catalog path; it becomes a generated deterministic projection.

A repository state containing two independently editable authorities is invalid.

## File layout

```text
planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG_INDEX.json
planning/work-packages/WP-RESP-001.json
planning/work-packages/WP-RESP-002.json
...
```

Schemas:

```text
schemas/ev4-automation-work-package-catalog-index.schema.json
schemas/ev4-automation-work-package-file.schema.json
schemas/ev4-automation-work-package-catalog.schema.json
```

Each package file wraps exactly one existing Work Package record:

```json
{
  "schema": "ev4-automation-work-package-file@1.0.0",
  "id": "WP-RESP-009",
  "work_package": {
    "id": "WP-RESP-009"
  }
}
```

The package record must continue to validate against `#/$defs/work_package` in the current catalog schema. The reassembly validator must enforce equality between the wrapper `id`, the nested `work_package.id`, the index entry `id`, and the filename.

## Deterministic ordering and parity

The index order is ascending by the numeric suffix of `WP-RESP-NNN`. Reassembly must reject:

- duplicate IDs;
- duplicate paths;
- ID/path/filename mismatch;
- missing indexed files;
- unindexed package files;
- non-canonical JSON formatting;
- package-record drift from the approved monolithic catalog;
- metadata deletion or addition outside the approved schema;
- any changed evidence or readiness boundary claim.

`content_sha256` is calculated over the exact canonical UTF-8 bytes of each package file, including one trailing newline.

## Boundary preservation

This contract does not:

- create submitted evidence;
- mutate Issue #8;
- authorize real pilot execution;
- establish production or release readiness;
- establish live-render, export, accessibility, pixel-perfect, or responsive-correctness validation;
- treat CI, catalog parity, migration completion, or merged PRs as domain evidence.

All existing false evidence and readiness claims must remain false during migration and reassembly.

## PR-B acceptance requirements

`WP-RESP-009/PR-B` must add the actual index and package files, deterministic reassembly/parity validator, negative fixtures, CI wiring, controller-path changes, documentation, and STATUS parity. It must prove round-trip equality against the current canonical catalog before any authority-mode transition.
