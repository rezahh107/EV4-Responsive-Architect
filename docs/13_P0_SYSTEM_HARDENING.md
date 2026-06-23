# P0 System Hardening

Version: 0.1.0  
Status: merged_after_validation_pending

This document records the P0 hardening layer added after the holistic system inspection.

## Scope

This layer hardens five weak points:

```text
1. evidence capability claims
2. conflict resolution behavior
3. responsive failure-map validation
4. responsive final-audit validation
5. handoff ingest and fast-path decision gates
```

## Evidence capability closed enums

`ev4-responsive-evidence-intake-packet@1.1.0` closes `can_support` and `cannot_support`.

Visual evidence may support visible symptoms only. It must not support:

```text
- computed_css_value
- dom_structure_observation
- exported_widget_structure
- exported_control_value
- declared_breakpoint_value
```

Visual evidence must explicitly carry these limitations:

```text
- exact_css_cause
- dom_reading_order
- accessibility_pass
- production_ready_claim
```

## Conflict resolution

`ev4-responsive-conflict-resolution@1.0.0` records competing sources, source priority, winner/loser, and downstream effect.

Unresolved conflicts must use:

```yaml
conflict_status: unresolved_blocking
resolution_action: block_downstream_until_resolved
downstream_effect: blocked
```

## Failure map

`ev4-responsive-failure-map@1.0.0` prevents responsive failure maps from moving forward when:

```text
- a repair-critical unknown is unresolved;
- a high architecture mutation risk exists but the map does not route back to the main pipeline.
```

## Final audit

`ev4-responsive-final-audit@1.0.0` prevents handoff when blockers remain. A controlled handoff requires every audit check to pass.

## Handoff ingest failure policy

`ev4-responsive-handoff-ingest-decision@1.0.0` defines three safe routes:

```text
accepted → start_responsive_intake
blocked_* → downstream_allowed=false
continue_degraded_with_visible_flags → visible flags required
```

No schema-failed handoff may silently continue.

## Fast-path eligibility

`ev4-responsive-fast-path-eligibility@1.0.0` makes triage fast-path machine-checkable. Fast-path is allowed only when:

```text
affected_viewport_count <= 1
custom_css_required = false
meaningful_visibility_change = false
content_order_change = false
overlay_or_connector_risk = false
architecture_mutation_risk = false
cascade_risk = low
unknowns_required_for_repair = false
accessibility_gate_triggered = false
```

## CI

The P0 layer is checked by:

```bash
python validation/e2e/run_p0_system_hardening_check.py
```

It also extends:

```bash
python validation/schema_validator/validate_schemas.py
python validation/e2e/run_evidence_intake_check.py
```

## Boundary

This layer does not prove live Elementor rendering, export validation, accessibility pass, or production readiness.
