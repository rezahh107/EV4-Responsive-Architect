# Issue #8 to Evidence Intake Packet Bridge

Version: 1.0.0  
Status: contract-only bridge  
Target packet: `EVIDENCE_INTAKE_PACKET.submitted.json`  
Target schema: `ev4-responsive-evidence-intake-packet@1.1.0`

## Purpose

This bridge defines how evidence submitted through Issue #8 may be converted into a real `EVIDENCE_INTAKE_PACKET.submitted.json` candidate.

It is deliberately conservative. It may organize submitted evidence; it must not invent, scrape, infer, or silently repair missing evidence.

## Source boundary

Allowed source material:

```text
- Issue #8 body
- Issue #8 comments
- Issue #8 attachments
- explicitly linked repository files
```

Forbidden source material:

```text
- model inference
- old chat memory
- sample fixtures
- generated dry-run outputs
- visual claims from text-only descriptions
- unreviewed private URLs or client-identifying data
```

## Mapping rules

| Packet field | Required Issue #8 material | If missing | If conflicting |
|---|---|---|---|
| `section_id` | Explicit section identity | Block packet creation | Human review |
| `selected_candidate_id` | Explicit Main EV4 selected candidate | Block packet creation | Block downstream |
| `main_ev4_handoff.*_present` | Submitted handoff bundle or linked file | Block packet creation | Block downstream |
| `main_ev4_handoff.payload_identity_hash` | Stable hash for submitted handoff bundle | Block packet creation | Block downstream |
| `desktop_baseline` | Desktop screenshot or linked artifact with root/viewport identity | Block packet creation | Block downstream |
| `evidence_items[]` | Desktop, tablet, and mobile evidence items with quality/limitations | Block validation | Block downstream |
| `breakpoint_inventory` | Export/project settings, user declaration, or explicitly marked fallback | Block validation if absent | Human review |
| `privacy_review` | Explicit checklist acknowledgement | Block packet creation | Block downstream |
| `intake_verdict` | Derived only from present evidence and blockers | Must be blocked if required evidence is absent | Block downstream |

## Blocked states

A bridge result must block downstream when any of these are present:

```text
MISSING_ATTACHMENT
MISSING_HASH
PRIVACY_NOT_ACKED
CONFLICTING_SOURCE
SAMPLE_MARKER_PRESENT
TEXT_ONLY_VISUAL_PROOF
```

## Non-inference rule

Text in Issue #8 may identify intent, labels, and declared values. Text alone must not prove:

```text
- screenshot existence
- visual correctness
- DOM structure
- computed CSS
- Elementor export values
- accessibility pass
- live-render validation
- production readiness
```

## Privacy rule

If the submitter omits or redacts an artifact for privacy, the packet must record that omission as a blocker or visible limitation. The bridge must not backfill the missing artifact from memory or inference.

## Machine-readable contract

Schema:

```text
schemas/ev4-responsive-issue-to-packet-bridge.schema.json
```

Fixtures:

```text
validation/fixtures/valid/issue_to_packet_bridge.valid.json
validation/fixtures/invalid/issue_to_packet_bridge.text_as_visual_proof.invalid.json
```

Validation command:

```text
python validation/schema_validator/validate_schemas.py
```

## Current Issue #8 state

Issue #8 is still open and evidence-pending. The bridge currently blocks packet creation because the issue does not yet contain a real submitted packet, required visual artifacts, and required payload identity hashes.

## Boundary

This bridge does not authorize the real pilot. The real pilot remains blocked until a real submitted packet exists and the readiness gates pass.
