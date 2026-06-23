#!/usr/bin/env python3
"""Dry-run the smart-home connector pilot execution boundary.

This check validates that a submitted-like intake packet can pass intake,
produce a readiness report, verify the pilot manifest, and persist a run record.
It does not execute Elementor, inspect real screenshots, validate export JSON, run
Playwright, or claim production readiness.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from validation.e2e.run_pilot_readiness_check import run_readiness_for_packet  # noqa: E402

DEFAULT_PACKET = ROOT / "examples" / "smart-home-connector" / "intake" / "EVIDENCE_INTAKE_PACKET.sample-submitted.json"
DEFAULT_READINESS_OUT = ROOT / "examples" / "smart-home-connector" / "readiness" / "PILOT_READINESS_REPORT.dry-run.generated.json"
DEFAULT_RUN_RECORD_OUT = ROOT / "examples" / "smart-home-connector" / "runs" / "PILOT_RUN_RECORD.dry-run.generated.json"
RUN_RECORD_SCHEMA = ROOT / "schemas" / "ev4-responsive-pilot-run-record.schema.json"
PILOT_MANIFEST_CHECK = ROOT / "validation" / "e2e" / "run_pilot_manifest_check.py"

BLOCKED_ACTIONS = [
    "do_not_claim_production_ready",
    "do_not_claim_live_render_validated",
    "do_not_claim_export_json_validated",
    "do_not_claim_accessibility_passed",
    "do_not_claim_playwright_visual_regression_validated",
    "do_not_replace_real_evidence_with_sample_packet",
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    data.pop("$schema_file", None)
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_manifest_check() -> None:
    result = subprocess.run(
        [sys.executable, str(PILOT_MANIFEST_CHECK)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            "pilot manifest check failed\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )


def validate_run_record_schema(record: dict[str, Any]) -> None:
    try:
        import jsonschema
    except ImportError as exc:
        raise AssertionError("jsonschema package is required") from exc
    schema = load_json(RUN_RECORD_SCHEMA)
    jsonschema.Draft202012Validator(schema).validate(record)


def build_run_record(
    readiness: dict[str, Any],
    *,
    dry_run_only: bool,
    readiness_out: Path,
    run_record_out: Path,
) -> dict[str, Any]:
    if readiness["readiness_status"].startswith("blocked"):
        raise AssertionError("dry-run requires a non-blocked readiness report")

    auth = readiness["pilot_start_authorization"]
    if auth["authorized"] is not True:
        raise AssertionError("readiness authorization must be true for dry-run record")

    run_mode = "sample_submitted_packet_dry_run" if dry_run_only else "submitted_packet_shadow_mode"
    next_action = "collect_real_evidence" if dry_run_only else "start_shadow_mode_pilot_with_current_packet"

    return {
        "schema": "ev4-responsive-pilot-run-record@1.0.0",
        "run_id": f"{readiness['source_packet_id']}-DRY-RUN",
        "run_mode": run_mode,
        "section_id": readiness["section_id"],
        "source_packet_id": readiness["source_packet_id"],
        "source_readiness_id": readiness["readiness_id"],
        "readiness_status": readiness["readiness_status"],
        "authorization_scope": auth["authorization_scope"],
        "dry_run_only": dry_run_only,
        "stage_sequence_verified": {
            "pilot_manifest_checked": True,
            "required_sequence_complete": True,
            "execution_templates_present": True,
        },
        "generated_artifacts": [
            {
                "artifact_path": str(readiness_out.relative_to(ROOT)),
                "artifact_type": "readiness_report",
                "status": "generated",
            },
            {
                "artifact_path": str(run_record_out.relative_to(ROOT)),
                "artifact_type": "run_record",
                "status": "generated",
            },
            {
                "artifact_path": "examples/smart-home-connector/PILOT_MANIFEST.json",
                "artifact_type": "template_reference",
                "status": "referenced",
            },
        ],
        "carry_forward_flags": auth["required_carry_forward_flags"],
        "blocked_actions": BLOCKED_ACTIONS,
        "forbidden_claims": auth["forbidden_claims"],
        "validation_boundary": readiness["validation_boundary"],
        "next_allowed_action": next_action,
    }


def run_dry_run(packet_path: Path, readiness_out: Path, run_record_out: Path, *, dry_run_only: bool) -> dict[str, Any]:
    run_manifest_check()
    readiness = run_readiness_for_packet(
        packet_path,
        out_path=readiness_out,
        allow_blocked=False,
        run_full_schema_validator=True,
    )
    record = build_run_record(
        readiness,
        dry_run_only=dry_run_only,
        readiness_out=readiness_out,
        run_record_out=run_record_out,
    )
    validate_run_record_schema(record)
    write_json(run_record_out, record)
    return record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dry-run smart-home pilot execution from a submitted evidence packet.")
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET, help="Submitted evidence intake packet JSON.")
    parser.add_argument("--readiness-out", type=Path, default=DEFAULT_READINESS_OUT, help="Generated readiness report path.")
    parser.add_argument("--run-record-out", type=Path, default=DEFAULT_RUN_RECORD_OUT, help="Generated pilot run record path.")
    parser.add_argument(
        "--submitted-shadow-mode",
        action="store_true",
        help="Mark run record as submitted shadow-mode instead of sample dry-run. Use only with real submitted evidence.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        packet_path = args.packet if args.packet.is_absolute() else ROOT / args.packet
        readiness_out = args.readiness_out if args.readiness_out.is_absolute() else ROOT / args.readiness_out
        run_record_out = args.run_record_out if args.run_record_out.is_absolute() else ROOT / args.run_record_out
        record = run_dry_run(
            packet_path,
            readiness_out,
            run_record_out,
            dry_run_only=not args.submitted_shadow_mode,
        )
    except AssertionError as exc:
        print(f"Pilot dry-run check failed: {exc}", file=sys.stderr)
        return 1
    except Exception:
        print("Pilot dry-run check crashed unexpectedly:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1

    print(f"Pilot dry-run check passed: {record['run_mode']} -> {record['next_allowed_action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
