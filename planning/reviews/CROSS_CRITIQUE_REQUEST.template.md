# Cross-Critique Request Template

Use this file as the handoff packet for a separate reviewer step.

```yaml
task_ref: RQ-0000
task_type: automation_control
task_sensitivity: sensitive
reviewer_role: strict_pessimistic_reviewer
temperature_policy: temperature_0_1_recommended
prompt_file: prompts/CROSS_CRITIQUE_STRICT_REVIEWER_PROMPT.md
required_output_schema: ev4-responsive-task-quality-review@1.0.0
```

## Inputs to provide

```text
- task spec from planning/EV4_ROLLING_QUEUE.json
- changed files or PR diff
- CI result
- run ledger record if present
- self-critique summary
- acceptance criteria
```

## Required reviewer decision

```text
pass | needs_follow_up | blocked
```

The reviewer must not mark a sensitive task pass unless deterministic checks pass and cross-critique fields are completed.
