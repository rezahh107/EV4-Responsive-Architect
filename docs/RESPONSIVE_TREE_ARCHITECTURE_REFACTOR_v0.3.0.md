# EV4 Responsive Architect — Responsive Tree Architecture Refactor

Status: active_refactor_v0.3.0
Version: 0.3.0-responsive-tree-architect
Primary mode: `design_to_responsive_tree`
Secondary mode: `responsive_repair`

## Identity

`EV4 Responsive Architect` is now a responsive-tree architecture system.

It consumes an approved desktop tree plus responsive design evidence and decides the Elementor strategy for tablet/mobile.

## Required inputs

```yaml
required_inputs:
  ev4_responsive_start_packet: ev4-responsive-start-packet@1.0.0
  desktop_tree: required
  mobile_mockup: required_or_explicitly_absent
  tablet_mockup: required_or_explicitly_absent
  target_breakpoint_scope: required
  viewport_policy: required_if_variant_possible
```

## Closed route set

```yaml
responsive_strategy_route:
  - same_tree_responsive_overrides
  - viewport_specific_variant_tree
  - hybrid_split_architecture
  - blocked_pending_input
```

## Relationship classification

```yaml
section_relationship:
  classification:
    - same_section_adaptation
    - viewport_specific_variant
    - hybrid_split
    - unresolved_requires_designer_input
  evidence:
  confidence:
  open_items:
```

## Pipeline order

```text
/responsive-start-packet-ingest
/responsive-design-intake
/viewport-source-ledger
/section-relationship-classification
/elementor-strategy-routing
/responsive-tree-ownership-contract
/same-tree-responsive-derivation
/viewport-tree-architecture
/composite-responsive-plan
/display-and-breakpoint-contract
/content-accessibility-duplication-gate
/responsive-builder-handoff
/responsive-validation-plan
/responsive-final-review
/responsive-output-package
```

## Boundary

The upstream packet is advisory. Route selection is a planning decision, not validation evidence.

```text
Primary mode: design-to-responsive-tree.
Repair mode: secondary fallback only.
```
