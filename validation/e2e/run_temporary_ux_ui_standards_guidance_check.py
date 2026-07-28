#!/usr/bin/env python3
"""Validate temporary UX/UI standards guidance fixtures fail-closed."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "contracts/guidance/temporary-ux-ui-standards-guidance.v1.schema.json"
FIXTURE_ROOT = ROOT / "validation/fixtures/temporary_ux_ui_standards_guidance"
APPROVED_REPOSITORY_URL = "https://github.com/rezahh107/EV4-Responsive-Architect"

EXPECTED_INVALID_DIAGNOSTICS = {
    "accessibility_upgrade.invalid.json": {"ACCESSIBILITY_UPGRADE_FORBIDDEN"},
    "authority_substitution.invalid.json": {"AUTHORITY_SUBSTITUTION_FORBIDDEN"},
    "correctness_upgrade.invalid.json": {"CORRECTNESS_UPGRADE_FORBIDDEN"},
    "expired_guidance.invalid.json": {"LIFECYCLE_NOT_SELECTABLE"},
    "export_upgrade.invalid.json": {"EXPORT_UPGRADE_FORBIDDEN"},
    "live_render_upgrade.invalid.json": {"LIVE_RENDER_UPGRADE_FORBIDDEN"},
    "malformed_lifecycle.invalid.json": {"SCHEMA:type:lifecycle"},
    "missing_conflict_disposition.invalid.json": {"CONFLICT_DISPOSITION_REQUIRED"},
    "missing_exceptions.invalid.json": {"EXCEPTIONS_REQUIRED"},
    "missing_provenance.invalid.json": {"PROVENANCE_REQUIRED"},
    "pilot_upgrade.invalid.json": {"PILOT_UPGRADE_FORBIDDEN"},
    "pixel_upgrade.invalid.json": {"PIXEL_UPGRADE_FORBIDDEN"},
    "production_ready_authored.invalid.json": {"PRODUCTION_READINESS_AUTHORED"},
    "release_upgrade.invalid.json": {"RELEASE_UPGRADE_FORBIDDEN"},
    "resolved_conflict_without_reference.invalid.json": {"CONFLICT_RESOLUTION_REFERENCE_REQUIRED"},
    "stale_active_review.invalid.json": {"LIFECYCLE_REVIEW_OVERDUE"},
    "submitted_evidence_upgrade.invalid.json": {"SUBMITTED_EVIDENCE_UPGRADE_FORBIDDEN"},
    "universal_rule.invalid.json": {"UNIVERSAL_RULE_FORBIDDEN"},
    "unresolved_conflict.invalid.json": {"UNRESOLVED_HIGHER_AUTHORITY_CONFLICT"},
    "unverifiable_provenance.invalid.json": {"PROVENANCE_UNVERIFIABLE"},
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def schema_error_code(error: ValidationError) -> str:
    path = tuple(str(part) for part in error.absolute_path)
    if path in {
        ("authority_boundary", "replaces_contracts_or_validators"),
        ("authority_boundary", "replaces_stage_anchors"),
        ("authority_boundary", "replaces_kernel_decisions"),
        ("authority_boundary", "replaces_project_gate_authority"),
    }:
        return "AUTHORITY_SUBSTITUTION_FORBIDDEN"
    if path == ("authority_boundary", "may_establish_correctness"):
        return "CORRECTNESS_UPGRADE_FORBIDDEN"
    boundary_codes = {
        ("boundary_claims", "submitted_evidence_created"): "SUBMITTED_EVIDENCE_UPGRADE_FORBIDDEN",
        ("boundary_claims", "pilot_authorized"): "PILOT_UPGRADE_FORBIDDEN",
        ("boundary_claims", "release_ready"): "RELEASE_UPGRADE_FORBIDDEN",
        ("boundary_claims", "live_render_validated"): "LIVE_RENDER_UPGRADE_FORBIDDEN",
        ("boundary_claims", "export_json_validated"): "EXPORT_UPGRADE_FORBIDDEN",
        ("boundary_claims", "accessibility_passed"): "ACCESSIBILITY_UPGRADE_FORBIDDEN",
        ("boundary_claims", "pixel_perfect"): "PIXEL_UPGRADE_FORBIDDEN",
        ("boundary_claims", "responsive_correctness_validated"): "CORRECTNESS_UPGRADE_FORBIDDEN",
    }
    if path in boundary_codes:
        return boundary_codes[path]
    if error.validator == "required" and path[:1] == ("guidance_items",):
        if "'provenance'" in error.message:
            return "PROVENANCE_REQUIRED"
        if "'exceptions'" in error.message:
            return "EXCEPTIONS_REQUIRED"
    if error.validator == "required" and "guidance_items" in path and "conflicts" in path:
        if "'resolution_reference'" in error.message:
            return "CONFLICT_RESOLUTION_REFERENCE_REQUIRED"
        if "'higher_authority_reference'" in error.message or "'status'" in error.message:
            return "CONFLICT_DISPOSITION_REQUIRED"
    if path and path[-1] == "resolution_reference" and error.validator in {"type", "minLength"}:
        return "CONFLICT_RESOLUTION_REFERENCE_REQUIRED"
    if len(path) >= 3 and path[0] == "guidance_items" and path[-1] == "universal_rule_claimed":
        return "UNIVERSAL_RULE_FORBIDDEN"
    if error.validator == "additionalProperties" and path == ("boundary_claims",) and "'production_ready'" in error.message:
        return "PRODUCTION_READINESS_AUTHORED"
    return f"SCHEMA:{error.validator}:{'/'.join(path) or '<root>'}"


def provenance_is_locally_verifiable(provenance: object) -> bool:
    if not isinstance(provenance, dict):
        return False
    source_url = provenance.get("source_url")
    if not isinstance(source_url, str):
        return False
    parsed = urlparse(source_url)
    if parsed.scheme != "https" or parsed.netloc != "github.com":
        return False
    normalized = source_url.rstrip("/")
    return normalized == APPROVED_REPOSITORY_URL or normalized.startswith(f"{APPROVED_REPOSITORY_URL}/blob/")


def semantic_error_codes(payload: dict) -> list[str]:
    errors: list[str] = []
    lifecycle = payload.get("lifecycle", {})
    if isinstance(lifecycle, dict):
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

    guidance_items = payload.get("guidance_items", [])
    if not isinstance(guidance_items, list):
        return errors
    for item in guidance_items:
        if not isinstance(item, dict):
            continue
        if "provenance" in item and not provenance_is_locally_verifiable(item.get("provenance")):
            errors.append("PROVENANCE_UNVERIFIABLE")
        conflicts = item.get("conflicts", [])
        if not isinstance(conflicts, list):
            continue
        for conflict in conflicts:
            if not isinstance(conflict, dict):
                continue
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
