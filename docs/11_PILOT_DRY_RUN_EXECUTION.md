# Pilot Dry-Run Execution

Status: `contract_validation_only`

This document defines the smart-home connector pilot dry-run layer.

## Purpose

The dry-run proves that a submitted-like evidence packet can move through:

```text
Evidence Intake Packet
→ Evidence Intake Validation
→ Pilot Readiness Report
→ Pilot Manifest Check
→ Pilot Run Record
```

It does not execute Elementor and does not validate a live rendered section.

## Default CI command

```bash
python validation/e2e/run_pilot_dry_run_check.py
```

Default input:

```text
examples/smart-home-connector/intake/EVIDENCE_INTAKE_PACKET.sample-submitted.json
```

Generated outputs:

```text
examples/smart-home-connector/readiness/PILOT_READINESS_REPORT.dry-run.generated.json
examples/smart-home-connector/runs/PILOT_RUN_RECORD.dry-run.generated.json
```

Generated runtime outputs must end with `.generated.json` and must not be committed. Committed examples must use `.example.json` or fixture names.

## Sample vs real packet boundary

The sample packet is only allowed for dry-run contract validation.

```yaml
sample_packet_rules:
  packet_origin: sample_contract_fixture
  allowed_scope: sample_dry_run_only
  real_pilot_allowed_to_start: false
  issue_reference: null
  submitted_shadow_mode_allowed: false
```

A real submitted packet must come from Issue #8 or an equivalent tracked issue and must carry:

```yaml
real_packet_preflight:
  packet_origin: real_issue_submission
  issue_reference: required
  packet_id: must_not_contain_SAMPLE_or_sample
  source_ref: must_not_contain_sample
  payload_identity_hash: must_not_be_placeholder
  evidence_file_names: must_not_contain_sample_or_.sample
  privacy_review: fully_acknowledged
  allowed_scope: real_shadow_mode_only
  real_pilot_allowed_to_start: true
```

## Real submitted packet mode

Use this only after Issue #8 contains real evidence and a submitted packet:

```bash
python validation/e2e/run_pilot_dry_run_check.py \
  --packet examples/smart-home-connector/intake/EVIDENCE_INTAKE_PACKET.submitted.json \
  --readiness-out examples/smart-home-connector/readiness/PILOT_READINESS_REPORT.generated.json \
  --run-record-out examples/smart-home-connector/runs/PILOT_RUN_RECORD.generated.json \
  --submitted-shadow-mode
```

The command fails if the packet still carries sample markers, placeholder hashes, missing issue reference, or non-real packet origin.

## Blocked packet negative path

Use this to prove that blocked evidence does not create an authorized run record:

```bash
python validation/e2e/run_pilot_dry_run_check.py \
  --packet validation/fixtures/valid/evidence_intake_packet.blocked.valid.json \
  --expect-blocked
```

## Run record traceability

A generated run record must carry:

```yaml
traceability_required:
  source_packet_sha256: required
  source_readiness_sha256: required
  generated_at_utc: required
  generator_command: required
  git_ref_or_commit: required
  manifest_check_result: required
  generated_artifacts:
    - readiness_report hash
    - run_record self_hash_deferred marker
    - pilot_manifest hash
    - source_packet hash
```

## Required boundary

The dry-run may create a run record, but it must not claim:

```text
production_ready
release_ready
live_render_validated
export_json_validated
accessibility_passed
playwright_visual_regression_validated
```

## Next step after default dry-run

The next valid action is:

```text
collect_real_evidence
```

The sample packet must not replace real screenshots, main EV4 handoff, breakpoint inventory, or export evidence.
