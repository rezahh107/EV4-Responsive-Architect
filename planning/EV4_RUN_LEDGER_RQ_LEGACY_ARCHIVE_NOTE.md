# RQ Legacy Run Ledger Archive Note

PR #65 reset the active queue from the legacy `RQ-*` lineage to the post-refactor `RTAQ-*` lineage.

This merge-final bookkeeping update keeps `planning/EV4_RUN_LEDGER.json` focused on the active `RTAQ` lineage from `RTAQ-0001` forward.

The earlier `RQ-*` ledger records are not evidence for the new active queue. They remain preserved as historical repository records through git history before this merge-final update, with the queue reset context also recorded in:

```text
planning/EV4_QUEUE_RESET_RTAQ_0001.audit.json
```

Boundary:

```text
- no submitted evidence is created here
- Issue #8 is not modified here
- the real pilot remains blocked
- CI success is repository-check evidence only
```
