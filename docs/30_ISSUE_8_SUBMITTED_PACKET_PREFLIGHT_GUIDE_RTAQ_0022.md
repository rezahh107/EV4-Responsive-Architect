# Issue #8 Submitted-Packet Preflight Guide (RTAQ-0022)

## Purpose

This guide is a non-executing checklist for preparing a real submitted evidence packet for Issue #8. It exists to reduce operator ambiguity before a future human submission without creating evidence, mutating Issue #8, or authorizing pilot execution.

Current observed Issue #8 state remains blocked:

```yaml
issue_number: 8
packet_status: draft
validation_result: pending
pilot_allowed_to_start: false
real_pilot_allowed_to_start: false
allowed_scope: not_allowed
```

## Boundary

This document is preparation only.

It does not:

- create or submit an evidence packet;
- attach files to Issue #8;
- edit Issue #8;
- run the real pilot;
- authorize shadow-mode pilot execution;
- prove responsive correctness;
- prove live-render, export, accessibility, pixel, production, release, or prompt-pack readiness.

CI success or repository merge state remains repository-check evidence only. It cannot upgrade packet status, pilot readiness, or production truth.

## Required packet identity

A future submitted packet must identify itself as real Issue #8 evidence and must not reuse sample identity markers.

Required identity fields:

```yaml
schema: ev4-responsive-evidence-intake-packet@1.1.0
packet_origin: real_issue_submission
issue_reference:
  issue_number: 8
  issue_url_or_ref: "#8"
  evidence_submission_status: submitted
```

Reject the packet before pilot readiness if any of these sample or placeholder markers appear in identity, hashes, payload names, or attachment descriptors:

```text
SAMPLE
.sample
sha256-sample-placeholder
placeholder payload hash
```

## Required evidence inventory

A future submitted packet must include real evidence items for every required class below:

| Required item | Preflight expectation |
| --- | --- |
| Main EV4 handoff payloads | Real handoff content is attached or referenced with non-placeholder identity and quality fields. |
| Desktop baseline screenshot and root section identity | Desktop width is explicit and the root section identity is stated. |
| Tablet screenshot and visible symptoms | Tablet width and observed symptoms are concrete, not generic placeholders. |
| Mobile screenshot and visible symptoms | Mobile width and observed symptoms are concrete, not generic placeholders. |
| Breakpoint inventory or declaration | Breakpoint data is attached or the absence of custom breakpoints is explicitly declared. |
| Evidence quality fields | Every evidence item declares quality, completeness, and any known limitation. |
| Closed-enum support values | Only repository-supported enum values such as `can_support` and `cannot_support` are used. |
| Privacy review acknowledgement | The submitter confirms no private or unsafe content is being introduced. |

Expected file naming remains:

```text
main-ev4-handoff.md
desktop-baseline-[width].png
tablet-[width].png
mobile-[width].png
breakpoint-inventory.json
EVIDENCE_INTAKE_PACKET.submitted.json
```

## Preflight sequence

1. Assemble the JSON packet against `schemas/ev4-responsive-evidence-intake-packet.schema.json`.
2. Verify the packet uses `evidence_submission_status: submitted` only after the evidence files are real and complete.
3. Verify no sample marker or placeholder hash remains.
4. Verify required screenshot widths and visible symptoms are concrete.
5. Verify closed enums are valid and no free-form unsupported readiness values are present.
6. Run evidence intake validation on the packet.
7. Only after intake passes, generate the pilot readiness report.
8. Start no pilot unless the readiness report explicitly allows shadow-mode pilot start under the repository contracts.

Validation commands:

```bash
python validation/e2e/run_evidence_intake_check.py --packet examples/smart-home-connector/intake/EVIDENCE_INTAKE_PACKET.submitted.json
python validation/e2e/run_pilot_readiness_check.py --packet examples/smart-home-connector/intake/EVIDENCE_INTAKE_PACKET.submitted.json --out examples/smart-home-connector/readiness/PILOT_READINESS_REPORT.generated.json --skip-schema-suite
```

## Stop conditions

Stop before readiness generation if any of the following is true:

- packet status is still `draft`;
- evidence files are missing;
- screenshot widths are absent;
- symptoms are generic placeholders;
- sample markers remain;
- attachment hashes are placeholders;
- privacy review is missing;
- enum values are outside the schema;
- Issue #8 has not received a real submitted packet.

Stop before pilot execution if the readiness report says blocked, draft, unresolved, pending, or not allowed.

## RTAQ-0022 critique

The guide closes a real operator-gap: Issue #8 already lists required evidence and validation commands, but it does not separate preparation, submitted-packet conversion, intake validation, readiness generation, and pilot-start authorization as explicit stop-gated phases.

The guide preserves truth boundaries because it keeps Issue #8 unchanged, creates no submitted packet, and treats all validation commands as future checks against real evidence rather than evidence by themselves.
