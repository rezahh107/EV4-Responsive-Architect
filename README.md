# EV4 Responsive Architect

سیستم post-build responsive repair، validation، و handoff برای سکشن‌های Elementor V4 که قبلاً با EV4 Architect معماری شده‌اند.

This repository stores the stable master specification, contracts, stage protocols, machine-readable schemas, state-as-code files, validation tools, and pilot fixtures for `EV4 Responsive Architect`.

## Core Idea

`EV4 Architect` answers:

```text
What is the safest, editable, Elementor-native architecture for this section?
```

`EV4 Responsive Architect` answers:

```text
After the section is built, what breaks across real viewports, who owns the repair, how do we repair atomically, and how do we prove that no other viewport regressed?
```

## Current Status

```yaml
version: 0.1.0-final-draft
status: repository_initialization_ready
production_ready: false
prompt_pack_release_ready: false
```

## Repository Layers

```text
1. Human-readable contracts
2. Machine-readable schemas
3. Stage protocols
4. State and validation tooling
5. E2E and fixture evidence
```

## Start Here

- `PROJECT_MASTER_SPEC.md`
- `STATUS.md`
- `docs/00_OVERVIEW.md`
- `contracts/MAIN_PIPELINE_HANDOFF_INPUT_CONTRACT.md`
- `contracts/ARCHITECTURE_MUTATION_VETO.md`
- `validation/schema_validator/validate_schemas.py`

## Production Boundary

This project may produce controlled builder handoffs and validation-ready repair plans. It must not claim `production_ready`, `release_ready`, `pixel_perfect`, `export_validated`, or `live_render_validated` unless matching evidence exists.
