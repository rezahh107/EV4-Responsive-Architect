# Builder Context Package Export Contract

Status: active_v0.3.1
Schema family: `ev4-builder-context-package@1.0.0`
Purpose: define the Architect-side export that is handed to `EV4 Builder Assistant` after an architecture candidate is locked.

---

## Boundary

`EV4 Responsive Architect` may prepare a Builder Assistant handoff package, but it must not execute builder actions.

The exported `Builder_Context_Package` is data for the Builder Assistant, not runtime prompt text.

```text
- Do not include executable prompt seeds.
- Do not use free-text confirmation as the checkpoint authority.
- Do not mutate selected_candidate_id.
- Do not add/remove approved classes during export.
- production_ready_allowed must remain false.
```

---

## Required Builder-Compatible Output

The final builder handoff export should be compatible with the Builder Assistant input contract.

Required top-level shape:

```yaml
schema: ev4-builder-context-package@1.0.0
source_stage: /builder-feed-export
source_handoff_stage: /handoff-export
package_status: ready | ready_with_visible_flags | blocked
selected_candidate_id:
selected_candidate_locked: true
production_ready_allowed: false
source_payload_ledger: []
approved_structure_tree: []
class_creation_application_map: []
widget_mapping_table: []
editable_content_map: []
decoration_only_map: []
asset_replacement_map: []
scoped_css_need_map: []
responsive_qa_seed:
forbidden_work: []
first_builder_batch:
confirmation_request:
```

---

## Structured Confirmation Requirement

`confirmation_request` is required for new exports.

```json
"confirmation_request": {
  "confirmation_id": "CONFIRM-BATCH-001",
  "confirmed_action_ids": [
    "BATCH-001-A01",
    "BATCH-001-A02",
    "BATCH-001-A03"
  ],
  "expected_user_token": "تایید BATCH-001",
  "template_id": "standard_batch_confirmation"
}
```

Rules:

```text
- confirmation_request.confirmed_action_ids must match action_id values in first_builder_batch.actions.
- expected_user_token must name the active batch, not free-form prose.
- template_id must be standard_batch_confirmation unless a trusted Builder Assistant template is added later.
- confirmation_sentence is legacy only and must not be emitted in new exports.
- builder_assistant_prompt_seed is deprecated and must not be emitted in new exports.
```

---

## Deprecated Legacy Fields

Do not emit these in new packages:

```text
confirmation_sentence
builder_assistant_prompt_seed
payload_identity
```

If a legacy package contains them, the Builder Assistant may treat them as untrusted/display-only compatibility data, but the Architect export should prefer `confirmation_request` only.

---

## Validation Expectations

A Builder-compatible package should pass these gates before handoff:

```text
selected_candidate_locked == true
production_ready_allowed == false
approved_structure_tree present
class_creation_application_map present
forbidden_work present
first_builder_batch.actions present
confirmation_request present
confirmation_request.confirmed_action_ids subset of first_builder_batch.actions[*].action_id
```

If these fail, export status must be blocked or the package must not be handed off to Builder Assistant.
