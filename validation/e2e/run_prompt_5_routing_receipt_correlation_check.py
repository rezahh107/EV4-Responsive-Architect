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
    "lineage_divergence.invalid.json": {"DECISION_LINEAGE_MISMATCH"},
    "outcome_mismatch.invalid.json": {"ROUTE_RECEIPT_OUTCOME_MISMATCH"},
    "misleading_success_text.invalid.json": {"RECEIPT_TEXT_AUTHORITY_FORBIDDEN"},
    "duplicate_identity.invalid.json": {"DUPLICATE_RECEIPT_IDENTITY_AMBIGUOUS"},
    "unsupported_version.invalid.json": {"UNSUPPORTED_CORRELATION_VERSION"},
    "authority_upgrade.invalid.json": {"AUTHORITY_SUBSTITUTION_FORBIDDEN"},
    "boundary_upgrade.invalid.json": {"RESPONSIVE_CORRECTNESS_UPGRADE_FORBIDDEN"},
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_receipt_bytes(receipt: dict[str, Any]) -> bytes:
    # The receipt schema identity source contains strings only. For this domain,
    # sorted object keys, compact separators, UTF-8, and no NaN are RFC 8785 JCS.
    return json.dumps(
        receipt,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def receipt_digest(receipt: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_receipt_bytes(receipt)).hexdigest()


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
    if path == ("schema_version",):
        return "UNSUPPORTED_CORRELATION_VERSION"
    return f"SCHEMA:{error.validator}:{'/'.join(path) or '<root>'}"


def validate_record(
    record: dict[str, Any],
    correlation_validator: Draft202012Validator,
    receipt_validator: Draft202012Validator,
) -> tuple[set[str], str | None, str | None]:
    correlation = record.get("correlation")
    errors = {
        schema_error_code(error)
        for error in correlation_validator.iter_errors(correlation)
    }
    source_receipt = record.get("source_receipt")
    source_lineage = record.get("source_lineage")

    if not isinstance(source_receipt, dict):
        errors.add("CANONICAL_RECEIPT_MISSING")
        return errors, None, None
    if list(receipt_validator.iter_errors(source_receipt)):
        errors.add("CANONICAL_RECEIPT_SCHEMA_INVALID")
    if not isinstance(source_lineage, dict) or not isinstance(correlation, dict):
        errors.add("CORRELATION_SOURCE_MISSING")
        return errors, None, None

    computed = receipt_digest(source_receipt)
    receipt = correlation.get("receipt", {})
    declared_sha = receipt.get("receipt_sha256")
    declared_id = receipt.get("receipt_id")

    if declared_sha != computed:
        errors.add("RECEIPT_DIGEST_MISMATCH")
    if declared_id != f"sha256:{computed}":
        errors.add("RECEIPT_IDENTITY_MISMATCH")

    lineage = correlation.get("lineage", {})
    for field in ("decision_family", "decision_card_ref"):
        if lineage.get(field) != source_lineage.get(field):
            errors.add("DECISION_LINEAGE_MISMATCH")

    outcome = correlation.get("outcome", {})
    route_decision = outcome.get("route_decision")
    pinned_state = outcome.get("receipt_state")
    actual_state = source_receipt.get("receipt_state")
    if pinned_state != actual_state:
        errors.add("ROUTE_RECEIPT_OUTCOME_MISMATCH")
    if route_decision == "reject" and actual_state == "success":
        errors.add("ROUTE_RECEIPT_OUTCOME_MISMATCH")
    if route_decision == "route" and actual_state not in {
        "success",
        "insufficient_evidence",
    }:
        errors.add("ROUTE_RECEIPT_OUTCOME_MISMATCH")

    message = source_receipt.get("message", "")
    if (
        route_decision == "reject"
        and isinstance(message, str)
        and ("✅" in message or "success" in message.lower())
    ):
        errors.add("RECEIPT_TEXT_AUTHORITY_FORBIDDEN")

    return errors, declared_id if isinstance(declared_id, str) else None, computed


def diagnostics(
    payload: Any,
    correlation_validator: Draft202012Validator,
    receipt_validator: Draft202012Validator,
) -> set[str]:
    if not isinstance(payload, dict):
        return {"FIXTURE_ROOT_INVALID"}
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        return {"FIXTURE_RECORDS_MISSING"}

    codes: set[str] = set()
    identities: dict[str, str] = {}
    for record in records:
        if not isinstance(record, dict):
            codes.add("FIXTURE_RECORD_INVALID")
            continue
        record_codes, declared_id, computed = validate_record(
            record, correlation_validator, receipt_validator
        )
        codes.update(record_codes)
        if declared_id is not None and computed is not None:
            previous = identities.get(declared_id)
            if previous is not None and previous != computed:
                codes.add("DUPLICATE_RECEIPT_IDENTITY_AMBIGUOUS")
            else:
                identities[declared_id] = computed
    return codes


def main() -> int:
    correlation_validator = Draft202012Validator(load_json(CORRELATION_SCHEMA_PATH))
    receipt_validator = Draft202012Validator(load_json(RECEIPT_SCHEMA_PATH))

    valid_codes = diagnostics(
        load_json(FIXTURE_ROOT / "valid.json"),
        correlation_validator,
        receipt_validator,
    )
    if valid_codes:
        print(f"valid fixture rejected: {sorted(valid_codes)}", file=sys.stderr)
        return 1

    for filename, expected in EXPECTED_INVALID_DIAGNOSTICS.items():
        observed = diagnostics(
            load_json(FIXTURE_ROOT / filename),
            correlation_validator,
            receipt_validator,
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
