# 12 — Responsive Output Package

Stage ID: `/responsive-output-package`
Status: active_v0.3.1

## Output

```yaml
ev4_responsive_output:
  schema: ev4-responsive-output@0.3.1
  source_packet_ref:
  selected_route:
  responsive_tree_output:
  breakpoint_overrides:
  display_contract:
  content_gate:
  builder_handoff:
  builder_context_package_export:
  validation_plan:
  final_review:
  unresolved_unknowns:
```

## Builder Context Package Export

When this stage is used to hand off implementation work to `EV4 Builder Assistant`, also emit a `Builder_Context_Package` compatible with:

```text
contracts/BUILDER_CONTEXT_PACKAGE_EXPORT_CONTRACT.md
```

The package must include structured confirmation metadata:

```yaml
confirmation_request:
  confirmation_id: CONFIRM-BATCH-001
  confirmed_action_ids:
    - BATCH-001-A01
    - BATCH-001-A02
    - BATCH-001-A03
  expected_user_token: تایید BATCH-001
  template_id: standard_batch_confirmation
```

Do not emit `confirmation_sentence` or `builder_assistant_prompt_seed` in new exports.

`builder_handoff` may remain as the responsive repair/action summary, but the executable Builder Assistant intake artifact is `builder_context_package_export` / `Builder_Context_Package`.
