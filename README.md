# EV4 Responsive Architect

Status: constructability_gate_alignment_planned  
Role: `post_build_responsive_validation_and_repair_system`  
Primary input: built section evidence after Builder execution  
Production readiness: false unless full downstream evidence exists

---

## Summary

`EV4 Responsive Architect` is the post-build responsive validation and repair layer for Elementor V4 sections.

It does not choose the original architecture, does not prove constructability before build, and does not perform interactive Builder execution.

```text
Architect says what should be built.
Constructability Engineer proves how it can be safely built.
Builder executes the proven strategy.
Responsive Architect validates and repairs post-build responsive behavior.
```

---

## Core Question

`EV4 Responsive Architect` answers:

```text
After the section is built, what breaks across real viewports,
who owns the repair,
how do we repair atomically,
and how do we prove that no other viewport regressed?
```

---

## Position in the EV4 Pipeline

```text
EV4 Architect Repo
        │
        ▼
EV4 Constructability Engineer Repo
        │
        ▼
EV4 Builder Assistant Repo
        │
        ▼
EV4 Responsive Architect
```

Responsive Architect runs after Builder execution or on real viewport evidence. It should not be used to bypass missing Constructability review.

---

## Repository Role

This repository owns:

```text
- post-build viewport inspection
- responsive issue classification
- responsive repair ownership
- atomic repair planning
- regression prevention across viewports
- validation-ready repair handoff
- evidence-bound responsive status tracking
```

This repository must not:

```text
- select or rescore the original architecture
- change selected_candidate_id
- add or remove approved class names without approved amendment
- invent missing implementation strategy that should have been resolved pre-build
- treat desktop-only unknowns as mobile/tablet proof
- claim production readiness without full evidence
```

---

## Constructability Boundary

Some failures should be caught before Builder execution by the Constructability Engineer, not repaired later as responsive work.

Examples:

```text
- connector geometry not proven
- overlay containment not defined
- SVG strategy missing
- asset source missing
- interaction behavior not approved
- Dynamic Loop assumed without approval
```

Responsive Architect may repair actual viewport behavior after build evidence exists, but it should not normalize pre-build guessing.

---

## Required Evidence

Responsive claims require evidence such as:

```text
- desktop screenshot
- tablet screenshot
- mobile screenshot
- frontend rendering evidence
- browser evidence when relevant
- export / diagnostics evidence when relevant
```

A screenshot proves only visible assertions it supports. A frontend screenshot does not prove hidden Elementor control values. A structure-panel screenshot does not prove responsive rendering.

---

## Current Status

```yaml
version: 0.1.0-final-draft
status: repository_initialization_ready
constructability_gate_aligned: planned
production_ready: false
prompt_pack_release_ready: false
```

---

## Repository Layers

```text
1. Human-readable contracts
2. Machine-readable schemas
3. Stage protocols
4. State and validation tooling
5. E2E and fixture evidence
```

---

## Start Here

```text
PROJECT_MASTER_SPEC.md
STATUS.md
docs/00_OVERVIEW.md
contracts/MAIN_PIPELINE_HANDOFF_INPUT_CONTRACT.md
contracts/ARCHITECTURE_MUTATION_VETO.md
validation/schema_validator/validate_schemas.py
```

---

## Companion Repositories

```text
EV4 Architect Repo
Recommended slug: EV4-Architect-Repo
Current slug: elementor-v4-architect-prompt-pack

EV4 Constructability Engineer Repo
https://github.com/rezahh107/EV4-Constructability-Engineer-Repo

EV4 Builder Assistant Repo
https://github.com/rezahh107/EV4-Builder-Assistant-Repo
```

---

## Production Boundary

This project may produce controlled responsive repair handoffs and validation-ready repair plans.

It must not claim:

```text
production_ready
release_ready
pixel_perfect
export_validated
live_render_validated
browser_validated
responsive_final_qa_complete
```

unless matching evidence exists.
