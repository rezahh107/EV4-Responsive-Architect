# REPAIR_OPTION_ANALYSIS

## Purpose

Require option analysis before repair selection.

## Required Shape

```yaml
repair_option_analysis:
  schema: ev4-responsive-repair-option-analysis@1.0.0
  for_each_failure:
    failure_id:
    options:
      - option_id:
        repair_owner:
        repair_type:
        native_control_possible:
        scoped_css_needed:
        desktop_regression_risk:
        cascade_risk:
        accessibility_risk:
        evidence_support:
        rejected_reason_if_not_selected:
        verification_required:
```

## Forbidden

```text
No repair selection without option ledger.
No selected option without rejected-option record.
No CSS option if native option was not evaluated.
No hidden recommendation language before selection.
```
