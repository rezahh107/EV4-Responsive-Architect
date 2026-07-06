#!/usr/bin/env python3
"""Ensure Issue #8 preflight remains blocked and non-executing.

This gate validates repository-controlled preflight/status text only. It does
not fetch or mutate Issue #8, create submitted evidence, generate readiness,
or authorize pilot execution.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT_GUIDE = ROOT / "docs" / "30_ISSUE_8_SUBMITTED_PACKET_PREFLIGHT_GUIDE_RTAQ_0022.md"
STATUS = ROOT / "STATUS.md"
COMMAND_INDEX = ROOT / "docs" / "17_VALIDATION_COMMAND_INDEX.md"
ISSUE_8_SUBMITTED_PACKET_PATH = "issue-8/evidence_intake_packet.submitted.json"
ISSUE_8_READINESS_REPORT_PATH = "issue-8/pilot_readiness_report.generated.json"
ISSUE_8_REFERENCE_PATTERNS = (
    r'issue_url_or_ref:\s*["\']?#8["\']?',
    r'issue_url_or_ref:\s*["\']?https://github\.com/rezahh107/EV4-Responsive-Architect/issues/8["\']?',
)
FORBIDDEN_ISSUE_REFERENCE_PATTERNS = (
    r'issue_url_or_ref:\s*["\']?#(?!8\b)\d+["\']?',
    r'issue_url_or_ref:\s*["\']?https://github\.com/rezahh107/EV4-Responsive-Architect/issues/(?!8\b)\d+["\']?',
)
FORBIDDEN_SUBMITTED_COMMAND_PATH_SNIPPETS = (
    "examples/smart-home-connector/intake/EVIDENCE_INTAKE_PACKET.submitted.json",
    "examples/smart-home-connector/intake/evidence_intake_packet.submitted.json",
)

REQUIRED_PREFLIGHT_SNIPPETS = (
    "issue_number: 8",
    "issue_url_or_ref: \"#8\"",
    "packet_status: draft",
    "validation_result: pending",
    "pilot_allowed_to_start: false",
    "real_pilot_allowed_to_start: false",
    "allowed_scope: not_allowed",
    "does not create or submit an evidence packet",
    "does not run the real pilot",
    f"python validation/e2e/run_evidence_intake_check.py --packet {ISSUE_8_SUBMITTED_PACKET_PATH} --submitted-mode",
    f"python validation/e2e/run_pilot_readiness_check.py --packet {ISSUE_8_SUBMITTED_PACKET_PATH} --out {ISSUE_8_READINESS_REPORT_PATH} --skip-schema-suite --submitted-mode",
    "Stop before readiness generation",
    "Stop before pilot execution",
    "Issue #8 has not received a real submitted packet",
    "Issue reference URL or shorthand does not point to #8",
)

REQUIRED_COMMAND_INDEX_SNIPPETS = (
    f"python validation/e2e/run_evidence_intake_check.py --packet {ISSUE_8_SUBMITTED_PACKET_PATH} --submitted-mode",
    "Use submitted mode only for an explicit non-default Issue #8 real-submission packet path.",
)

REQUIRED_STATUS_SNIPPETS = (
    "real_submitted_packet_present: false",
    "pilot_allowed_to_start: false",
    "readiness_claims_upgraded: false",
    "issue_8_status: draft_evidence_pending",
    "pilot_execution_scope: not_allowed",
    "ci_success_claim_boundary: repository checks only; not responsive correctness evidence",
)

FORBIDDEN_PREFLIGHT_SNIPPETS = (
    "pilot_allowed_to_start: true",
    "real_pilot_allowed_to_start: true",
    "allowed_scope: real_shadow_mode_only",
    "packet_status: submitted",
    "packet_status: validated",
    "production_ready: true",
    "release_ready: true",
)


def _read(path: Path) -> str:
    if not path.exists():
        raise AssertionError(f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def _contains_distinct_snippet(text: str, snippet: str) -> bool:
    pattern = r"(?<![A-Za-z0-9_])" + re.escape(snippet)
    return re.search(pattern, text) is not None


def _assert_all_present(text: str, snippets: tuple[str, ...], label: str) -> None:
    missing = [snippet for snippet in snippets if not _contains_distinct_snippet(text, snippet)]
    if missing:
        raise AssertionError(f"{label} is missing required blocked-boundary snippets: {missing}")


def _assert_all_absent(text: str, snippets: tuple[str, ...], label: str) -> None:
    present = [snippet for snippet in snippets if _contains_distinct_snippet(text, snippet)]
    if present:
        raise AssertionError(f"{label} contains forbidden readiness-upgrade snippets: {present}")


def _assert_issue_8_reference_locked(text: str) -> None:
    if not any(re.search(pattern, text) for pattern in ISSUE_8_REFERENCE_PATTERNS):
        raise AssertionError("Issue #8 preflight guide must include an explicit issue_url_or_ref for #8")
    conflicts = []
    for pattern in FORBIDDEN_ISSUE_REFERENCE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            conflicts.append(match.group(0))
    if conflicts:
        raise AssertionError(f"Issue #8 preflight guide contains conflicting issue_url_or_ref values: {conflicts}")


def _assert_submitted_command_paths_are_issue_8_only(preflight: str, command_index: str) -> None:
    combined = preflight + "\n" + command_index
    _assert_all_absent(
        combined,
        FORBIDDEN_SUBMITTED_COMMAND_PATH_SNIPPETS,
        "submitted-mode documentation",
    )


def main() -> int:
    try:
        preflight = _read(PREFLIGHT_GUIDE)
        status = _read(STATUS)
        command_index = _read(COMMAND_INDEX)
        _assert_all_present(preflight, REQUIRED_PREFLIGHT_SNIPPETS, "Issue #8 preflight guide")
        _assert_all_absent(preflight, FORBIDDEN_PREFLIGHT_SNIPPETS, "Issue #8 preflight guide")
        _assert_issue_8_reference_locked(preflight)
        _assert_submitted_command_paths_are_issue_8_only(preflight, command_index)
        _assert_all_present(command_index, REQUIRED_COMMAND_INDEX_SNIPPETS, "Validation command index")
        _assert_all_present(status, REQUIRED_STATUS_SNIPPETS, "STATUS.md evidence boundary")
    except (AssertionError, OSError) as exc:
        print(f"Issue #8 preflight boundary check failed: {exc}", file=sys.stderr)
        return 1
    print("Issue #8 preflight boundary check passed: draft evidence remains non-executing and pilot-blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
