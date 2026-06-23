#!/usr/bin/env python3
"""Dry-run smart-home connector pilot execution without claiming live validation."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from validation.e2e.run_evidence_intake_check import sample_indicators  # noqa: E402
from validation.e2e.run_pilot_readiness_check import run_readiness_for_packet  # noqa: E402

DEFAULT_PACKET = ROOT / "examples" / "smart-home-connector" / "intake" / "EVIDENCE_INTAKE_PACKET.sample-submitted.json"
DEFAULT_BLOCKED_PACKET = ROOT / "validation" / "fixtures" / "valid" / "evidence_intake_packet.blocked.valid.json"
DEFAULT_READINESS_OUT = ROOT / "examples" / "smart-home-connector" / "readiness" / "PILOT_READINESS_REPORT.dry-run.generated.json"
DEFAULT_RUN_RECORD_OUT = ROOT / "examples" / "smart-home-connector" / "runs" / "PILOT_RUN_RECORD.dry-run.generated.json"
RUN_RECORD_SCHEMA = ROOT / "schemas" / "ev4-responsive-pilot-run-record.schema.json"
PILOT_MANIFEST = ROOT / "examples" / "smart-home-connector" / "PILOT_MANIFEST.json"
PILOT_MANIFEST_CHECK = ROOT / "validation" / "e2e" / "run_pilot_manifest_check.py"
BLOCKED_ACTIONS = ["do_not_claim_production_ready", "do_not_claim_release_ready", "do_not_claim_live_render_validated", "do_not_claim_export_json_validated", "do_not_claim_accessibility_passed", "do_not_claim_playwright_visual_regression_validated", "do_not_replace_real_evidence_with_sample_packet"]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def git_ref_or_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False)
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else "git_ref_unavailable"


def run_manifest_check() -> dict[str, Any]:
    result = subprocess.run([sys.executable, str(PILOT_MANIFEST_CHECK)], cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise AssertionError(f"pilot manifest check failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return {"command": f"{sys.executable} {relative(PILOT_MANIFEST_CHECK)}", "exit_code": 0, "checked_manifest_path": relative(PILOT_MANIFEST), "checked_at_utc": utc_now(), "result": "pass"}


def ensure_generated_output_policy(*paths: Path) -> None:
    for path in paths:
        if path.suffix != ".json" or not path.name.endswith(".generated.json"):
            raise AssertionError(f"generated runtime output must end with .generated.json: {relative(path)}")
    result = subprocess.run(["git", "ls-files", "*.generated.json"], cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode == 0 and result.stdout.strip():
        raise AssertionError(f"generated runtime outputs must not be committed: {result.stdout.strip().splitlines()}")


def validate_run_record_schema(record: dict[str, Any]) -> None:
    try:
        import jsonschema
    except ImportError as exc:
        raise AssertionError("jsonschema package is required") from exc
    jsonschema.Draft202012Validator(load_json(RUN_RECORD_SCHEMA)).validate(record)


def assert_submitted_shadow_packet_is_real(packet: dict[str, Any], packet_path: Path) -> None:
    if packet.get("packet_origin") != "real_issue_submission":
        raise AssertionError("--submitted-shadow-mode requires packet_origin=real_issue_submission")
    if not isinstance(packet.get("issue_reference"), dict):
        raise AssertionError("--submitted-shadow-mode requires structured issue_reference")
    indicators = sample_indicators(packet, packet_path)
    if indicators:
        raise AssertionError(f"--submitted-shadow-mode refuses sample/placeholder indicators: {indicators}")
    verdict = packet.get("intake_verdict", {})
    if verdict.get("real_pilot_allowed_to_start") is not True:
        raise AssertionError("--submitted-shadow-mode requires real_pilot_allowed_to_start=true")
    if verdict.get("allowed_scope") != "real_shadow_mode_only":
        raise AssertionError("--submitted-shadow-mode requires allowed_scope=real_shadow_mode_only")


def command_string(args: argparse.Namespace | None) -> str:
    if args is None:
        return "python validation/e2e/run_pilot_dry_run_check.py"
    parts = ["python", "validation/e2e/run_pilot_dry_run_check.py"]
    if args.packet != DEFAULT_PACKET:
        parts += ["--packet", str(args.packet)]
    if args.readiness_out != DEFAULT_READINESS_OUT:
        parts += ["--readiness-out", str(args.readiness_out)]
    if args.run_record_out != DEFAULT_RUN_RECORD_OUT:
        parts += ["--run-record-out", str(args.run_record_out)]
    if args.submitted_shadow_mode:
        parts.append("--submitted-shadow-mode")
    if args.expect_blocked:
        parts.append("--expect-blocked")
    return " ".join(parts)


def build_run_record(readiness: dict[str, Any], packet: dict[str, Any], *, packet_path: Path, dry_run_only: bool, readiness_out: Path, run_record_out: Path, manifest_check: dict[str, Any], generator_command: str) -> dict[str, Any]:
    if readiness["readiness_status"].startswith("blocked"):
        raise AssertionError("dry-run requires a non-blocked readiness report")
    auth = readiness["pilot_start_authorization"]
    if auth["authorized"] is not True:
        raise AssertionError("readiness authorization must be true for run record")
    readiness_hash = sha256_file(readiness_out)
    packet_hash = sha256_file(packet_path)
    return {"schema": "ev4-responsive-pilot-run-record@1.0.0", "run_id": f"{readiness['source_packet_id']}-{'DRY-RUN' if dry_run_only else 'SHADOW-RUN'}", "run_mode": "sample_submitted_packet_dry_run" if dry_run_only else "submitted_packet_shadow_mode", "section_id": readiness["section_id"], "source_packet_id": readiness["source_packet_id"], "source_packet_origin": packet["packet_origin"], "issue_reference": packet["issue_reference"], "source_packet_sha256": packet_hash, "source_readiness_id": readiness["readiness_id"], "source_readiness_sha256": readiness_hash, "readiness_status": readiness["readiness_status"], "authorization_scope": auth["authorization_scope"], "dry_run_only": dry_run_only, "generated_at_utc": utc_now(), "generator_command": generator_command, "git_ref_or_commit": git_ref_or_commit(), "stage_sequence_verified": {"manifest_check_result": manifest_check, "required_sequence_complete": True, "execution_templates_present": True}, "generated_artifacts": [{"artifact_path": relative(readiness_out), "artifact_type": "readiness_report", "status": "generated", "hash_status": "available", "artifact_sha256": readiness_hash}, {"artifact_path": relative(run_record_out), "artifact_type": "run_record", "status": "generated", "hash_status": "self_hash_deferred", "artifact_sha256": None}, {"artifact_path": relative(PILOT_MANIFEST), "artifact_type": "template_reference", "status": "referenced", "hash_status": "available", "artifact_sha256": sha256_file(PILOT_MANIFEST)}, {"artifact_path": relative(packet_path), "artifact_type": "source_packet", "status": "referenced", "hash_status": "available", "artifact_sha256": packet_hash}], "carry_forward_flags": auth["required_carry_forward_flags"], "blocked_actions": BLOCKED_ACTIONS, "forbidden_claims": auth["forbidden_claims"], "validation_boundary": readiness["validation_boundary"], "next_allowed_action": "collect_real_evidence" if dry_run_only else "start_shadow_mode_pilot_with_current_packet"}


def run_dry_run(packet_path: Path, readiness_out: Path, run_record_out: Path, *, dry_run_only: bool, generator_command: str) -> dict[str, Any]:
    ensure_generated_output_policy(readiness_out, run_record_out)
    manifest_check = run_manifest_check()
    packet = load_json(packet_path)
    if not dry_run_only:
        assert_submitted_shadow_packet_is_real(packet, packet_path)
    readiness = run_readiness_for_packet(packet_path, out_path=readiness_out, allow_blocked=False, run_full_schema_validator=True)
    record = build_run_record(readiness, packet, packet_path=packet_path, dry_run_only=dry_run_only, readiness_out=readiness_out, run_record_out=run_record_out, manifest_check=manifest_check, generator_command=generator_command)
    validate_run_record_schema(record)
    write_json(run_record_out, record)
    return record


def run_expect_blocked(packet_path: Path) -> dict[str, Any]:
    run_manifest_check()
    readiness = run_readiness_for_packet(packet_path, out_path=None, allow_blocked=True, run_full_schema_validator=True)
    if not readiness["readiness_status"].startswith("blocked"):
        raise AssertionError(f"--expect-blocked expected blocked readiness, got {readiness['readiness_status']}")
    return readiness


def run_default_self_test() -> None:
    run_dry_run(DEFAULT_PACKET, DEFAULT_READINESS_OUT, DEFAULT_RUN_RECORD_OUT, dry_run_only=True, generator_command="python validation/e2e/run_pilot_dry_run_check.py")
    run_expect_blocked(DEFAULT_BLOCKED_PACKET)
    try:
        assert_submitted_shadow_packet_is_real(load_json(DEFAULT_PACKET), DEFAULT_PACKET)
    except AssertionError:
        return
    raise AssertionError("sample packet was unexpectedly accepted for submitted shadow mode")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dry-run smart-home pilot execution from an evidence intake packet.")
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET, help="Evidence intake packet JSON.")
    parser.add_argument("--readiness-out", type=Path, default=DEFAULT_READINESS_OUT, help="Generated readiness report path.")
    parser.add_argument("--run-record-out", type=Path, default=DEFAULT_RUN_RECORD_OUT, help="Generated pilot run record path.")
    parser.add_argument("--submitted-shadow-mode", action="store_true", help="Create submitted shadow-mode record. Requires real_issue_submission evidence and no sample markers.")
    parser.add_argument("--expect-blocked", action="store_true", help="Assert that the packet is blocked and do not create a run record.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        packet_path = args.packet if args.packet.is_absolute() else ROOT / args.packet
        readiness_out = args.readiness_out if args.readiness_out.is_absolute() else ROOT / args.readiness_out
        run_record_out = args.run_record_out if args.run_record_out.is_absolute() else ROOT / args.run_record_out
        if args.expect_blocked and args.submitted_shadow_mode:
            raise AssertionError("--expect-blocked cannot be combined with --submitted-shadow-mode")
        if args.expect_blocked:
            readiness = run_expect_blocked(packet_path)
            print(f"Pilot dry-run blocked-path check passed: {readiness['readiness_status']}")
            return 0
        if packet_path == DEFAULT_PACKET and readiness_out == DEFAULT_READINESS_OUT and run_record_out == DEFAULT_RUN_RECORD_OUT and not args.submitted_shadow_mode:
            run_default_self_test()
            print("Pilot dry-run self-test passed: positive dry-run, blocked packet, and sample-shadow rejection validated")
            return 0
        record = run_dry_run(packet_path, readiness_out, run_record_out, dry_run_only=not args.submitted_shadow_mode, generator_command=command_string(args))
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
