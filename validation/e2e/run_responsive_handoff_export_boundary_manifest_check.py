#!/usr/bin/env python3
"""Validate repository-only responsive handoff export boundary manifests."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALID = ROOT / "validation/fixtures/valid/responsive_handoff_export_boundary_manifest.valid.json"
INVALID_DIR = ROOT / "validation/fixtures/invalid"
INVALID_FIXTURES = {
    "responsive_handoff_export_boundary_manifest_missing_source.invalid.json": "requires non-empty source lineage",
    "responsive_handoff_export_boundary_manifest_missing_artifact.invalid.json": "missing required artifact classes",
    "responsive_handoff_export_boundary_manifest_boundary_upgrade.invalid.json": "upgraded forbidden boundary claims",
}
REQUIRED_ARTIFACTS = {
    "responsive_tree_output",
    "breakpoint_overrides",
    "viewport_display_contract",
    "content_gate",
    "builder_handoff",
    "validation_plan",
    "final_review",
}
REQUIRED_FALSE = {
    "submitted_evidence_created",
    "issue_8_mutated",
    "pilot_executed_or_authorized",
    "production_ready",
    "release_ready",
    "live_render_validated",
    "export_validated",
    "accessibility_passed",
    "pixel_perfect",
    "responsive_correctness_validated",
    "ci_success_treated_as_domain_evidence",
}


def _load(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise AssertionError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return data


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate(data: dict[str, object], source: str) -> None:
    if data.get("schema") != "ev4-responsive-handoff-export-boundary-manifest@0.1.0":
        raise AssertionError(f"{source} uses an unexpected schema")
    if data.get("status") != "eligible_for_repository_validation":
        raise AssertionError(f"{source} valid fixture must be repository-validation eligible")
    if not _text(data.get("source_handoff_ref")) or not _text(data.get("source_packet_ref")):
        raise AssertionError(f"{source} requires non-empty source lineage")
    for key in ("selected_route_ref", "relationship_classification_ref"):
        if not _text(data.get(key)):
            raise AssertionError(f"{source} requires non-empty {key}")
    refs = data.get("contract_refs")
    if not isinstance(refs, dict) or not all(_text(refs.get(k)) for k in ("responsive_handoff", "viewport_display")):
        raise AssertionError(f"{source} requires canonical contract references")
    artifacts = data.get("expected_artifact_classes")
    if not isinstance(artifacts, list) or any(not _text(item) for item in artifacts):
        raise AssertionError(f"{source} expected_artifact_classes must be a list of non-empty strings")
    missing = REQUIRED_ARTIFACTS - set(artifacts)
    if missing:
        raise AssertionError(f"{source} missing required artifact classes: {', '.join(sorted(missing))}")
    plans = data.get("validation_plan_refs")
    if not isinstance(plans, list) or not plans or any(not _text(item) for item in plans):
        raise AssertionError(f"{source} requires validation_plan_refs")
    for key in ("unresolved_unknowns", "blocking_conflicts"):
        value = data.get(key)
        if not isinstance(value, list) or any(not _text(item) for item in value):
            raise AssertionError(f"{source} {key} must be a list of non-empty strings")
    if data.get("unresolved_unknowns") or data.get("blocking_conflicts"):
        raise AssertionError(f"{source} cannot be eligible while unknowns or conflicts remain")
    boundaries = data.get("boundary_assertions")
    if not isinstance(boundaries, dict):
        raise AssertionError(f"{source} missing boundary_assertions")
    upgraded = sorted(name for name in REQUIRED_FALSE if boundaries.get(name) is not False)
    if upgraded:
        raise AssertionError(f"{source} upgraded forbidden boundary claims: {', '.join(upgraded)}")


def main() -> int:
    _validate(_load(VALID), str(VALID.relative_to(ROOT)))
    observed = {p.name for p in INVALID_DIR.glob("responsive_handoff_export_boundary_manifest_*.invalid.json")}
    if observed != set(INVALID_FIXTURES):
        raise AssertionError("export manifest invalid fixture registry drift")
    for name, marker in INVALID_FIXTURES.items():
        path = INVALID_DIR / name
        try:
            _validate(_load(path), str(path.relative_to(ROOT)))
        except AssertionError as error:
            if marker not in str(error):
                raise AssertionError(f"{path.relative_to(ROOT)} failed unexpectedly: {error}") from error
        else:
            raise AssertionError(f"{path.relative_to(ROOT)} unexpectedly passed")
    print("Responsive handoff export boundary manifest fixtures: PASS")
    print("Boundary: repository validation only; not live export or responsive correctness evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
