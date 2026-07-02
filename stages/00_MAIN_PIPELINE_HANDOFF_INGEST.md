# 00 — /main-pipeline-handoff-ingest

## Input Authorization

Requires a completed Builder handoff, Builder build evidence, and explicit CE/Builder provenance.

Production flow:

```text
Architect → CE → Builder → Responsive
```

A direct Architect packet may be used only as preflight/debug evidence. It is not production Responsive intake unless CE and Builder provenance have been preserved in `upstream_provenance`.

## Allowed Work

```text
- verify required Builder payload presence
- verify CE executable-ready provenance
- verify Builder runtime intake authorization provenance
- verify visual governance carriers are present
- normalize inherited payload references
- record payload identity hashes
- carry unknowns and audit flags into responsive state
```

## Forbidden Work

```text
- no direct Architect-to-Responsive production bypass
- no redesign
- no responsive diagnosis
- no repair planning
- no architecture candidate changes
- no invention of missing CE or Builder evidence
```

## Main Output

```yaml
Main_Pipeline_Handoff_Ingest_Payload:
  schema: ev4-responsive-main-input@1.0.0
  upstream_provenance:
    production_handoff_source: builder_output_and_build_evidence
```

## Self-Audit

```text
Confirm selected_candidate_id, Builder evidence, CE executable-ready status, visual governance provenance, Build_Tree_Payload identity, unknowns, audit flags, and repair routes survived ingestion.
```
