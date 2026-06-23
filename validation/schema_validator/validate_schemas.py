#!/usr/bin/env python3
"""Validate EV4 Responsive Architect JSON schemas and fixtures.

The validator deliberately has two layers:

1. JSON Schema validation:
   - every schema file parses as JSON;
   - every schema file is a valid Draft 2020-12 schema;
   - every schema file should reject unknown top-level fields;
   - valid fixtures must pass their referenced schema;
   - invalid fixtures must fail either schema validation or semantic validation.

2. EV4 semantic checks:
   - schema files should reject unknown top-level fields with additionalProperties=false;
   - payloads should expose a schema discriminator;
   - CSS selector safety payloads must not use global or broad Elementor selectors;
   - CSS selector payloads must include the project root class and target node class in the selector;
   - P0 system gates must reject schema-valid but semantically unsafe handoff, conflict,
     failure-map, final-audit, and fast-path payloads.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = ROOT / "schemas"
FIXTURES_DIR = ROOT / "validation" / "fixtures"

FORBIDDEN_ELEMENTOR_CLASSES = (
    ".elementor-widget-container",
    ".elementor-section",
    ".elementor-container",
)


class SemanticValidationError(AssertionError):
    """Raised when a payload passes JSON Schema but violates EV4 semantic gates."""


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_schema_files() -> dict[str, Any]:
    schemas: dict[str, Any] = {}
    for schema_path in sorted(SCHEMAS_DIR.glob("*.schema.json")):
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)
        if schema.get("type") == "object" and schema.get("additionalProperties") is not False:
            raise SemanticValidationError(f"{schema_path.name} must set additionalProperties=false")
        required = schema.get("required", [])
        if schema.get("type") == "object" and "schema" not in required:
            raise SemanticValidationError(f"{schema_path.name} must require schema discriminator")
        schemas[schema_path.name] = schema
    if not schemas:
        raise RuntimeError("No schema files found.")
    return schemas


def normalize_selector(selector: str) -> str:
    """Normalize selector whitespace without changing selector semantics."""

    return re.sub(r"\s+", " ", selector.strip())


def strip_attribute_selectors(selector: str) -> str:
    """Remove attribute selectors before token checks.

    Attribute values may legally contain characters such as # or *:
    [href="#section"], [class*="card"]. Those must not be interpreted as
    ID selectors or universal selectors by the coarse semantic safety gate.
    """

    return re.sub(r"\[[^\]]*\]", "", selector)


def semantic_validate_css_selector(payload: dict[str, Any]) -> None:
    if payload.get("schema") != "ev4-responsive-css-selector-safety@1.0.0":
        return

    selector = payload.get("selector", "")
    root_class = payload.get("project_root_class", "")
    target_class = payload.get("target_node_class", "")

    normalized = normalize_selector(selector)
    required_prefix = f".{root_class} .{target_class}"
    if not normalized.startswith(required_prefix):
        raise SemanticValidationError(
            "CSS selector must start with .<project_root_class> .<target_node_class>"
        )

    no_attributes = strip_attribute_selectors(normalized)

    if re.search(r"(?<![\w.-])(html|body)(?![\w-])", no_attributes):
        raise SemanticValidationError("CSS selector uses forbidden tag selector: html or body")
    if "*" in no_attributes:
        raise SemanticValidationError("CSS selector uses forbidden universal selector: *")
    if "#" in no_attributes:
        raise SemanticValidationError("CSS selector uses forbidden ID selector: #")

    for class_token in FORBIDDEN_ELEMENTOR_CLASSES:
        if class_token in no_attributes:
            raise SemanticValidationError(f"CSS selector uses forbidden Elementor class: {class_token}")

    if payload.get("uses_important") and not payload.get("important_justification"):
        raise SemanticValidationError("!important requires important_justification")

    if payload.get("breakpoint_source") in {"user_declaration", "assumed_default_with_unverified_label"}:
        if payload.get("production_ready_claim_allowed") is not False:
            raise SemanticValidationError(
                "Unverified breakpoint source must not allow production-ready claim"
            )


def semantic_validate_conflict_resolution(payload: dict[str, Any]) -> None:
    if payload.get("schema") != "ev4-responsive-conflict-resolution@1.0.0":
        return

    status = payload["conflict_status"]
    action = payload["resolution_action"]
    effect = payload["downstream_effect"]

    if status == "unresolved_blocking":
        if action != "block_downstream_until_resolved":
            raise SemanticValidationError(
                "unresolved_blocking conflict must use block_downstream_until_resolved"
            )
        if effect != "blocked":
            raise SemanticValidationError("unresolved_blocking conflict must block downstream")
        if payload.get("winning_source") is not None:
            raise SemanticValidationError("unresolved_blocking conflict must not declare a winner")
        if payload.get("losing_sources"):
            raise SemanticValidationError("unresolved_blocking conflict must not declare losers")

    if status == "resolved":
        if not payload.get("source_priority_applied"):
            raise SemanticValidationError("resolved conflict must apply source priority")
        if not payload.get("winning_source"):
            raise SemanticValidationError("resolved conflict must declare winning_source")
        if action == "block_downstream_until_resolved":
            raise SemanticValidationError("resolved conflict must not use unresolved block action")
        if effect == "blocked":
            raise SemanticValidationError("resolved conflict must not block downstream")

    if status == "not_a_conflict":
        if action != "mark_not_a_conflict":
            raise SemanticValidationError("not_a_conflict must use mark_not_a_conflict action")
        if effect == "blocked":
            raise SemanticValidationError("not_a_conflict must not block downstream")


def semantic_validate_failure_map(payload: dict[str, Any]) -> None:
    if payload.get("schema") != "ev4-responsive-failure-map@1.0.0":
        return

    unresolved_repair_unknowns = [
        item for item in payload.get("unknown_register", [])
        if item.get("required_to_select_repair") and not item.get("resolved")
    ]
    high_architecture_failures = [
        item for item in payload.get("failure_items", [])
        if item.get("architecture_mutation_risk") == "high"
    ]
    verdict = payload["map_verdict"]
    status = verdict["status"]
    action = verdict["required_next_action"]
    blockers = verdict.get("blocking_reasons", [])

    if unresolved_repair_unknowns:
        if status != "blocked_by_unknowns":
            raise SemanticValidationError(
                "repair-critical unresolved unknowns must set map_verdict.status=blocked_by_unknowns"
            )
        if action != "request_missing_evidence":
            raise SemanticValidationError(
                "repair-critical unresolved unknowns must request missing evidence"
            )
        if not blockers:
            raise SemanticValidationError(
                "repair-critical unresolved unknowns require blocking_reasons"
            )

    if high_architecture_failures:
        if status != "route_back_to_main_pipeline":
            raise SemanticValidationError(
                "high architecture mutation risk must route failure map back to main pipeline"
            )
        if action != "route_back_to_main_pipeline":
            raise SemanticValidationError(
                "high architecture mutation risk requires route_back_to_main_pipeline action"
            )
        if not blockers:
            raise SemanticValidationError(
                "high architecture mutation risk requires blocking_reasons"
            )

    if status == "ready_for_priority_ordering":
        if unresolved_repair_unknowns:
            raise SemanticValidationError(
                "ready_for_priority_ordering cannot have repair-critical unresolved unknowns"
            )
        if high_architecture_failures:
            raise SemanticValidationError(
                "ready_for_priority_ordering cannot include high architecture mutation risk"
            )
        if blockers:
            raise SemanticValidationError("ready_for_priority_ordering must not carry blocking_reasons")
        if action != "run_failure_priority_ordering":
            raise SemanticValidationError(
                "ready_for_priority_ordering must run failure priority ordering next"
            )


def semantic_validate_final_audit(payload: dict[str, Any]) -> None:
    if payload.get("schema") != "ev4-responsive-final-audit@1.0.0":
        return

    checks = payload["checks"]
    all_checks_passed = all(checks.values())
    verdict = payload["audit_verdict"]
    blockers = verdict.get("blocking_reasons", [])

    if verdict["handoff_allowed"]:
        if verdict["status"] != "controlled_handoff_allowed":
            raise SemanticValidationError("handoff_allowed=true requires controlled_handoff_allowed")
        if blockers:
            raise SemanticValidationError("handoff_allowed=true must not have blocking_reasons")
        if verdict["next_action"] != "handoff_export":
            raise SemanticValidationError("handoff_allowed=true requires next_action=handoff_export")
        if not all_checks_passed:
            raise SemanticValidationError("handoff_allowed=true requires every final-audit check to pass")

    if verdict["status"] == "controlled_handoff_allowed":
        if not verdict["handoff_allowed"]:
            raise SemanticValidationError("controlled_handoff_allowed requires handoff_allowed=true")
        if blockers:
            raise SemanticValidationError("controlled_handoff_allowed must not carry blocking_reasons")

    if blockers and verdict["handoff_allowed"]:
        raise SemanticValidationError("blocking_reasons must force handoff_allowed=false")


def semantic_validate_handoff_ingest_decision(payload: dict[str, Any]) -> None:
    if payload.get("schema") != "ev4-responsive-handoff-ingest-decision@1.0.0":
        return

    status = payload["payload_status"]
    all_payloads_present = all(payload["required_payloads"].values())
    blockers = payload.get("blocking_reasons", [])
    flags = payload.get("visible_flags", [])
    downstream_allowed = payload["downstream_allowed"]
    next_action = payload["required_next_action"]

    if status == "accepted":
        if not payload["handoff_schema_valid"]:
            raise SemanticValidationError("accepted handoff requires handoff_schema_valid=true")
        if not all_payloads_present:
            raise SemanticValidationError("accepted handoff requires every required payload")
        if blockers or flags:
            raise SemanticValidationError("accepted handoff must not carry blockers or visible flags")
        if not downstream_allowed:
            raise SemanticValidationError("accepted handoff must allow downstream")
        if next_action != "start_responsive_intake":
            raise SemanticValidationError("accepted handoff must start responsive intake")

    if status in {"blocked_missing_payload", "blocked_schema_failure"}:
        if downstream_allowed:
            raise SemanticValidationError("blocked handoff status must set downstream_allowed=false")
        if not blockers:
            raise SemanticValidationError("blocked handoff status requires blocking_reasons")
        if next_action == "start_responsive_intake":
            raise SemanticValidationError("blocked handoff status must not start responsive intake")
        if status == "blocked_missing_payload" and all_payloads_present:
            raise SemanticValidationError("blocked_missing_payload requires at least one missing payload")
        if status == "blocked_schema_failure" and payload["handoff_schema_valid"]:
            raise SemanticValidationError("blocked_schema_failure requires handoff_schema_valid=false")

    if status == "continue_degraded_with_visible_flags":
        if not downstream_allowed:
            raise SemanticValidationError("degraded handoff must allow downstream with visible flags")
        if not flags:
            raise SemanticValidationError("degraded handoff requires visible_flags")
        if blockers:
            raise SemanticValidationError("degraded handoff must not carry blocking_reasons")
        if next_action != "continue_degraded_with_flags":
            raise SemanticValidationError("degraded handoff requires continue_degraded_with_flags action")

    if status == "routed_to_main_pipeline":
        if downstream_allowed:
            raise SemanticValidationError("routed_to_main_pipeline must not allow responsive downstream")
        if next_action != "route_back_to_main_pipeline":
            raise SemanticValidationError("routed_to_main_pipeline requires route_back_to_main_pipeline action")
        if not blockers:
            raise SemanticValidationError("routed_to_main_pipeline requires blocking_reasons")


def semantic_validate_fast_path_eligibility(payload: dict[str, Any]) -> None:
    if payload.get("schema") != "ev4-responsive-fast-path-eligibility@1.0.0":
        return

    criteria = payload["criteria"]
    safe_for_fast_path = (
        criteria["affected_viewport_count"] <= 1
        and criteria["custom_css_required"] is False
        and criteria["meaningful_visibility_change"] is False
        and criteria["content_order_change"] is False
        and criteria["overlay_or_connector_risk"] is False
        and criteria["architecture_mutation_risk"] is False
        and criteria["cascade_risk"] == "low"
        and criteria["unknowns_required_for_repair"] is False
        and criteria["accessibility_gate_triggered"] is False
    )

    if payload["eligibility_status"] == "eligible":
        if not safe_for_fast_path:
            raise SemanticValidationError("eligible fast-path requires every fast-path criterion to be safe")
        if payload["required_next_action"] != "use_triage_fast_path":
            raise SemanticValidationError("eligible fast-path requires use_triage_fast_path action")

    if payload["required_next_action"] == "use_triage_fast_path" and not safe_for_fast_path:
        raise SemanticValidationError("use_triage_fast_path is forbidden when fast-path criteria are unsafe")

    if payload["eligibility_status"] == "not_eligible" and payload["required_next_action"] == "use_triage_fast_path":
        raise SemanticValidationError("not_eligible fast-path must not use triage fast path")


def semantic_validate_payload(payload: dict[str, Any]) -> None:
    semantic_validate_css_selector(payload)
    semantic_validate_conflict_resolution(payload)
    semantic_validate_failure_map(payload)
    semantic_validate_final_audit(payload)
    semantic_validate_handoff_ingest_decision(payload)
    semantic_validate_fast_path_eligibility(payload)


def validate_fixture(path: Path, schemas: dict[str, Any], should_pass: bool) -> None:
    original_payload = load_json(path)
    if not isinstance(original_payload, dict):
        raise RuntimeError(f"Fixture {path} must be a JSON object")

    payload = dict(original_payload)
    schema_file = payload.pop("$schema_file", None)
    if not schema_file:
        raise RuntimeError(f"Fixture {path} is missing $schema_file")
    if schema_file not in schemas:
        raise RuntimeError(f"Fixture {path} references missing schema {schema_file}")

    validator = Draft202012Validator(schemas[schema_file])
    errors = sorted(validator.iter_errors(payload), key=lambda e: [str(p) for p in e.path])

    semantic_error: Exception | None = None
    if not errors:
        try:
            semantic_validate_payload(payload)
        except Exception as exc:  # noqa: BLE001 - report semantic failures uniformly
            semantic_error = exc

    failed = bool(errors) or semantic_error is not None

    if should_pass and failed:
        if errors:
            raise AssertionError(f"Expected {path} to pass, got schema error: {errors[0].message}")
        raise AssertionError(f"Expected {path} to pass, got semantic error: {semantic_error}")

    if not should_pass and not failed:
        raise AssertionError(f"Expected {path} to fail, but it passed")


def validate_fixtures(schemas: dict[str, Any]) -> None:
    valid_dir = FIXTURES_DIR / "valid"
    invalid_dir = FIXTURES_DIR / "invalid"
    for path in sorted(valid_dir.glob("*.json")) if valid_dir.exists() else []:
        validate_fixture(path, schemas, should_pass=True)
    for path in sorted(invalid_dir.glob("*.json")) if invalid_dir.exists() else []:
        validate_fixture(path, schemas, should_pass=False)


def main() -> int:
    try:
        schemas = validate_schema_files()
        validate_fixtures(schemas)
    except Exception as exc:  # noqa: BLE001 - CLI should print compact failure
        print(f"schema validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"schema validation passed: {len(schemas)} schema(s) checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
