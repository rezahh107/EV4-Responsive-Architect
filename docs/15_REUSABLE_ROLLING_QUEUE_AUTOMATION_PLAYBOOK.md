# Reusable Rolling Queue Automation Playbook

Version: 1.0.0
Status: reusable_pattern_document
Audience: a language model or automation agent with no prior project context

## 1. What problem this solves

A scheduled automation often fails to move a project forward because it has no durable project memory. It may know the prompt for the next run, but it does not reliably know:

- what was already completed,
- which PR is active,
- whether CI passed,
- what task is blocked,
- what evidence is still missing,
- whether a previous run only started work but did not finish it,
- whether a task was actually reviewed or only marked done.

The failure mode is usually this:

```text
A scheduled model run performs a useful action.
The next run does not have a reliable execution state.
It either repeats work, skips work, starts unrelated work, or claims progress that did not actually happen.
```

The solution is not to create many independent scheduled prompts. The solution is to move the execution state into the repository and make the scheduled automation a queue controller.

## 2. Core idea

Use one scheduled automation that reads a repository-backed rolling queue.

```text
Repository = durable project memory
Rolling Queue = next execution intent
Control Plane = rules the controller must obey
Run Ledger = audit history of completed controller runs
CI = deterministic validation gate
PR = review and change boundary
Automation Prompt = executor instructions, not project memory
```

The scheduled automation must not be the source of truth. It should only execute one bounded task from the queue, critique that same task, update state, and stop.

## 3. Separation of authority

Keep these responsibilities separate.

| Concern | Source of truth |
|---|---|
| What task should run next | `planning/ROLLING_QUEUE.json` |
| What rules the controller must obey | `planning/QUEUE_CONTROL_PLANE.json` |
| What happened in completed controller runs | `planning/RUN_LEDGER.json` |
| Whether repo changes are technically valid | CI workflows |
| Whether a PR changed source files | GitHub PR metadata |
| Human-readable project status | `STATUS.md` |
| Project-specific truth or evidence | project evidence files, manifests, validated artifacts, and issues |

Critical rule:

```text
Queue task completion is not evidence validation.
CI success is not product validation.
Merged PR is not authoritative evidence.
Run ledger record is not production readiness.
```

In the EV4 Responsive Architect project this rule is captured by the queue control plane. The control-plane file records that queue completion must not upgrade evidence truth, CI success is not responsive validation, and real pilot execution requires a real submitted packet plus readiness pass.

## 4. Minimum repository files

Create these files in the target project:

```text
planning/ROLLING_QUEUE.json
planning/QUEUE_CONTROL_PLANE.json
planning/RUN_LEDGER.json
schemas/rolling-queue.schema.json
schemas/queue-control-plane.schema.json
schemas/run-ledger.schema.json
validation/e2e/run_rolling_queue_check.py
validation/e2e/run_run_ledger_check.py
docs/ROLLING_QUEUE.md
STATUS.md
```

Names can be project-specific. In the EV4 project these files are named:

```text
planning/EV4_ROLLING_QUEUE.json
planning/EV4_QUEUE_CONTROL_PLANE.json
planning/EV4_RUN_LEDGER.json
schemas/ev4-responsive-rolling-queue.schema.json
schemas/ev4-responsive-queue-control-plane.schema.json
schemas/ev4-responsive-run-ledger.schema.json
```

## 5. Rolling queue contract

The rolling queue should contain:

- project identifier,
- queue status,
- controller policy,
- active cycle,
- task list,
- at least four pending tasks while active,
- one queue-refresh task after each group of four bounded work units.

Recommended task shape:

```json
{
  "id": "RQ-0001",
  "title": "Sync status and active issue",
  "status": "pending",
  "priority": "P0",
  "task_type": "repo_sync",
  "scope": "Update STATUS.md and the active tracking issue so they match the current schema and project state.",
  "allowed_work": [
    "read repo state",
    "update STATUS.md",
    "update active issue",
    "run CI if repository files changed"
  ],
  "forbidden_work": [
    "start real execution without required evidence",
    "claim production readiness",
    "perform a second unrelated task"
  ],
  "acceptance_criteria": [
    "STATUS.md reflects current state",
    "the tracking issue references the current schema",
    "no stale schema version remains",
    "CI passes if repo files changed"
  ],
  "critique_required": true
}
```

A task must be small enough to complete, critique, and repair in one automation run, unless it explicitly enters `awaiting_external` while waiting for CI, review, or human input.

## 6. Control plane contract

The control plane stores non-negotiable execution rules. It protects the project from silent drift.

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

The first implementation may validate lease and transition policy as a contract before enforcing full write-mode leases. That is acceptable if the limitation is documented.

## 7. Recommended task states

Use explicit status values. Do not allow direct completion from ambiguous states.

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

Allowed examples:

```text
pending -> leased
leased -> executing
executing -> awaiting_external
executing -> needs_review
executing -> completed
blocked -> pending
blocked -> superseded
```

Forbidden examples:

```text
pending -> completed
awaiting_external -> completed
blocked -> completed
```

## 8. Lease model

A lease prevents two scheduled runs from executing the same task or mutating queue state at the same time.

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

Rules:

- only one active lease is allowed,
- a stale lease does not complete a task,
- a stale lease must be reconciled,
- a controller must not silently overwrite queue changes,
- future hardening may move runtime queue state to a dedicated branch such as `control/rolling-queue`.

## 9. Run ledger contract

The run ledger is an audit companion. It is not a replacement for the queue.

A ledger record should exist for each completed controller run that changes repository state.

Recommended record fields:

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
  "created_at_utc": "2026-06-24T08:00:00Z",
  "artifacts": [
    {"path": "docs/example.md", "artifact_type": "documentation", "status": "created"}
  ],
  "critique_summary": [
    "The task closed the immediate gap.",
    "A follow-up is needed for deeper runtime enforcement."
  ],
  "boundary_assertions": [
    "no_production_claim",
    "no_unrelated_task",
    "ci_checked"
  ],
  "next_queue_effect": "RQ-0002 remains pending."
}
```

The ledger should be validated in CI.

## 10. CI gates

At minimum, CI should validate:

```text
- queue schema
- control plane schema
- run ledger schema
- queue task ID uniqueness
- at least four pending tasks while active
- exactly one active queue-refresh rule per cycle
- illegal transitions are not present
- completed tasks contain completion evidence
- ledger records for completed controller runs are complete
```

Recommended commands:

```bash
python validation/e2e/run_rolling_queue_check.py
python validation/e2e/run_run_ledger_check.py
```

If a repository already has a main validation workflow, add the queue checks to it or run them in a separate workflow.

## 11. Controller algorithm

Each scheduled run should do exactly this:

```text
START

1. Read repository state:
   - main HEAD
   - open PRs
   - CI status
   - STATUS.md
   - project spec or master spec
   - active tracking issue
   - rolling queue
   - control plane
   - run ledger

2. Validate queue, control plane, and ledger.

3. Reconcile queue state with real GitHub state.
   Do not silently fix drift.

4. Select exactly one bounded task.

5. Execute only that task.
   If repository files change:
   - create a branch
   - commit changes
   - open a PR
   - wait for or poll CI according to project policy
   - merge only if CI is green and merge conditions are satisfied

6. Critique the same task.

7. Apply only small in-scope corrections.
   If a larger gap is found, create or update a follow-up queue task.

8. Update queue status and run ledger.

9. If fewer than four pending tasks remain, add enough bounded tasks to restore the pending target.

10. Every fifth logical work unit must be a queue-refresh task.

END
```

## 12. Queue-refresh task

A queue-refresh task must not be a generic planning note. It should audit the last four completed work units.

It must check:

- whether the previous four tasks really completed,
- whether CI passed for each repository-changing task,
- whether ledger records exist,
- whether docs drifted from live queue state,
- whether blocked items remain unresolved,
- whether the next four tasks are bounded,
- whether any real execution is blocked by missing evidence.

The refresh task then writes the next four bounded tasks plus the next refresh task.

## 13. Automation prompt template

Use this prompt for the scheduled controller:

```text
Act as the project rolling queue controller.

The repository is the only persistent project memory.

On each run, inspect the current repository state, open PRs, CI status, STATUS.md, project spec, active tracking issue, planning/ROLLING_QUEUE.json, planning/QUEUE_CONTROL_PLANE.json, and planning/RUN_LEDGER.json.

Treat planning/ROLLING_QUEUE.json as the source of execution intent. It is not a source of evidence truth.

Execute exactly one bounded safe task from the active queue.

After completing that task, critique the same task as a strict reviewer. Identify whether the task really closed the gap, whether enforcement exists, whether CI covers it, whether state remains consistent, and whether anything remains stale.

Apply only small in-scope corrections during the same run. If the correction is larger than the task scope, create or update a follow-up queue task instead.

Use branch, PR, CI, and merge workflow for repository changes. Do not merge if CI fails, if the PR head changed unexpectedly, if required review is missing, or if the workflow result is action_required or missing jobs.

Maintain a rolling backlog. If fewer than four pending tasks remain, add enough bounded tasks to restore four pending tasks. Every fifth logical work unit must be a queue-refresh task that audits the last four completed work units and writes the next four.

Never claim production-ready, release-ready, live-render validation, export validation, accessibility pass, or authoritative evidence unless direct project-specific evidence and validation gates exist.

Do not execute a real project workflow unless required evidence exists and readiness gates pass.

Return a concise report with:
- controller run ID
- task selected
- action executed
- critique findings
- fixes applied
- PR/CI/merge status
- queue changes
- ledger changes
- blockers
- next queued task
```

## 14. Anti-patterns to avoid

Do not use these patterns:

```text
- one scheduled prompt per task with no repo-backed queue
- marking a task completed because a PR was opened
- marking a task completed because CI started
- marking evidence valid because a queue task completed
- waiting silently for CI without setting awaiting_external
- making unrelated improvements inside the current task
- updating docs without updating queue or ledger state
- storing the only project state in chat memory
- letting a sample or fixture stand in for real submitted evidence
```

## 15. Acceptance criteria for implementation

The automation system is not implemented merely because a prompt exists.

It is implemented only when:

```yaml
queue_file_exists: true
queue_schema_validated: true
control_plane_exists: true
truth_boundaries_recorded: true
run_ledger_exists: true
run_ledger_validated: true
ci_runs_queue_checks: true
tasks_have_allowed_and_forbidden_work: true
tasks_have_acceptance_criteria: true
completed_tasks_have_audit_records: true
one_task_per_run_policy_exists: true
same_task_critique_required: true
four_plus_one_refresh_policy_exists: true
real_execution_blocked_without_evidence: true
production_claims_forbidden_without_evidence: true
```

For a more advanced implementation, add:

```yaml
lease_runtime_enforced: true
optimistic_locking_tested: true
runtime_queue_branch_exists: true
queue_repo_reconciliation_tested: true
stale_lease_recovery_tested: true
illegal_transition_tests_exist: true
action_required_detected: true
missing_ci_jobs_detected: true
```

## 16. Migration path

Recommended phased migration:

```text
Phase 1 — Repo-backed queue
Create queue, schema, control plane, run ledger, docs, and CI checks.

Phase 2 — Controller prompt
Update the scheduled automation to read the queue and perform one bounded task per run.

Phase 3 — Ledger discipline
Require every repository-changing completed task to have a ledger record.

Phase 4 — Transition and lease hardening
Add runtime leases, legal transitions, stale lease recovery, and queue/repo reconciliation.

Phase 5 — Runtime branch split
Move runtime queue state to a dedicated control branch only after lease and reconciliation are tested.

Phase 6 — Full controller maturity
Add dry-run controller mode, expected-head merge checks, action_required detection, missing-job detection, review-state validation, and stronger work-unit refresh.
```

## 17. How to adapt to another project

Replace EV4-specific items with the target project's own evidence and execution boundaries.

For example:

```text
EV4 real submitted packet -> target project required input artifact
EV4 readiness gate -> target project start gate
EV4 responsive validation -> target project domain validation
Issue #8 -> target project active tracking issue
production-ready claim -> target project release claim
```

Do not copy the domain-specific evidence rules blindly. Copy the control pattern.

## 18. Final rule

The scheduled model should not be trusted because it remembers. It should be trusted only when the repository state, queue, ledger, CI, and issue state agree.
