#!/usr/bin/env python3
"""Audit evidence-intake fixture identity and attachment inventory invariants.

This gate is intentionally evidence-safe: it validates contract fixtures and
negative fixtures only. It does not fetch Issue #8, create submitted evidence,
or authorize a real pilot.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
VALID_PACKET = ROOT / "validation" / "fixtures" / "valid" / "evidence_intake_packet.valid.json"
INVALID_FIXTURES = [
    ROOT / "validation" / "fixtures" / "invalid" / "evidence_intake_missing_attachment.invalid.json",
    ROOT / "validation" / "fixtures" / "invalid" / "evidence_intake_duplicate_attachment.invalid.json",
    ROOT / "validation" / "fixtures" / "invalid" / "evidence_intake_real_generated_artifact.invalid.json",
]
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


def _load_intake_module() -> Any:
    module_path = ROOT / "validation" / "e2e" / "run_evidence_intake_check.py"
    spec = importlib.util.spec_from_file_location("ev4_intake_check", module_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    payload.pop("$schema_file", None)
    return payload


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
    if packet.get("evidence_complete_definition", {}).get("all_required_evidence_ids_present") is True and missing_viewports:
        raise AssertionError(f"complete evidence packet is missing attachment inventory for viewports: {missing_viewports}")

    if packet.get("packet_origin") == "real_issue_submission":
        issue_reference = packet.get("issue_reference")
        if not isinstance(issue_reference, dict) or issue_reference.get("issue_number") != 8:
            raise AssertionError("real_issue_submission fixture matrix is locked to Issue #8")
        for field, ref in _artifact_refs(packet):
            lowered = ref.lower()
            if any(marker in lowered for marker in GENERATED_OR_BOOKKEEPING_MARKERS):
                raise AssertionError(f"{field} must reference submitted evidence, not generated/report/bookkeeping artifact: {ref}")


def expect_invalid(path: Path, intake_module: Any) -> None:
    try:
        packet = intake_module.validate_packet(path, run_full_schema_validator=False)
        validate_fixture_matrix(packet)
    except AssertionError:
        return
    raise AssertionError(f"expected invalid fixture to fail matrix validation: {path}")


def main() -> int:
    intake_module = _load_intake_module()
    try:
        valid_packet = intake_module.validate_packet(VALID_PACKET, run_full_schema_validator=True)
        validate_fixture_matrix(valid_packet)
        for fixture in INVALID_FIXTURES:
            if not fixture.exists():
                raise AssertionError(f"missing invalid fixture: {fixture}")
            expect_invalid(fixture, intake_module)
    except AssertionError as exc:
        print(f"evidence intake fixture matrix check failed: {exc}", file=sys.stderr)
        return 1
    print("evidence intake fixture matrix check passed: identity and attachment invariants are covered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
