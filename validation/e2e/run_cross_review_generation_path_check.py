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
    if template["cross_critique"]["status"] != "blocked_missing_cross_critique":
        raise QualityGateError("cross-review record template must require a completed separate review")
    if template["cross_critique"]["reviewer_role"] != "strict_pessimistic_reviewer":
        raise QualityGateError("cross-review record template must preserve strict reviewer role")


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
