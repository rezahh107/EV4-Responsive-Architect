#!/usr/bin/env python3
"""Validate viewport inheritance/reset decision fixtures for WP-RESP-007."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALID_FIXTURE = ROOT / "validation" / "fixtures" / "valid" / "viewport_inheritance_reset_matrix.valid.json"
INVALID_DIR = ROOT / "validation" / "fixtures" / "invalid"
INVALID_FIXTURES = {
    "viewport_inheritance_reset_narrower_source.invalid.json": "must inherit only from a wider viewport",
    "viewport_inheritance_reset_missing_source.invalid.json": "requires a non-empty source_ref",
    "viewport_inheritance_reset_boundary_upgrade.invalid.json": "upgraded forbidden boundary claims",
    "viewport_inheritance_reset_unknown_source.invalid.json": "must not inherit through an unknown source viewport",
}
CANONICAL_VIEWPORTS = {"desktop", "tablet", "mobile"}
CANONICAL_DECISIONS = {"explicit", "inherited", "reset", "inactive", "unknown"}
VIEWPORT_RANK = {"desktop": 0, "tablet": 1, "mobile": 2}
REQUIRED_FALSE_BOUNDARIES = {
    "submitted_evidence_created",
    "issue_8_mutated",
    "pilot_executed_or_authorized",
    "production_ready",
    "release_ready",
    "live_render_validated",
    "export_json_validated",
    "accessibility_passed",
    "pixel_perfect",
    "responsive_correctness_validated",
    "ci_success_treated_as_responsive_correctness_evidence",
}


def _load(path: Path) -> dict[str, object]:
    if not path.exists():
        raise AssertionError(f"missing required fixture: {path.relative_to(ROOT)}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise AssertionError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return data


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_boundaries(data: dict[str, object], source: str) -> None:
    boundaries = data.get("boundary_assertions")
    if not isinstance(boundaries, dict):
        raise AssertionError(f"{source} missing boundary_assertions object")
    upgraded = sorted(name for name in REQUIRED_FALSE_BOUNDARIES if boundaries.get(name) is not False)
    if upgraded:
        raise AssertionError(f"{source} upgraded forbidden boundary claims: {', '.join(upgraded)}")


def _decision_key(decision: dict[str, object]) -> tuple[object, object, object]:
    return decision.get("node_ref"), decision.get("property_path"), decision.get("viewport")


def _validate_decision(
    decision: object,
    source: str,
    index: int,
    decisions_by_key: dict[tuple[object, object, object], dict[str, object]],
) -> None:
    label = f"{source} viewport_decisions[{index}]"
    if not isinstance(decision, dict):
        raise AssertionError(f"{label} must be an object")

    node_ref = decision.get("node_ref")
    viewport = decision.get("viewport")
    property_path = decision.get("property_path")
    decision_state = decision.get("decision")
    source_viewport = decision.get("source_viewport")
    source_ref = decision.get("source_ref")
    reason = decision.get("reason")
    conflicts = decision.get("conflicts")

    if not _non_empty_string(node_ref):
        raise AssertionError(f"{label} requires a non-empty node_ref")
    if viewport not in CANONICAL_VIEWPORTS:
        raise AssertionError(f"{label} uses a non-canonical viewport")
    if not _non_empty_string(property_path):
        raise AssertionError(f"{label} requires a non-empty property_path")
    if decision_state not in CANONICAL_DECISIONS:
        raise AssertionError(f"{label} uses a non-canonical decision")
    if not _non_empty_string(reason):
        raise AssertionError(f"{label} requires a non-empty reason")
    if not isinstance(conflicts, list) or any(not _non_empty_string(item) for item in conflicts):
        raise AssertionError(f"{label} conflicts must be a list of non-empty strings")

    if decision_state in {"explicit", "reset", "inactive"} and not _non_empty_string(source_ref):
        raise AssertionError(f"{label} {decision_state} requires a non-empty source_ref")
    if decision_state == "explicit" and source_viewport != viewport:
        raise AssertionError(f"{label} explicit decision requires source_viewport to match viewport")
    if decision_state in {"reset", "inactive"} and source_viewport is not None:
        raise AssertionError(f"{label} {decision_state} decision must not specify a source_viewport")

    if decision_state == "inherited":
        if source_viewport not in CANONICAL_VIEWPORTS:
            raise AssertionError(f"{label} inherited decision requires a canonical source_viewport")
        if VIEWPORT_RANK[source_viewport] >= VIEWPORT_RANK[viewport]:
            raise AssertionError(f"{label} must inherit only from a wider viewport")
        if not _non_empty_string(source_ref):
            raise AssertionError(f"{label} inherited decision requires a non-empty source_ref")
        source_decision = decisions_by_key.get((node_ref, property_path, source_viewport))
        if source_decision is not None and source_decision.get("decision") == "unknown":
            raise AssertionError(f"{label} must not inherit through an unknown source viewport")

    if decision_state == "unknown":
        if source_viewport is not None or source_ref is not None:
            raise AssertionError(f"{label} unknown decision must not claim an authoritative source")
        if not conflicts:
            raise AssertionError(f"{label} unknown decision must record at least one unresolved conflict")


def _validate_payload(data: dict[str, object], source: str) -> None:
    decisions = data.get("viewport_decisions")
    if not isinstance(decisions, list) or not decisions:
        raise AssertionError(f"{source} must contain a non-empty viewport_decisions list")

    decisions_by_key: dict[tuple[object, object, object], dict[str, object]] = {}
    for index, decision in enumerate(decisions):
        if not isinstance(decision, dict):
            raise AssertionError(f"{source} viewport_decisions[{index}] must be an object")
        key = _decision_key(decision)
        if key in decisions_by_key:
            raise AssertionError(f"{source} contains duplicate viewport decision key: {key}")
        decisions_by_key[key] = decision

    for index, decision in enumerate(decisions):
        _validate_decision(decision, source, index, decisions_by_key)
    _validate_boundaries(data, source)


def main() -> int:
    _validate_payload(_load(VALID_FIXTURE), str(VALID_FIXTURE.relative_to(ROOT)))

    observed = {path.name for path in INVALID_DIR.glob("viewport_inheritance_reset_*.invalid.json")}
    registered = set(INVALID_FIXTURES)
    missing = registered - observed
    if missing:
        raise AssertionError("missing required viewport matrix invalid fixtures: " + ", ".join(sorted(missing)))
    extra = observed - registered
    if extra:
        raise AssertionError("unregistered viewport matrix invalid fixtures: " + ", ".join(sorted(extra)))

    for name, marker in INVALID_FIXTURES.items():
        path = INVALID_DIR / name
        try:
            _validate_payload(_load(path), str(path.relative_to(ROOT)))
        except AssertionError as error:
            if marker not in str(error):
                raise AssertionError(f"{path.relative_to(ROOT)} failed for unexpected reason: {error}") from error
        else:
            raise AssertionError(f"{path.relative_to(ROOT)} unexpectedly passed viewport matrix validation")

    print("Viewport inheritance/reset decision matrix fixtures: PASS")
    print("Boundary: repository validation only; not responsive correctness evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
