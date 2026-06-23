# STATE_AS_CODE

## Purpose

Avoid relying on conversational memory or opaque local databases as authoritative project state.

## Strategy

```yaml
state_strategy:
  authoritative_state:
    format: versioned_json_in_git
    purpose:
      - audit
      - diff
      - rollback
      - CI validation
      - convergence_tracking

  optional_index:
    format: sqlite
    purpose:
      - fast_lookup
      - local_querying
      - evidence_registry_index
    authoritative: false
```

## Git-Tracked State Files

```yaml
git_tracked_files:
  - state/current_state_snapshot.json
  - state/payload_registry.json
  - state/evidence_registry.json
  - state/unknown_register.json
  - state/audit_flag_register.json
  - state/repair_route_register.json
  - state/convergence_history.json
```

## Privacy Rule

Do not commit production URLs, credentials, private assets, form data, analytics IDs, emails, tokens, or client identifiers without explicit review.
