# Shadow-Mode Preparation Path

Work Package: `WP-RESP-004`
PR slice: `WP-RESP-004/PR-B`
Capability area: `pilot_readiness_boundary`

This document records the manual shadow-mode preparation path after the readiness boundary guard was hardened. It is a blocked preparation path only. It does not create submitted evidence, mutate Issue #8, authorize a real pilot, or upgrade production, release, live-render, export, accessibility, pixel, or responsive-correctness claims.

## Current boundary

```yaml
real_submitted_packet_present: false
issue_8_mutation_allowed: false
real_pilot_execution_allowed: false
pilot_allowed_to_start: false
production_ready: false
release_ready: false
live_render_validated: false
export_json_validated: false
accessibility_passed: false
pixel_perfect: false
responsive_correctness_validated: false
ci_success_is_domain_evidence: false
```

## What shadow-mode preparation means

Shadow-mode preparation may inspect repository-local fixtures, dry-run readiness reports, and boundary diagnostics so an operator can understand what would still be required before any real pilot route exists.

It may produce planning notes such as:

```yaml
readiness_report_review: repository_check_only
blocking_reasons_reviewed: true
visible_flags_reviewed: true
required_next_action_reviewed: true
operator_decision: blocked_or_prepare_missing_inputs
submitted_evidence_created: false
issue_8_mutated: false
real_pilot_started: false
```

These notes are not evidence. They must not be attached to Issue #8 as submitted evidence unless a future explicit authorization and submitted-mode contract allow it.

## Allowed operator actions

An operator may:

1. Run repository validation commands against committed fixtures.
2. Generate or inspect dry-run readiness reports from repository-local packet fixtures.
3. Record missing evidence, conflict, or visible-flag observations as planning-only notes.
4. Route blockers back to the owning EV4 stage when evidence is missing, conflicting, or only visual/static.
5. Keep all readiness and production claims false.

## Forbidden operator actions

An operator must not:

1. Create, label, or upload submitted evidence.
2. Modify Issue #8 or mark Issue #8 evidence as satisfied.
3. Start, schedule, or authorize a real pilot.
4. Treat `ready_for_shadow_mode_pilot` or `partial_ready_with_visible_flags` as production, release, live-render, export, accessibility, pixel, or responsive-correctness proof.
5. Treat CI success, fixture success, merged PRs, catalog progress, or Work Package progress as domain evidence.
6. Infer tablet/mobile evidence from desktop-only material.
7. Convert sample, fixture, template, or placeholder packet behavior into a real submitted-mode claim.

## Manual command sequence

Run from repository root after installing dependencies:

```bash
python -m pip install -r requirements.txt
python validation/e2e/run_pilot_readiness_check.py
python validation/e2e/run_pilot_readiness_boundary_check.py
python validation/e2e/run_submitted_packet_readiness_dry_run.py --self-test
python validation/e2e/run_evidence_intake_check.py --self-test
python validation/e2e/run_issue_8_preflight_boundary_check.py
```

For a specific packet review, use an explicit packet path and preserve the result as planning-only unless the packet is a future authorized real submitted-mode packet:

```bash
python validation/e2e/run_pilot_readiness_check.py --packet validation/fixtures/valid/evidence_intake_packet.valid.json --out examples/smart-home-connector/readiness/PILOT_READINESS_REPORT.generated.json
```

If the report is blocked, rerun with `--allow-blocked` only for inspection of blocker diagnostics:

```bash
python validation/e2e/run_pilot_readiness_check.py --packet validation/fixtures/valid/evidence_intake_packet.blocked.valid.json --allow-blocked
```

## Stop conditions

Stop immediately if any of these would become true:

```yaml
submitted_evidence_created: true
issue_8_mutated: true
real_pilot_execution_started: true
pilot_allowed_to_start: true
production_ready: true
release_ready: true
live_render_validated: true
export_json_validated: true
accessibility_passed: true
pixel_perfect: true
responsive_correctness_validated: true
ci_success_used_as_domain_evidence: true
```

If a readiness report produces `authorization_scope: shadow_mode_only` or `authorization_scope: shadow_mode_only_with_visible_flags`, that scope remains a repository-local dry-run classification. It is not permission to run the real pilot while `real_submitted_packet_present: false` is recorded in `planning/EV4_AUTOMATION_CONTROL_STATE.json` and `STATUS.md`.

## Required evidence before any future real pilot discussion

A future real pilot discussion remains blocked until all of the following are true under then-current contracts:

1. A real submitted packet exists through an authorized Issue #8 evidence path.
2. Submitted-mode evidence intake validates the packet and rejects sample, fixture, template, and placeholder evidence.
3. Privacy, conflict, source-kind, payload-hash, and artifact-path gates pass.
4. Readiness generation produces a report from the real submitted packet without forbidden claim upgrades.
5. A human explicitly authorizes the next real-pilot action under the current repository gates.

## Boundary

This document is a manual preparation guide only. It preserves the current blocked state and records how to avoid crossing evidence, Issue #8, pilot, production, release, and responsive-correctness boundaries.
