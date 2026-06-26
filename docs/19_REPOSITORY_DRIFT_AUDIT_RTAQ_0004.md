# Repository Drift Audit — RTAQ-0004

Task: `RTAQ-0004`

This audit checks repository drift across queue, status, master spec, contracts, schemas, validators, and CI boundary text. It is evidence-bounded and does not change readiness state.

## Inputs inspected

```yaml
queue:
  - planning/EV4_ROLLING_QUEUE.json
ledger:
  - planning/EV4_RUN_LEDGER.json
status:
  - STATUS.md
master_spec:
  - PROJECT_MASTER_SPEC.md
control:
  - planning/EV4_QUEUE_CONTROL_PLANE.json
  - planning/EV4_AUTOMATION_QUALITY_GATE.json
controlled_use_docs:
  - docs/15_CONTROLLED_USE_READINESS_SNAPSHOT.md
  - docs/16_CONTROLLED_MANUAL_FIRST_RUN_GUIDE.md
  - docs/17_VALIDATION_COMMAND_INDEX.md
  - docs/18_GUARDED_HANDOFF_PACK.md
  - docs/19_REPOSITORY_DRIFT_AUDIT_RTAQ_0004.md
  - docs/20_ACTIVE_CONTRACT_SCHEMA_VALIDATOR_INDEX.md
```

## Findings

### Queue and task order

```yaml
result: pass
observed:
  active_queue_lineage: RTAQ
  RTAQ-0001: merged
  RTAQ-0002: merged
  RTAQ-0003: merged
  RTAQ-0004: pending_before_this_pr
  RTAQ-0005: pending_queue_refresh
  minimum_pending_tasks_policy: 4
```

No legacy `RQ-0023` driver was observed in the active queue. The post-refactor RTAQ lineage remains the active driver.

### STATUS alignment

```yaml
result: pass
observed:
  latest_completed_task: RTAQ-0003
  next_executable_task: RTAQ-0004
  production_ready: false
  prompt_pack_release_ready: false
  real_submitted_packet_present: false
  pilot_allowed_to_start: false
```

`STATUS.md` correctly points to `RTAQ-0004` as next executable before this PR and keeps controlled-use/evidence boundaries visible.

### Master spec alignment

```yaml
result: minor_documentation_drift
observed:
  active_refactor_doc_present: true
  active_contracts_present: true
  active_schema_present: true
  active_validation_present: true
  submitted_packet_validator_not_listed_in_master_spec: true
  controlled_use_docs_not_listed_in_master_spec: true
```

This is non-blocking for RTAQ-0004 because the newer controlled-use docs and submitted-packet validator are listed in `STATUS.md` and the validation command index. The drift should be considered by `RTAQ-0005` queue refresh before deciding whether to update `PROJECT_MASTER_SPEC.md`.

### Contract/schema/validator boundary

```yaml
result: pass_with_guard
observed:
  route_vocabulary_boundary_present: true
  active_output_schema_present: true
  queue_schema_present: true
  run_ledger_schema_present: true
  ci_boundary_text_present: true
```

The active contract/schema/validator surface is indexed in the guarded handoff pack and the active index. No validation or readiness claim is upgraded by this audit.

### CI boundary text

```yaml
result: pass
observed:
  ci_success_is_repository_check_only: true
  ci_not_responsive_correctness_evidence: true
  real_pilot_requires_submitted_packet_and_readiness: true
```

The CI boundary is consistently present in queue/control/status documentation.

## Drift queue for RTAQ-0005

```yaml
candidate_follow_up:
  task: RTAQ-0005
  type: queue_refresh
  items:
    - decide whether PROJECT_MASTER_SPEC.md should list docs/15, docs/16, docs/17, docs/18, docs/19, docs/20 and the submitted-packet validator
    - record RTAQ-0004 completion in queue and ledger after merge
    - preserve minimum pending task depth after RTAQ-0004 moves from pending to merged
```

## Acceptance criteria check

```yaml
handoff_pack_guarded_by_evidence_boundaries: pass
queue_status_master_spec_drift_checked: pass
issue_8_evidence_pending_visible: pass
real_pilot_blocked_visible: pass
readiness_claims_not_upgraded: pass
```

## Boundary statement

This audit is a repository drift audit only. It does not create submitted evidence, mutate Issue #8, execute the real pilot, or claim production/release/readiness validation.
