# Guarded Handoff Pack

Task: `RTAQ-0004`

This pack summarizes the active handoff surface for controlled manual use of EV4 Responsive Architect after the responsive-tree refactor. It is guarded: it packages references and boundaries only. It does not create submitted evidence, mutate Issue #8, run a pilot, or upgrade readiness claims.

## Active state

```yaml
project: EV4 Responsive Architect
active_mode: design_to_responsive_tree
secondary_mode: responsive_repair
active_queue_lineage: RTAQ
latest_merged_task_before_pack: RTAQ-0003
next_queue_task_after_pack: RTAQ-0005
production_ready: false
prompt_pack_release_ready: false
real_submitted_packet_present: false
pilot_allowed_to_start: false
```

## Active source-of-truth files

```yaml
master_status:
  - STATUS.md
  - PROJECT_MASTER_SPEC.md
queue_and_ledger:
  - planning/EV4_ROLLING_QUEUE.json
  - planning/EV4_RUN_LEDGER.json
  - planning/EV4_QUEUE_CONTROL_PLANE.json
  - planning/EV4_AUTOMATION_QUALITY_GATE.json
controlled_use_docs:
  - docs/15_CONTROLLED_USE_READINESS_SNAPSHOT.md
  - docs/16_CONTROLLED_MANUAL_FIRST_RUN_GUIDE.md
  - docs/17_VALIDATION_COMMAND_INDEX.md
```

## Active contracts

```yaml
contracts:
  - contracts/EV4_RESPONSIVE_TREE_ARCHITECTURE_CONTRACT.md
  - contracts/EV4_VIEWPORT_RELATIONSHIP_CLASSIFICATION_CONTRACT.md
  - contracts/EV4_RESPONSIVE_STRATEGY_ROUTING_CONTRACT.md
  - contracts/EV4_VIEWPORT_DISPLAY_CONTRACT.md
  - contracts/EV4_RESPONSIVE_HANDOFF_EXPORT_CONTRACT.md
```

## Active schemas

```yaml
schemas:
  - schemas/ev4-responsive-output.schema.json
  - schemas/ev4-responsive-rolling-queue.schema.json
  - schemas/ev4-responsive-run-ledger.schema.json
```

## Active validators

```yaml
validators:
  - validation/e2e/run_responsive_tree_architecture_refactor_check.py
  - validation/e2e/run_submitted_packet_eligibility_gate_check.py
  - validation/e2e/run_rolling_queue_check.py
  - validation/e2e/run_run_ledger_check.py
```

## Manual-use boundary

Manual use is allowed only as controlled repository-guided operation. A human may use the docs and validators to inspect deterministic repository behavior, prepare a responsive-tree handoff, or identify blockers. The run must stop if it would rely on fixture behavior, sample payloads, CI success, or merged PR status as real responsive evidence.

## Evidence blockers

```yaml
blocked_until_real_evidence:
  submitted_packet_creation: blocked
  issue_8_evidence_state_change: blocked
  real_pilot_execution: blocked
  production_ready_claim: blocked
  release_ready_claim: blocked
  live_render_validation_claim: blocked
  export_validation_claim: blocked
  accessibility_pass_claim: blocked
  pixel_perfect_claim: blocked
```

## Handoff checklist

Before any handoff is treated as more than controlled-use guidance, verify:

- the input packet is real and not a sample or fixture;
- Issue #8 evidence state explicitly supports the submitted packet;
- route selection is based on responsive evidence, not desktop-only inference;
- viewport-specific unknowns remain unknown rather than converted into claims;
- CI is interpreted as repository-check status only;
- pilot/readiness gates are passed by real evidence, not queue completion.

## Boundary statement

This pack is documentation only. It preserves active references and guardrails but does not validate a real responsive output, authorize a pilot, or change release/readiness state.
