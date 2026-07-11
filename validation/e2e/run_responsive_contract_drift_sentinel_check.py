#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "planning/EV4_RESPONSIVE_CONTRACT_DRIFT_SENTINEL.json"
WORKFLOW = ROOT / ".github/workflows/validate.yml"
STATUS = ROOT / "STATUS.md"
COMMAND_INDEX = ROOT / "docs/17_VALIDATION_COMMAND_INDEX.md"
ACTIVE_INDEX = ROOT / "docs/20_ACTIVE_CONTRACT_SCHEMA_VALIDATOR_INDEX.md"
INVALID_FIXTURES = ROOT / "validation/fixtures/invalid"
FIXTURE_FILES = (
    INVALID_FIXTURES / "responsive_contract_drift_missing_owner_check.invalid.json",
    INVALID_FIXTURES / "responsive_contract_drift_commented_command.invalid.json",
)
SENTINEL_COMMAND = "python validation/e2e/run_responsive_contract_drift_sentinel_check.py"

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


def load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise AssertionError(f"JSON object required: {path.relative_to(ROOT)}")
    return data


def load_manifest() -> dict:
    data = load_json(MANIFEST)
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


def active_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]


def validate_documentation_parity() -> None:
    surfaces = {
        "STATUS.md": STATUS.read_text(encoding="utf-8"),
        "docs/17_VALIDATION_COMMAND_INDEX.md": COMMAND_INDEX.read_text(encoding="utf-8"),
        "docs/20_ACTIVE_CONTRACT_SCHEMA_VALIDATOR_INDEX.md": ACTIVE_INDEX.read_text(encoding="utf-8"),
    }
    for name, text in surfaces.items():
        if not any(SENTINEL_COMMAND in line for line in active_lines(text)):
            raise AssertionError(f"responsive contract drift sentinel missing from parity surface: {name}")


def validate_manifest(data: dict, workflow_text: str) -> None:
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

    active_workflow_lines = active_lines(workflow_text)
    required = data.get("required_validate_commands")
    if not isinstance(required, list) or not required:
        raise AssertionError("required_validate_commands must be a non-empty list")
    for command in required:
        if not isinstance(command, str) or not command:
            raise AssertionError("required Validate command must be a non-empty string")
        if not any(command in line for line in active_workflow_lines):
            raise AssertionError(f"required Validate command missing or commented out: {command}")

    if not any(SENTINEL_COMMAND in line for line in active_workflow_lines):
        raise AssertionError("responsive contract drift sentinel missing from primary Validate workflow")


def apply_fixture(base_manifest: dict, workflow_text: str, fixture: dict) -> tuple[dict, str]:
    mutated_manifest = copy.deepcopy(base_manifest)
    mutated_workflow = workflow_text
    mutation = fixture.get("mutation")

    if mutation == "remove_owner_check":
        surface = fixture.get("surface")
        for item in mutated_manifest["owned_surfaces"]:
            if item.get("surface") == surface:
                item.pop("owner_check", None)
                break
        else:
            raise AssertionError(f"fixture surface not found: {surface}")
    elif mutation == "comment_required_command":
        command = fixture.get("command")
        if not isinstance(command, str) or command not in mutated_workflow:
            raise AssertionError(f"fixture command not found: {command}")
        lines = mutated_workflow.splitlines()
        for index, line in enumerate(lines):
            if command in line:
                indent = len(line) - len(line.lstrip())
                lines[index] = line[:indent] + "# " + line[indent:]
                break
        else:
            raise AssertionError(f"fixture command not found: {command}")
        mutated_workflow = "\n".join(lines)
    else:
        raise AssertionError(f"unsupported drift fixture mutation: {mutation}")

    return mutated_manifest, mutated_workflow


def validate_negative_fixtures(base_manifest: dict, workflow_text: str) -> None:
    for path in FIXTURE_FILES:
        fixture = load_json(path)
        expected = fixture.get("expected_diagnostic")
        if not isinstance(expected, str) or not expected:
            raise AssertionError(f"fixture requires expected_diagnostic: {path.relative_to(ROOT)}")
        mutated_manifest, mutated_workflow = apply_fixture(base_manifest, workflow_text, fixture)
        try:
            validate_manifest(mutated_manifest, mutated_workflow)
        except AssertionError as exc:
            if expected not in str(exc):
                raise AssertionError(
                    f"{path.relative_to(ROOT)} failed for wrong reason; expected={expected}; actual={exc}"
                ) from exc
        else:
            raise AssertionError(f"negative drift fixture unexpectedly passed: {path.relative_to(ROOT)}")


def validate() -> None:
    data = load_manifest()
    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    validate_manifest(data, workflow_text)
    validate_documentation_parity()
    validate_negative_fixtures(data, workflow_text)


def main() -> int:
    validate()
    print("responsive contract drift sentinel passed: inventory, parity, and negative fixtures are enforced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
