# EV4 Responsive Risk & Priority Rubric

## Purpose

This rubric ranks responsive repair risk and execution priority. It is not a scoring system.

It exists to answer:

```text
Can this responsive repair planning step continue?
What must be handled first?
Which risks must be carried forward?
Does any hard gate block progress?
Which repair candidates require mitigation before Builder execution?
```

It must not answer with a numeric score.

## Non-Purpose

This rubric does not:

```text
- select a new main architecture
- replace evidence validation
- override hard gates
- create a production-ready claim
- create a release-ready claim
- prove live Elementor rendering
- prove export JSON validity
- prove accessibility pass
- produce an average score
```

## Core Rule

```text
A hard gate failure wins over every risk level and every priority label.
```

No result like `low risk`, `P2`, or `medium confidence` may mark an assessment ready when a blocker gate failed.

## Required Artifact

Schema:

```text
schemas/ev4-responsive-risk-priority-assessment.schema.json
```

Example:

```text
examples/smart-home-connector/risk/RISK_PRIORITY_ASSESSMENT.example.json
```

Primary CI runner:

```bash
python validation/e2e/run_risk_priority_check.py
```

Parameterized report mode:

```bash
python validation/e2e/run_risk_priority_check.py \
  --assessment validation/fixtures/valid/risk_priority_assessment.valid.json \
  --out /tmp/risk_priority_assessment.generated.json
```

`--out` must end with `.generated.json`.

## Evidence Basis Requirements

Every assessment must identify its input artifacts and their hashes:

```yaml
evidence_basis:
  source_packet_ref: path-or-issue-ref
  source_packet_sha256: sha256-...
  readiness_report_ref: path
  readiness_report_sha256: sha256-...
  pilot_run_record_ref: path
  pilot_run_record_sha256: sha256-...
  packet_origin: sample_contract_fixture | real_issue_submission
  run_mode: sample_submitted_packet_dry_run | submitted_packet_shadow_mode
  issue_reference: not_applicable_sample_dry_run | GitHub issue URL
  evidence_refs: []
  evidence_confidence_floor: high | medium | low
```

Sample packets may not be used for `submitted_evidence_risk_priority`.

## Hard Gates

Supported hard gates:

```text
architecture_mutation_veto
missing_required_evidence
privacy_review_missing
desktop_baseline_missing
blocked_readiness_status
sample_packet_used_as_real
selected_candidate_conflict
unresolved_unknown_required_for_repair_selection
```

A hard gate now uses explicit fields:

```yaml
blocking_if_failed: true | false
gate_weight: hard_blocker | soft_warning
```

`blocking_if_failed: true` must pair with `gate_weight: hard_blocker`.

A failed hard blocker requires one of these outcomes:

```text
blocked_by_hard_gate
blocked_by_insufficient_evidence
route_back_to_main_pipeline
```

It cannot produce:

```text
ready_for_repair_planning
ready_with_visible_flags
```

## Ranked Dimensions

The rubric uses categorical values only.

```yaml
failure_severity:
  values: [blocker, high, medium, minor, note]

priority:
  values: [P0, P1, P2, P3, note]

evidence_confidence:
  values: [high, medium, low]

repair_urgency:
  values: [immediate, next, later, monitor]

desktop_regression_risk:
  values: [high, medium, low, not_applicable]

accessibility_risk:
  values: [high, medium, low, not_triggered, unknown]

architecture_mutation_risk:
  values: [high, medium, low, none]
```

## Priority Rules

```yaml
blocker_failure:
  aggregate_verdict: cannot_be_ready
  required_priority: P0
  required_urgency: immediate
  cannot_route_to: no_action_note

high_architecture_mutation_risk:
  required_owner_route: main_pipeline_reroute
  selected_for_repair: false
  aggregate_verdict: route_back_to_main_pipeline

low_evidence_confidence:
  selected_for_repair: false
  required_owner_route: evidence_request
  aggregate_verdict: blocked_by_insufficient_evidence
```

## Cross-Reference Rules

The runner verifies that:

```text
- failure_items[].evidence_refs exist in evidence_basis.evidence_refs
- repair_risks[].failure_refs exist in failure_items[].failure_id
- aggregate_verdict.blocking_gate_refs exist in hard_gates[].gate_id
- blocking_gate_refs point only to failed hard blocker gates
```

## Repair Risk Mitigation Rules

```yaml
risk_level_high:
  required_mitigation_check: rollback_plan_required

desktop_regression_risk_high:
  required_mitigation_check: desktop_recheck_each_step

accessibility_risk_high:
  required_mitigation_check: accessibility_gate_required

architecture_mutation_risk_high:
  required_mitigation_check: route_back_to_main_pipeline_required
```

Generic mitigation text such as `be careful` is not acceptable.

## Forbidden Score Behavior

Forbidden fields and claims:

```text
score
numeric_score
responsive_score
readiness_score
average_score
numeric_score_claimed
average_score_used_to_override_gate
```

The validator rejects numeric-score fields and score override claims.

## Negative Path Coverage

The runner includes a controlled negative case suite for:

```text
- failed hard gate with ready verdict
- blocking ref to unknown gate
- blocker failure with ready verdict
- blocker failure with wrong priority/urgency
- high architecture mutation not routed back
- low confidence still treated as ready
- unknown evidence reference
- repair referencing unknown failure
- high repair risk missing rollback
- high desktop risk missing desktop recheck
- high accessibility risk missing accessibility gate
- high architecture repair risk missing reroute check
- sample packet used as submitted assessment
```

## Valid Verdicts

```text
ready_for_repair_planning
ready_with_visible_flags
blocked_by_hard_gate
blocked_by_insufficient_evidence
route_back_to_main_pipeline
```

## Release Boundary

This rubric may support a shadow-mode pilot or builder repair planning. It does not make the project production-ready.
