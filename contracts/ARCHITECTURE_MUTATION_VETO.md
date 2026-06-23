# ARCHITECTURE_MUTATION_VETO

## Purpose

Prevent responsive repair from becoming hidden re-architecture.

## Global Rule

`Architecture Mutation Veto` is a global gate. Every stage after `/responsive-failure-map` must check it.

## Triggers

```yaml
architecture_mutation_veto_triggers:
  - selected_candidate_identity_change
  - selected_candidate_family_change
  - meaningful_content_must_be_hidden_to_fit
  - decorative_element_must_become_meaningful
  - connector_layer_requires_semantic_role_change
  - normal_flow_content_requires_absolute_positioning_without_prior_approval
  - tree_node_identity_change_required
  - major_wrapper_addition_or_removal_required
  - duplicate_mobile_section_required
  - Build_Tree_Payload_contradiction
  - Implementation_Payload_contradiction
  - Handoff_Payload_contradiction
```

## Action

```yaml
architecture_mutation_veto_action:
  - stop_current_responsive_stage
  - emit_architecture_mutation_veto_report
  - preserve_all_responsive_evidence
  - route_to_earliest_owning_main_pipeline_stage
```

## Forbidden

```text
No self-authorized build-tree change.
No silent selected-candidate change.
No hiding architecture mutation inside CSS.
No proceeding to handoff after veto.
```
