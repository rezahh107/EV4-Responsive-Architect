# Validation Command Index

Task: `RTAQ-0003`
Updated by: `RTAQ-0052`

This index lists repository validation commands for controlled manual use. Command success is repository-check evidence only; it is not responsive correctness evidence and does not authorize production, release, real pilot, export, live-render, accessibility, or pixel-validation claims.

## Dependency setup

```bash
python -m pip install -r requirements.txt
```

## Primary Validate chain

The current primary repository validation chain is the `Validate` GitHub Actions workflow in `.github/workflows/validate.yml`. For pull requests, pushes to `main`, and exact-SHA manual recovery dispatches, it runs the repository-supported Python matrix and executes:

```bash
python validation/e2e/run_rolling_queue_check.py
python validation/e2e/run_run_ledger_check.py
python validation/e2e/run_task_quality_gate_check.py
python validation/e2e/run_submitted_packet_eligibility_gate_check.py
python validation/e2e/run_responsive_tree_architecture_refactor_check.py
python validation/e2e/run_submitted_packet_readiness_dry_run.py --self-test
python validation/e2e/run_evidence_intake_check.py --self-test
python validation/e2e/run_evidence_intake_submitted_mode_path_check.py
python validation/e2e/run_evidence_intake_submitted_payload_hash_check.py
python validation/e2e/run_evidence_intake_fixture_matrix_check.py
python validation/e2e/run_pilot_readiness_check.py
python validation/e2e/run_pilot_readiness_boundary_check.py
python validation/e2e/run_issue_8_preflight_boundary_check.py
python validation/e2e/run_issue_to_packet_bridge_check.py
python validation/e2e/run_builder_responsive_input_boundary_check.py
python validation/e2e/run_rtaq_ssot_guard_check.py
python validation/e2e/run_status_merged_foundation_guard_check.py
python validation/e2e/run_automation_control_state_check.py
```

## Manual evidence-intake commands

Use submitted mode only for an explicit non-default Issue #8 real-submission packet path. These commands do not create submitted evidence, do not mutate Issue #8, and do not authorize pilot execution by themselves:

```bash
python validation/e2e/run_evidence_intake_check.py --self-test
python validation/e2e/run_evidence_intake_check.py --packet issue-8/evidence_intake_packet.submitted.json --submitted-mode
python validation/e2e/run_evidence_intake_submitted_mode_path_check.py
python validation/e2e/run_evidence_intake_submitted_payload_hash_check.py
python validation/e2e/run_evidence_intake_submitted_payload_hash_check.py --packet issue-8/evidence_intake_packet.submitted.json
python validation/e2e/run_evidence_intake_fixture_matrix_check.py
```

A real pilot may only proceed after a valid submitted packet and readiness gates required by the current repository contracts. CI success or self-test success is never a substitute for submitted evidence.

## Manual readiness and boundary commands

These commands inspect deterministic readiness and boundary behavior. They are repository checks only; they do not prove live render correctness or production readiness:

```bash
python validation/e2e/run_submitted_packet_readiness_dry_run.py --self-test
python validation/e2e/run_pilot_readiness_check.py
python validation/e2e/run_pilot_readiness_boundary_check.py
python validation/e2e/run_issue_8_preflight_boundary_check.py
python validation/e2e/run_issue_to_packet_bridge_check.py
python validation/e2e/run_builder_responsive_input_boundary_check.py
```

## Control-plane and archive commands

These commands preserve repository execution discipline and historical queue/ledger boundaries:

```bash
python validation/e2e/run_rolling_queue_check.py
python validation/e2e/run_run_ledger_check.py
python validation/e2e/run_task_quality_gate_check.py
python validation/e2e/run_rtaq_ssot_guard_check.py
python validation/e2e/run_status_merged_foundation_guard_check.py
python validation/e2e/run_automation_control_state_check.py
```

## Legacy/manual guard commands

The repository may still contain older guard validators for inspecting historical submitted-evidence guard behavior. They are not the primary Validate chain and must not be used to bypass current submitted-mode, Issue #8, or readiness gates:

```bash
python validation/e2e/run_submitted_packet_source_kind_lock_check.py
python validation/e2e/run_submitted_privacy_review_guard_check.py
python validation/e2e/run_submitted_evidence_completeness_contract_check.py
python validation/e2e/run_submitted_readiness_status_contract_check.py
python validation/e2e/run_submitted_packet_artifact_path_allowlist_check.py
```

Manual guard command success still means only that the bounded repository guard behavior passed for its fixtures or inspected inputs. It must not be used to claim that a real submitted packet exists, that Issue #8 evidence is satisfied, or that a real pilot may start.

## Automatic workflow boundary

The GitHub Actions workflow runs the primary Validate chain on pull requests and pushes to `main`, with a same-head `workflow_dispatch` recovery path that verifies the requested ref resolves to the supplied exact SHA. Its success means the configured repository checks passed. It does not prove that a real submitted packet exists, that Issue #8 has real evidence, or that the responsive output is production/release ready.

## Manual-only interpretation

The commands can be used to inspect deterministic repository behavior:

- responsive-tree architecture contracts, schema, and route fixtures
- invalid fixture rejection
- submitted-packet eligibility failure modes
- submitted evidence source-kind, completeness, readiness-status, artifact-path, submitted-mode, payload-hash, Issue #8 identity, issue-to-packet bridge, and privacy guard behavior
- pilot readiness report generation boundaries
- task quality-gate policy shape and required boundary assertions
- queue, ledger, control-state, and STATUS checkpoint discipline
- boundary text preservation

They must not be used to bypass the real submitted-packet gate or pilot-readiness gate.

## Required stop conditions

Stop and do not upgrade claims if:

- real submitted evidence is absent
- Issue #8 remains evidence-pending
- the run would treat fixture or sample behavior as real evidence
- the run would rely on CI success as responsive validation
- any required validation command fails or is not run

## Boundary

This command index is documentation only. It does not create evidence, mutate Issue #8, run the pilot, or change readiness state.
