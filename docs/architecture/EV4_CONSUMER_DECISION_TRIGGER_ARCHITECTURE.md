# EV4 Consumer Decision Trigger Architecture — Responsive Adoption

```yaml
document_type: consumer_repo_adoption_reference
consumer_repo: EV4-Responsive-Architect
canonical_source:
  repo: EV4-Decision-Kernel
  path: docs/architecture/EV4_CONSUMER_DECISION_TRIGGER_ARCHITECTURE.md
  profile: EV4_CONSUMER_DECISION_TRIGGER_ARCHITECTURE_v0.4.1
wave: 0
wave_name: Architecture Baseline / Adoption
adoption_state: upstream_contract_adopted
```

## Purpose

This document records `EV4-Responsive-Architect` adoption of the upstream EV4 Consumer Decision Trigger Architecture as a decision-gate contract reference for Responsive-stage work.

Responsive remains a post-build responsive/runtime behavior repository. It validates responsive evidence, route boundaries, handoff inputs, viewport outputs, and related runtime-facing artifacts. It does not select the original architecture, redesign upstream decisions, replace EV4 Decision Kernel authority, or silently convert missing upstream decisions into responsive repairs.

## Wave 0 Boundary

This Wave 0 adoption adds the architecture baseline and state/schema placeholders needed for later BRC-aligned review. It does not perform a full decision escape-route audit and does not add enforcement logic.

Allowed Wave 0 claims:

```yaml
allowed_claims:
  - architecture_document_added
  - upstream_contract_adopted
```

Explicit non-claims:

```yaml
non_claims:
  escape_routes_audited: false
  schema_enforced: false
  validator_backed: false
  fixture_tested: false
  ci_enforced: false
  sequence_ci_enforced: false
  runtime_monitor_enforced: false
  os_harness_enforced: false
  downstream_contract_enforced: false
  responsive_runtime_proven: false
  production_ready: false
```

## Consumer State Artifacts

The Responsive consumer state template is maintained at:

```text
planning/DECISION_ESCAPE_ROUTES.yml
```

The baseline schema for that state file is maintained at:

```text
planning/decision-escape-routes.schema.json
```

Wave 0 state starts as `expected_unverified` with an empty `records` array. The Wave 0 schema intentionally sets `records.maxItems` to `0`; non-empty records require a later schema wave that defines the full BRC-aligned record object. The state file must not use a `routes` array, and authored records must not add `resolved` or `production_ready` fields. Those are derived audit conclusions for later waves only when evidence supports them.

## Responsive Boundary

When future Responsive-specific audit or enforcement waves are approved, they must preserve the existing repository boundary:

- Responsive validates viewport and runtime-facing responsive behavior only from matching evidence.
- Screenshots prove only visible assertions they support.
- Structure evidence does not prove frontend rendering.
- Frontend evidence does not prove hidden control values.
- Missing upstream decision evidence must remain `insufficient_evidence` rather than being inferred.
- Runtime enforcement may be claimed only when inspected carriers and evidence prove it.
