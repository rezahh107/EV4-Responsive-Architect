#!/usr/bin/env python3
"""Validate Prompt 5 routing-to-receipt correlation fixtures fail closed."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "contracts/project-gate/prompt-5-routing-receipt-correlation.v1.schema.json"
FIXTURE_ROOT = ROOT / "validation/fixtures/prompt_5_routing_receipt_correlation"

EXPECTED_INVALID_DIAGNOSTICS = {
    "receipt_identity_mismatch.invalid.json": {"RECEIPT_IDENTITY_MISMATCH"},
    "authority_upgrade.invalid.json": {"AUTHORITY_SUBSTITUTION_FORBIDDEN"},
    "boundary_upgrade.invalid.json": {"RESPONSIVE_CORRECTNESS_UPGRADE_FORBIDDEN"},
}


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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


def semantic_error_codes(payload: object) -> set[str]:
    errors: set[str] = set()
    if not isinstance(payload, dict):
        return errors
    receipt = payload.get("receipt")
    if isinstance(receipt, dict):
        receipt_id = receipt.get("receipt_id")
        receipt_sha256 = receipt.get("receipt_sha256")
        if isinstance(receipt_id, str) and isinstance(receipt_sha256, str):
            if receipt_id != f"sha256:{receipt_sha256}":
                errors.add("RECEIPT_IDENTITY_MISMATCH")
    return errors


def diagnostics(payload: object, validator: Draft202012Validator) -> set[str]:
    codes = {schema_error_code(error) for error in validator.iter_errors(payload)}
    codes.update(semantic_error_codes(payload))
    return codes


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema)

    valid_payload = load_json(FIXTURE_ROOT / "valid.json")
    valid_codes = diagnostics(valid_payload, validator)
    if valid_codes:
        print(f"valid fixture rejected: {sorted(valid_codes)}", file=sys.stderr)
        return 1

    for filename, expected in EXPECTED_INVALID_DIAGNOSTICS.items():
        payload = load_json(FIXTURE_ROOT / filename)
        observed = diagnostics(payload, validator)
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
