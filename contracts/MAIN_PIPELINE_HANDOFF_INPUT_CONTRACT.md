# MAIN_PIPELINE_HANDOFF_INPUT_CONTRACT

## Purpose

Define what may enter EV4 Responsive Architect from the completed EV4 Architect pipeline.

## Required Inputs

```yaml
required_payloads:
  - ev4-stage-anchor@1.1.0
  - Recommendation_Payload
  - Build_Tree_Payload
  - Implementation_Payload
  - Final_Audit_Payload
  - Handoff_Payload
  - EV4_DEBUG_TRACE
```

## Required Inherited Fields

```yaml
required_inherited_fields:
  - selected_candidate_id
  - selected_candidate_family
  - structure_tree
  - class_map
  - content_editability_map
  - overlay_decoration_map
  - responsive_structure_contract
  - carried_unknowns
  - audit_flags
  - repair_routes
```

## Forbidden as Authoritative Baseline

```yaml
forbidden_as_authoritative_baseline:
  - raw_section_screenshot_without_ev4_baseline
  - unselected_architecture_candidate
  - rejected_candidate
  - user_memory_without_current_payload
  - lessons_learned_as_current_evidence
  - official_docs_as_project_specific_behavior
```

## Gate Rule

If the required EV4 baseline is missing, stop and route to EV4 Architect owner stage instead of starting responsive repair.
