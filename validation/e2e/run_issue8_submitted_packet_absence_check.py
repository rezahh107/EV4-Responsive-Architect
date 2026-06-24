#!/usr/bin/env python3
"""Validate that Issue #8 evidence-pending state is not a submitted packet.

This check is intentionally narrow and local. It does not call GitHub, scrape
attachments, create submitted evidence, or run the real pilot. It locks the
contract that the current Issue #8 checklist/prose state is only an evidence
intake placeholder until a machine-checkable real_issue_submission packet exists.
"""
from __future__ import annotations

import sys
import traceback
from typing import Any

ISSUE_8_EVIDENCE_PENDING_SNAPSHOT: dict[str, Any] = {
    "issue_number": 8,
    "state": "open",
    "labels": ["pilot", "evidence-intake", "evidence-pending"],
    "intake_packet_status": {
        "packet_status": "draft",
        "validation_result": "pending",
        "pilot_allowed_to_start": False,
    },
    "submitted_packet": None,
    "required_evidence_checklist_complete": False,
    "machine_checkable_packet_present": False,
    "source_scope": "issue_prose_and_checklist_only",
}


def assert_issue8_absence_snapshot_blocks_submission(snapshot: dict[str, Any]) -> None:
    labels = set(snapshot.get("labels", []))
    status = snapshot.get("intake_packet_status", {})

    if snapshot.get("issue_number") != 8:
        raise AssertionError("absence contract must target Issue #8")
    if snapshot.get("submitted_packet") is not None:
        raise AssertionError("Issue #8 absence snapshot must not contain a submitted packet")
    if snapshot.get("machine_checkable_packet_present") is not False:
        raise AssertionError("Issue #8 absence snapshot must record no machine-checkable packet")
    if snapshot.get("required_evidence_checklist_complete") is not False:
        raise AssertionError("Issue #8 checklist is not complete and must remain blocking")
    if "evidence-pending" not in labels:
        raise AssertionError("Issue #8 evidence-pending label must block submitted-packet interpretation")
    if status.get("packet_status") != "draft" or status.get("validation_result") != "pending":
        raise AssertionError("Issue #8 draft/pending status cannot be treated as submitted readiness")
    if status.get("pilot_allowed_to_start") is not False:
        raise AssertionError("Issue #8 absence snapshot must not allow pilot start")
    if snapshot.get("source_scope") != "issue_prose_and_checklist_only":
        raise AssertionError("Issue #8 prose/checklist alone must not become real_issue_submission")


def assert_text_only_issue_cannot_be_real_submission(snapshot: dict[str, Any]) -> None:
    attempted_packet = {
        "packet_origin": "real_issue_submission",
        "issue_reference": {"repository": "rezahh107/EV4-Responsive-Architect", "issue_number": 8},
        "source_scope": snapshot.get("source_scope"),
        "machine_checkable_packet_present": snapshot.get("machine_checkable_packet_present"),
        "intake_verdict": {
            "real_pilot_allowed_to_start": True,
            "allowed_scope": "real_shadow_mode_only",
        },
    }

    if attempted_packet["source_scope"] == "issue_prose_and_checklist_only":
        raise AssertionError("Issue #8 text/checklist alone cannot satisfy real_issue_submission")
    if attempted_packet["machine_checkable_packet_present"] is not True:
        raise AssertionError("real_issue_submission requires a machine-checkable packet")


def main() -> int:
    try:
        assert_issue8_absence_snapshot_blocks_submission(ISSUE_8_EVIDENCE_PENDING_SNAPSHOT)
        try:
            assert_text_only_issue_cannot_be_real_submission(ISSUE_8_EVIDENCE_PENDING_SNAPSHOT)
        except AssertionError as exc:
            if "text/checklist alone cannot satisfy real_issue_submission" not in str(exc):
                raise
        else:
            raise AssertionError("text-only Issue #8 state unexpectedly satisfied real_issue_submission")
    except AssertionError as exc:
        print(f"Issue #8 submitted-packet absence check failed: {exc}", file=sys.stderr)
        return 1
    except Exception:
        print("Issue #8 submitted-packet absence check crashed unexpectedly:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1

    print("Issue #8 submitted-packet absence check passed: evidence-pending issue text is not real submitted evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
