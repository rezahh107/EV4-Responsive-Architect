# Cross-Repo Role Alignment

Patch: Patch 1 — Cross-Repo Role Alignment  
Repo role: Responsive Architect / post-build responsive validation and repair  
Shared Contracts status: future-planned only; no canonical schema migration in this patch.

## Responsive owns

- Tablet/mobile adaptation review.
- Scoped reference-family extension.
- Responsive evidence gates.
- No raw screenshot authority.
- Validation that mobile/tablet reference behavior has explicit scoped authorization.

## Responsive consumes

- Architect/CE baseline identity and handoff data.
- `golden_reference_id`.
- `golden_reference_version`.
- `golden_reference_scope`.
- `golden_reference_family`.
- Per-viewport reference authorization when responsive behavior depends on a visual reference.

## Responsive must not infer

- Mobile/tablet behavior from a desktop screenshot.
- Responsive pass status from raw screenshot evidence.
- Reference scope/family/version when absent.
- Permission to hide meaningful content from visual similarity alone.

## Cross-repo responsibilities

### Architect owns

- `reference_role` at design-intent level.
- `experience_intent` as advisory design intent.
- Desired outcome.
- Design-level source evidence.
- Approved architecture handoff.

### CE owns

- Constructability review.
- Execution strategy proof.
- `golden_reference_contract` locking/carrying after evidence review.
- `reference_paradigm_lock`.
- `paradigm_to_structure_map`.
- `build_intent_brief` structured execution seed.
- Builder package gate.
- Builder Executable Package only when zero decisions remain.

### Builder owns

- Runtime intake validation.
- Deterministic Build Intent rendering.
- Action batch execution.
- Checkpoint/evidence loop.
- Visual parity report.
- Completion wording gate.
- No design invention.

### Future shared owner

A future `EV4-Shared-Contracts` may own schemas, enums, spatial lexicon, build-intent templates, reference-family schema, and compatibility manifest. This patch must not create that repo or move canonical schemas.
