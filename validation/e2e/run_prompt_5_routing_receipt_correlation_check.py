#!/usr/bin/env python3
"""Validate Prompt 5 routing-to-receipt correlation fixtures fail closed."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[2]
CORRELATION_SCHEMA_PATH = ROOT / "contracts/project-gate/prompt-5-routing-receipt-correlation.v1.schema.json"
RECEIPT_SCHEMA_PATH = ROOT / "schemas/ev4-responsive-kernel-decision-receipt.schema.json"
FIXTURE_ROOT = ROOT / "validation/fixtures/prompt_5_routing_receipt_correlation"

EXPECTED_INVALID_DIAGNOSTICS = {
    "receipt_identity_mismatch.invalid.json": {"RECEIPT_IDENTITY_MISMATCH"},
    "receipt_content_digest_mismatch.invalid.json": {"RECEIPT_DIGEST_MISMATCH"},
    "authority_upgrade.invalid.json": {"AUTHORITY_SUBSTITUTION_FORBIDDEN"},
    "boundary_upgrade.invalid.json": {"RESPONSIVE_CORRECTNESS_UPGRADE_FORBIDDEN"},
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def receipt_digest(receipt: dict[str, Any]) -> str:
    canonical = json.dumps(
        receipt,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def schema_error_code(error: ValidationError) -> str:
    path = tuple(str(part) for part in error.absolute_path)
    authority_paths = {
        ("authority", "responsive_executes_project_gate_transport"),
        ("authority", "receipt_text_is_kernel_authority"),
        ("authority", "correlation_replaces_kernel_decision"),
        ("authority", "correlation_replaces_project_gate_decision"),
    }
    if path in authority_paths:
        return "AUTHORITY_SUBSTITUTION_FORBIDDEN"
    if path == ("boundary_claims", "responsive_correctness_validated"):
        return "RESPONSIVE_CORRECTNESS_UPGRADE_FORBIDDEN"
    return f"SCHEMA:{error.validator}:{'/'.join(path) or '<root>'}"


def diagnostics(
    payload: Any,
    correlation_validator: Draft202012Validator,
    receipt_validator: Draft202012Validator,
) -> set[str]:
    if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
        return {"FIXTURE_RECORDS_MISSING"}

    codes: set[str] = set()
    for record in payload["records"]:
        if not isinstance(record, dict):
            codes.add("FIXTURE_RECORD_INVALID")
            continue
        source_receipt = record.get("source_receipt")
        correlation = record.get("correlation")
        if not isinstance(source_receipt, dict) or not isinstance(correlation, dict):
            codes.add("CORRELATION_SOURCE_MISSING")
            continue
        if list(receipt_validator.iter_errors(source_receipt)):
            codes.add("CANONICAL_RECEIPT_SCHEMA_INVALID")
        codes.update(
            schema_error_code(error)
            for error in correlation_validator.iter_errors(correlation)
        )
        computed = receipt_digest(source_receipt)
        receipt = correlation.get("receipt", {})
        if receipt.get("receipt_sha256") != computed:
            codes.add("RECEIPT_DIGEST_MISMATCH")
        if receipt.get("receipt_id") != f"sha256:{computed}":
            codes.add("RECEIPT_IDENTITY_MISMATCH")
    return codes


def main() -> int:
    correlation_validator = Draft202012Validator(load_json(CORRELATION_SCHEMA_PATH))
    receipt_validator = Draft202012Validator(load_json(RECEIPT_SCHEMA_PATH))

    valid_codes = diagnostics(
        load_json(FIXTURE_ROOT / "valid.json"), correlation_validator, receipt_validator
    )
    if valid_codes:
        print(f"valid fixture rejected: {sorted(valid_codes)}", file=sys.stderr)
        return 1

    for filename, expected in EXPECTED_INVALID_DIAGNOSTICS.items():
        observed = diagnostics(
            load_json(FIXTURE_ROOT / filename), correlation_validator, receipt_validator
        )
        missing = expected - observed
        if missing:
            print(
                f"{filename}: missing diagnostics {sorted(missing)}; observed {sorted(observed)}",
                file=sys.stderr,
            )
            return 1

    print("Prompt 5 routing-to-receipt correlation fixtures: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
