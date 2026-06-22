# Stages

Stage files define executable LLM protocols. They are separate from contracts: contracts define rules; stages define what one run is allowed to do.

Every stage file should include:

- Input Authorization
- Source Payload Ledger
- Allowed Work
- Forbidden Work
- Main Output
- Unknowns / Carried Flags
- Repair Routes
- Self-Audit
- EV4_DEBUG_TRACE
- Next Stage Anchor or Repair Anchor

Current stage order is listed in `PROJECT_MASTER_SPEC.md`.
