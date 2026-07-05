#!/usr/bin/env python3
"""Exercise evidence-intake submitted-mode validation through the full packet path.

This is a deterministic guard: it uses synthetic probes only and does not create,
submit, validate, or upgrade real Issue #8 evidence.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import traceback
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_INTAKE_CHECK = ROOT / "validation" / "e2e" / "run_evidence_intake_check.py"
ISSUE_8_NUMBER = 8


def _load_evidence_module() -> Any:
    spec = importlib.util.spec_from_file_location("ev4_evidence_intake_check", EVIDENCE_INTAKE_CHECK)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {EVIDENCE_INTAKE_CHECK}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECK = _load_evidence_module()


def _submitted_probe() -> dict[str, Any]:
    packet = CHECK.load_json(CHECK.DEFAULT_PACKET)
    packet["packet_id"] = "issue-8-submitted-mode-path-probe"
    packet["packet_status"] = "submitted"
    packet["packet_origin"] = "real_issue_submission"
    packet["issue_reference"] = {
        "issue_number": ISSUE_8_NUMBER,
        "issue_url_or_ref": "https://github.com/rezahh107/EV4-Responsive-Architect/issues/8",
        "evidence_submission_status": "submitted",
    }
    packet["main_ev4_handoff"]["source_ref"] = "issue-8/main-ev4-handoff.md"
    packet["main_ev4_handoff"]["payload_identity_hash"] = "sha256-issue-8-submitted-mode-probe"
    packet["evidence_items"][0]["file_name"] = "issue-8/desktop-1440.png"
    packet["evidence_items"][1]["file_name"] = "issue-8/tablet-768.png"
    packet["evidence_items"][2]["file_name"] = "issue-8/mobile-390.png"
    packet["intake_verdict"] = {
        "status": "allowed",
        "missing_required_items": [],
        "blocker_conflicts": [],
        "evidence_quality_summary": "Synthetic submitted-mode path probe only; not submitted evidence.",
        "pilot_allowed_to_start": True,
        "sample_dry_run_allowed": False,
        "real_pilot_allowed_to_start": True,
        "allowed_scope": CHECK.REAL_SHADOW_SCOPE,
    }
    return packet


def _write_probe(packet: dict[str, Any]) -> Path:
    issue_parent = ROOT / "issue-8"
    issue_parent.mkdir(exist_ok=True)
    temp_dir = tempfile.TemporaryDirectory(prefix="submitted-mode-probe-", dir=issue_parent)
    path = Path(temp_dir.name) / "evidence_intake_packet.submitted.json"
    path.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    # Keep the TemporaryDirectory alive for the caller by attaching it to the Path object holder.
    path._ev4_temp_dir = temp_dir  # type: ignore[attr-defined]
    return path


def _validate(packet: dict[str, Any]) -> None:
    path = _write_probe(packet)
    try:
        CHECK.validate_packet(path, run_full_schema_validator=False, submitted_mode=True)
    finally:
        temp_dir = getattr(path, "_ev4_temp_dir", None)
        if temp_dir is not None:
            temp_dir.cleanup()


def _assert_rejected(label: str, mutate: Callable[[dict[str, Any]], None], expected_fragment: str) -> None:
    packet = _submitted_probe()
    mutate(packet)
    try:
        _validate(packet)
    except AssertionError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"{label} rejection must cite {expected_fragment!r}, got: {exc}") from exc
    else:
        raise AssertionError(f"{label} must be rejected by submitted-mode validation")


def main() -> int:
    try:
        _validate(_submitted_probe())
        _assert_rejected("draft packet status", lambda p: p.update({"packet_status": "draft"}), "packet_status=submitted or validated")
        _assert_rejected(
            "draft issue evidence status",
            lambda p: p["issue_reference"].update({"evidence_submission_status": "draft"}),
            "issue_reference.evidence_submission_status=submitted or validated",
        )
        _assert_rejected(
            "wrong issue number",
            lambda p: p["issue_reference"].update({"issue_number": 9, "issue_url_or_ref": "https://github.com/rezahh107/EV4-Responsive-Architect/issues/9"}),
            "Issue #8",
        )
        _assert_rejected(
            "generated artifact source",
            lambda p: p["main_ev4_handoff"].update({"source_ref": "examples/smart-home-connector/readiness/PILOT_READINESS_REPORT.generated.json"}),
            "generated/report/bookkeeping artifact path",
        )
        _assert_rejected(
            "sample marker",
            lambda p: p.update({"packet_id": "SAMPLE-issue-8-submitted-mode-path-probe"}),
            "sample markers",
        )
    except AssertionError as exc:
        print(f"Evidence intake submitted-mode path check failed: {exc}")
        return 1
    except Exception:
        print("Evidence intake submitted-mode path check crashed unexpectedly:")
        traceback.print_exc()
        return 1
    print("Evidence intake submitted-mode path check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
