# Controlled Manual First-Run Guide

Task: `RTAQ-0003`

This guide describes how to perform a controlled manual first run of the EV4 Responsive Architect repository without upgrading evidence, readiness, production, release, or pilot claims.

## Preconditions

Before a controlled manual run, confirm:

```yaml
repository_branch: main_or_review_pr_branch
active_lineage: RTAQ
real_submitted_packet_present: false
issue_8_evidence_state: evidence_pending
pilot_allowed_to_start: false
```

If a real submitted packet is later introduced, it must pass the submitted-packet eligibility gate before it can be treated as submitted evidence. Until then, all runs remain controlled manual review only.

## Manual inputs

A controlled first run may inspect or prepare the following inputs:

1. `ev4_responsive_start_packet`
2. approved desktop tree from the upstream EV4 process
3. explicit mobile/tablet evidence or explicit absence records
4. target breakpoint scope
5. viewport policy when variants are possible

Do not infer missing tablet/mobile evidence from desktop-only material. If an input is absent, record it as absent instead of converting it into a validation claim.

## Manual execution flow

Use this order:

1. Read [STATUS.md](../STATUS.md) and [PROJECT_MASTER_SPEC.md](../PROJECT_MASTER_SPEC.md).
2. Read [RESPONSIVE_TREE_ARCHITECTURE_REFACTOR_v0.3.0.md](RESPONSIVE_TREE_ARCHITECTURE_REFACTOR_v0.3.0.md).
3. Read the active contracts in [contracts/](../contracts/).
4. Inspect [schemas/ev4-responsive-output.schema.json](../schemas/ev4-responsive-output.schema.json).
5. Run the validation command index below.
6. Review whether any output is only planning material or eligible for a future evidence gate.
7. Stop if any evidence, readiness, or pilot boundary would be crossed.

## Stop conditions

Stop immediately if any of these occur:

- A run would create or label submitted evidence without an eligible real packet.
- A run would modify Issue #8 without explicit task authorization.
- A run would start or authorize the real pilot.
- A run would claim production readiness or release readiness.
- A run would claim live-render validation, export validation, accessibility pass, or pixel-perfect validation.
- A run would treat CI success or fixture success as real responsive correctness evidence.

## Validation command index

Run from repository root:

```bash
python validation/e2e/run_responsive_tree_architecture_refactor_check.py
python validation/e2e/run_submitted_packet_eligibility_gate_check.py
```

If dependencies are missing, install the repository requirements first:

```bash
python -m pip install -r requirements.txt
```

The automated GitHub workflow currently runs the responsive-tree refactor check. The submitted-packet eligibility gate is part of the active validation index, but its result remains repository-check evidence only.

## Expected outputs

A controlled manual run may produce notes such as:

```yaml
classification_review: draft_or_blocked
route_review: draft_or_blocked
handoff_review: draft_or_blocked
validation_plan: planning_only
real_evidence_status: not_present
pilot_status: blocked
```

These outputs are not submitted evidence and must not be used as readiness proof.

## First-run boundary

This guide is for controlled manual use only. It does not authorize real pilot work, submitted-evidence creation, Issue #8 mutation, production use, release use, or higher-readiness claims.
