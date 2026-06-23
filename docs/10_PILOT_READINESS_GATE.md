# Pilot Readiness Gate

Status: v0.2 conflict-summary gate

## Purpose

The Pilot Readiness Gate decides whether a validated evidence intake packet is allowed to start the smart-home connector shadow-mode pilot.

It is intentionally stricter than the human checklist and weaker than a real Elementor validation run.

## Modes

### CI fixture mode

CI mode runs the built-in positive and negative readiness paths:

```bash
python validation/e2e/run_pilot_readiness_check.py
```

This proves that:

```text
- the default valid intake packet can reach partial_ready_with_visible_flags or ready_for_shadow_mode_pilot;
- the blocked intake fixture maps to a blocked readiness status;
- readiness schema consistency is enforced;
- conflict summaries are carried forward without inventing conflict records.
```

### Submitted packet mode

Submitted packet mode validates a real or draft intake packet and writes a readiness report:

```bash
python validation/e2e/run_pilot_readiness_check.py \
  --packet examples/smart-home-connector/intake/EVIDENCE_INTAKE_PACKET.submitted.json \
  --out examples/smart-home-connector/readiness/PILOT_READINESS_REPORT.generated.json \
  --skip-schema-suite
```

Use `--allow-blocked` only when intentionally generating a blocked readiness report for review.

## Required input for submitted mode

```text
examples/smart-home-connector/intake/EVIDENCE_INTAKE_PACKET.submitted.json
```

The packet must satisfy:

```text
- schema validation;
- evidence intake semantic validation;
- privacy review acknowledgement;
- minimum desktop must-not-regress list;
- per-item evidence quality;
- breakpoint claim scope;
- intake verdict consistency.
```

## Output report

The readiness report is a persistent handoff artifact for the next pilot stage:

```text
examples/smart-home-connector/readiness/PILOT_READINESS_REPORT.generated.json
```

The report includes:

```text
- readiness_status
- structured blocking_reasons
- structured visible_flags
- evidence_conflict_summary
- required_next_action
- validation_boundary with reasons
- pilot_start_authorization
```

## Conflict summary contract

Every readiness report must include `evidence_conflict_summary`:

```text
unresolved_blocking_conflict_count
resolved_conflict_count
conflict_records[]
```

Rules:

```text
- unresolved blocking conflicts must remain blockers;
- unresolved blocking conflicts cannot be downgraded into visible_flags;
- ready or partial-ready reports must have unresolved_blocking_conflict_count=0;
- resolved conflict records must keep source_priority_applied, winning_source, and resolution_rationale visible;
- blocker conflicts from intake_verdict.blocker_conflicts are carried forward as unresolved_blocking records.
```

## Possible statuses

```text
ready_for_shadow_mode_pilot
partial_ready_with_visible_flags
blocked_missing_evidence
blocked_conflicting_evidence
blocked_privacy_review_missing
blocked_schema_or_semantic_failure
```

Status consistency is schema-enforced:

```text
ready_for_shadow_mode_pilot: no blocking reasons, no visible flags, and no unresolved blocking conflicts
partial_ready_with_visible_flags: no blocking reasons, at least one visible flag, and no unresolved blocking conflicts
blocked_conflicting_evidence: at least one blocking reason and unresolved_blocking_conflict_count >= 1
blocked_*: at least one blocking reason and no pilot authorization
```

## Validation boundary

This gate does not validate:

```text
- live Elementor rendering
- Elementor export JSON truth
- Playwright visual regression
- accessibility pass
- production readiness
```

Those boundaries are carried as explicit false claims with reasons in the readiness report.

## Pilot start authorization

A readiness report may authorize only:

```text
shadow_mode_only
shadow_mode_only_with_visible_flags
```

It may never authorize:

```text
production_ready
release_ready
live_render_validated
export_json_validated
accessibility_passed
Playwright visual regression validated
```

## Why this exists

Evidence intake can be valid while still carrying flags. The readiness gate converts intake status into a start/stop decision before pilot execution begins.

The conflict summary prevents a more dangerous failure mode: a conflicting evidence state looking ready merely because the conflict was omitted from the downstream report.
