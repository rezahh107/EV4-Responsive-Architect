#!/usr/bin/env python3
"""Audit evidence-intake fixture identity and attachment inventory invariants.

This gate is intentionally evidence-safe: it validates contract fixtures and
negative fixtures only. It does not fetch Issue #8, create submitted evidence,
or authorize a real pilot.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
VALID_PACKET = ROOT / "validation" / "fixtures" / "valid" / "evidence_intake_packet.valid.json"
MATRIX_INVALID_FIXTURE_EXPECTATIONS = {
    ROOT / "validation" / "fixtures" / "invalid" / "evidence_intake_missing_attachment.invalid.json": "non-empty file_name",
    ROOT / "validation" / "fixtures" / "invalid" / "evidence_intake_duplicate_attachment.invalid.json": "must be unique",
    ROOT / "validation" / "fixtures" / "invalid" / "evidence_intake_real_generated_artifact.invalid.json": "generated/report/bookkeeping",
    ROOT / "validation" / "fixtures" / "invalid" / "evidence_intake_real_example_artifact.invalid.json": "submitted Issue #8 attachments",
    ROOT / "validation" / "fixtures" / "invalid" / "evidence_intake_real_wrong_issue_artifact.invalid.json": "Issue #8-scoped attachment",
}
REQUIRED_VIEWPORTS = {"desktop", "tablet", "mobile"}
SAMPLE_MARKERS = ("SAMPLE", "sample", ".sample", "placeholder")
GENERATED_OR_BOOKKEEPING_MARKERS = (
    "planning/",
    "readiness/",
    "reports/",
    "status.md",
    "ev4_run_ledger",
    "ev4_rolling_queue",
    "pilot_readiness_report",
)
EXAMPLE_OR_TEMPLATE_MARKERS = (
    "examples/",
    "/examples/",
    "template/",
    "/template/",
)
ISSUE8_ATTACHMENT_MARKERS = (
    "issues/8/",
    "/issues/8/",
    "issue-8",
    "issue_8",
)


def _load_intake_module() -> Any:
    module_path = ROOT / "validation" / "e2e" / "run_evidence_intake_check.py"
    spec = importlib.util.spec_from_file_location("ev4_intake_check", module_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _has_marker(value: Any, markers: tuple[str, ...]) -> bool:
    return isinstance(value, str) and any(marker in value for marker in markers)


def _artifact_refs(packet: dict[str, Any]) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    handoff = packet.get("main_ev4_handoff")
    if isinstance(handoff, dict) and isinstance(handoff.get("source_ref"), str):
        refs.append(("main_ev4_handoff.source_ref", handoff["source_ref"]))
    for index, item in enumerate(packet.get("evidence_items", [])):
        if not isinstance(item, dict):
            continue
        if isinstance(item.get("file_name"), str):
            refs.append((f"evidence_items[{index}].file_name", item["file_name"]))
    return refs


def validate_fixture_matrix(packet: dict[str, Any]) -> None:
    items = packet.get("evidence_items")
    if not isinstance(items, list):
        raise AssertionError("evidence_items must be an array")

    file_names: list[str] = []
    viewport_to_files: dict[str, list[str]] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise AssertionError(f"evidence_items[{index}] must be an object")
        evidence_id = item.get("evidence_id", f"index_{index}")
        file_name = item.get("file_name")
        if not isinstance(file_name, str) or not file_name.strip():
            raise AssertionError(f"{evidence_id} must carry a non-empty file_name attachment reference")
        if _has_marker(file_name, SAMPLE_MARKERS) and packet.get("packet_origin") == "real_issue_submission":
            raise AssertionError(f"real evidence item {evidence_id} must not reference sample or placeholder attachment names")
        file_names.append(file_name)
        viewport = item.get("viewport")
        if isinstance(viewport, str):
            viewport_to_files.setdefault(viewport, []).append(file_name)

    duplicates = sorted({name for name in file_names if file_names.count(name) > 1})
    if duplicates:
        raise AssertionError(f"evidence attachment file_name values must be unique: {duplicates}")

    missing_viewports = sorted(REQUIRED_VIEWPORTS - set(viewport_to_files))
    complete_definition = packet.get("evidence_complete_definition")
    if (
        isinstance(complete_definition, dict)
        and complete_definition.get("all_required_evidence_ids_present") is True
        and missing_viewports
    ):
        raise AssertionError(f"complete evidence packet is missing attachment inventory for viewports: {missing_viewports}")

    if packet.get("packet_origin") == "real_issue_submission":
        issue_reference = packet.get("issue_reference")
        if not isinstance(issue_reference, dict) or issue_reference.get("issue_number") != 8:
            raise AssertionError("real_issue_submission fixture matrix is locked to Issue #8")
        for field, ref in _artifact_refs(packet):
            lowered = ref.lower()
            if any(marker in lowered for marker in EXAMPLE_OR_TEMPLATE_MARKERS):
                raise AssertionError(
                    f"{field} must reference submitted Issue #8 attachments, not repository examples/templates: {ref}"
                )
            if any(marker in lowered for marker in GENERATED_OR_BOOKKEEPING_MARKERS):
                raise AssertionError(f"{field} must reference submitted evidence, not generated/report/bookkeeping artifact: {ref}")
            if not any(marker in lowered for marker in ISSUE8_ATTACHMENT_MARKERS):
                raise AssertionError(f"{field} must reference an Issue #8-scoped attachment: {ref}")


def expect_matrix_invalid(path: Path, intake_module: Any, expected_fragment: str) -> None:
    # Matrix-negative fixtures must prove the matrix rule directly. Do not call
    # the broader intake semantic validator first, because that can reject some
    # packets before this gate exercises its own invariant.
    packet = intake_module.load_json(path)
    try:
        validate_fixture_matrix(packet)
    except AssertionError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(
                f"expected {path.name} to fail a matrix rule containing {expected_fragment!r}, got: {exc}"
            ) from exc
        return
    raise AssertionError(f"expected invalid fixture to fail matrix validation: {path}")


def main() -> int:
    intake_module = _load_intake_module()
    try:
        # The full schema suite owns generic valid/invalid fixture validation.
        # This gate owns matrix-specific semantic fixtures, so it avoids letting
        # the global schema runner decide negative fixture outcomes for this test.
        valid_packet = intake_module.validate_packet(VALID_PACKET, run_full_schema_validator=False)
        validate_fixture_matrix(valid_packet)
        for fixture, expected_fragment in MATRIX_INVALID_FIXTURE_EXPECTATIONS.items():
            if not fixture.exists():
                raise AssertionError(f"missing invalid fixture: {fixture}")
            expect_matrix_invalid(fixture, intake_module, expected_fragment)
    except AssertionError as exc:
        print(f"evidence intake fixture matrix check failed: {exc}", file=sys.stderr)
        return 1
    print("evidence intake fixture matrix check passed: identity and attachment invariants are covered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
