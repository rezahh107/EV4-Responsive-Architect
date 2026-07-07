# Prompt 04 Handoff — Responsive Producer Adoption

```yaml
branch: project-gate-prompt-04-responsive-producer-adoption
status: pending_merge
next_allowed_prompt: Prompt 5 after human review and merge
prompt_5_handoff_block: true
```

## Files changed

Prompt 4 adds a Responsive pipeline manifest, Responsive Stage Payload schema, viewport ledger schema, breakpoint and Elementor capability registries, Project Gate vendored common contract carriers, validation fixtures, a pinned reusable workflow caller, and this handoff.

## Tests run

Recorded by final agent response. Do not treat CI as responsive correctness evidence.

## Tests not run

Live viewport rendering, Elementor export validation, accessibility pass, production readiness, and Prompt 5 cross-repository routing were not run.

## Coverage advanced

- Mode separation for `design_to_responsive_tree` and `responsive_repair`.
- Architecture identity preservation and Architecture Mutation Veto in the machine payload path.
- Matching viewport evidence isolation.
- Producer Gate Export with `producer_emitted_gate_artifact` and `silent_fallback_allowed: false`.
- Stage Bundle v1 tracked separately from the Project Gate common lock.

## Rules still gap

Real browser evidence and final Project Gate acceptance remain `insufficient_evidence` until Prompt 5 and human-run viewport validation.

## New diagnostics

- Invalid cross-viewport Responsive Stage Payload fixture.
- Invalid silent-fallback Producer Gate Export fixture.

## CLI/CI changes

- `validation/project_gate/validate_responsive_producer_adoption.py`
- `.github/workflows/verify-vendored-common-contract.yml`

## Important design decisions

- The common lock locks only `producer-gate-export.v1`; Stage Bundle v1 is verified and referenced separately.
- User summary remains documentation; machine truth is in schema, fixtures, manifest, and export artifacts.
- Project Gate routing is not implemented in this prompt.

## Web or official sources used

Project Gate commit `ea19c22c32458068e167b267da8b819e9263cdf7` was inspected via immutable GitHub raw content fallback because direct local `git fetch` was blocked by the environment proxy.

## Open PR handling

PR 141 was treated as unrelated to Prompt 4 and not used as a dependency. Its known changed files are outside Prompt 4 carriers: `validation/e2e/run_issue_to_packet_bridge_check.py` and `validation/fixtures/valid/issue_to_packet_bridge.valid.json`.

## Blockers and remaining insufficient_evidence

- Human review is mandatory.
- Exact CI for the PR head is not observed in this local environment.
- Live responsive correctness is not claimed.
- Prompt 5 integration is blocked by scope.
