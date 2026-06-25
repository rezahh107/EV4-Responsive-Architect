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
PROMPT = ROOT / "prompts" / "CROSS_CRITIQUE_STRICT_REVIEWER_PROMPT.md"
REQUEST_TEMPLATE = ROOT / "planning" / "reviews" / "CROSS_CRITIQUE_REQUEST.template.md"
REVIEW_EXAMPLE = ROOT / "planning" / "reviews" / "TQR-RQ-0000.cross-review.example.json"
REVIEW_RECORD_TEMPLATE = ROOT / "planning" / "reviews" / "CROSS_REVIEW_RECORD.template.json"
REVIEW_SCHEMA = ROOT / "schemas" / "ev4-responsive-task-quality-review.schema.json"

REQUIRED_PROMPT_TERMS = {
    "strict_pessimistic_reviewer",
    "temperature_0_1_recommended",
    "not the implementer",
    "green CI",
    "merged PR",
    "self-critique",
}

REQUIRED_REQUEST_TERMS = {
    "prompt_file: prompts/CROSS_CRITIQUE_STRICT_REVIEWER_PROMPT.md",
    "required_output_schema: ev4-responsive-task-quality-review@1.0.0",
    "task_sensitivity: sensitive",
    "reviewer_role: strict_pessimistic_reviewer",
    "review_record_path: planning/reviews/TQR-{TASK_REF}.cross-review.json",
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


def main() -> int:
    try:
        prompt_text = read_text(PROMPT)
        request_text = read_text(REQUEST_TEMPLATE)
        require_terms(prompt_text, REQUIRED_PROMPT_TERMS, "cross-critique reviewer prompt")
        require_terms(request_text, REQUIRED_REQUEST_TERMS, "cross-critique request template")

        schema = load_json(REVIEW_SCHEMA)
        review = load_json(REVIEW_EXAMPLE)
        assert_schema_valid(review, schema, "cross-critique review example")
        semantic_validate_review(review)

        record_template = load_json(REVIEW_RECORD_TEMPLATE)
        assert_schema_valid(record_template, schema, "cross-review record template")
        if record_template["completion_allowed"] is not False:
            raise QualityGateError("cross-review record template must block completion until completed")
    except QualityGateError as exc:
        print(f"cross-critique stub validation failed: {exc}")
        return 1
    except Exception:
        traceback.print_exc()
        return 1

    print("Cross-critique stub validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
