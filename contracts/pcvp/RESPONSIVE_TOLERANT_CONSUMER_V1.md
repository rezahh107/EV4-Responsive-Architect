# EV4-PCVP v1 Tolerant Responsive Consumer

Status: implementation pending merge  
Policy: `EV4-PCVP@1.0.0`  
Architecture lock: `EV4-PCVP-ROLL-LOCK-20260727-R1`  
Compatibility: `DUAL_READ`  
Adoption: `not_yet_adopted`  
Activation effect: `NONE`

## Boundary

The Builder → Responsive intake may contain an optional `continuation_assurance` carrier.

```text
Builder package
  ├─ continuation_assurance absent → existing legacy Responsive intake
  └─ continuation_assurance present
       → immutable canonical byte/policy check
       → JSON_SCHEMA
       → CROSS_RECORD
       → RESPONSIVE_INTEGRATION
       → SEMANTIC_POLICY
       → lossless validated intake data
```

Absence is intentionally dependency-free: the legacy path does not load the PCVP lock, profile, vendored schemas, or a Decision Kernel checkout.

## Canonical authority

Decision Kernel remains the canonical PCVP owner. Responsive vendors non-authoritative integration copies pinned to immutable commit:

`069a50fa243b01fa578a7c1bcb8864d9e796d34b`

The local lock requires byte equality for:

- `03-PROFILES/responsive.profile.yaml`
- `04-SCHEMAS/authorization.schema.json`
- `04-SCHEMAS/claim.schema.json`
- `04-SCHEMAS/effect.schema.json`
- `04-SCHEMAS/handoff.schema.json`

`.github/workflows/validate.yml` checks out that exact Decision Kernel commit and runs `validation/e2e/run_pcvp_canonical_parity_check.py`. Moving Decision Kernel `main` is not a substitute for the immutable pin.

## Validation layers

`validation/e2e/responsive_pcvp.py` preserves canonical failure boundaries instead of collapsing all failures into a Responsive-specific diagnostic:

- `JSON_SCHEMA`: canonical structural/type/enum/required-property failures.
- `CROSS_RECORD`: global identifier uniqueness, Claim/Effect/Authorization references, active Authorization, coverage, scope, and stage-summary reference integrity.
- `RESPONSIVE_INTEGRATION`: Builder source-stage and Builder→Responsive stage-scope compatibility, local lock/profile/schema identity, and rejection of caller-supplied data that attempts to manufacture Responsive/Project Gate/readiness authority.
- `SEMANTIC_POLICY`: safe-default restrictions and mechanically enforceable contradiction/owner-projection invariants.

Present invalid carriers fail closed. They are never silently repaired.

## Authority boundary

A valid carrier is supplemental continuation/authorization state only. It is not evidence of:

- Responsive correctness or successful viewport validation;
- Runtime execution or repair correctness;
- Project Gate PASS or final handoff PASS;
- production, release, or deployment readiness;
- accessibility conformance;
- export validity;
- pixel-perfect output;
- final QA.

The Responsive output schema does not contain `continuation_assurance`; this work unit adds no Responsive producer or emission path.

## Regression contract

`validation/e2e/run_pcvp_tolerant_consumer_check.py` proves:

- legacy absence remains valid and does not require canonical dependency loading;
- a valid present carrier is accepted and retained losslessly;
- malformed/version-drifted carriers fail at `JSON_SCHEMA`;
- reference, identity, Authorization status/coverage/scope failures fail at `CROSS_RECORD`;
- source/stage drift and false downstream-authority claims fail at `RESPONSIVE_INTEGRATION`;
- invalid safe-default, contradiction, dependency, and GREEN/YELLOW/RED projections fail at `SEMANTIC_POLICY`;
- local canonical profile/schema drift fails closed;
- no PCVP field is added to Responsive output.

Success of these repository checks remains repository evidence only. It does not activate PCVP and does not establish Responsive correctness.
