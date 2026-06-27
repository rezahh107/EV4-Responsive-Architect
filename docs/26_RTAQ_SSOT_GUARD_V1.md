# RTAQ SSOT Guard v1

## Purpose

Protect the RTAQ queue, ledger, and status files from unsafe state rewrites.

The guard is designed for the failure mode seen during the closed PR #86 attempt: JSON was valid and CI passed, but state history became too compressed and too much completed-task detail was rewritten.

## Protected files

```text
planning/EV4_ROLLING_QUEUE.json
planning/EV4_RUN_LEDGER.json
STATUS.md
planning/EV4_QUEUE_CONTROL_PLANE.json
planning/EV4_AUTOMATION_QUALITY_GATE.json
```

## Required rules

```text
Use full untruncated source before mutating state files.
Do not synthesize state files from memory or partial snippets.
Use allowlisted semantic patches only.
Preserve completed historical queue tasks.
Keep ledger history append-only.
Keep JSON state files pretty-printed.
Apply a deleted-line budget before PR creation.
Do not merge transient PR lifecycle state to main.
Keep Issue #8, evidence, pilot, readiness, release, production, live-render, export, accessibility, and pixel boundaries unchanged unless the active task explicitly authorizes otherwise.
```

## Allowed patch classes

```text
append_missing_ledger_record
mark_active_task_merge_final
restore_minimum_pending_depth
update_status_final_stable_state
add_reconciliation_note
add_guard_policy_or_validator
```

## Forbidden patch classes

```text
rewrite_completed_task_title_or_objective
rewrite_completed_task_allowed_or_forbidden_work
rewrite_existing_ledger_records
minify_json_state_file
synthesize_state_file_from_memory
synthesize_state_file_from_truncated_tool_output
merge_transient_in_pr_or_executing_status_to_main
treat_green_ci_as_responsive_correctness_evidence
```

## Validator

Static repository guard:

```bash
python validation/e2e/run_rtaq_ssot_guard_check.py
```

Pairwise checkout guard:

```bash
python validation/e2e/run_rtaq_ssot_guard_check.py --base-dir /path/to/base --head-dir /path/to/head --allow-task RTAQ-0010
```

Pairwise mode checks that completed historical tasks are preserved, existing ledger records are unchanged, JSON remains readable, and deletion budget is respected.

## Boundary

This guard is repository-state hardening only. It does not create submitted evidence, modify Issue #8, authorize a real pilot, or upgrade readiness, release, production, live-render, export, accessibility, or pixel-validation claims.
