# Active Contract / Schema / Validator Index

Task: `RTAQ-0004`
Updated by: `RTAQ-0007`

This index records the active repository surfaces needed for controlled manual use and queue-safe handoff. It is an index only; it does not validate a real submitted packet or authorize pilot execution.

## Source-of-truth hierarchy

```yaml
primary_status:
  - STATUS.md
master_spec:
  - PROJECT_MASTER_SPEC.md
active_queue:
  - planning/EV4_ROLLING_QUEUE.json
run_ledger:
  - planning/EV4_RUN_LEDGER.json
control_plane:
  - planning/EV4_QUEUE_CONTROL_PLANE.json
quality_gate:
  - planning/EV4_AUTOMATION_QUALITY_GATE.json
```

## Responsive-tree contracts

```yaml
contracts:
  responsive_tree_architecture:
    path: contracts/EV4_RESPONSIVE_TREE_ARCHITECTURE_CONTRACT.md
    role: output shape and primary route boundary
  viewport_relationship_classification:
    path: contracts/EV4_VIEWPORT_RELATIONSHIP_CLASSIFICATION_CONTRACT.md
    role: desktop/mobile/tablet relationship classification
  responsive_strategy_routing:
    path: contracts/EV4_RESPONSIVE_STRATEGY_ROUTING_CONTRACT.md
    role: safe route selection
  viewport_display:
    path: contracts/EV4_VIEWPORT_DISPLAY_CONTRACT.md
    role: display and breakpoint behavior boundary
  responsive_handoff_export:
    path: contracts/EV4_RESPONSIVE_HANDOFF_EXPORT_CONTRACT.md
    role: builder handoff/export package boundary
```

## Schemas

```yaml
schemas:
  responsive_output:
    path: schemas/ev4-responsive-output.schema.json
    role: responsive output package schema
  rolling_queue:
    path: schemas/ev4-responsive-rolling-queue.schema.json
    role: active RTAQ queue schema
  run_ledger:
    path: schemas/ev4-responsive-run-ledger.schema.json
    role: active RTAQ ledger schema
```

## Active validators

```yaml
validators:
  responsive_tree_refactor:
    path: validation/e2e/run_responsive_tree_architecture_refactor_check.py
    role: responsive-tree repository contract/schema/fixture checks and delegated RTAQ checks
    ci_path: automatic
  submitted_packet_eligibility:
    path: validation/e2e/run_submitted_packet_eligibility_gate_check.py
    role: negative eligibility checks for submitted-packet gate failure modes
    ci_path: delegated through responsive-tree checker
  rolling_queue:
    path: validation/e2e/run_rolling_queue_check.py
    role: active queue shape and policy checks
    ci_path: delegated through responsive-tree checker
  run_ledger:
    path: validation/e2e/run_run_ledger_check.py
    role: ledger shape and record-policy checks
    ci_path: delegated through responsive-tree checker
  task_quality_gate:
    path: validation/e2e/run_task_quality_gate_check.py
    role: task quality gate policy checks
    ci_path: delegated through responsive-tree checker
```

## Manual evidence-bound guard validators

```yaml
manual_guard_validators:
  submitted_packet_source_kind_lock:
    path: validation/e2e/run_submitted_packet_source_kind_lock_check.py
    role: submitted source-kind lock guard for evidence-bound paths
    ci_path: manual_or_legacy_guard; not a real submitted-packet validation claim
  submitted_privacy_review_guard:
    path: validation/e2e/run_submitted_privacy_review_guard_check.py
    role: privacy-review acknowledgement guard for submitted evidence paths
    ci_path: manual_or_legacy_guard; not a real submitted-packet validation claim
  submitted_evidence_completeness_contract:
    path: validation/e2e/run_submitted_evidence_completeness_contract_check.py
    role: submitted evidence completeness contract guard
    ci_path: manual_or_legacy_guard; not a real submitted-packet validation claim
  submitted_readiness_status_contract:
    path: validation/e2e/run_submitted_readiness_status_contract_check.py
    role: submitted readiness status contract guard
    ci_path: manual_or_legacy_guard; not a real pilot-readiness approval
  submitted_packet_artifact_path_allowlist:
    path: validation/e2e/run_submitted_packet_artifact_path_allowlist_check.py
    role: submitted packet artifact path allowlist guard
    ci_path: manual_or_legacy_guard; not a real submitted-packet validation claim
```

These manual guard validators may document or inspect deterministic guard behavior only. They do not create submitted evidence, satisfy Issue #8, authorize pilot execution, or prove responsive correctness.

## Controlled-use docs

```yaml
controlled_use_docs:
  readiness_snapshot:
    path: docs/15_CONTROLLED_USE_READINESS_SNAPSHOT.md
    role: non-production controlled-use readiness boundary
  first_run_guide:
    path: docs/16_CONTROLLED_MANUAL_FIRST_RUN_GUIDE.md
    role: manual first-run inputs, stops, and flow
  validation_command_index:
    path: docs/17_VALIDATION_COMMAND_INDEX.md
    role: repository validation commands and CI boundary
  guarded_handoff_pack:
    path: docs/18_GUARDED_HANDOFF_PACK.md
    role: guarded handoff references and blockers
  repository_drift_audit:
    path: docs/19_REPOSITORY_DRIFT_AUDIT_RTAQ_0004.md
    role: RTAQ-0004 drift findings and RTAQ-0005 follow-up candidates
  active_contract_schema_validator_index:
    path: docs/20_ACTIVE_CONTRACT_SCHEMA_VALIDATOR_INDEX.md
    role: active contract, schema, and validator index
  queue_refresh_audit:
    path: docs/21_QUEUE_REFRESH_AUDIT_RTAQ_0005.md
    role: fifth-cycle queue refresh audit and next bounded task plan
  master_status_drift_closure:
    path: docs/22_MASTER_STATUS_DRIFT_CLOSURE_RTAQ_0006.md
    role: RTAQ-0006 closure of remaining master-spec/status/index drift
```

## CI interpretation

```yaml
ci_success_means:
  - configured repository checks passed
ci_success_does_not_mean:
  - responsive correctness validated
  - real submitted packet exists
  - Issue #8 evidence is satisfied
  - real pilot may start
  - production or release readiness is achieved
  - export, accessibility, live-render, or pixel validation passed
```

## Blockers before stronger claims

```yaml
required_before_stronger_claims:
  - real submitted packet with non-placeholder payload identity
  - Issue #8 evidence reference consistency
  - submitted-packet eligibility gate pass on real evidence
  - explicit pilot-readiness approval
  - real pilot execution evidence
  - separate validation evidence for live render, export, accessibility, and pixel behavior if those claims are requested
```

## Boundary statement

This index is documentation only. It does not create submitted evidence, mutate Issue #8, execute a pilot, or upgrade readiness/release/production state.
