# EV4 Responsive Strategy Routing Contract

Status: active_v0.3.0
Schema family: `ev4-responsive-strategy-routing@0.3.0`

## Closed route set

```yaml
route:
  - same_tree_responsive_overrides
  - viewport_specific_variant_tree
  - hybrid_split_architecture
  - blocked_pending_input
```

## Output shape

```yaml
responsive_strategy_routing:
  relationship_classification_ref:
  route:
  confidence: high | medium | low | unknown
  reason:
  allowed_elementor_mechanisms:
  open_items:
```
