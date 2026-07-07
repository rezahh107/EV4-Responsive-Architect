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


## PR #142 workflow startup fix

The Project Gate reusable workflow caller now passes only `lock_path` to the pinned workflow. Unsupported `lock-file` and `vendored-contract` inputs were removed. The Producer Gate Export lock now uses the official `project-gate-common-contract-lock.v1` shape with `canonical`, `vendored`, and `verification` sections. Stage Bundle v1 remains separate evidence and is not claimed as covered by the common lock.

## PR #142 canonical contract correction

The vendored `contracts/project-gate/producer-gate-export.v1.schema.json` was replaced with the canonical Project Gate contract bytes from commit `ea19c22c32458068e167b267da8b819e9263cdf7`, producing SHA-256 `c556bb9deeccdcafeb885a1c8b3dbd660e4e06f452b8ac3c7040d21377465fcc`. The local `contracts/project-gate/common-contract-lock.v1.schema.json` was also replaced with the canonical Project Gate common-lock schema shape so local schema documentation no longer contradicts the lock used by the reusable workflow.

The Responsive Prompt 4 validator now verifies the actual vendored Producer Gate Export schema file hash and resolves the Stage Bundle `$ref` through the local vendored Stage Bundle schema instead of attempting network retrieval.
