# Prompts

Prompt files are not the source of truth. Contracts and schemas are the source of truth.

Prompt files should only orchestrate stage execution and must not override:

```text
- architecture mutation veto
- evidence quality contract
- forbidden inference rule
- production boundary
- payload identity hashing
- state-as-code policy
```

Planned files:

```text
RESPONSIVE_ARCHITECT_MASTER_PROMPT.md
BUILDER_SESSION_STARTER.md
RUN_COPILOT_REVIEW_PROMPT.md
```
