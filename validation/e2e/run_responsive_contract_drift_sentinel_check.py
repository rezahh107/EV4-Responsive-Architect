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
        path = item.get("path")
        owner_check = item.get("owner_check")
        if not isinstance(path, str) or not path:
            raise AssertionError("every owned surface requires a path")
        if path in seen_paths:
            raise AssertionError(f"duplicate owned surface path: {path}")
        seen_paths.add(path)
        if not (ROOT / path).is_file():
            raise AssertionError(f"owned surface path missing: {path}")
        if not isinstance(owner_check, str) or not (ROOT / owner_check).is_file():
            raise AssertionError(f"owner check missing for {path}: {owner_check}")

    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    required = data.get("required_validate_commands")
    if not isinstance(required, list) or not required:
        raise AssertionError("required_validate_commands must be a non-empty list")
    for command in required:
        if not isinstance(command, str) or command not in workflow_text:
            raise AssertionError(f"required Validate command missing: {command}")


def main() -> int:
    validate()
    print("responsive contract drift sentinel inventory passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
