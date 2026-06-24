#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "planning" / "EV4_ISSUE8_STATE.snapshot.json"

REQUIRED_ABSENT_PACKET_LABELS = {"evidence-intake", "evidence-pending"}
FORBIDDEN_ABSENT_PACKET_LABELS = {
    "evidence-accepted",
    "evidence-complete",
    "submitted-packet-present",
    "readiness-passed",
    "pilot-ready",
    "pilot-authorized",
    "real-pilot-authorized",
    "production-ready",
    "release-ready",
    "export-validated",
    "live-render-validated",
    "accessibility-passed",
}
FORBIDDEN_PRESENT_PACKET_LABELS = {"evidence-pending"}


def load_snapshot() -> dict[str, Any]:
    with SNAPSHOT.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError("Issue #8 snapshot must be a JSON object")
    return payload


def fail(message: str) -> None:
    raise AssertionError(message)


def assert_issue8_label_state(snapshot: dict[str, Any]) -> None:
    if snapshot.get("schema") != "ev4-responsive-issue8-state-snapshot@1.0.0":
        fail("Issue #8 snapshot schema must remain ev4-responsive-issue8-state-snapshot@1.0.0")
    if snapshot.get("issue_number") != 8:
        fail("Issue #8 snapshot must reference issue_number=8")
    if snapshot.get("issue_state") != "open":
        fail("Issue #8 must remain open while evidence is pending")

    labels = set(snapshot.get("labels", []))
    if len(labels) != len(snapshot.get("labels", [])):
        fail("Issue #8 snapshot labels must be unique")

    submitted_present = snapshot.get("real_submitted_packet_present") is True
    packet_path = ROOT / snapshot.get("submitted_packet_path", "")

    if not submitted_present:
        missing_required = REQUIRED_ABSENT_PACKET_LABELS - labels
        if missing_required:
            fail(f"Issue #8 without submitted packet must keep labels: {sorted(missing_required)}")
        contradictory = FORBIDDEN_ABSENT_PACKET_LABELS & labels
        if contradictory:
            fail(f"Issue #8 labels contradict submitted-packet absence: {sorted(contradictory)}")
        if snapshot.get("packet_status") != "draft":
            fail("Issue #8 without submitted packet must keep packet_status=draft")
        if snapshot.get("evidence_submission_status") != "draft":
            fail("Issue #8 without submitted packet must keep evidence_submission_status=draft")
        if snapshot.get("pilot_allowed_to_start") is not False:
            fail("Issue #8 without submitted packet must not allow pilot start")
        if snapshot.get("real_pilot_allowed_to_start") is not False:
            fail("Issue #8 without submitted packet must not allow real pilot start")
        if snapshot.get("allowed_scope") != "not_allowed":
            fail("Issue #8 without submitted packet must keep allowed_scope=not_allowed")
        if packet_path.exists():
            fail("real_submitted_packet_present=false conflicts with an existing submitted packet artifact")
    else:
        contradictory = FORBIDDEN_PRESENT_PACKET_LABELS & labels
        if contradictory:
            fail(f"Issue #8 submitted-packet state cannot keep pending labels: {sorted(contradictory)}")
        if not packet_path.exists():
            fail("real_submitted_packet_present=true requires the submitted packet artifact to exist")

    if snapshot.get("packet_origin") != "real_issue_submission":
        fail("Issue #8 snapshot must preserve packet_origin=real_issue_submission")
    if "machine-checkable submitted evidence packet" not in snapshot.get("boundary", ""):
        fail("Issue #8 snapshot boundary must state labels/prose are not submitted evidence")


def assert_negative_paths(snapshot: dict[str, Any]) -> None:
    bad_label = copy.deepcopy(snapshot)
    bad_label["labels"] = sorted(set(bad_label.get("labels", [])) | {"pilot-ready"})
    try:
        assert_issue8_label_state(bad_label)
    except AssertionError:
        pass
    else:
        fail("negative path failed: absent submitted packet with pilot-ready label was accepted")

    missing_pending = copy.deepcopy(snapshot)
    missing_pending["labels"] = [label for label in missing_pending.get("labels", []) if label != "evidence-pending"]
    try:
        assert_issue8_label_state(missing_pending)
    except AssertionError:
        pass
    else:
        fail("negative path failed: absent submitted packet without evidence-pending label was accepted")

    bad_scope = copy.deepcopy(snapshot)
    bad_scope["allowed_scope"] = "real_shadow_mode_only"
    try:
        assert_issue8_label_state(bad_scope)
    except AssertionError:
        pass
    else:
        fail("negative path failed: absent submitted packet with real_shadow_mode_only was accepted")


def main() -> int:
    try:
        snapshot = load_snapshot()
        assert_issue8_label_state(snapshot)
        assert_negative_paths(snapshot)
    except AssertionError as exc:
        print(f"Issue #8 label-state check failed: {exc}")
        return 1
    print("Issue #8 label-state check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
