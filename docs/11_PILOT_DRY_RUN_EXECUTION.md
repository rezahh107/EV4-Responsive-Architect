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

## Real submitted packet mode

Use this only after Issue #8 contains real evidence and a submitted packet:

```bash
python validation/e2e/run_pilot_dry_run_check.py \
  --packet examples/smart-home-connector/intake/EVIDENCE_INTAKE_PACKET.submitted.json \
  --readiness-out examples/smart-home-connector/readiness/PILOT_READINESS_REPORT.generated.json \
  --run-record-out examples/smart-home-connector/runs/PILOT_RUN_RECORD.generated.json \
  --submitted-shadow-mode
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
