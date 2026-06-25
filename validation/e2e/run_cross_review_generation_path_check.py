#!/usr/bin/env python3
from __future__ import annotations

import json
import traceback
from pathlib import Path
from typing import Any

from run_task_quality_gate_check import (
    QualityGateError,
    assert_schema_valid,
    semantic_validate_review,
)

ROOT = Path(__file__).resolve().parents[2]
REQUEST_TEMPLATE = ROOT / "planning" / "reviews" / "CROSS_CRITIQUE_REQUEST.template.md"
REVIEW_RECORD_TEMPLATE = ROOT / "planning" / "reviews" / "CROSS_REVIEW_RECORD.template.json"
REVIEW_RECORD_EXAMPLE = ROOT / "planning" / "reviews" / "TQR-RQ-0000.cross-review.example.json"
REVIEW_README = ROOT / "planning" / "reviews" / "README.md"
REVIEW_SCHEMA = ROOT / "schemas" / "ev4-responsive-task-quality-review.schema.json"

REQUIRED_REQUEST_TERMS = {
    "request_path: planning/reviews/CRR-{TASK_REF}.cross-review-request.md",
    "review_record_path: planning/reviews/TQR-{TASK_REF}.cross-review.json",
    "required_output_schema: ev4-responsive-task-quality-review@1.0.0",
    "reviewer_role: strict_pessimistic_reviewer",
    "cross_critique.status=completed",
}

REQUIRED_README_TERMS = {
    "planning/reviews/TQR-{TASK_REF}.cross-review.json",
    "planning/reviews/CRR-{TASK_REF}.cross-review-request.md",
    "ev4-responsive-task-quality-review@1.0.0",
    "not responsive evidence",
}

EXPECTED_DETERMINISTIC_CHECKS = {
    "acceptance_criteria_checked",
    "scope_respected",
    "forbidden_work_absent",
    "ci_checked_or_no_ci_reason_recorded",
    "artifacts_listed",
    "queue_state_checked",
    "ledger_state_checked",
    "stale_reference_search_done",
    "delayed_bot_review_window_checked",
    "boundary_assertions_checked",
}

EXPECTED_BOUNDARY_ASSERTIONS = {
    "no_self_critique_only_completion",
    "deterministic_checks_passed",
    "bot_review_window_checked",
    "no_production_claim",
    "no_unrelated_task",
    "follow_up_created_when_required",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_terms(text: str, terms: set[str], label: str) -> None:
    missing = [term for term in sorted(terms) if term not in text]
    if missing:
        raise QualityGateError(f"{label} is missing required terms: {', '.join(missing)}")


def assert_review_record_paths() -> None:
    for path in (REQUEST_TEMPLATE, REVIEW_RECORD_TEMPLATE, REVIEW_RECORD_EXAMPLE, REVIEW_README):
        if not path.exists():
            raise QualityGateError(f"missing cross-review artifact path: {path.relative_to(ROOT)}")


def assert_blocking_template(template: dict[str, Any], schema: dict[str, Any]) -> None:
    assert_schema_valid(template, schema, "cross-review record template")
    if template["completion_allowed"] is not False:
        raise QualityGateError("cross-review record template must not allow completion")
    if template["final_verdict"] != "blocked":
        raise QualityGateError("cross-review record template must start blocked")

    deterministic_checks = template["deterministic_checks"]
    actual_checks = set(deterministic_checks)
    if actual_checks != EXPECTED_DETERMINISTIC_CHECKS:
        missing = sorted(EXPECTED_DETERMINISTIC_CHECKS - actual_checks)
        extra = sorted(actual_checks - EXPECTED_DETERMINISTIC_CHECKS)
        raise QualityGateError(
            "cross-review record template has invalid deterministic checks; "
            f"missing={missing}, extra={extra}"
        )
    for check, value in deterministic_checks.items():
        if value is not False:
            raise QualityGateError(f"deterministic check '{check}' must be false in the template")

    cross = template["cross_critique"]
    if cross["required"] is not True:
        raise QualityGateError("cross-review record template must require cross critique")
    if cross["status"] != "blocked_missing_cross_critique":
        raise QualityGateError("cross-review record template must require a completed separate review")
    if cross["reviewer_role"] != "strict_pessimistic_reviewer":
        raise QualityGateError("cross-review record template must preserve strict reviewer role")
    if cross["prompt_separation"] is not True:
        raise QualityGateError("cross-review record template must require prompt separation")
    if cross["temperature_policy"] != "temperature_0_1_recommended":
        raise QualityGateError("cross-review record template must require recommended temperature policy")

    actual_assertions = set(template.get("boundary_assertions", []))
    if actual_assertions != EXPECTED_BOUNDARY_ASSERTIONS:
        missing = sorted(EXPECTED_BOUNDARY_ASSERTIONS - actual_assertions)
        extra = sorted(actual_assertions - EXPECTED_BOUNDARY_ASSERTIONS)
        raise QualityGateError(
            "cross-review record template has invalid boundary assertions; "
            f"missing={missing}, extra={extra}"
        )


def main() -> int:
    try:
        assert_review_record_paths()
        require_terms(read_text(REQUEST_TEMPLATE), REQUIRED_REQUEST_TERMS, "cross-review request template")
        require_terms(read_text(REVIEW_README), REQUIRED_README_TERMS, "cross-review README")

        schema = load_json(REVIEW_SCHEMA)
        assert_blocking_template(load_json(REVIEW_RECORD_TEMPLATE), schema)
        example = load_json(REVIEW_RECORD_EXAMPLE)
        assert_schema_valid(example, schema, "cross-review completed example")
        semantic_validate_review(example)
    except QualityGateError as exc:
        print(f"cross-review generation path validation failed: {exc}")
        return 1
    except Exception:
        traceback.print_exc()
        return 1

    print("Cross-review generation path validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
