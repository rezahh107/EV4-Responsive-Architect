# E2E-001 — Textual Fixture Contract Validation

Version: 0.1.0-draft  
Status: contract_validation_only  
Production status: not_production_ready

## Purpose

`E2E-001` validates that the repository can execute a minimum EV4 Responsive Architect contract chain using JSON Schemas, valid/invalid fixtures, and CI.

It is intentionally textual and repository-backed. It does not use Elementor, browser rendering, export JSON, Playwright, or real screenshots.

## Validated Chain

```text
/main-pipeline-handoff-ingest
/responsive-evidence-ingest-ledger
/repair-option-analysis
/responsive-repair-plan
/accessibility-reading-order-gate
/css-selector-safety-check
```

## Commands

```bash
python validation/schema_validator/validate_schemas.py
python validation/e2e/run_e2e_001.py
```

## What This Proves

```text
- core schema files parse and validate;
- valid fixtures pass;
- invalid fixtures fail;
- the minimum textual contract chain is present;
- the CSS selector semantic gate catches a known unsafe selector case;
- E2E-001 can run in CI.
```

## What This Does Not Prove

```text
- live Elementor rendering;
- Elementor export JSON validation;
- Playwright visual regression;
- pixel matching;
- real responsive repair success;
- accessibility pass;
- production readiness.
```

## Next After E2E-001

```text
1. Run the smart-home connector pilot case.
2. Add E2E-002 real builder evidence plan.
3. Expand non-core schemas as needed by the pilot.
```
