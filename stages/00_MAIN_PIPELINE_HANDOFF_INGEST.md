# 00 — /main-pipeline-handoff-ingest

## Input Authorization

Requires completed EV4 Architect handoff payloads and a valid stage anchor.

## Allowed Work

```text
- verify required payload presence
- normalize inherited payload references
- record payload identity hashes
- carry unknowns and audit flags into responsive state
```

## Forbidden Work

```text
- no redesign
- no responsive diagnosis
- no repair planning
- no architecture candidate changes
```

## Main Output

```yaml
Main_Pipeline_Handoff_Ingest_Payload:
  schema: ev4-responsive-main-input@1.0.0
```

## Self-Audit

```text
Confirm selected_candidate_id, Build_Tree_Payload identity, unknowns, audit flags, and repair routes survived ingestion.
```
