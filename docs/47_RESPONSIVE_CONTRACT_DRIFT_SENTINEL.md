# Responsive Contract Drift Sentinel

Status: repository consistency guard  
Work Package: `WP-RESP-006`  
Implementation slices: `WP-RESP-006/PR-A` inventory, `WP-RESP-006/PR-B` fixtures/docs/CI

## Purpose

The sentinel detects divergence among the responsive automation-control contract, Work Package catalog, STATUS projection, validation command index, active contract/schema/validator index, and the primary Validate workflow.

Authoritative inventory:

```text
planning/EV4_RESPONSIVE_CONTRACT_DRIFT_SENTINEL.json
```

Executable check:

```bash
python validation/e2e/run_responsive_contract_drift_sentinel_check.py
```

The check verifies that every owned surface and owner check resolves to a repository-local file, required Validate commands remain active rather than commented out, duplicate owned paths are rejected, and all evidence/readiness boundary values remain false.

## Negative fixture coverage

The validator executes focused mutation fixtures:

```text
validation/fixtures/invalid/responsive_contract_drift_missing_owner_check.invalid.json
validation/fixtures/invalid/responsive_contract_drift_commented_command.invalid.json
```

The first proves that an owned surface cannot silently lose its validator owner. The second proves that a required command appearing only as a YAML comment does not satisfy workflow parity.

These fixtures are mutation specifications consumed by the sentinel validator; they are not responsive runtime evidence.

## CI path

The primary `.github/workflows/validate.yml` workflow runs the sentinel on both supported Python versions. A successful run proves only repository consistency for the inspected ownership inventory and negative fixture behavior.

## Explicit non-claims

Passing the sentinel does not prove or upgrade any of the following:

```yaml
production_ready: false
release_ready: false
live_render_validated: false
export_json_validated: false
accessibility_passed: false
pixel_perfect: false
responsive_correctness_validated: false
```

It does not create submitted evidence, mutate Issue #8, authorize a pilot, or convert CI success into domain evidence.
