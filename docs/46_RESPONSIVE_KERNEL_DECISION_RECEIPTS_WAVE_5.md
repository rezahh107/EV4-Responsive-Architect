# Responsive Kernel Decision Receipts — Wave 5

Status: presentation-layer extension only  
Scope: `EV4-Responsive-Architect`

## Purpose

Wave 5 adds a short user-facing receipt for Responsive outputs that already carry machine-readable Kernel decision lineage. The receipt helps the user understand whether a Responsive validation, runtime-evidence reference, mismatch report, repair request, or handoff output is connected to a real Kernel decision trace.

This document does not make the receipt authoritative. The source of truth remains `decision_lineage` and the validators that inspect it.

## Receipt surfaces

```yaml
responsive_receipt_surfaces:
  - responsive_intake
  - responsive_validation_report
  - runtime_evidence_reference
  - mismatch_report
  - repair_request
  - handoff_output
```

The formatter for these surfaces is implemented in:

```text
validation/e2e/responsive_kernel_receipts.py
```

The targeted validator is:

```text
validation/e2e/run_responsive_kernel_receipt_check.py
```

The receipt object shape is documented in:

```text
schemas/ev4-responsive-kernel-decision-receipt.schema.json
```

## Success receipt

A success receipt is allowed only when the machine-readable trace has all required fields:

```yaml
required_trace_fields:
  - decision_family
  - decision_card_ref
  - selected_option
  - rejected_options
  - evidence_refs
  - evidence_state
  - consumer_stage
```

Required user-facing pattern:

```text
✅ این Responsive validation به decision card کرنل وصل است؛ Responsive فقط رفتار responsive/runtime را بررسی کرده و lineage تصمیم حفظ شده است.
```

This success wording intentionally avoids exposing raw internal identifiers by default.

## Warning receipt

If the trace is missing or incomplete, Responsive must use the warning receipt instead of a green check:

```text
⚠️ این Responsive item هنوز رسید معتبر کرنل ندارد؛ بدون machine-readable trace کامل نباید به‌عنوان تصمیم responsive معتبر عبور کند.
```

The warning is not a replacement for the trace. It is an explicit insufficient-evidence state.

## Runtime mismatch receipt

Runtime mismatches must stay warnings. They do not authorize Responsive to create a new architecture decision:

```text
⚠️ runtime mismatch دیده شد، اما این رسید تصمیم جدید نیست؛ تصمیم باید با trace معتبر reopen یا repair شود.
```

A runtime mismatch receipt must not claim `runtime_monitor_enforced`, downstream enforcement, production readiness, or new Responsive design authority.

## Non-claims

```yaml
wave_5_non_claims:
  ci_success: not_claimed_by_this_document
  sequence_ci_enforced_upgrade: not_claimed
  downstream_contract_enforced: not_claimed
  runtime_monitor_enforced: not_claimed
  production_ready: false
  responsive_design_authority_added: false
  authored_resolved_field_added: false
  authored_production_ready_field_added: false
```

## Fixtures

Positive and warning fixtures:

```yaml
positive_fixture:
  - validation/fixtures/valid/kernel_receipt_complete_trace.valid.json
warning_fixtures:
  - validation/fixtures/valid/kernel_receipt_missing_decision_card_ref.warning.json
  - validation/fixtures/valid/kernel_receipt_missing_evidence_refs.warning.json
```

Negative fixtures:

```yaml
negative_fixtures:
  - validation/fixtures/invalid/kernel_receipt_success_without_trace.invalid.json
  - validation/fixtures/invalid/kernel_receipt_runtime_mismatch_without_reopen_trace.invalid.json
  - validation/fixtures/invalid/kernel_receipt_claims_redesign_authority.invalid.json
  - validation/fixtures/invalid/kernel_receipt_claims_runtime_monitor_enforcement.invalid.json
```

## Validation boundary

Run:

```bash
python validation/e2e/run_responsive_kernel_receipt_check.py
```

Passing this command is repository validation evidence for receipt/trace consistency only. It does not prove live render correctness, export correctness, accessibility, pixel accuracy, runtime monitoring, downstream enforcement, or production readiness.
