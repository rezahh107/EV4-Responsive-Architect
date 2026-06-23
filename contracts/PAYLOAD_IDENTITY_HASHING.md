# PAYLOAD_IDENTITY_HASHING

## Purpose

Ensure every payload has stable identity and downstream stale-state detection.

## Payload Identity

```yaml
payload_identity:
  schema: ev4-responsive-payload-identity@1.0.0
  payload_id:
  schema_version:
  source_stage:
  content_hash:
  created_at:
  supersedes:
  depends_on:
  source_files_or_evidence_ids:
```

## Stage Input Hashes

```yaml
stage_input_payload_hashes:
  Build_Tree_Payload:
  Implementation_Payload:
  Handoff_Payload:
  Responsive_Evidence_Ledger:
  Desktop_Baseline_Lock:
  Breakpoint_Inventory_Lock:
```

## If Upstream Hash Changes

```yaml
if_upstream_payload_hash_changes:
  - mark_downstream_payloads_stale
  - rerun_from_earliest_dependent_stage
  - do_not_reuse_stale_handoff
```
