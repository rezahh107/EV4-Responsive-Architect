# EV4 Responsive Handoff Export Contract

Status: active_v0.3.1
Schema family: `ev4-responsive-handoff-export@0.3.1`

## Output shape

```yaml
ev4_responsive_handoff:
  schema: ev4-responsive-handoff@0.3.1
  source_packet_ref:
  selected_route:
  relationship_classification_ref:
  responsive_tree_output:
  breakpoint_overrides:
  viewport_display_contract:
  content_gate:
  builder_handoff:
  builder_context_package_export:
  validation_plan:
  final_review:
  unresolved_unknowns:
```

## Builder Assistant Intake Artifact

`builder_context_package_export` is the Builder Assistant intake artifact.

It must follow:

```text
contracts/BUILDER_CONTEXT_PACKAGE_EXPORT_CONTRACT.md
```

New exports must include `confirmation_request` and must not rely on legacy `confirmation_sentence` or `builder_assistant_prompt_seed`.

Minimum confirmation shape:

```json
"confirmation_request": {
  "confirmation_id": "CONFIRM-BATCH-001",
  "confirmed_action_ids": ["BATCH-001-A01", "BATCH-001-A02", "BATCH-001-A03"],
  "expected_user_token": "تایید BATCH-001",
  "template_id": "standard_batch_confirmation"
}
```

## Boundary

`builder_handoff` can summarize responsive repair actions.

`builder_context_package_export` is the package that should be pasted/uploaded into `EV4 Builder Assistant`.

Do not claim production readiness from this handoff.
