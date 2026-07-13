#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "STATUS.md"
CATALOG = ROOT / "planning" / "EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json"

U = "_".join
C = lambda name: f"python validation/e2e/{name}"

REQUIRED_MERGED_FOUNDATION = {
    "PR #101 evidence intake fixture matrix hardening",
    "PR #102 pilot readiness boundary hardening",
    "PR #103 Issue 8 submitted-packet preflight guide",
    "PR #104 backlog boundary refresh after preflight guide",
    "PR #105 Issue 8 preflight boundary validation",
    "PR #106 RTAQ-0024 preflight boundary status reconciliation",
    "PR #107 RTAQ-0025 active STATUS guard validation",
    "PR #108 RTAQ-0026 STATUS foundation guard refresh",
    "PR #112 RTAQ-0029 responsive intake decision guard",
}

REQUIRED_BOUNDARIES = {
    U(["production", "ready"]): "false",
    U(["prompt", "pack", "release", "ready"]): "false",
    U(["foundation", "checkpoint", "policy"]): "bounded checkpoints only; not append every merged PR",
    U(["real", "submitted", "packet", "present"]): "false",
    U(["pilot", "allowed", "to", "start"]): "false",
    U(["readiness", "claims", "upgraded"]): "false",
    U(["ci", "success", "claim", "boundary"]): "repository checks only; not responsive correctness evidence",
    U(["live", "render", "validated"]): "false",
    U(["export", "json", "validated"]): "false",
    U(["accessibility", "passed"]): "false",
    U(["pixel", "perfect"]): "false",
    U(["responsive", "correctness", "validated"]): "false",
    U(["pilot", "execution", "scope"]): U(["not", "allowed"]),
}

REQUIRED_AUTOMATIC_CHECKS = [
    C("run_rolling_queue_check.py"),
    C("run_run_ledger_check.py"),
    C("run_task_quality_gate_check.py"),
    C("run_submitted_packet_eligibility_gate_check.py"),
    C("run_responsive_tree_architecture_refactor_check.py"),
    C("run_submitted_packet_readiness_dry_run.py") + " --self-test",
    C("run_evidence_intake_check.py") + " --self-test",
    C("run_evidence_intake_submitted_mode_path_check.py"),
    C("run_evidence_intake_submitted_payload_hash_check.py"),
    C("run_evidence_intake_fixture_matrix_check.py"),
    C("run_" + "pilot" + "_readiness_check.py"),
    C("run_" + "pilot" + "_readiness_boundary_check.py"),
    C("run_issue_8_preflight_boundary_check.py"),
    C("run_issue_to_packet_bridge_check.py"),
    C("run_builder_responsive_input_boundary_check.py"),
    C("run_prompt_5_routing_envelope_check.py"),
    C("run_runtime_mismatch_reopen_package_check.py"),
    C("run_responsive_contract_drift_sentinel_check.py"),
    C("run_viewport_inheritance_reset_matrix_check.py"),
    C("run_responsive_handoff_export_boundary_manifest_check.py"),
    C("run_rtaq_ssot_guard_check.py"),
    C("run_status_merged_foundation_guard_check.py"),
    C("run_automation_control_state_check.py"),
    C("run_automation_work_package_catalog_check.py"),
]

STATUS_CATALOG_HEADING = "## WP-RESP-005/PR-B — State-driven catalog replenishment"
STATUS_CATALOG_SCHEMA = "ev4-status-work-package-catalog-snapshot@1.0.0"
CATALOG_PATH = "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json"
CATALOG_STATUS_KEYS = {
    "schema",
    "source",
    "catalog_state_snapshot_is_derived",
    "policy",
    "selectable_ready_horizon",
    "active_work_packages",
    "completed_work_packages",
}
POLICY_KEYS = {
    "ready_work_package_target",
    "refresh_when_ready_below",
    "max_ready_work_packages",
}
TRACKED_STATES = {
    "ready": "selectable_ready_horizon",
    "active": "active_work_packages",
    "completed": "completed_work_packages",
}
WP_ID_RE = re.compile(r"^WP-RESP-(\d{3})$")


def clean(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]
    return value.strip()


def yaml_pairs(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    in_yaml = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("```yaml"):
            in_yaml = True
            continue
        if in_yaml and line.startswith("```"):
            in_yaml = False
            continue
        if not in_yaml or not line or line.startswith("-") or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        pairs.append((key.strip(), clean(value)))
    return pairs


def yaml_list(text: str, key: str) -> list[str]:
    out: list[str] = []
    in_yaml = False
    in_list = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("```yaml"):
            in_yaml = True
            in_list = False
            continue
        if in_yaml and line.startswith("```"):
            in_yaml = False
            in_list = False
            continue
        if not in_yaml:
            continue
        if line == f"{key}:":
            in_list = True
            continue
        if in_list:
            if line.startswith("- "):
                out.append(clean(line.split("-", 1)[1]))
            elif line and not line.startswith("#"):
                break
    return out


def merged_foundation(text: str) -> set[str]:
    entries = set()
    for item in yaml_list(text, "merged_foundation"):
        match = re.match(r'"?(.+?)"?$', item)
        if not match:
            raise AssertionError(f"malformed merged_foundation entry: {item}")
        entries.add(match.group(1))
    return entries


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"JSON object required: {path.relative_to(ROOT)}")
    return payload


def wp_sort_key(work_package_id: str) -> int:
    match = WP_ID_RE.fullmatch(work_package_id)
    if not match:
        raise AssertionError(f"invalid Work Package ID: {work_package_id}")
    return int(match.group(1))


def sorted_work_package_ids(values: list[str]) -> list[str]:
    if len(values) != len(set(values)):
        raise AssertionError("STATUS catalog snapshot contains duplicate Work Package IDs")
    return sorted(values, key=wp_sort_key)


def expected_catalog_status_snapshot(catalog: dict[str, Any]) -> dict[str, Any]:
    policy = catalog.get("catalog_replenishment_policy")
    packages = catalog.get("work_packages")
    if not isinstance(policy, dict) or not isinstance(packages, dict):
        raise AssertionError("canonical Work Package catalog structure is invalid")

    state_lists = {field: [] for field in TRACKED_STATES.values()}
    for work_package_id, package in packages.items():
        if not isinstance(package, dict):
            raise AssertionError(f"catalog Work Package must be an object: {work_package_id}")
        if package.get("id") != work_package_id:
            raise AssertionError(f"catalog Work Package key/id mismatch: {work_package_id}")
        if package.get("selectable") is not True:
            continue
        ready_state = package.get("ready_state")
        target_field = TRACKED_STATES.get(ready_state)
        if target_field is not None:
            state_lists[target_field].append(work_package_id)

    for field, values in state_lists.items():
        state_lists[field] = sorted_work_package_ids(values)

    return {
        "schema": STATUS_CATALOG_SCHEMA,
        "source": CATALOG_PATH,
        "catalog_state_snapshot_is_derived": True,
        "policy": {key: policy.get(key) for key in sorted(POLICY_KEYS)},
        **state_lists,
    }


def extract_status_catalog_snapshot(text: str) -> dict[str, Any]:
    if text.count(STATUS_CATALOG_HEADING) != 1:
        raise AssertionError("STATUS.md must contain exactly one catalog status section")
    section = text.split(STATUS_CATALOG_HEADING, 1)[1]
    next_heading = re.search(r"\n## ", section)
    if next_heading:
        section = section[: next_heading.start()]
    match = re.search(r"```json\s*\n(?P<payload>.*?)\n```", section, flags=re.DOTALL)
    if not match:
        raise AssertionError("STATUS.md catalog status section must contain one JSON snapshot")
    try:
        payload = json.loads(match.group("payload"))
    except json.JSONDecodeError as exc:
        raise AssertionError(f"STATUS.md catalog status snapshot is invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise AssertionError("STATUS.md catalog status snapshot must be a JSON object")
    return payload


def validate_status_catalog_snapshot(text: str, catalog: dict[str, Any]) -> None:
    observed = extract_status_catalog_snapshot(text)
    if set(observed) != CATALOG_STATUS_KEYS:
        raise AssertionError(
            "STATUS.md catalog status snapshot keys mismatch; "
            f"observed={sorted(observed)} expected={sorted(CATALOG_STATUS_KEYS)}"
        )
    if observed.get("schema") != STATUS_CATALOG_SCHEMA:
        raise AssertionError("STATUS.md catalog status snapshot schema mismatch")
    if observed.get("source") != CATALOG_PATH:
        raise AssertionError("STATUS.md catalog status snapshot source mismatch")
    if observed.get("catalog_state_snapshot_is_derived") is not True:
        raise AssertionError("STATUS.md catalog state snapshot must declare derived=true")

    observed_policy = observed.get("policy")
    if not isinstance(observed_policy, dict) or set(observed_policy) != POLICY_KEYS:
        raise AssertionError("STATUS.md catalog replenishment policy keys mismatch")

    expected = expected_catalog_status_snapshot(catalog)
    if observed_policy != expected["policy"]:
        raise AssertionError(
            "STATUS.md catalog replenishment policy differs from canonical catalog; "
            f"observed={observed_policy} expected={expected['policy']}"
        )

    for field in TRACKED_STATES.values():
        values = observed.get(field)
        if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
            raise AssertionError(f"STATUS.md {field} must be a list of Work Package IDs")
        if values != sorted_work_package_ids(values):
            raise AssertionError(f"STATUS.md {field} must be unique and numerically sorted")
        if values != expected[field]:
            raise AssertionError(
                f"STATUS.md {field} differs from canonical catalog; "
                f"observed={values} expected={expected[field]}"
            )

    stale_horizon = "Selectable ready horizon: `WP-RESP-009` through `WP-RESP-012`."
    if stale_horizon in text:
        raise AssertionError("STATUS.md retains the superseded WP-RESP-009 through WP-RESP-012 horizon")


def validate_status_text(text: str, catalog: dict[str, Any]) -> None:
    missing_foundation = sorted(REQUIRED_MERGED_FOUNDATION - merged_foundation(text))
    if missing_foundation:
        raise AssertionError("STATUS.md missing merged_foundation entries: " + ", ".join(missing_foundation))

    values_by_key: dict[str, set[str]] = {}
    for key, value in yaml_pairs(text):
        if key in REQUIRED_BOUNDARIES:
            values_by_key.setdefault(key, set()).add(value)

    for key, expected in REQUIRED_BOUNDARIES.items():
        observed = values_by_key.get(key, set())
        if observed != {expected}:
            raise AssertionError(f"STATUS.md boundary key {key} must appear only as {expected!r}; observed {sorted(observed)!r}")

    checks = yaml_list(text, "automatic_check")
    if checks != REQUIRED_AUTOMATIC_CHECKS:
        missing = [check for check in REQUIRED_AUTOMATIC_CHECKS if check not in checks]
        extra = [check for check in checks if check not in REQUIRED_AUTOMATIC_CHECKS]
        detail = []
        if missing:
            detail.append("missing: " + ", ".join(missing))
        if extra:
            detail.append("extra: " + ", ".join(extra))
        if not missing and not extra:
            detail.append("order differs from Validate workflow")
        raise AssertionError("STATUS.md automatic_check must mirror the primary Validate chain; " + "; ".join(detail))

    validate_status_catalog_snapshot(text, catalog)


def fixture_catalog() -> dict[str, Any]:
    states = {
        "WP-RESP-009": "completed",
        "WP-RESP-010": "ready",
        "WP-RESP-011": "ready",
        "WP-RESP-012": "completed",
        "WP-RESP-013": "completed",
        "WP-RESP-014": "ready",
        "WP-RESP-015": "active",
        "WP-RESP-016": "ready",
    }
    return {
        "catalog_replenishment_policy": {
            "ready_work_package_target": 4,
            "refresh_when_ready_below": 4,
            "max_ready_work_packages": 5,
        },
        "work_packages": {
            work_package_id: {
                "id": work_package_id,
                "selectable": True,
                "ready_state": ready_state,
            }
            for work_package_id, ready_state in states.items()
        },
    }


def status_catalog_section(catalog: dict[str, Any]) -> str:
    snapshot = expected_catalog_status_snapshot(catalog)
    return (
        f"{STATUS_CATALOG_HEADING}\n\n"
        "The snapshot below is derived from the canonical monolithic catalog and is validator-enforced. "
        "It supersedes earlier prose horizons.\n\n"
        "```json\n"
        f"{json.dumps(snapshot, indent=2, ensure_ascii=False)}\n"
        "```\n"
    )


def status_fixture(
    catalog: dict[str, Any] | None = None,
    checks: list[str] | None = None,
    extra: str = "",
    catalog_section: str | None = None,
) -> str:
    catalog = fixture_catalog() if catalog is None else catalog
    checks = REQUIRED_AUTOMATIC_CHECKS if checks is None else checks
    foundation = "\n".join(f'  - "{item}"' for item in sorted(REQUIRED_MERGED_FOUNDATION))
    boundaries = "\n".join(f"{key}: {value}" for key, value in REQUIRED_BOUNDARIES.items())
    check_lines = "\n".join(f"    - {item}" for item in checks)
    section = status_catalog_section(catalog) if catalog_section is None else catalog_section
    return f"""# STATUS
```yaml
foundation_checkpoint_policy: bounded checkpoints only; not append every merged PR
merged_foundation:
{foundation}
```
```yaml
{boundaries}
```
{extra}
```yaml
automatic_check:
{check_lines}
```

{section}
"""


def assert_invalid(text: str, catalog: dict[str, Any], expected: str) -> None:
    try:
        validate_status_text(text, catalog)
    except AssertionError as exc:
        if expected not in str(exc):
            raise AssertionError(f"expected {expected!r}, got {exc!s}") from exc
        return
    raise AssertionError(f"expected invalid STATUS text for {expected!r}")


def run_self_tests() -> None:
    catalog = fixture_catalog()
    validate_status_text(status_fixture(catalog=catalog), catalog)
    assert_invalid(
        status_fixture(
            catalog=catalog,
            extra="```yaml\nfoundation_checkpoint_policy: conflicting checkpoint wording\n```\n",
        ),
        catalog,
        "foundation_checkpoint_policy",
    )
    assert_invalid(
        status_fixture(
            catalog=catalog,
            extra="```yaml\nci_success_claim_boundary: conflicting CI boundary wording\n```\n",
        ),
        catalog,
        "ci_success_claim_boundary",
    )
    assert_invalid(
        status_fixture(
            catalog=catalog,
            checks=[c for c in REQUIRED_AUTOMATIC_CHECKS if "run_automation_work_package_catalog_check.py" not in c],
        ),
        catalog,
        "run_automation_work_package_catalog_check.py",
    )
    assert_invalid(
        status_fixture(catalog=catalog, checks=list(reversed(REQUIRED_AUTOMATIC_CHECKS))),
        catalog,
        "order differs from Validate workflow",
    )

    stale_snapshot = expected_catalog_status_snapshot(catalog)
    stale_snapshot["selectable_ready_horizon"] = [
        "WP-RESP-009",
        "WP-RESP-010",
        "WP-RESP-011",
        "WP-RESP-012",
    ]
    stale_section = (
        f"{STATUS_CATALOG_HEADING}\n\n"
        "```json\n"
        f"{json.dumps(stale_snapshot, indent=2)}\n"
        "```\n\n"
        "- Selectable ready horizon: `WP-RESP-009` through `WP-RESP-012`.\n"
    )
    assert_invalid(
        status_fixture(catalog=catalog, catalog_section=stale_section),
        catalog,
        "selectable_ready_horizon",
    )

    stale_active = expected_catalog_status_snapshot(catalog)
    stale_active["active_work_packages"] = ["WP-RESP-013", "WP-RESP-015"]
    stale_active_section = (
        f"{STATUS_CATALOG_HEADING}\n\n"
        "```json\n"
        f"{json.dumps(stale_active, indent=2)}\n"
        "```\n"
    )
    assert_invalid(
        status_fixture(catalog=catalog, catalog_section=stale_active_section),
        catalog,
        "active_work_packages",
    )

    stale_completed = expected_catalog_status_snapshot(catalog)
    stale_completed["completed_work_packages"] = ["WP-RESP-009", "WP-RESP-012"]
    stale_completed_section = (
        f"{STATUS_CATALOG_HEADING}\n\n"
        "```json\n"
        f"{json.dumps(stale_completed, indent=2)}\n"
        "```\n"
    )
    assert_invalid(
        status_fixture(catalog=catalog, catalog_section=stale_completed_section),
        catalog,
        "completed_work_packages",
    )


def main() -> int:
    run_self_tests()
    catalog = load_json_object(CATALOG)
    validate_status_text(STATUS.read_text(encoding="utf-8"), catalog)
    print("STATUS merged-foundation and catalog-horizon guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
