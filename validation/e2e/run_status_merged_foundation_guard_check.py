#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "STATUS.md"

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
    "production_ready": "false",
    "prompt_pack_release_ready": "false",
    "foundation_checkpoint_policy": "bounded checkpoints only; not append every merged PR",
    "real_submitted_packet_present": "false",
    "pilot_allowed_to_start": "false",
    "readiness_claims_upgraded": "false",
    "ci_success_claim_boundary": "repository checks only; not responsive correctness evidence",
    "live_render_validated": "false",
    "export_json_validated": "false",
    "accessibility_passed": "false",
    "pixel_perfect": "false",
    "responsive_correctness_validated": "false",
    "pilot_execution_scope": "not_allowed",
    "fixed_ordinal_refresh_policy": "forbidden",
    "state_driven_refresh": "true",
    "catalog_replenishment_must_not_block_active_execution": "true",
    "catalog_replenishment_must_respect_single_active_pr_policy": "true",
}

REQUIRED_AUTOMATIC_CHECKS = [
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
    "python validation/e2e/run_rtaq_ssot_guard_check.py",
    "python validation/e2e/run_status_merged_foundation_guard_check.py",
    "python validation/e2e/run_automation_control_state_check.py",
    "python validation/e2e/run_automation_work_package_catalog_check.py",
]

FORBIDDEN_PAIRS = {
    "production_ready": "true",
    "prompt_pack_release_ready": "true",
    "real_submitted_packet_present": "true",
    "pilot_allowed_to_start": "true",
    "readiness_claims_upgraded": "true",
    "live_render_validated": "true",
    "export_json_validated": "true",
    "accessibility_passed": "true",
    "pixel_perfect": "true",
    "responsive_correctness_validated": "true",
    "pilot_execution_scope": "allowed",
    "fixed_ordinal_refresh_policy": "allowed",
    "catalog_replenishment_must_not_block_active_execution": "false",
    "catalog_replenishment_must_respect_single_active_pr_policy": "false",
}


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
    entries: set[str] = set()
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

    pairs = yaml_pairs(text)
    pair_set = set(pairs)
    missing_boundaries = [f"{key}: {value}" for key, value in REQUIRED_BOUNDARIES.items() if (key, value) not in pair_set]
    if missing_boundaries:
        raise AssertionError("STATUS.md missing or incorrect boundary entries: " + ", ".join(missing_boundaries))

    forbidden = [f"{key}: {value}" for key, value in pairs if FORBIDDEN_PAIRS.get(key) == value]
    if forbidden:
        raise AssertionError("STATUS.md upgrades forbidden claims: " + ", ".join(forbidden))

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
    if checks is None:
        checks = REQUIRED_AUTOMATIC_CHECKS
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
    assert_invalid(status_fixture(extra="```yaml\nproduction_ready: true\n```\n"), "production_ready: true")
    assert_invalid(status_fixture(extra="```yaml\nfixed_ordinal_refresh_policy: allowed\n```\n"), "fixed_ordinal_refresh_policy: allowed")
    assert_invalid(status_fixture(checks=[c for c in REQUIRED_AUTOMATIC_CHECKS if "run_automation_work_package_catalog_check.py" not in c]), "run_automation_work_package_catalog_check.py")
    assert_invalid(status_fixture(checks=list(reversed(REQUIRED_AUTOMATIC_CHECKS))), "order differs from Validate workflow")


def main() -> int:
    run_self_tests()
    validate_status_text(STATUS.read_text(encoding="utf-8"))
    print("STATUS merged-foundation guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
