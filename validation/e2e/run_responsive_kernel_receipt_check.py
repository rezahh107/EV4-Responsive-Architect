#!/usr/bin/env python3
"""Validate Wave 5 Responsive Kernel decision receipt behavior.

The check is intentionally presentation-layer scoped: it proves that user-facing
receipt text is derived from an existing decision_lineage and cannot replace,
weaken, or overclaim the machine-readable trace.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

from responsive_kernel_receipts import (
    SUCCESS_MESSAGE,
    WARNING_MESSAGE,
    format_responsive_kernel_receipt,
    assert_receipt_matches_trace,
)

ROOT = Path(__file__).resolve().parents[2]
RECEIPT_SCHEMA = ROOT / "schemas" / "ev4-responsive-kernel-decision-receipt.schema.json"
VALID_DIR = ROOT / "validation" / "fixtures" / "valid"
INVALID_DIR = ROOT / "validation" / "fixtures" / "invalid"

VALID_RESPONSIVE_OUTPUTS = (
    VALID_DIR / "responsive_output_same_tree.valid.json",
    VALID_DIR / "responsive_output_viewport_tree.valid.json",
    VALID_DIR / "responsive_output_hybrid.valid.json",
    VALID_DIR / "responsive_output_blocked.valid.json",
)

SUCCESS_RECEIPT_FIXTURE = VALID_DIR / "kernel_receipt_complete_trace.valid.json"
WARNING_RECEIPT_FIXTURES = (
    VALID_DIR / "kernel_receipt_missing_decision_card_ref.warning.json",
    VALID_DIR / "kernel_receipt_missing_evidence_refs.warning.json",
)
INVALID_RECEIPT_FIXTURES = {
    INVALID_DIR / "kernel_receipt_success_without_trace.invalid.json": "EV4_RESPONSIVE_KERNEL_RECEIPT_GREEN_WITHOUT_TRACE",
    INVALID_DIR / "kernel_receipt_runtime_mismatch_without_reopen_trace.invalid.json": "EV4_RESPONSIVE_RUNTIME_MISMATCH_REOPEN_REQUIRED",
    INVALID_DIR / "kernel_receipt_runtime_mismatch_incomplete_reopen_trace.invalid.json": "EV4_RESPONSIVE_RUNTIME_MISMATCH_INCOMPLETE_TRACE",
    INVALID_DIR / "kernel_receipt_claims_redesign_authority.invalid.json": "EV4_RESPONSIVE_KERNEL_RECEIPT_FORBIDDEN_CLAIM",
    INVALID_DIR / "kernel_receipt_claims_runtime_monitor_enforcement.invalid.json": "EV4_RESPONSIVE_KERNEL_RECEIPT_FORBIDDEN_CLAIM",
}

SURFACE = "responsive_validation_report"


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def schema_validator() -> Draft202012Validator:
    schema = load(RECEIPT_SCHEMA)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def assert_receipt_schema(payload: dict[str, object], path: Path, validator: Draft202012Validator) -> None:
    receipt = payload.get("kernel_decision_receipt")
    errors = list(validator.iter_errors(receipt))
    if errors:
        detail = "; ".join(error.message for error in errors)
        raise ValueError(f"EV4_RESPONSIVE_KERNEL_RECEIPT_SCHEMA_INVALID: {rel(path)}: {detail}")


def assert_existing_outputs_render_success(validator: Draft202012Validator) -> None:
    for path in VALID_RESPONSIVE_OUTPUTS:
        payload = load(path)
        receipt = format_responsive_kernel_receipt(payload, SURFACE)
        errors = list(validator.iter_errors(receipt))
        if errors:
            detail = "; ".join(error.message for error in errors)
            raise ValueError(f"EV4_RESPONSIVE_KERNEL_RECEIPT_SCHEMA_INVALID: rendered {rel(path)}: {detail}")
        if receipt["receipt_state"] != "success":
            raise ValueError(f"EV4_RESPONSIVE_KERNEL_RECEIPT_VALID_OUTPUT_NOT_SUCCESS: {rel(path)}")
        if receipt["message"] != SUCCESS_MESSAGE:
            raise ValueError(f"EV4_RESPONSIVE_KERNEL_RECEIPT_MESSAGE_DRIFT: {rel(path)}")
        if "kernel-decision-card:" in receipt["message"]:
            raise ValueError(f"EV4_RESPONSIVE_KERNEL_RECEIPT_EXPOSED_TECHNICAL_ID: {rel(path)}")


def assert_success_fixture(validator: Draft202012Validator) -> None:
    payload = load(SUCCESS_RECEIPT_FIXTURE)
    assert_receipt_schema(payload, SUCCESS_RECEIPT_FIXTURE, validator)
    assert_receipt_matches_trace(payload, rel(SUCCESS_RECEIPT_FIXTURE), SURFACE)


def assert_warning_fixtures(validator: Draft202012Validator) -> None:
    for path in WARNING_RECEIPT_FIXTURES:
        payload = load(path)
        assert_receipt_schema(payload, path, validator)
        assert_receipt_matches_trace(payload, rel(path), SURFACE)
        receipt = payload["kernel_decision_receipt"]
        if receipt["receipt_state"] != "insufficient_evidence":
            raise ValueError(f"EV4_RESPONSIVE_KERNEL_RECEIPT_WARNING_EXPECTED: {rel(path)}")
        if receipt["message"] != WARNING_MESSAGE:
            raise ValueError(f"EV4_RESPONSIVE_KERNEL_RECEIPT_WARNING_TEXT_DRIFT: {rel(path)}")


def assert_invalid_fixtures_fail(validator: Draft202012Validator) -> None:
    for path, expected_diagnostic in INVALID_RECEIPT_FIXTURES.items():
        payload = load(path)
        assert_receipt_schema(payload, path, validator)
        try:
            surface = "mismatch_report" if "runtime_mismatch" in path.name else SURFACE
            assert_receipt_matches_trace(payload, rel(path), surface)
        except ValueError as exc:
            if expected_diagnostic not in str(exc):
                raise ValueError(
                    f"{rel(path)} failed for wrong reason; expected={expected_diagnostic}; actual={exc}"
                ) from exc
        else:
            raise ValueError(f"{rel(path)} unexpectedly passed Responsive Kernel receipt guard")


def main() -> int:
    try:
        validator = schema_validator()
        assert_existing_outputs_render_success(validator)
        assert_success_fixture(validator)
        assert_warning_fixtures(validator)
        assert_invalid_fixtures_fail(validator)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Responsive Kernel receipt check failed: {exc}", file=sys.stderr)
        return 1

    print("Responsive Kernel receipt check passed: receipts remain presentation-only and trace-backed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
