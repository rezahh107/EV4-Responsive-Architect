# Real Pilot Artifact Slots

Status: template_only  
Scope: RQ-0004 — Prepare real pilot artifact slots

## Purpose

This document reserves the real-pilot artifact paths that will be used after Issue #8 contains a complete real submitted evidence packet and the readiness gate passes.

These slots are not evidence. They are path and command templates only.

## Non-evidence rule

The repository may contain templates and manifests for the real pilot, but it must not contain runtime-generated submitted outputs unless the real evidence workflow explicitly allows them later.

Forbidden in this task:

```text
- committing *.generated.json runtime outputs
- fabricating screenshots
- fabricating hashes
- fabricating Elementor export data
- treating placeholder text as submitted evidence
- authorizing the real pilot
```

## Reserved artifact paths

```text
artifacts/real-pilot/submitted/EVIDENCE_INTAKE_PACKET.submitted.json
artifacts/real-pilot/readiness/PILOT_READINESS_REPORT.submitted.json
artifacts/real-pilot/failure-map/RESPONSIVE_FAILURE_MAP.submitted.json
artifacts/real-pilot/risk/RISK_PRIORITY_ASSESSMENT.submitted.json
artifacts/real-pilot/repair/RESPONSIVE_REPAIR_PLAN.submitted.md
artifacts/real-pilot/final-audit/RESPONSIVE_FINAL_AUDIT.submitted.json
```

The paths above are reserved names only. Do not create populated submitted artifacts until real evidence exists.

## Template source

Use this template manifest as the preparation artifact:

```text
templates/real-pilot/REAL_PILOT_ARTIFACT_SLOTS.template.json
```

The manifest intentionally uses:

```yaml
artifact_status: template_only
is_real_evidence: false
pilot_authorized: false
```

Any downstream script or reviewer must reject the template as proof of a submitted packet.

## Submitted-mode commands

Sample dry-run validation remains separate:

```bash
python validation/e2e/run_pilot_dry_run_check.py
python validation/e2e/run_pilot_dry_run_check.py --packet validation/fixtures/valid/evidence_intake_packet.blocked.valid.json --expect-blocked
```

Submitted shadow mode must reject sample packets:

```bash
python validation/e2e/run_pilot_dry_run_check.py --submitted-shadow-mode
```

Real submitted validation may only be attempted after Issue #8 provides a real packet. Use `--submitted-mode` so validators reject sample fixtures, templates, placeholder paths, and non-`real_issue_submission` packets:

```bash
python validation/e2e/run_evidence_intake_check.py --packet artifacts/real-pilot/submitted/EVIDENCE_INTAKE_PACKET.submitted.json --submitted-mode
python validation/e2e/run_pilot_readiness_check.py --packet artifacts/real-pilot/submitted/EVIDENCE_INTAKE_PACKET.submitted.json --submitted-mode --out artifacts/real-pilot/readiness/PILOT_READINESS_REPORT.submitted.json
```

For local debugging of one submitted packet, `--skip-schema-suite` may be added to skip the full fixture suite, but it does not weaken submitted-mode sample rejection:

```bash
python validation/e2e/run_evidence_intake_check.py --packet artifacts/real-pilot/submitted/EVIDENCE_INTAKE_PACKET.submitted.json --submitted-mode --skip-schema-suite
python validation/e2e/run_pilot_readiness_check.py --packet artifacts/real-pilot/submitted/EVIDENCE_INTAKE_PACKET.submitted.json --submitted-mode --skip-schema-suite --out /tmp/PILOT_READINESS_REPORT.submitted.json
```

Do not emulate submitted mode with sample fixtures.

## Reviewer checklist

Before treating any real-pilot artifact as evidence, verify:

```text
- the file is not under templates/
- artifact_status is not template_only
- is_real_evidence is true
- sample markers are absent
- packet_origin is real_issue_submission
- screenshots/hashes/export references point to real submitted artifacts
- privacy review is complete
- pilot_authorized remains false until readiness explicitly passes
```

## Boundary

This document does not claim live rendering, export validation, accessibility pass, production readiness, or release readiness.
