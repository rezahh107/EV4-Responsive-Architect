# RTAQ-0027 Foundation Checkpoint Guard

## Objective

Close the verified post-merge drift after PR #108 without preserving an append-only bookkeeping loop.

## Technical decision

`merged_foundation` remains a historical checkpoint record for active repository foundations, but it is not a mandate to open a new PR after every merged PR solely to append the latest number.

The executable guard now requires a bounded checkpoint through PR #108 and a status boundary:

```yaml
foundation_checkpoint_policy: bounded checkpoints only; not append every merged PR
```

This keeps the repository from silently dropping the currently verified foundation set while preventing status-only or merge-final PR churn.

## Boundary

- This does not create submitted evidence.
- This does not mutate Issue #8.
- This does not start or authorize pilot execution.
- This does not upgrade readiness, production, release, live-render, export, accessibility, pixel, or responsive-correctness claims.
- CI success remains repository-check evidence only.

## Follow-up rule

Future STATUS updates should be batched with material semantic changes or a deliberate checkpoint refresh. They should not be created merely because another PR merged, a controller checked again, or CI completed.
