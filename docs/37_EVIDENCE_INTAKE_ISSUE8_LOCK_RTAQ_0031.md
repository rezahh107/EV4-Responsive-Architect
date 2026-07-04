# RTAQ-0031 Evidence Intake Issue #8 Lock

## Objective

Close a semantic intake-boundary gap where `real_issue_submission` packets were only locked to Issue #8 when real shadow-mode eligibility was requested. A blocked or `not_allowed` real packet with a different issue number could still pass the primary intake semantic validator.

## Technical decision

All `real_issue_submission` packets are now locked to Issue #8 at the primary evidence-intake validator boundary, independent of whether the packet is allowed, blocked, submitted, validated, or only being checked in submitted mode.

## Enforcement

- `validation/e2e/run_evidence_intake_check.py` rejects every `real_issue_submission` whose structured `issue_reference.issue_number` is not `8`.
- `--self-test` includes a blocked, non-pilot, wrong-issue real-submission probe and requires it to fail on the Issue #8 boundary.
- `.github/workflows/validate.yml` runs the evidence-intake semantic guard in the primary Validate workflow on the repository-supported Python matrix.
- `STATUS.md` lists the semantic guard as active validation and as an automatic repository check.

## Boundary

This is validation hardening only:

- No submitted evidence is created.
- Issue #8 is not mutated.
- No real pilot starts or becomes authorized.
- No readiness, production, release, live-render, export, accessibility, pixel, or responsive-correctness claim is upgraded.
- CI success remains repository-check evidence only.
