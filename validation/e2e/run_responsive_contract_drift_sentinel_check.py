#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "planning/EV4_RESPONSIVE_CONTRACT_DRIFT_SENTINEL.json"
WORKFLOW = ROOT / ".github/workflows/validate.yml"

FALSE_BOUNDARIES = {
    "ci_success_is_responsive_correctness_evidence",
    "inventory_completion_is_responsive_correctness_evidence",
    "production_ready",
    "release_ready",
    "live_render_validated",
    "export_json_validated",
    "accessibility_passed",
    "pixel_perfect",
    "responsive_correctness_validated",
}


def load_manifest() -> dict:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data.get("schema") != "ev4-responsive-contract-drift-sentinel@1.0.0":
        raise AssertionError("unexpected drift sentinel schema")
    if data.get("work_package_id") != "WP-RESP-006" or data.get("slice_id") != "WP-RESP-006/PR-A":
        raise AssertionError("drift sentinel must remain scoped to WP-RESP-006/PR-A")
    return data


def resolve_repo_file(value: object, field_name: str) -> Path:
    if not isinstance(value, str) or not value:
        raise AssertionError(f"every owned surface requires a {field_name}")

    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise AssertionError(f"absolute or traversing {field_name} rejected: {value}")

    resolved = (ROOT / candidate).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise AssertionError(f"{field_name} escapes repository root: {value}") from exc

    if not resolved.is_file():
        raise AssertionError(f"{field_name} file missing: {value}")
    return resolved


def validate() -> None:
    data = load_manifest()
    boundaries = data.get("domain_evidence_boundary", {})
    for key in sorted(FALSE_BOUNDARIES):
        if boundaries.get(key) is not False:
            raise AssertionError(f"domain evidence boundary must remain false: {key}")

    surfaces = data.get("owned_surfaces")
    if not isinstance(surfaces, list) or not surfaces:
        raise AssertionError("owned_surfaces must be a non-empty list")

    seen_paths: set[str] = set()
    for item in surfaces:
        if not isinstance(item, dict):
            raise AssertionError("every owned surface must be an object")

        path = item.get("path")
        owner_check = item.get("owner_check")
        if not isinstance(path, str) or not path:
            raise AssertionError("every owned surface requires a path")
        if path in seen_paths:
            raise AssertionError(f"duplicate owned surface path: {path}")
        seen_paths.add(path)

        resolve_repo_file(path, "path")
        resolve_repo_file(owner_check, "owner_check")

    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    active_workflow_lines = [
        line for line in workflow_text.splitlines() if line.strip() and not line.lstrip().startswith("#")
    ]
    required = data.get("required_validate_commands")
    if not isinstance(required, list) or not required:
        raise AssertionError("required_validate_commands must be a non-empty list")
    for command in required:
        if not isinstance(command, str) or not command:
            raise AssertionError("required Validate command must be a non-empty string")
        if not any(command in line for line in active_workflow_lines):
            raise AssertionError(f"required Validate command missing or commented out: {command}")


def main() -> int:
    validate()
    print("responsive contract drift sentinel inventory passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
