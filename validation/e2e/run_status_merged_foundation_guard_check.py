#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "STATUS.md"
CATALOG = ROOT / "planning" / "EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json"
VALIDATE_WORKFLOW = ROOT / ".github" / "workflows" / "validate.yml"

U = "_".join

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
JSON_FENCE_RE = re.compile(r"```json[^\n]*\n(?P<payload>.*?)\n```", flags=re.DOTALL | re.IGNORECASE)
ANY_FENCE_RE = re.compile(r"```(?P<language>[^\n`]*)\n(?P<body>.*?)\n```", flags=re.DOTALL)
CATALOG_BLOCK_MARKERS = re.compile(
    r"selectable_ready_horizon|active_work_packages|completed_work_packages|"
    r"catalog_replenishment_policy|ready_state|WP-RESP-\d{3}",
    flags=re.IGNORECASE,
)
CONTRADICTORY_CATALOG_PROSE = re.compile(
    r"(?:selectable\s+ready\s+horizon|ready\s+horizon|active\s+work\s+packages|"
    r"completed\s+work\s+packages|ready_state)"
    r"|(?:WP-RESP-\d{3}.*\b(?:ready|active|completed|horizon)\b)"
    r"|(?:\b(?:ready|active|completed|horizon)\b.*WP-RESP-\d{3})",
    flags=re.IGNORECASE | re.DOTALL,
)

# Exact pre-repair STATUS fixture retained only as negative regression coverage.
PRE_REPAIR_AUTOMATIC_CHECKS = [
    "python validation/e2e/run_rolling_queue_check.py",
    "python validation/e2e/run_run_ledger_check.py",
    "python validation/e2e/run_task_quality_gate_check.py",
    "python validation/e2e/run_submitted_packet_eligibility_gate_check.py",
    "python validation/e2e/run_responsive_tree_architecture_refactor_check.py",
    "python validation/e2e/run_submitted_packet_readiness_dry_run.py --self-test",
    "python validation/e2e/run_evidence_intake_check.py --self-test",
    "python validation/e2e/run_evidence_intake_submitted_mode_path_check.py",
    "python validation/e2e/run_evidence_intake_submitted_payload_hash_check.py",
    "python validation/e2e/run_evidence_intake_fixture_matrix_check.py",
    "python validation/e2e/run_pilot_readiness_check.py",
    "python validation/e2e/run_pilot_readiness_boundary_check.py",
    "python validation/e2e/run_issue_8_preflight_boundary_check.py",
    "python validation/e2e/run_issue_to_packet_bridge_check.py",
    "python validation/e2e/run_builder_responsive_input_boundary_check.py",
    "python validation/e2e/run_prompt_5_routing_envelope_check.py",
    "python validation/e2e/run_runtime_mismatch_reopen_package_check.py",
    "python validation/e2e/run_responsive_contract_drift_sentinel_check.py",
    "python validation/e2e/run_viewport_inheritance_reset_matrix_check.py",
    "python validation/e2e/run_responsive_handoff_export_boundary_manifest_check.py",
    "python validation/e2e/run_rtaq_ssot_guard_check.py",
    "python validation/e2e/run_status_merged_foundation_guard_check.py",
    "python validation/e2e/run_automation_control_state_check.py",
    "python validation/e2e/run_automation_work_package_catalog_check.py",
]


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


def workflow_validation_section(workflow_text: str) -> str:
    lines = workflow_text.splitlines()
    try:
        jobs_index = next(i for i, line in enumerate(lines) if line == "jobs:")
        start = next(i for i in range(jobs_index + 1, len(lines)) if lines[i] == "  validation:")
    except StopIteration as exc:
        raise AssertionError("Validate workflow must contain jobs.validation") from exc

    end = len(lines)
    for i in range(start + 1, len(lines)):
        if re.fullmatch(r"  [A-Za-z0-9_-]+:", lines[i]):
            end = i
            break
    return "\n".join(lines[start:end])


def workflow_command_projection(workflow_text: str) -> list[str]:
    section = workflow_validation_section(workflow_text)
    commands: list[str] = []
    for raw in section.splitlines():
        match = re.match(r"^\s+run:\s*(python validation/e2e/\S.*)$", raw)
        if match:
            commands.append(match.group(1).strip())

    if not commands:
        raise AssertionError("Validate workflow command projection is empty")
    if len(commands) != len(set(commands)):
        duplicates = sorted({command for command in commands if commands.count(command) > 1})
        raise AssertionError("Validate workflow command projection contains duplicates: " + ", ".join(duplicates))
    return commands


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


def extract_status_catalog_section(text: str) -> str:
    if text.count(STATUS_CATALOG_HEADING) != 1:
        raise AssertionError("STATUS.md must contain exactly one catalog status section")
    section = text.split(STATUS_CATALOG_HEADING, 1)[1]
    next_heading = re.search(r"\n## ", section)
    if next_heading:
        section = section[: next_heading.start()]
    return section


def extract_status_catalog_snapshot(text: str) -> dict[str, Any]:
    section = extract_status_catalog_section(text)
    matches = list(JSON_FENCE_RE.finditer(section))
    if not matches:
        raise AssertionError("STATUS.md catalog status section must contain exactly one JSON snapshot; observed 0")
    if len(matches) != 1:
        raise AssertionError(
            "STATUS.md catalog status section must contain exactly one JSON snapshot; "
            f"observed {len(matches)}"
        )

    match = matches[0]
    try:
        payload = json.loads(match.group("payload"))
    except json.JSONDecodeError as exc:
        raise AssertionError(f"STATUS.md catalog status snapshot is invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise AssertionError("STATUS.md catalog status snapshot must be a JSON object")

    trailing = section[match.end():]
    for fenced in ANY_FENCE_RE.finditer(trailing):
        if CATALOG_BLOCK_MARKERS.search(fenced.group("body")):
            raise AssertionError(
                "STATUS.md catalog status section contains another machine-readable catalog-state block"
            )

    prose_only = ANY_FENCE_RE.sub("", trailing)
    if CONTRADICTORY_CATALOG_PROSE.search(prose_only):
        raise AssertionError("STATUS.md catalog status section contains contradictory catalog-state prose after snapshot")
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


def validate_automatic_check_projection(text: str, workflow_text: str) -> None:
    observed = yaml_list(text, "automatic_check")
    expected = workflow_command_projection(workflow_text)
    if observed == expected:
        return

    missing = [command for command in expected if command not in observed]
    extra = [command for command in observed if command not in expected]
    detail: list[str] = []
    if missing:
        detail.append("missing: " + ", ".join(missing))
    if extra:
        detail.append("extra: " + ", ".join(extra))
    if not missing and not extra:
        detail.append("order differs from Validate workflow")
    raise AssertionError(
        "STATUS.md automatic_check must exactly mirror the primary Validate workflow command projection; "
        + "; ".join(detail)
    )


def validate_status_text(text: str, catalog: dict[str, Any], workflow_text: str) -> None:
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
            raise AssertionError(
                f"STATUS.md boundary key {key} must appear only as {expected!r}; observed {sorted(observed)!r}"
            )

    validate_automatic_check_projection(text, workflow_text)
    validate_status_catalog_snapshot(text, catalog)


def fixture_catalog() -> dict[str, Any]:
    states = {
        "WP-RESP-002": "completed",
        "WP-RESP-003": "completed",
        "WP-RESP-004": "completed",
        "WP-RESP-006": "completed",
        "WP-RESP-007": "completed",
        "WP-RESP-008": "completed",
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
        "```\n\n"
        "- No submitted evidence was created; Issue #8 was not mutated; no pilot was run or authorized.\n"
        "- Project Gate transport was not executed and human-readable receipts are not Kernel authority.\n"
        "- Production, release, live-render, export, accessibility, pixel-perfect, and responsive-correctness claims remain false.\n"
        "- CI, catalog state, and catalog completion remain repository-check evidence only.\n"
    )


def status_fixture(
    catalog: dict[str, Any],
    checks: list[str],
    *,
    extra: str = "",
    catalog_section: str | None = None,
) -> str:
    foundation = "\n".join(f'  - "{item}"' for item in sorted(REQUIRED_MERGED_FOUNDATION))
    boundaries = "\n".join(f"{key}: {value}" for key, value in REQUIRED_BOUNDARIES.items())
    check_lines = "\n".join(f"  - {item}" for item in checks)
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


def assert_invalid(
    text: str,
    catalog: dict[str, Any],
    workflow_text: str,
    expected_message: str,
) -> None:
    try:
        validate_status_text(text, catalog, workflow_text)
    except AssertionError as exc:
        if expected_message not in str(exc):
            raise AssertionError(f"expected {expected_message!r}, got {exc!s}") from exc
        return
    raise AssertionError(f"expected invalid STATUS text for {expected_message!r}")


def json_section(*payloads: dict[str, Any], trailing: str = "") -> str:
    fences = "\n\n".join(
        "```json\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\n```"
        for payload in payloads
    )
    return f"{STATUS_CATALOG_HEADING}\n\n{fences}\n{trailing}"


def run_self_tests(workflow_text: str) -> None:
    catalog = fixture_catalog()
    expected_checks = workflow_command_projection(workflow_text)
    valid = status_fixture(catalog, expected_checks)
    validate_status_text(valid, catalog, workflow_text)

    assert_invalid(
        status_fixture(
            catalog,
            expected_checks,
            extra="```yaml\nfoundation_checkpoint_policy: conflicting checkpoint wording\n```\n",
        ),
        catalog,
        workflow_text,
        "foundation_checkpoint_policy",
    )
    assert_invalid(
        status_fixture(
            catalog,
            expected_checks,
            extra="```yaml\nci_success_claim_boundary: conflicting CI boundary wording\n```\n",
        ),
        catalog,
        workflow_text,
        "ci_success_claim_boundary",
    )

    missing_command = expected_checks[len(expected_checks) // 2]
    assert_invalid(
        status_fixture(catalog, [command for command in expected_checks if command != missing_command]),
        catalog,
        workflow_text,
        "missing:",
    )
    assert_invalid(
        status_fixture(catalog, expected_checks + ["python validation/e2e/run_unlisted_extra_check.py"]),
        catalog,
        workflow_text,
        "extra:",
    )
    reordered = list(expected_checks)
    reordered[0], reordered[1] = reordered[1], reordered[0]
    assert_invalid(
        status_fixture(catalog, reordered),
        catalog,
        workflow_text,
        "order differs from Validate workflow",
    )
    assert_invalid(
        status_fixture(catalog, PRE_REPAIR_AUTOMATIC_CHECKS),
        catalog,
        workflow_text,
        "primary Validate workflow command projection",
    )

    snapshot = expected_catalog_status_snapshot(catalog)
    assert_invalid(
        status_fixture(catalog, expected_checks, catalog_section=f"{STATUS_CATALOG_HEADING}\n\nNo snapshot.\n"),
        catalog,
        workflow_text,
        "observed 0",
    )

    stale_snapshot = dict(snapshot)
    stale_snapshot["selectable_ready_horizon"] = [
        "WP-RESP-009",
        "WP-RESP-010",
        "WP-RESP-011",
        "WP-RESP-012",
    ]
    assert_invalid(
        status_fixture(
            catalog,
            expected_checks,
            catalog_section=json_section(snapshot, stale_snapshot),
        ),
        catalog,
        workflow_text,
        "observed 2",
    )
    assert_invalid(
        status_fixture(
            catalog,
            expected_checks,
            catalog_section=json_section(
                snapshot,
                trailing="\nSelectable ready horizon: `WP-RESP-009` through `WP-RESP-012`.\n",
            ),
        ),
        catalog,
        workflow_text,
        "contradictory catalog-state prose",
    )
    assert_invalid(
        status_fixture(
            catalog,
            expected_checks,
            catalog_section=json_section(
                snapshot,
                trailing=(
                    "\n```yaml\n"
                    "selectable_ready_horizon:\n"
                    "  - WP-RESP-009\n"
                    "  - WP-RESP-010\n"
                    "  - WP-RESP-011\n"
                    "  - WP-RESP-012\n"
                    "```\n"
                ),
            ),
        ),
        catalog,
        workflow_text,
        "another machine-readable catalog-state block",
    )


def main() -> int:
    workflow_text = VALIDATE_WORKFLOW.read_text(encoding="utf-8")
    run_self_tests(workflow_text)
    catalog = load_json_object(CATALOG)
    validate_status_text(STATUS.read_text(encoding="utf-8"), catalog, workflow_text)
    print("STATUS merged-foundation, workflow-parity, and single catalog-snapshot guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
