# Reusable Rolling Queue Automation Playbook

Version: 1.1.0
Status: reusable_pattern_document
Audience: a language model or automation agent with no prior project context

## 1. Problem

Scheduled automations often stop making reliable progress because their state lives in a prompt, chat memory, or a vague instruction such as “continue the project.” The next run may not know which task was completed, which PR is active, whether CI passed, whether a reviewer commented after the first CI pass, or whether a task was only started.

The common failure mode is:

```text
A scheduled model run performs a useful action.
The next run does not have durable execution state.
It repeats work, skips work, starts unrelated work, or claims progress that did not happen.
```

The solution is to move execution state into the repository and make the scheduled automation a queue controller.

## 2. Core pattern

```text
Repository = durable project memory
Rolling Queue = next execution intent
Control Plane = non-negotiable execution rules
Run Ledger = audit history of completed controller runs
Quality Gate = deterministic and cross-critique review record
CI = deterministic validation gate
PR = change and review boundary
Automation Prompt = executor instructions, not project memory
```

The automation executes one bounded task, critiques that same task, records the outcome, and stops.

## 3. Separation of authority

Keep these concerns separate.

| Concern | Source of truth |
|---|---|
| Next execution task | `planning/ROLLING_QUEUE.json` |
| Controller rules | `planning/QUEUE_CONTROL_PLANE.json` |
| Quality policy | `planning/AUTOMATION_QUALITY_GATE.json` |
| Completed run history | `planning/RUN_LEDGER.json` or append-only event log |
| Technical validity of repo changes | CI workflows |
| Change boundary | GitHub PR metadata and review state |
| Human-readable project state | `STATUS.md` |
| Domain truth or evidence | project-specific evidence files, manifests, validated artifacts, and issues |

Critical boundary rules:

```text
Queue task completion != domain evidence validation.
CI success != product or domain validation.
Merged PR != authoritative evidence.
Run ledger record != release readiness.
```

This is not a contradiction with storing `merge_sha` or `ci_conclusion` in the ledger. Those fields are technical change evidence: they prove what repository change happened and whether technical checks passed. They do not prove domain truth. If a task changes domain evidence, the ledger should also include a separate `domain_evidence_ref` or explicitly state `domain_evidence_ref: null`.

## 4. Minimum repository files

Create these files in the target project:

```text
planning/ROLLING_QUEUE.json
planning/QUEUE_CONTROL_PLANE.json
planning/AUTOMATION_QUALITY_GATE.json
planning/RUN_LEDGER.json
schemas/rolling-queue.schema.json
schemas/queue-control-plane.schema.json
schemas/automation-quality-gate.schema.json
schemas/task-quality-review.schema.json
schemas/run-ledger.schema.json
validation/e2e/run_rolling_queue_check.py
validation/e2e/run_task_quality_gate_check.py
validation/e2e/run_run_ledger_check.py
docs/ROLLING_QUEUE.md
STATUS.md
```

Names may be project-specific. Do not copy domain-specific evidence rules blindly; copy the control pattern.

## 5. Rolling queue contract

The queue should contain:

```text
project or queue id
queue status
controller policy
active cycle
task list
current pending target or horizon policy
refresh task policy
```

The “four pending tasks” rule is a default horizon, not a universal law. It prevents the controller from running out of planned work, but it must not cause task inflation.

Recommended policy:

```yaml
planning_horizon:
  default_pending_target: 4
  allow_lower_pending_count_when:
    - waiting_for_external_evidence
    - project_has_less_than_four_legitimate_next_tasks
    - refresh_task_is_pending
  forbid_artificial_tasks: true
```

Each task should include immutable intent and mutable runtime state. A simple starter shape:

```json
{
  "id": "RQ-0001",
  "title": "Sync status and active issue",
  "status": "pending",
  "priority": "P0",
  "task_type": "repo_sync",
  "scope": "Update STATUS.md and the active tracking issue so they match the current schema and project state.",
  "allowed_work": ["read repo state", "update STATUS.md", "update active issue", "run CI if repo files changed"],
  "forbidden_work": ["start real execution without required evidence", "claim release readiness", "perform a second unrelated task"],
  "acceptance_criteria": ["STATUS.md reflects current state", "active issue references current schema", "no stale schema version remains"],
  "critique_required": true
}
```

A task must be small enough to complete, critique, and repair in one automation run unless it explicitly enters `awaiting_external` while waiting for CI, review, or human input.

## 6. Control plane contract

The control plane stores non-negotiable execution rules.

Minimum fields:

```json
{
  "schema": "queue-control-plane@1.0.0",
  "status": "active",
  "truth_boundary": {
    "queue_task_completion_is_not_evidence_validation": true,
    "ci_success_is_not_product_validation": true,
    "merged_pr_is_not_authoritative_evidence": true,
    "queue_may_not_upgrade_evidence_truth": true
  },
  "lease_policy": {
    "enabled": true,
    "max_active_leases": 1,
    "lease_duration_minutes": 55,
    "stale_lease_action": "block_and_require_reconcile",
    "optimistic_locking_required": true
  },
  "transition_policy": {
    "forbidden_transitions": [
      {"from": "pending", "to": "completed"},
      {"from": "awaiting_external", "to": "completed"},
      {"from": "blocked", "to": "completed"}
    ]
  }
}
```

The first implementation may validate lease and transition policy as a contract before enforcing full runtime leases. Document that limitation.

## 7. Task states and transitions

Recommended states:

```text
pending
leased
executing
awaiting_external
needs_review
blocked
completed
superseded
cancelled
```

Forbidden direct transitions:

```text
pending -> completed
awaiting_external -> completed without polling external evidence
blocked -> completed
```

A controller must not silently repair drift. If state does not match reality, mark the task `blocked`, `needs_review`, or `awaiting_external` with a diagnostic.

## 8. Lease and crash recovery

A lease prevents concurrent scheduled runs from mutating queue state at the same time.

Recommended lease object:

```json
{
  "controller_run_id": "RQRUN-20260624T080000Z-8f21",
  "leased_at": "2026-06-24T08:00:00Z",
  "expires_at": "2026-06-24T08:55:00Z",
  "base_queue_commit_sha": "abc123",
  "controller_version": "1.0.0"
}
```

Crash recovery rules:

```text
1. The next controller run owns stale-lease reconciliation.
2. A stale lease never completes a task.
3. If a branch or PR was created but the ledger was not updated, reconcile from GitHub state.
4. If queue state says completed but ledger or PR evidence is missing, mark needs_review or blocked.
5. If a ledger entry is pending but the PR never existed, mark the task blocked with a diagnostic.
```

Preferred implementation:

```text
before mutation: write or prepare pending ledger intent
perform one bounded action
read actual tool result
commit queue and ledger update with expected parent SHA
```

This is not a rollback system for arbitrary code. It is a reconciliation system for controller state.

## 9. Run ledger contract

The run ledger is an audit companion, not a source of domain truth.

A ledger record should exist for each completed controller run that changes repository state.

Recommended fields:

```json
{
  "record_id": "LEDGER-0001",
  "run_id": "automation-run-001",
  "task_ref": "RQ-0001",
  "run_type": "automation_task",
  "status": "merged",
  "pr_number": 12,
  "merge_sha": "abc123",
  "ci_conclusion": "success",
  "domain_evidence_ref": null,
  "created_at_utc": "2026-06-24T08:00:00Z",
  "artifacts": [
    {"path": "docs/example.md", "artifact_type": "documentation", "status": "created"}
  ],
  "quality_review_ref": "TQR-0001",
  "critique_summary": ["The task closed the immediate gap."],
  "boundary_assertions": ["no_release_claim", "no_unrelated_task", "ci_checked"],
  "next_queue_effect": "RQ-0002 remains pending."
}
```

Ledger retention policy:

```yaml
active_ledger_max_records: 100
archive_after_records: 100
archive_path_pattern: planning/archive/RUN_LEDGER_YYYYMMDD_NNN.json
active_ledger_must_keep_index: true
ci_must_validate_active_ledger_and_archive_index: true
```

## 10. Automation quality gate

Self-critique is required but insufficient.

Use two layers:

```text
Deterministic critique:
  Schema, CI, acceptance criteria, artifact list, queue state, ledger state, stale references, boundary assertions.

Cross-critique:
  A separate reviewer record for sensitive tasks using a strict pessimistic reviewer role and prompt separation.
```

Sensitive task examples:

```text
schema_hardening
automation_control
readiness_gate
sample_vs_real_safety
risk_priority_engine
evidence_boundary
production_boundary
ci_workflow
```

A task quality review record should include:

```yaml
deterministic_checks:
  acceptance_criteria_checked: true
  scope_respected: true
  forbidden_work_absent: true
  ci_checked_or_no_ci_reason_recorded: true
  artifacts_listed: true
  queue_state_checked: true
  ledger_state_checked: true
  stale_reference_search_done: true
  delayed_bot_review_window_checked: true
  boundary_assertions_checked: true
self_critique:
  recorded: true
cross_critique:
  required: true
  status: completed
  reviewer_role: strict_pessimistic_reviewer
completion_allowed: true
```

For sensitive tasks, completion must be blocked if cross-critique is missing.

## 11. Delayed reviewer window

Some review bots or human reviewers comment several minutes after a PR is opened or after CI first turns green. Do not merge sensitive automation-control PRs immediately after the first green CI result.

Recommended policy:

```yaml
delayed_review_policy:
  enabled: true
  minimum_wait_minutes_before_merge: 10
  review_sources_to_check:
    - github_review_threads
    - gemini-code-assist[bot]
    - human_reviewer
  block_merge_on_unresolved_high_priority_review: true
  if_feedback_arrives_after_merge: create_follow_up_task_and_record_in_ledger
```

The controller should re-read PR comments/reviews before merge. If high-priority review feedback appears, handle it before merge or create a follow-up if it arrives after merge.

## 12. CI gates

At minimum, CI should validate:

```text
queue schema
control plane schema
quality gate schema
run ledger schema
queue task ID uniqueness
pending horizon policy
illegal transitions
completed tasks contain completion evidence
ledger records are complete
task quality records are valid
```

Recommended commands:

```bash
python validation/e2e/run_rolling_queue_check.py
python validation/e2e/run_task_quality_gate_check.py
python validation/e2e/run_run_ledger_check.py
```

## 13. Controller algorithm

Each scheduled run should do one bounded transition:

```text
START
1. Read repo state: main HEAD, open PRs, CI, STATUS, project spec, active issue, queue, control plane, quality gate, run ledger.
2. Validate queue, control plane, quality policy, and ledger.
3. Reconcile queue state with real GitHub state. Do not silently fix drift.
4. Select exactly one bounded task or one external poll action.
5. Lease or mark the task according to policy.
6. Execute only that task.
7. If CI/review is asynchronous, set awaiting_external and stop.
8. If completion is possible, run deterministic checks.
9. Run or require cross-critique for sensitive tasks.
10. Re-read PR comments/reviews before merge when the delayed reviewer window applies.
11. Apply only small in-scope corrections.
12. Update queue and run ledger.
13. If a larger issue remains, create a follow-up task.
END
```

## 14. Prompt tiers

Do not put every rule into one long unstructured prompt. Split the controller prompt into three tiers.

```text
Tier 1 — Invariants:
  one task only, repo is memory, no release claims without evidence, no silent drift, CI/review gates required.

Tier 2 — Session context:
  repository, active queue file, active issue, current branch policy, current blockers.

Tier 3 — Task scope:
  selected task, allowed work, forbidden work, acceptance criteria, expected output.
```

If tiers conflict, Tier 1 wins.

## 15. Queue refresh and audit-of-audit

A queue-refresh task audits the last completed work units and writes the next bounded tasks. It is itself a normal task and must also have a task-quality review record.

There is no infinite regress. The refresh task is reviewed once by the same quality gate. If the quality review finds a larger issue, create a follow-up task instead of recursively auditing forever.

## 16. Blocked escalation

A blocked task must not remain invisible.

Recommended fields:

```yaml
blocked_since:
escalate_after_hours: 72
blocked_reason_code:
required_external_action:
notification_target:
```

CI or a scheduled controller check should report tasks that exceed the escalation window.

## 17. Anti-patterns

Avoid:

```text
one scheduled prompt per task with no repo-backed queue
marking a task completed because a PR was opened
marking a task completed because CI started
marking evidence valid because a queue task completed
merging immediately after first green CI when delayed reviewers are active
making unrelated improvements inside the current task
updating docs without updating queue or ledger state
storing the only project state in chat memory
letting sample evidence stand in for real submitted evidence
```

## 18. Acceptance criteria

The automation system is not implemented merely because a prompt exists.

Minimum implementation:

```yaml
queue_file_exists: true
queue_schema_validated: true
control_plane_exists: true
truth_boundaries_recorded: true
automation_quality_gate_exists: true
self_critique_declared_insufficient: true
cross_critique_required_for_sensitive_tasks: true
run_ledger_exists: true
run_ledger_validated: true
ci_runs_queue_checks: true
tasks_have_allowed_and_forbidden_work: true
tasks_have_acceptance_criteria: true
completed_tasks_have_audit_records: true
one_task_per_run_policy_exists: true
real_execution_blocked_without_evidence: true
release_claims_forbidden_without_evidence: true
```

Advanced implementation:

```yaml
lease_runtime_enforced: true
optimistic_locking_tested: true
runtime_queue_branch_exists: true
queue_repo_reconciliation_tested: true
stale_lease_recovery_tested: true
illegal_transition_tests_exist: true
action_required_detected: true
missing_ci_jobs_detected: true
blocked_escalation_enabled: true
ledger_archiving_enabled: true
```

## 19. Migration path

```text
Phase 1 — Repo-backed queue
Create queue, schema, control plane, run ledger, docs, and CI checks.

Phase 2 — Controller prompt
Update scheduled automation to read the queue and perform one bounded task per run.

Phase 3 — Ledger discipline
Require completed repo-changing tasks to have ledger records.

Phase 4 — Quality gate
Add deterministic checks, cross-critique records, and delayed reviewer window.

Phase 5 — Transition and lease hardening
Add runtime leases, legal transitions, stale lease recovery, and queue/repo reconciliation.

Phase 6 — Runtime branch split
Move runtime queue state to a dedicated control branch only after lease and reconciliation are tested.

Phase 7 — Full controller maturity
Add dry-run controller mode, expected-head merge checks, action_required detection, missing-job detection, review-state validation, blocked escalation, and ledger archiving.
```

## 20. How to adapt to another project

Start with generic files and then map domain-specific concepts.

```text
generic required input artifact -> target project evidence packet or work item
start gate -> target project readiness gate
domain validation -> target project validation type
active tracking issue -> target project issue/ticket
release claim -> target project release or production claim
```

Do not require a new reader to understand the original project before they understand the pattern. Keep domain examples in an appendix or mapping section.

## 21. Final rule

The scheduled model should not be trusted because it remembers. It should be trusted only when the repository state, queue, quality gate, ledger, CI, PR review state, and active issue agree.
