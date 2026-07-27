# EV4-PCVP v1 tolerant Responsive consumer

The Builder → Responsive intake may carry an optional
`continuation_assurance` object. The carrier remains data at the Responsive
boundary.

## Locked behavior

- Decision Kernel remains the canonical policy and schema owner.
- The local Responsive profile and four schemas are non-authoritative byte
  copies pinned to immutable Decision Kernel commit
  `069a50fa243b01fa578a7c1bcb8864d9e796d34b`.
- Legacy intake without the carrier remains valid.
- A present carrier fails closed unless canonical schema, cross-record,
  source-stage, and Builder-through-Responsive authorization scope checks pass.
- A valid carrier is retained only as validated intake data.
- The carrier does not authorize responsive repair, prove any viewport,
  replace `responsive_intake_decision`, emit a Responsive carrier, or upgrade
  any forbidden readiness/correctness claim.

Rollout status remains `not_yet_adopted`; activation effect remains `NONE`.
