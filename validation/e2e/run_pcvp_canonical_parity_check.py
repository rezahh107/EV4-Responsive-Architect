#!/usr/bin/env python3
"""Verify Responsive PCVP vendor bytes against the immutable Decision Kernel pin."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CANONICAL_COMMIT = "069a50fa243b01fa578a7c1bcb8864d9e796d34b"
LOCAL_ROOT = ROOT / "contracts" / "pcvp"
LOCK_PATH = LOCAL_ROOT / "pcvp-v1.lock.json"
LOCAL_PROFILE = LOCAL_ROOT / "responsive.profile.yaml"
LOCAL_VENDOR = LOCAL_ROOT / "vendor" / "decision-kernel" / "v1.0.0"
CANONICAL_PROFILE = Path("kernel/pcvp/v1.0.0/bundle/03-PROFILES/responsive.profile.yaml")
CANONICAL_SCHEMAS = Path("kernel/pcvp/v1.0.0/bundle/04-SCHEMAS")
EXPECTED_FILES = (
    "authorization.schema.json",
    "claim.schema.json",
    "effect.schema.json",
    "handoff.schema.json",
)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path} must be a JSON object")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_head(repo: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--decision-kernel-root",
        required=True,
        type=Path,
        help="Decision Kernel checkout pinned to the canonical PCVP commit.",
    )
    args = parser.parse_args()
    kernel = args.decision_kernel_root.resolve()

    if _git_head(kernel) != CANONICAL_COMMIT:
        raise AssertionError("Decision Kernel checkout is not at the immutable PCVP pin")

    lock = _load_json(LOCK_PATH)
    if lock.get("canonical", {}).get("commit_sha") != CANONICAL_COMMIT:
        raise AssertionError("Responsive PCVP lock does not pin the expected Decision Kernel commit")
    if lock.get("verification", {}).get("byte_equality_required") is not True:
        raise AssertionError("Responsive PCVP lock must require byte equality")

    canonical_profile = kernel / CANONICAL_PROFILE
    if LOCAL_PROFILE.read_bytes() != canonical_profile.read_bytes():
        raise AssertionError("Responsive profile bytes differ from canonical Decision Kernel bytes")
    if _sha256(LOCAL_PROFILE) != lock.get("profile", {}).get("sha256"):
        raise AssertionError("Responsive profile hash differs from lock")

    locked_files = {
        entry.get("name"): entry.get("sha256")
        for entry in lock.get("files", [])
        if isinstance(entry, dict)
    }
    if set(locked_files) != set(EXPECTED_FILES):
        raise AssertionError("Responsive PCVP lock does not cover exactly the canonical schema set")

    for name in EXPECTED_FILES:
        local = LOCAL_VENDOR / name
        canonical = kernel / CANONICAL_SCHEMAS / name
        if local.read_bytes() != canonical.read_bytes():
            raise AssertionError(f"{name} differs from canonical Decision Kernel bytes")
        if _sha256(local) != locked_files[name]:
            raise AssertionError(f"{name} hash differs from Responsive lock")

    print(json.dumps({
        "result": "PASS",
        "canonical_repository": "rezahh107/EV4-Decision-Kernel",
        "canonical_commit": CANONICAL_COMMIT,
        "profile_byte_equal": True,
        "schema_byte_equal_count": len(EXPECTED_FILES),
        "local_copy_authoritative": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Responsive PCVP canonical parity check failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
