#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "STATUS.md"
CATALOG = ROOT / "planning" / "EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json"
GUARD = ROOT / "validation" / "e2e" / "run_status_merged_foundation_guard_check.py"

HEADING = "## WP-RESP-005/PR-B — State-driven catalog replenishment"
SCHEMA = "ev4-status-work-package-catalog-snapshot@1.0.0"
CATALOG_PATH = "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json"
TRACKED = {
    "ready": "selectable_ready_horizon",
    "active": "active_work_packages",
    "completed": "completed_work_packages",
}
WP_ID_RE = re.compile(r"^WP-RESP-(\d{3})$")
FINAL_GUARD = " + repr(guard) + "


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"JSON object required: {path.relative_to(ROOT)}")
    return payload


def sort_key(work_package_id: str) -> int:
    match = WP_ID_RE.fullmatch(work_package_id)
    if not match:
        raise AssertionError(f"invalid Work Package ID: {work_package_id}")
    return int(match.group(1))


def derive_snapshot(catalog: dict[str, Any]) -> dict[str, Any]:
    policy = catalog["catalog_replenishment_policy"]
    state_lists = {field: [] for field in TRACKED.values()}
    for work_package_id, package in catalog["work_packages"].items():
        if package.get("id") != work_package_id:
            raise AssertionError(f"catalog Work Package key/id mismatch: {work_package_id}")
        if package.get("selectable") is not True:
            continue
        target = TRACKED.get(package.get("ready_state"))
        if target is not None:
            state_lists[target].append(work_package_id)
    for field in state_lists:
        state_lists[field] = sorted(state_lists[field], key=sort_key)
    return {
        "schema": SCHEMA,
        "source": CATALOG_PATH,
        "catalog_state_snapshot_is_derived": True,
        "policy": {
            "max_ready_work_packages": policy["max_ready_work_packages"],
            "ready_work_package_target": policy["ready_work_package_target"],
            "refresh_when_ready_below": policy["refresh_when_ready_below"],
        },
        **state_lists,
    }


def update_status(catalog: dict[str, Any]) -> None:
    text = STATUS.read_text(encoding="utf-8")
    if text.count(HEADING) != 1:
        raise AssertionError("STATUS.md must contain exactly one catalog status section")
    prefix = text.split(HEADING, 1)[0].rstrip()
    snapshot = derive_snapshot(catalog)
    expected_ready = ["WP-RESP-010", "WP-RESP-011", "WP-RESP-014", "WP-RESP-016"]
    if snapshot["selectable_ready_horizon"] != expected_ready:
        raise AssertionError(
            "authoritative ready horizon differs from reviewed finding: "
            f"{snapshot['selectable_ready_horizon']}"
        )
    expected_active = ["WP-RESP-015"]
    if snapshot["active_work_packages"] != expected_active:
        raise AssertionError(
            "authoritative active package differs from reviewed finding: "
            f"{snapshot['active_work_packages']}"
        )
    for work_package_id in ("WP-RESP-009", "WP-RESP-012", "WP-RESP-013"):
        if work_package_id not in snapshot["completed_work_packages"]:
            raise AssertionError(f"reviewed completed package missing from catalog: {work_package_id}")
    if snapshot["policy"] != {
        "max_ready_work_packages": 5,
        "ready_work_package_target": 4,
        "refresh_when_ready_below": 4,
    }:
        raise AssertionError(f"catalog replenishment policy changed unexpectedly: {snapshot['policy']}")

    section = (
        f"{HEADING}\n\n"
        "The snapshot below is derived from the canonical monolithic catalog and is validator-enforced. "
        "It explicitly supersedes the former `WP-RESP-009` through `WP-RESP-012` ready-horizon statement.\n\n"
        "```json\n"
        f"{json.dumps(snapshot, indent=2, ensure_ascii=False)}\n"
        "```\n\n"
        "- No submitted evidence was created; Issue #8 was not mutated; no pilot was run or authorized.\n"
        "- Project Gate transport was not executed and human-readable receipts are not Kernel authority.\n"
        "- Production, release, live-render, export, accessibility, pixel-perfect, and responsive-correctness claims remain false.\n"
        "- CI, catalog state, and catalog completion remain repository-check evidence only.\n"
    )
    updated = prefix + "\n\n" + section
    if "Selectable ready horizon: `WP-RESP-009` through `WP-RESP-012`." in updated:
        raise AssertionError("stale ready-horizon statement survived STATUS repair")
    STATUS.write_text(updated, encoding="utf-8")


def main() -> int:
    catalog = load_json(CATALOG)
    update_status(catalog)
    GUARD.write_text(FINAL_GUARD, encoding="utf-8")
    print("PR #179 STATUS catalog-horizon repair materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
