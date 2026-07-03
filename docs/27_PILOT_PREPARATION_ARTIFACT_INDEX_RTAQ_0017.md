# RTAQ-0017 Pilot Preparation Artifact Index

## Purpose

This document prepares a non-executing pilot artifact index and operator checklist for a future EV4 responsive-architecture pilot. It is preparation only. It does not start, authorize, simulate, or complete a real pilot.

## Current Boundary State

```yaml
real_submitted_packet_present: false
pilot_allowed_to_start: false
readiness_claims_upgraded: false
production_ready: false
release_ready: false
live_render_validated: false
export_json_validated: false
accessibility_passed: false
pixel_perfect: false
```

The only allowed use of this artifact is to identify which repository-owned records and checks an operator must inspect before a later pilot can be considered. It cannot replace submitted evidence, Issue #8 evidence, readiness gates, live-render observations, export validation, accessibility validation, or pixel review.

## Artifact Index

| Artifact | Role | Current use allowed | Pilot-start authority |
| --- | --- | --- | --- |
| `STATUS.md` | Human-readable operating status and boundary summary | Confirm that repository status still says no submitted packet and pilot is blocked | None |
| `planning/EV4_ROLLING_QUEUE.json` | Execution intent and bounded task plan | Confirm RTAQ task sequencing and pending preparation scope | None |
| `planning/EV4_RUN_LEDGER.json` | Historical run and merge record | Confirm prior terminal queue history without upgrading evidence | None |
| `validation/e2e/run_rolling_queue_check.py` | Rolling queue policy and task-shape guard | Run only as repository validation | None |
| `validation/e2e/run_run_ledger_check.py` | Run ledger structure and boundary guard | Run only as repository validation | None |
| `validation/e2e/run_task_quality_gate_check.py` | Task quality and artificial-work guard | Run only as repository validation | None |
| `validation/e2e/run_rtaq_ssot_guard_check.py` | RTAQ single-source-of-truth guard | Run only as repository validation | None |
| `validation/e2e/run_submitted_packet_eligibility_gate_check.py` | Submitted-packet eligibility guard | Run only as repository validation | None |
| `validation/e2e/run_submitted_packet_readiness_dry_run.py` | Dry-run explanation and placeholder/sample rejection | Explain missing readiness fields and reject non-real packets | None |
| `validation/e2e/run_responsive_tree_architecture_refactor_check.py` | Repository refactor invariant check | Confirm repository contract consistency | None |
| `.github/workflows/validate.yml` | Primary repository validation workflow | Require exact-head repository checks before merging changes | None |
| Future submitted packet | External submitted evidence packet | Not present in repository at this time | Required but not sufficient |
| Future readiness verdict | Gate result after valid submitted packet | Not present in repository at this time | Required but not sufficient |

## Operator Checklist Before Any Future Pilot

All items below must be true before a later run may even consider a real pilot path. If any item is false or unknown, the pilot remains blocked.

1. A real submitted packet exists from the required source channel.
2. The packet is not a sample, placeholder, template, default fixture, synthetic record, or controller-created substitute.
3. The packet includes `packet_id`, `packet_origin`, `packet_status`, `issue_reference`, `section_id`, `selected_candidate_id`, `main_ev4_handoff`, `desktop_baseline`, `evidence_items`, `breakpoint_inventory`, `privacy_review`, `evidence_complete_definition`, and `intake_verdict`.
4. The submitted packet eligibility gate passes for the real packet.
5. The submitted packet readiness dry-run does not block the packet.
6. Issue #8 state, if required by the current contract, is observed directly rather than inferred from queue text.
7. No repository document still says `real_submitted_packet_present: false` for the active pilot candidate.
8. No active review thread, failing validation, or required approval blocks the pilot-preparation change.
9. The operator has not converted CI success into responsive correctness, production readiness, release readiness, live-render validation, export validation, accessibility pass, or pixel-perfect evidence.
10. Any pilot execution command is explicitly approved by the current repository contract after the above gates pass.

## Explicit Non-Actions

This artifact does not:

- create or modify submitted evidence;
- modify Issue #8;
- run or authorize a real pilot;
- claim responsive correctness;
- claim production or release readiness;
- claim live-render, export, accessibility, or pixel validation;
- allow a sample packet to stand in for real evidence;
- permit numeric score output to override any readiness gate.

## Critique

- Root gap addressed: operators now have a single non-executing index for what must be inspected before any later pilot path.
- Enforcement boundary: this document is intentionally not a validator and does not grant readiness. Existing gates remain authoritative.
- Completeness correction: the index includes queue, ledger, task-quality, RTAQ SSOT, submitted-packet, readiness dry-run, and refactor validators so operators do not skip repository-owned guards.
- Truth boundary: all pilot, readiness, production, release, live-render, export, accessibility, and pixel claims remain false unless separate submitted evidence and gates later prove otherwise.
