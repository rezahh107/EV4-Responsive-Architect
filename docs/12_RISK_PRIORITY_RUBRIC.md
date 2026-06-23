# EV4 Responsive Risk & Priority Rubric

## Purpose

This rubric ranks responsive repair risk and execution priority. It is not a scoring system.

It exists to answer:

```text
Can this responsive repair planning step continue?
What must be handled first?
Which risks must be carried forward?
Does any hard gate block progress?
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

## Hard Gates

The supported hard gates are:

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

A failed blocker gate requires one of these outcomes:

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
blocker:
  required_priority: P0
  required_urgency: immediate
  cannot_route_to: no_action_note

high_architecture_mutation_risk:
  required_owner_route: main_pipeline_reroute

low_evidence_confidence:
  selected_for_repair: false
  required_next_action: request_missing_evidence
```

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

## Required Artifact

Use:

```text
schemas/ev4-responsive-risk-priority-assessment.schema.json
```

Primary CI runner:

```bash
python validation/e2e/run_risk_priority_check.py
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
