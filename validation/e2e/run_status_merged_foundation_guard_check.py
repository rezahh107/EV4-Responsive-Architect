#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "STATUS.md"

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
    C("run_responsive_contract_drift_sentinel_check.py"),
    C("run_viewport_inheritance_reset_matrix_check.py"),
    C("run_rtaq_ssot_guard_check.py"),
    C("run_status_merged_foundation_guard_check.py"),
    C("run_automation_control_state_check.py"),
    C("run_automation_work_package_catalog_check.py"),
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


def validate_status_text(text: str) -> None:
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


def status_fixture(checks: list[str] | None = None, extra: str = "") -> str:
    checks = REQUIRED_AUTOMATIC_CHECKS if checks is None else checks
    foundation = "\n".join(f'  - "{item}"' for item in sorted(REQUIRED_MERGED_FOUNDATION))
    boundaries = "\n".join(f"{key}: {value}" for key, value in REQUIRED_BOUNDARIES.items())
    check_lines = "\n".join(f"    - {item}" for item in checks)
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
"""


def assert_invalid(text: str, expected: str) -> None:
    try:
        validate_status_text(text)
    except AssertionError as exc:
        if expected not in str(exc):
            raise AssertionError(f"expected {expected!r}, got {exc!s}") from exc
        return
    raise AssertionError(f"expected invalid STATUS text for {expected!r}")


def run_self_tests() -> None:
    validate_status_text(status_fixture())
    assert_invalid(status_fixture(extra="```yaml\nfoundation_checkpoint_policy: conflicting checkpoint wording\n```\n"), "foundation_checkpoint_policy")
    assert_invalid(status_fixture(extra="```yaml\nci_success_claim_boundary: conflicting CI boundary wording\n```\n"), "ci_success_claim_boundary")
    assert_invalid(status_fixture(checks=[c for c in REQUIRED_AUTOMATIC_CHECKS if "run_automation_work_package_catalog_check.py" not in c]), "run_automation_work_package_catalog_check.py")
    assert_invalid(status_fixture(checks=list(reversed(REQUIRED_AUTOMATIC_CHECKS))), "order differs from Validate workflow")


def main() -> int:
    run_self_tests()
    validate_status_text(STATUS.read_text(encoding="utf-8"))
    print("STATUS merged-foundation guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
