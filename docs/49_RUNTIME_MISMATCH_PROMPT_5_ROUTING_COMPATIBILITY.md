# Runtime-Mismatch Reopen to Prompt 5 Routing Compatibility

Work Package: `WP-RESP-015`
Slice: `WP-RESP-015/PR-C`

## Purpose

This document records the repository-local compatibility boundary between a runtime-mismatch authoritative-reopen request and the Prompt 5 Project Gate routing envelope. It documents implemented contract, schema, fixture, validator, and CI behavior; it does not execute external transport or establish domain correctness.

## Active artifacts

| Surface | Path | Role |
|---|---|---|
| Compatibility contract | `contracts/compatibility/RUNTIME_MISMATCH_PROMPT_5_ROUTING_COMPATIBILITY.md` | Human-readable authority and compatibility boundary |
| Compatibility schema | `contracts/compatibility/runtime-mismatch-prompt-5-routing-compatibility.v1.schema.json` | Pinned dependency, lineage, action, route, diagnostic, authority, and boundary shape |
| Positive fixture | `validation/fixtures/compatibility/runtime-mismatch-prompt5/valid/runtime_mismatch_prompt5_compatibility.valid.json` | Canonical compatible reopen-to-route example |
| Negative fixture | `validation/fixtures/compatibility/runtime-mismatch-prompt5/invalid/runtime_mismatch_prompt5_missing_lineage.invalid.json` | Persistent missing-lineage rejection example |
| Focused validator | `validation/e2e/run_runtime_mismatch_prompt_5_compatibility_check.py` | Schema and semantic compatibility checks plus deterministic negative self-tests |
| Primary CI entry | `validation/e2e/run_runtime_mismatch_reopen_package_check.py` | Invokes the focused compatibility validator from the primary `Validate` workflow |

## Compatibility guarantees

A compatible package must:

1. pin the runtime-mismatch and Prompt 5 dependency identities, versions, blob identities, and schema hashes;
2. preserve shared Kernel decision lineage and producer-export lineage;
3. request exactly `reopen_for_authoritative_review`;
4. map to `decision=route`, `transport_eligible=true`, and target `ev4-project-gate`;
5. carry no rejection diagnostic for the compatible route;
6. keep EV4 Decision Kernel as decision owner and EV4 Project Gate as transport owner;
7. forbid Responsive from replacing or reinterpreting the Kernel decision or executing Project Gate transport; and
8. keep every evidence, pilot, readiness, release, export, accessibility, pixel, and responsive-correctness claim false.

The validator also fails closed on missing lineage, rejected-option drift, invalid evidence references, unsupported action, diagnostic mismatch, authority substitution, dependency schema-version drift, and boundary upgrades.

## Validation

Focused command:

```bash
python validation/e2e/run_runtime_mismatch_prompt_5_compatibility_check.py
```

Primary-chain command:

```bash
python validation/e2e/run_runtime_mismatch_reopen_package_check.py
```

The primary command runs the runtime-mismatch package checks and then invokes the focused compatibility validator. `.github/workflows/validate.yml` runs the primary command on the supported Python matrix.

## Authority boundary

| Concern | Authority |
|---|---|
| Original or replacement technical decision | EV4 Decision Kernel |
| Local route eligibility | EV4 Responsive Architect |
| Transport execution and downstream gate behavior | EV4 Project Gate |

Responsive may observe a mismatch and package an authoritative-review request. It may not claim that transport occurred, author a replacement decision, or treat receipt or diagnostic prose as Kernel authority.

## Evidence and readiness boundary

Validation success, schema validity, fixture acceptance, CI success, PR review, or merge are repository-check evidence only. They do not:

- create submitted evidence or mutate Issue #8;
- authorize or run a real pilot;
- prove production or release readiness;
- prove live-render or export validity;
- prove accessibility conformance or pixel-perfect output; or
- prove responsive correctness.

All corresponding claims remain false until separate real-evidence gates and explicit authority permit an upgrade.
