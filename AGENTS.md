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

## Pull Requests

State the behavior or contract changed, affected viewports and ownership boundaries, validation executed, regression coverage, and remaining unknowns.
## Decision Escape Route Review

Before opening or completing any PR that changes schemas, validators, prompts, fixtures, pipeline docs, handoff artifacts, fallback behavior, responsive validation outputs, runtime evidence outputs, or decision-bearing outputs, review `planning/DECISION_ESCAPE_ROUTES.yml`.

Do not mark an escape route as resolved unless its `enforcement_status` meets the required threshold for its risk and `session_scope`; a Critical cross-turn rule is not resolved by single-artifact `ci_enforced` evidence. Do not add authored `resolved` or `production_ready` fields; those are derived audit conclusions.

Responsive validates runtime/responsive behavior; it must not redesign architecture or claim runtime enforcement unless inspected evidence proves the required carriers exist.

