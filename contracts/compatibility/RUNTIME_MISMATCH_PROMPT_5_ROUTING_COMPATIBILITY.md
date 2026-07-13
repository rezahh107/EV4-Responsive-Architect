# Runtime-Mismatch Reopen to Prompt 5 Routing Compatibility Boundary

## Scope

This contract defines the repository-local compatibility boundary between:

- `runtime-mismatch-reopen-package.v1`; and
- `prompt-5-routing-envelope.v1`.

It does not execute Project Gate transport, replace a Kernel decision, create submitted evidence, authorize a pilot, or establish responsive correctness.

## Compatibility rule

A runtime-mismatch reopen package is compatible with Prompt 5 routing only when all of the following remain true:

1. The two dependency identities and schema hashes are explicitly pinned.
2. The reopen package preserves the prior Kernel decision lineage and the Prompt 5 route preserves the producer export lineage.
3. The reopen action is exactly `reopen_for_authoritative_review`.
4. The Prompt 5 route target is exactly `ev4-project-gate`.
5. A compatible reopen request is routed, not reinterpreted: `decision=route`, `transport_eligible=true`, and no rejection diagnostic is present.
6. Responsive may observe runtime mismatch and decide local route eligibility, but it may not replace or reinterpret the Kernel decision and may not execute Project Gate transport.
7. All evidence, pilot, readiness, release, export, accessibility, pixel, and responsive-correctness claims remain false.

Any missing, divergent, unsupported, or authority-substituting value must fail closed in the validator slice.

## Authority ownership

| Concern | Owner |
|---|---|
| Original and replacement decision authority | EV4 Decision Kernel |
| Local Prompt 5 routing eligibility | EV4 Responsive Architect |
| Transport execution and downstream gate behavior | EV4 Project Gate |

Responsive may package observations and route an authoritative-review request. It must not author a replacement decision, claim that transport occurred, or convert repository validation into domain evidence.

## Contract artifact

The machine-readable contract is:

`contracts/compatibility/runtime-mismatch-prompt-5-routing-compatibility.v1.schema.json`

The schema pins both dependency identities and requires:

- shared decision and producer-export lineage;
- the authoritative-review action;
- the Project Gate target and route state;
- explicit authority ownership; and
- false boundary claims.

## Required negative coverage for the validator slice

`WP-RESP-015/PR-B` must reject at least:

- missing or divergent decision lineage;
- missing or divergent producer-export lineage;
- unsupported reopen action;
- reject-state or diagnostic mismatch for an otherwise compatible reopen request;
- dependency contract or schema-version drift;
- dependency schema-hash drift;
- Responsive replacing or reinterpreting the Kernel decision;
- Responsive claiming transport execution; and
- any evidence or readiness boundary upgrade.

## Preserved boundaries

This compatibility contract does not prove or create:

- submitted evidence;
- Issue #8 mutation;
- pilot authorization or execution;
- production or release readiness;
- live-render or export validation;
- accessibility conformance;
- pixel-perfect output; or
- responsive correctness.

CI or schema validity is repository-check evidence only.
