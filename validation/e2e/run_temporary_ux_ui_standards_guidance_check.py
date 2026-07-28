#!/usr/bin/env python3
"""Validate temporary UX/UI standards guidance fixtures fail-closed."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "contracts/guidance/temporary-ux-ui-standards-guidance.v1.schema.json"
FIXTURE_ROOT = ROOT / "validation/fixtures/temporary_ux_ui_standards_guidance"

EXPECTED_INVALID_DIAGNOSTICS = {
    "authority_substitution.invalid.json": {"AUTHORITY_SUBSTITUTION_FORBIDDEN"},
    "correctness_upgrade.invalid.json": {"CORRECTNESS_UPGRADE_FORBIDDEN"},
    "expired_guidance.invalid.json": {"LIFECYCLE_NOT_SELECTABLE"},
    "missing_provenance.invalid.json": {"PROVENANCE_REQUIRED"},
    "stale_active_review.invalid.json": {"LIFECYCLE_REVIEW_OVERDUE"},
    "universal_rule.invalid.json": {"UNIVERSAL_RULE_FORBIDDEN"},
    "unresolved_conflict.invalid.json": {"UNRESOLVED_HIGHER_AUTHORITY_CONFLICT"},
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def schema_error_code(error: ValidationError) -> str:
    path = tuple(str(part) for part in error.absolute_path)
    if path == ("authority_boundary", "replaces_contracts_or_validators"):
        return "AUTHORITY_SUBSTITUTION_FORBIDDEN"
    if path in {
        ("authority_boundary", "may_establish_correctness"),
        ("boundary_claims", "responsive_correctness_validated"),
    }:
        return "CORRECTNESS_UPGRADE_FORBIDDEN"
    if error.validator == "required" and path[:1] == ("guidance_items",) and "'provenance'" in error.message:
        return "PROVENANCE_REQUIRED"
    if len(path) >= 3 and path[0] == "guidance_items" and path[-1] == "universal_rule_claimed":
        return "UNIVERSAL_RULE_FORBIDDEN"
    return f"SCHEMA:{error.validator}:{'/'.join(path) or '<root>'}"


def semantic_error_codes(payload: dict) -> list[str]:
    errors: list[str] = []
    lifecycle = payload.get("lifecycle", {})
    status = lifecycle.get("status")
    if status in {"expired", "superseded"}:
        errors.append("LIFECYCLE_NOT_SELECTABLE")
    if status == "active":
        review_by = lifecycle.get("review_by")
        try:
            review_date = date.fromisoformat(review_by)
        except (TypeError, ValueError):
            review_date = None
        if review_date is not None and review_date < date.today():
            errors.append("LIFECYCLE_REVIEW_OVERDUE")

    for item in payload.get("guidance_items", []):
        for conflict in item.get("conflicts", []):
            if conflict.get("status") == "unresolved":
                errors.append("UNRESOLVED_HIGHER_AUTHORITY_CONFLICT")
    return errors


def validate_payload(validator: Draft202012Validator, payload: dict) -> list[str]:
    schema_codes = [schema_error_code(error) for error in validator.iter_errors(payload)]
    return schema_codes + semantic_error_codes(payload)


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    valid_paths = sorted((FIXTURE_ROOT / "valid").glob("*.json"))
    invalid_paths = sorted((FIXTURE_ROOT / "invalid").glob("*.json"))
    if not valid_paths or not invalid_paths:
        print("fixture matrix must contain valid and invalid fixtures", file=sys.stderr)
        return 1

    invalid_names = {path.name for path in invalid_paths}
    expected_names = set(EXPECTED_INVALID_DIAGNOSTICS)
    if invalid_names != expected_names:
        missing = sorted(expected_names - invalid_names)
        unexpected = sorted(invalid_names - expected_names)
        print(
            "invalid fixture diagnostic manifest mismatch: "
            f"missing={missing}, unexpected={unexpected}",
            file=sys.stderr,
        )
        return 1

    failures: list[str] = []
    for path in valid_paths:
        errors = validate_payload(validator, load_json(path))
        if errors:
            failures.append(f"valid fixture rejected: {path.relative_to(ROOT)}: {errors}")

    for path in invalid_paths:
        errors = validate_payload(validator, load_json(path))
        expected = EXPECTED_INVALID_DIAGNOSTICS[path.name]
        missing = sorted(expected - set(errors))
        if missing:
            failures.append(
                f"invalid fixture missing expected diagnostic: {path.relative_to(ROOT)}: "
                f"expected={sorted(expected)}, observed={errors}"
            )

    if failures:
        print("temporary UX/UI standards guidance validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(
        "temporary UX/UI standards guidance validation passed "
        f"({len(valid_paths)} valid, {len(invalid_paths)} invalid fixtures; "
        "diagnostic-specific negative coverage enforced)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
