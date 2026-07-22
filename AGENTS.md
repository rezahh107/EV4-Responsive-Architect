# AGENTS.md

## Scope

These instructions apply to the whole repository unless a closer nested `AGENTS.md` or `AGENTS.override.md` overrides them.

## Role

`EV4-Responsive-Architect` owns post-build responsive validation and repair across real viewports. It does not select the original architecture, prove pre-build constructability, or perform Builder execution.

## Read First

1. `README.md`
2. `PROJECT_MASTER_SPEC.md`
3. `STATUS.md`
4. `docs/00_OVERVIEW.md`
5. `contracts/MAIN_PIPELINE_HANDOFF_INPUT_CONTRACT.md`
6. `contracts/ARCHITECTURE_MUTATION_VETO.md`
7. relevant validation, schema, fixture, and evidence files

Current contracts and executed evidence take precedence over proposals or historical notes.

## Project Gate Handoff

```text
Builder output and evidence → EV4 Project Gate → Responsive input
Responsive output and viewport evidence → final EV4 Project Gate check
```

Project Gate integration is documented, but its verifier and UI are not implemented yet. It must not replace Responsive contracts or invent evidence.

## Hard Boundaries

Do not change the selected candidate, redesign the original architecture, modify approved classes without amendment, invent missing pre-build strategy, treat one viewport as proof for another, infer hidden settings from screenshots, or claim final QA without complete evidence.

## Change Rules

- Preserve public contracts unless a breaking change is approved.
- Update contracts, schemas, validators, fixtures, E2E checks, and docs together.
- Preserve architecture identity and valid evidence.
- Add boundary, malformed-input, regression, and cross-viewport cases.
- Keep repair actions atomic and deterministic.
- Avoid unrelated refactoring.

## Validation

```bash
python -m pip install -r requirements.txt
python validation/e2e/run_responsive_tree_architecture_refactor_check.py
```

Run additional targeted checks relevant to the changed path. Report exactly what ran.

## Evidence

A screenshot proves only visible assertions it supports. Structure evidence does not prove frontend rendering, and frontend evidence does not prove hidden control values. Use `insufficient_evidence` instead of guessing.

## Wave 5 Kernel Decision Receipts

When producing or modifying a decision-bearing Responsive intake, validation report, runtime-evidence reference, mismatch report, repair request, or handoff output, render only the short human-readable Kernel decision receipt produced from the existing machine-readable `decision_lineage`.

Use the success receipt only when `decision_lineage` exists and includes `decision_family`, `decision_card_ref`, `selected_option`, `rejected_options`, `evidence_refs`, `evidence_state`, and `consumer_stage` with sufficient validated evidence. If any required trace field is missing, use the insufficient-evidence warning instead of a green check.

Runtime mismatch wording must remain a warning. It must not convert a mismatch into a new Responsive design choice and must not claim `runtime_monitor_enforced`, downstream enforcement, production readiness, or new Responsive design authority.

A human-readable receipt is presentation-layer text only. It must not replace the machine trace, invent Kernel decision cards, invent evidence refs, silently replace upstream decisions, or author `resolved` or `production_ready` fields.

## Pull Requests

State the behavior or contract changed, affected viewports and ownership boundaries, validation executed, regression coverage, and remaining unknowns.

## Decision Escape Route Review

Before opening or completing any PR that changes schemas, validators, prompts, fixtures, pipeline docs, handoff artifacts, fallback behavior, responsive validation outputs, runtime evidence outputs, or decision-bearing outputs, review `planning/DECISION_ESCAPE_ROUTES.yml`.

Do not mark an escape route as resolved unless its `enforcement_status` meets the required threshold for its risk and `session_scope`; a Critical cross-turn rule is not resolved by single-artifact `ci_enforced` evidence. Do not add authored `resolved` or `production_ready` fields; those are derived audit conclusions.

Responsive validates runtime/responsive behavior; it must not redesign architecture or claim runtime enforcement unless inspected evidence proves the required carriers exist.

## Temporary Shared UX/UI Policy Adapter

Use `policies/EV4_TEMP_CROSS_REPO_UX_UI_STANDARDS_POLICY_r002.md` only as a supplemental policy below repository authority.

```yaml
policy_id: EV4-TEMP-CROSS-REPO-UX-UI-STANDARDS-POLICY-r002
revision: r002
filename: EV4_TEMP_CROSS_REPO_UX_UI_STANDARDS_POLICY_r002.md
sha256: f09b6978e10833c1ab3c3e35a9128db894684c5ed9cd876fa87699016b6def95
repository_role: responsive_architect
local_consumption_scope: post-build viewport, content, direction, input, state, focus, reflow, obstruction, and target validation
role_must:
  - validate actual rendered behavior
  - test viewport, content, direction, input and state conditions
  - distinguish observation from inference
  - verify source order, focus order, reflow, obstruction and target usability
role_must_not:
  - treat device labels as proof of behavior
  - claim unobserved viewport results
  - replace upstream semantic intent
```

Keep nonmaterial routing internal. Represent material failures, unresolved requirements, evidence gaps, and downstream obligations through existing Responsive-supported fields or a concise visible status when continuation or owner action is affected. Do not add unsupported decision outputs or hidden-storage claims.

`r001` remains an immutable historical revision. A filename, ID, revision, byte, or digest mismatch is `TEMP_UX_UI_POLICY_IDENTITY_MISMATCH`. This adapter does not create Kernel adoption, new design authority, or a parallel approval path.
