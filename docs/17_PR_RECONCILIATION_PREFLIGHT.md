# PR Reconciliation Preflight

Version: 1.0.0
Status: active_policy_companion

## Purpose

The EV4 rolling queue controller must not start a new queue task while a previous automation-created PR is still open. Review handling is part of the previous PR lifecycle, not a separate queue task.

This policy exists to prevent parallel PR drift, stale queue overwrites, missed Gemini/reviewer comments, and rushed merges after first green CI.

## Core rule

```yaml
single_active_automation_pr_policy:
  enabled: true
  review_handling_counts_as_queue_task: false
  open_automation_pr_effect: block_new_queue_task_until_reconciled
```

## Required preflight order

Before selecting a new queue task, the controller must:

```text
1. Search for open automation-created PRs.
2. If any exist, stop new task selection.
3. Inspect CI status for the PR head SHA.
4. Inspect mergeability and current head SHA.
5. Read PR comments, review comments, Gemini/reviewer feedback, and human review threads.
6. Classify feedback as:
   - no_actionable_feedback
   - small_in_scope_feedback
   - broad_new_scope_feedback
   - blocking_or_ambiguous_feedback
7. If feedback is small and in scope, fix the same PR and rerun CI.
8. If feedback is broad new scope, create a backlog/queue candidate and do not force it into the current PR.
9. Merge only when CI is green, PR is mergeable, delayed-review/comment-check policy is satisfied, and no actionable feedback remains.
10. After merge, update queue, run ledger, and STATUS.md if required.
11. Usually stop after merge. Start the next queue task only if it is trivial, bounded, and there is no queue/ledger/status drift.
```

## Feedback classification

```yaml
no_actionable_feedback:
  action: merge_if_green_mergeable_and_review_window_satisfied

small_in_scope_feedback:
  action: fix_same_pr_rerun_ci_and_recheck_comments
  examples:
    - formatting drift in a changed JSON file
    - missing required boundary assertion in the same ledger record
    - naming mismatch introduced by the same PR

broad_new_scope_feedback:
  action: create_backlog_or_queue_candidate
  forbidden: force_into_current_pr
  examples:
    - redesign an unrelated schema family
    - add a new execution subsystem
    - change project scope beyond the PR acceptance criteria

blocking_or_ambiguous_feedback:
  action: mark_needs_review_or_blocked
  forbidden: merge_until_resolved
```

## Forbidden shortcuts

```text
- Starting a new queue task while an automation PR is open.
- Creating a parallel automation PR before resolving the previous one.
- Treating Gemini/reviewer review handling as an independent queue task.
- Merging without re-reading comments/reviews after the delayed window.
- Overwriting queue or ledger files from stale snapshots.
- Treating comments, CI success, or merged PRs as responsive evidence.
```

## Relationship to delayed reviewer policy

Delayed review waits for late comments before merge.
PR reconciliation decides what the controller does at the beginning of the next run.

They are complementary:

```text
delayed_review_policy = do not merge too early
pr_reconciliation_policy = do not start the next task before resolving the previous PR
```

## Completion boundary

A queue task is not complete merely because a PR exists or CI is green. Completion requires:

```text
- PR state reconciled
- CI checked
- comments/reviews checked
- small actionable feedback fixed or broad feedback recorded as follow-up
- merge state recorded when merged
- queue/ledger/STATUS sync completed when required
```

## Non-domain boundary

This policy improves automation reliability only. It does not validate real responsive evidence, does not authorize pilot execution, and does not support production-ready, release-ready, export-validated, live-render-validated, or accessibility-passed claims.
