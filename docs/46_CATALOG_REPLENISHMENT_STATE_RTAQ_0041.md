# RTAQ-0041 Catalog Replenishment State

## Work Package

- Selected Work Package: `WP-RESP-005`
- Selected PR slice: `WP-RESP-005/PR-B`
- Layer: `catalog_metadata`

## Trigger

This update is state-driven. The live merged PR history shows that the original selectable catalog packages were consumed by material PR slices:

- `WP-RESP-002`: completed by PRs #144, #147, and #148.
- `WP-RESP-003`: completed by PRs #149 and #150.
- `WP-RESP-004`: completed by PRs #151 and #152.

Because these packages are completed material objectives, leaving them as `ready` would make the controller repeatedly select consumed work. The effective ready depth after marking them completed is below the catalog threshold, so replenishment is allowed under the approved state-driven trigger set.

## Catalog action

`planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json` now:

- keeps `WP-RESP-001` blocked until a real, unambiguous Issue #8 submitted evidence source exists;
- marks `WP-RESP-002`, `WP-RESP-003`, and `WP-RESP-004` as completed;
- preserves `WP-RESP-005` as non-selectable governance;
- adds three new ready, selectable material Work Packages:
  - `WP-RESP-006`: responsive contract drift sentinel;
  - `WP-RESP-007`: viewport inheritance and reset decision matrix;
  - `WP-RESP-008`: responsive handoff export boundary manifest.

## Reviewability hardening

`planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json` must remain human-reviewable because it is the approved execution source for catalog-backed automation. Compact or minified JSON makes future Work Package review unsafe because small semantic edits become large single-line diffs.

This PR therefore also hardens catalog maintainability:

- the catalog is serialized as canonical readable JSON with 2-space indentation;
- existing key order is preserved unless a deliberate schema migration requires otherwise;
- the file must end with exactly one trailing newline;
- the CI-visible catalog validator rejects compact or minified catalog JSON;
- automation controller instructions now forbid single-line catalog object serialization.

The deterministic format contract is:

```text
json.dumps(data, indent=2, ensure_ascii=False) + "\n"
```

## Catalog split evaluation

The current catalog was not split into an index plus per-Work-Package files in this PR.

Reason: PR #153 is already an active catalog replenishment PR. A broad structural split would enlarge the active diff, increase review risk, and mix a migration architecture with the smaller in-scope repair: make the current catalog readable, enforce that format, and preserve state-driven replenishment.

Recommended next Work Package, if catalog growth continues:

```yaml
suggested_work_package_id: WP-RESP-009
suggested_title: Split Work Package Catalog into Index plus Package Files
acceptance_criteria:
  - create one catalog index file and one file per Work Package
  - preserve Work Package IDs, ready states, priorities, boundaries, and allowed PR slices
  - add schema or validator support for deterministic reassembly and identity checks
  - keep Validate, STATUS, docs/17, and docs/20 in parity
  - add valid and invalid fixtures for missing package file, duplicate ID, and reordered/reassembled catalog drift
  - preserve rolling queue as historical archive only
  - preserve false evidence, pilot, readiness, production, release, export, accessibility, pixel, and responsive-correctness claims
```

## Boundary

This document and catalog update do not create submitted evidence, mutate Issue #8, authorize pilot execution, or upgrade production, release, live-render, export, accessibility, pixel, or responsive-correctness claims.

CI success remains repository-check evidence only. Catalog replenishment and catalog-format validation are not domain evidence.
