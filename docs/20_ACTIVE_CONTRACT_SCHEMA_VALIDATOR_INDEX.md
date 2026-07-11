# Active Contract / Schema / Validator Index

Task: `WP-RESP-007/PR-B`
Updated by: `automation/wp-resp-007-pr-b-matrix-fixtures-validator`

This index records the active repository surfaces needed for controlled manual use and catalog-backed handoff. It is an index only; it does not validate a real submitted packet, mutate Issue #8, authorize pilot execution, or upgrade readiness.

## Source-of-truth hierarchy

```yaml
primary_status:
  - STATUS.md
master_spec:
  - PROJECT_MASTER_SPEC.md
automation_control_state:
  - planning/EV4_AUTOMATION_CONTROL_STATE.json
work_package_catalog:
  - planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json
contract_drift_inventory:
  - planning/EV4_RESPONSIVE_CONTRACT_DRIFT_SENTINEL.json
archived_queue:
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
  main_pipeline_handoff_input:
    path: contracts/MAIN_PIPELINE_HANDOFF_INPUT_CONTRACT.md
    role: upstream handoff input boundary
  builder_to_responsive_input_boundary:
    path: contracts/BUILDER_TO_RESPONSIVE_INPUT_BOUNDARY.md
    role: Builder -> Responsive intake decision boundary
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
  viewport_inheritance_reset_decision_matrix:
    path: contracts/VIEWPORT_INHERITANCE_RESET_DECISION_MATRIX.md
    role: deterministic viewport inheritance, reset, inactive, explicit, and unknown decision boundary
```

## Schemas

```yaml
schemas:
  responsive_output:
    path: schemas/ev4-responsive-output.schema.json
    role: responsive output package schema
  builder_responsive_input:
    path: schemas/ev4-builder-responsive-input.schema.json
    role: builder-to-responsive input schema
  automation_control_state:
    path: schemas/ev4-automation-control-state.schema.json
    role: post-queue automation control-state schema
  automation_work_package_catalog:
    path: schemas/ev4-automation-work-package-catalog.schema.json
    role: catalog-backed Work Package selection schema
  rolling_queue:
    path: schemas/ev4-responsive-rolling-queue.schema.json
    role: archived RTAQ queue schema
  run_ledger:
    path: schemas/ev4-responsive-run-ledger.schema.json
    role: RTAQ ledger schema
  automation_quality_gate:
    path: schemas/ev4-responsive-automation-quality-gate.schema.json
    role: automation quality-gate policy schema
  task_quality_review:
    path: schemas/ev4-responsive-task-quality-review.schema.json
    role: deterministic task quality review schema
```

## Primary Validate chain

```yaml
primary_validate_workflow:
  path: .github/workflows/validate.yml
  triggers:
    - pull_request
    - push to main
    - workflow_dispatch with exact ref and expected_sha
  python_matrix:
    - "3.11"
    - "3.13"
  validators:
    rolling_queue:
      path: validation/e2e/run_rolling_queue_check.py
      role: archived queue shape and throughput policy checks
    run_ledger:
      path: validation/e2e/run_run_ledger_check.py
      role: ledger shape and record-policy checks
    task_quality_gate:
      path: validation/e2e/run_task_quality_gate_check.py
      role: task quality gate policy, PR reconciliation, delayed-review, and task-quality review checks
    submitted_packet_eligibility:
      path: validation/e2e/run_submitted_packet_eligibility_gate_check.py
      role: submitted-packet eligibility failure-mode guard
    responsive_tree_refactor:
      path: validation/e2e/run_responsive_tree_architecture_refactor_check.py
      role: responsive-tree repository contract/schema/fixture checks and delegated RTAQ checks
    submitted_packet_readiness_dry_run:
      path: validation/e2e/run_submitted_packet_readiness_dry_run.py
      role: dry-run harness for readiness packet behavior; self-test mode only in CI
    evidence_intake_semantic_guard:
      path: validation/e2e/run_evidence_intake_check.py
      role: evidence intake semantic guard; self-test mode only in CI
    evidence_intake_submitted_mode_path_guard:
      path: validation/e2e/run_evidence_intake_submitted_mode_path_check.py
      role: submitted-mode path, Issue #8 ref, and artifact allowlist guard
    evidence_intake_submitted_payload_hash_guard:
      path: validation/e2e/run_evidence_intake_submitted_payload_hash_check.py
      role: real submitted payload identity hash format guard
    evidence_intake_fixture_matrix:
      path: validation/e2e/run_evidence_intake_fixture_matrix_check.py
      role: submitted evidence fixture matrix consistency guard
    pilot_readiness_generator:
      path: validation/e2e/run_pilot_readiness_check.py
      role: pilot readiness generation checks without real pilot authorization
    pilot_readiness_boundary:
      path: validation/e2e/run_pilot_readiness_boundary_check.py
      role: pilot readiness boundary checks
    issue_8_preflight_boundary:
      path: validation/e2e/run_issue_8_preflight_boundary_check.py
      role: Issue #8 preflight reference and boundary checks
    issue_to_packet_bridge:
      path: validation/e2e/run_issue_to_packet_bridge_check.py
      role: Issue #8-to-submitted-packet bridge guard without packet creation or pilot authorization
    builder_responsive_input_boundary:
      path: validation/e2e/run_builder_responsive_input_boundary_check.py
      role: Builder -> Responsive input boundary checks
    responsive_contract_drift_sentinel:
      path: validation/e2e/run_responsive_contract_drift_sentinel_check.py
      role: CI-visible parity guard for owned responsive contract, STATUS, command-index, active-index, and workflow surfaces
    viewport_inheritance_reset_matrix:
      path: validation/e2e/run_viewport_inheritance_reset_matrix_check.py
      role: fixture-backed viewport inheritance/reset decision guard; repository-check evidence only
    rtaq_ssot_guard:
      path: validation/e2e/run_rtaq_ssot_guard_check.py
      role: queue, ledger, status, and SSOT policy preservation guard
    status_merged_foundation_guard:
      path: validation/e2e/run_status_merged_foundation_guard_check.py
      role: bounded foundation checkpoint and readiness-boundary guard
    automation_control_state:
      path: validation/e2e/run_automation_control_state_check.py
      role: post-queue automation control-state guard
    automation_work_package_catalog:
      path: validation/e2e/run_automation_work_package_catalog_check.py
      role: catalog-backed Work Package selection and replenishment governance guard
```

## Primary Validate parity rule

```yaml
parity_owner: .github/workflows/validate.yml
status_parity_reference: STATUS.md automatic_check
manual_command_index_reference: docs/17_VALIDATION_COMMAND_INDEX.md
active_index_reference: docs/20_ACTIVE_CONTRACT_SCHEMA_VALIDATOR_INDEX.md
required_behavior:
  - every primary Validate validator must be discoverable in STATUS.md
  - every primary Validate validator must be documented in docs/17_VALIDATION_COMMAND_INDEX.md
  - every primary Validate validator must be represented in this active index
boundary: repository-check parity only; not responsive correctness evidence
```

## Manual or legacy evidence-bound guard validators

```yaml
manual_or_legacy_guard_validators:
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
    role: active contract, schema, validator, and workflow parity index
  responsive_contract_drift_sentinel:
    path: docs/47_RESPONSIVE_CONTRACT_DRIFT_SENTINEL.md
    role: WP-RESP-006 sentinel behavior, fixtures, CI path, and non-domain-evidence boundary
```
