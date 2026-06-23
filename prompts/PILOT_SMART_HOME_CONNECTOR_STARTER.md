# Pilot Starter Prompt — Smart Home Connector

Use this prompt to start the first EV4 Responsive Architect pilot run.

## Prompt

```text
Use EV4 Responsive Architect.
Reports must be in Persian.
Keep schema names, stage names, payload names, class names, and Elementor labels in English.

Run only the smart-home connector shadow-mode pilot.
Do not claim production readiness.
Do not claim live Elementor rendering, export JSON validation, Playwright validation, exact pixel matching, or accessibility pass unless explicit evidence is supplied.

Target pilot:
smart-home-connector-v0.1

Required source files:
- examples/smart-home-connector/PILOT_CASE_V0_1.md
- examples/smart-home-connector/PILOT_MANIFEST.json
- examples/smart-home-connector/evidence/EVIDENCE_MANIFEST.template.json
- examples/smart-home-connector/templates/RESPONSIVE_FAILURE_MAP.template.md
- examples/smart-home-connector/templates/REPAIR_OPTION_ANALYSIS.template.md
- examples/smart-home-connector/builder/BUILDER_REPAIR_CHECKLIST.template.md
- examples/smart-home-connector/audits/FINAL_AUDIT_LITE.template.md

Required user inputs:
- completed main EV4 handoff or enough payload excerpts to verify selected_candidate_id and Build_Tree_Payload identity
- desktop baseline screenshot or declared equivalent
- tablet screenshot or declared equivalent
- mobile screenshot or declared equivalent
- breakpoint inventory source or explicit declaration that fallback is being used

Run sequence:
1. /main-pipeline-handoff-ingest
2. /responsive-evidence-ingest-ledger
3. /desktop-baseline-lock
4. /breakpoint-inventory-lock
5. /breakpoint-observation
6. /responsive-failure-map
7. /failure-priority-ordering
8. /repair-ownership-routing
9. /repair-option-analysis
10. /responsive-repair-selection
11. /repair-scope-freeze
12. /responsive-repair-plan
13. /responsive-final-audit-lite

Hard rules:
- screenshot can show symptom, not technical cause
- unknowns must survive until resolved by named evidence
- no architecture mutation
- no hiding meaningful content
- connector decoration classification must be inherited from main EV4 payloads
- every builder step must be atomic and reversible
- CSS requires selector safety check
- order/hide/reverse behavior requires accessibility reading-order gate

Start by checking input authorization. If inputs are missing, output a missing-input checklist instead of diagnosing.
```
