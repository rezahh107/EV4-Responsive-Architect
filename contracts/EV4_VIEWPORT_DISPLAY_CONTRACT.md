# EV4 Viewport Display Contract

Status: active_v0.3.0
Schema family: `ev4-viewport-display-contract@0.3.0`

## Output shape

```yaml
viewport_display_contract:
  breakpoint_scope:
    desktop:
    tablet:
    mobile:
  viewport_rules:
    - node_ref:
      desktop: active | inactive | inherited | unknown
      tablet: active | inactive | inherited | unknown
      mobile: active | inactive | inherited | unknown
      reason:
  content_policy:
  sync_policy:
  unresolved_unknowns:
```
