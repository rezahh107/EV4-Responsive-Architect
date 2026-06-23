# Pilot Readiness Gate

Status: v0.1 shadow-mode gate

## Purpose

The Pilot Readiness Gate decides whether a validated evidence intake packet is allowed to start the smart-home connector shadow-mode pilot.

It is intentionally stricter than the human checklist and weaker than a real Elementor validation run.

## Required input

```text
validation/fixtures/valid/evidence_intake_packet.valid.json
```

The packet must already pass:

```bash
python validation/e2e/run_evidence_intake_check.py
```

## Command

```bash
python validation/e2e/run_pilot_readiness_check.py
```

## Possible statuses

```text
ready_for_shadow_mode_pilot
partial_ready_with_visible_flags
blocked_missing_evidence
blocked_conflicting_evidence
blocked_privacy_review_missing
blocked_schema_or_semantic_failure
```

For v0.1, a packet with user-declared breakpoints or visual-only screenshots may start only with visible flags. It must not create release-ready claims.

## Validation boundary

This gate does not validate:

```text
- live Elementor rendering
- Elementor export JSON truth
- Playwright visual regression
- accessibility pass
- production readiness
```

## Why this exists

Evidence intake can be valid while still carrying flags. The readiness gate converts intake status into a start/stop decision before pilot execution begins.
