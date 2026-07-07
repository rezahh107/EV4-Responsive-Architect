# Project Gate Prompt 04 Responsive Producer Adoption

Status: implemented for repository validation; human review remains mandatory.

This document records Responsive Producer adoption of the Project Gate common-contract foundation. It preserves both Responsive modes:

- `design_to_responsive_tree`: classify viewport relationship, route strategy, then produce a responsive tree or override plan.
- `responsive_repair`: diagnose post-build viewport defects from real viewport evidence, then route ownership and atomic repair plans without hidden re-architecture.

## Canonical carriers

- Pipeline manifest: `manifests/ev4-responsive-pipeline-manifest.v1.json`
- Responsive Stage Payload schema: `schemas/ev4-responsive-stage-payload.v1.schema.json`
- Viewport Source Ledger schema: `schemas/ev4-responsive-viewport-source-ledger.v1.schema.json`
- Breakpoint registry: `registries/breakpoint-profiles.v1.json`
- Elementor capability registry: `registries/elementor-responsive-capabilities.v1.json`
- Producer Gate Export schema vendor: `contracts/project-gate/producer-gate-export.v1.schema.json`
- Project Gate common lock: `contracts/project-gate/producer-gate-export.v1.lock.json`
- Stage Bundle v1 verified separate vendor reference: `schemas/project-gate/stage-bundle.v1.schema.json`

## Behavioral Rule Coverage

| Rule | Carrier | Status |
| --- | --- | --- |
| Classify first, route second, generate third | Pipeline manifest mode sequences | covered |
| Validate only with matching viewport evidence | Responsive Stage Payload viewport ledger requires `proves_only_viewport: true` | covered |
| Desktop/tablet/mobile evidence isolation | Prompt 4 invalid fixture rejects cross-viewport proof | covered |
| Responsive repair must not become hidden re-architecture | Stage sequence includes Architecture Mutation Veto before repair export | covered |
| CI success is repository evidence only | Stage Payload requires `ci_success_is_responsive_correctness: false` | covered |
| Producer emitted gate artifact only | Producer export schema and fixtures require silent fallback false | covered |

## Prompt 5 handoff block

Project Gate routing, final Project Gate acceptance, and cross-repository E2E remain `not_implemented`. This repository now emits Responsive-owned artifacts for a later Prompt 5 integration, but it does not perform Prompt 5 routing.
