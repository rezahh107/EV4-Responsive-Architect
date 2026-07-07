#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "STATUS.md"

# Bounded foundation checkpoint, not an append-every-merge rule. This locks the
# latest material Builder -> Responsive intake guard while avoiding status-only
# merge-final loops for every repository merge.
REQUIRED_MERGED_FOUNDATION = {
    'PR #101 evidence intake fixture matrix hardening',
    'PR #102 pilot readiness boundary hardening',
    'PR #103 Issue 8 submitted-packet preflight guide',
    'PR #104 backlog boundary refresh after preflight guide',
    'PR #105 Issue 8 preflight boundary validation',
    'PR #106 RTAQ-0024 preflight boundary status reconciliation',
    'PR #107 RTAQ-0025 active STATUS guard validation',
    'PR #108 RTAQ-0026 STATUS foundation guard refresh',
    'PR #112 RTAQ-0029 responsive intake decision guard',
}

REQUIRED_BOUNDARIES = {
    'production_ready': 'false',
    'prompt_pack_release_ready': 'false',
    'foundation_checkpoint_policy': 'bounded checkpoints only; not append every merged PR',
    'real_submitted_packet_present': 'false',
    'pilot_allowed_to_start': 'false',
    'readiness_claims_upgraded': 'false',
    'ci_success_claim_boundary': 'repository checks only; not responsive correctness evidence',
    'pilot_execution_scope': 'not_allowed',
}

REQUIRED_AUTOMATIC_CHECKS = [
    'python validation/e2e/run_rolling_queue_check.py',
    'python validation/e2e/run_run_ledger_check.py',
    'python validation/e2e/run_task_quality_gate_check.py',
    'python validation/e2e/run_submitted_packet_eligibility_gate_check.py',
    'python validation/e2e/run_responsive_tree_architecture_refactor_check.py',
    'python validation/e2e/run_submitted_packet_readiness_dry_run.py --self-test',
    'python validation/e2e/run_evidence_intake_check.py --self-test',
    'python validation/e2e/run_evidence_intake_submitted_mode_path_check.py',
    'python validation/e2e/run_evidence_intake_submitted_payload_hash_check.py',
    'python validation/e2e/run_evidence_intake_fixture_matrix_check.py',
    'python validation/e2e/run_pilot_readiness_check.py',
    'python validation/e2e/run_pilot_readiness_boundary_check.py',
    'python validation/e2e/run_issue_8_preflight_boundary_check.py',
    'python validation/e2e/run_builder_responsive_input_boundary_check.py',
    'python validation/e2e/run_rtaq_ssot_guard_check.py',
    'python validation/e2e/run_status_merged_foundation_guard_check.py',
    'python validation/e2e/run_automation_control_state_check.py',
]

FORBIDDEN_CLAIMS = {
    'production_ready': 'true',
    'prompt_pack_release_ready': 'true',
    'real_submitted_packet_present': 'true',
    'pilot_allowed_to_start': 'true',
    'readiness_claims_upgraded': 'true',
    'pilot_execution_scope': 'allowed',
}


def extract_merged_foundation(status_text: str) -> set[str]:
    entries: set[str] = set()
    inside = False
    for line in status_text.splitlines():
        if line.strip() == 'merged_foundation:':
            inside = True
            continue
        if inside and line.startswith('  - '):
            match = re.match(r'\s*-\s+"(.+)"\s*$', line)
            if not match:
                raise AssertionError(f'malformed merged_foundation entry: {line}')
            entries.add(match.group(1))
            continue
        if inside and line and not line.startswith('  - '):
            break
    return entries


def extract_yaml_string_list(status_text: str, key: str) -> list[str]:
    entries: list[str] = []
    inside_yaml = False
    inside_list = False
    target_prefix = f'{key}:'

    for raw_line in status_text.splitlines():
        line = raw_line.strip()
        if line.startswith('```yaml'):
            inside_yaml = True
            inside_list = False
            continue
        if inside_yaml and line.startswith('```'):
            inside_yaml = False
            inside_list = False
            continue
        if not inside_yaml:
            continue
        if line == target_prefix:
            inside_list = True
            continue
        if inside_list:
            if raw_line.startswith('  - '):
                entries.append(normalize_claim_value(raw_line.split('-', 1)[1]))
                continue
            if line.startswith('#'):
                continue
            if line:
                break
    return entries


def normalize_claim_value(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        value = value[1:-1]
    return value.strip()


def parse_yaml_claim_occurrences(status_text: str) -> list[tuple[str, str]]:
    claims: list[tuple[str, str]] = []
    inside_block = False

    for raw_line in status_text.splitlines():
        line = raw_line.strip()
        if line.startswith('```yaml'):
            inside_block = True
            continue
        if inside_block and line.startswith('```'):
            inside_block = False
            continue
        if not inside_block or ':' not in line or line.startswith('-') or line.startswith('#'):
            continue
        key, value = line.split(':', 1)
        claims.append((key.strip(), normalize_claim_value(value)))
    return claims


def validate_status_text(status_text: str) -> None:
    merged_foundation = extract_merged_foundation(status_text)
    missing_foundation = sorted(REQUIRED_MERGED_FOUNDATION - merged_foundation)
    if missing_foundation:
        raise AssertionError('STATUS.md missing merged_foundation entries: ' + ', '.join(missing_foundation))

    claim_occurrences = parse_yaml_claim_occurrences(status_text)
    claim_set = set(claim_occurrences)

    missing_boundaries = []
    for key, expected in REQUIRED_BOUNDARIES.items():
        if (key, expected) not in claim_set:
            missing_boundaries.append(f'{key}: {expected}')
    if missing_boundaries:
        raise AssertionError('STATUS.md missing or incorrect boundary entries: ' + ', '.join(missing_boundaries))

    conflicting_boundaries = []
    for key, value in claim_occurrences:
        expected = REQUIRED_BOUNDARIES.get(key)
        if expected is not None and value != expected:
            conflicting_boundaries.append(f'{key}: {value} (expected {key}: {expected})')
    if conflicting_boundaries:
        raise AssertionError('STATUS.md contains conflicting boundary entries; expected only: ' + ', '.join(sorted(set(conflicting_boundaries))))

    present_forbidden_claims = []
    for key, value in claim_occurrences:
        if FORBIDDEN_CLAIMS.get(key) == value:
            present_forbidden_claims.append(f'{key}: {value}')
    if present_forbidden_claims:
        raise AssertionError('STATUS.md upgrades forbidden claims: ' + ', '.join(present_forbidden_claims))

    automatic_checks = extract_yaml_string_list(status_text, 'automatic_check')
    if automatic_checks != REQUIRED_AUTOMATIC_CHECKS:
        missing_checks = [check for check in REQUIRED_AUTOMATIC_CHECKS if check not in automatic_checks]
        extra_checks = [check for check in automatic_checks if check not in REQUIRED_AUTOMATIC_CHECKS]
        order_mismatch = not missing_checks and not extra_checks
        details = []
        if missing_checks:
            details.append('missing: ' + ', '.join(missing_checks))
        if extra_checks:
            details.append('extra: ' + ', '.join(extra_checks))
        if order_mismatch:
            details.append('order differs from Validate workflow')
        raise AssertionError('STATUS.md automatic_check must mirror the primary Validate chain; ' + '; '.join(details))


def self_test_status_text(
    extra_yaml_blocks: str = '',
    foundation_set: set[str] | None = None,
    automatic_checks: list[str] | None = None,
    automatic_check_comment: str = '',
) -> str:
    if foundation_set is None:
        foundation_set = REQUIRED_MERGED_FOUNDATION
    if automatic_checks is None:
        automatic_checks = REQUIRED_AUTOMATIC_CHECKS
    foundation_entries = '\n'.join(f'  - "{entry}"' for entry in sorted(foundation_set))
    automatic_check_entries = '\n'.join(f'  - {entry}' for entry in automatic_checks)
    return f'''# STATUS

```yaml
project: EV4 Responsive Architect
production_ready: false
prompt_pack_release_ready: false
foundation_checkpoint_policy: bounded checkpoints only; not append every merged PR
merged_foundation:
{foundation_entries}
pending_control_plane_pr: null
```

{extra_yaml_blocks}

```yaml
real_submitted_packet_present: false
pilot_allowed_to_start: false
readiness_claims_upgraded: false
ci_success_claim_boundary: repository checks only; not responsive correctness evidence
pilot_execution_scope: not_allowed
```

```yaml
automatic_workflow: .github/workflows/validate.yml
automatic_check:
{automatic_check_comment}{automatic_check_entries}
```
'''


def assert_status_invalid(status_text: str, expected_fragment: str) -> None:
    try:
        validate_status_text(status_text)
    except AssertionError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f'expected error fragment {expected_fragment!r}, got {exc!s}') from exc
        return
    raise AssertionError(f'expected STATUS text to fail with {expected_fragment!r}')


def run_self_tests() -> None:
    validate_status_text(self_test_status_text())
    assert_status_invalid(
        self_test_status_text(
            foundation_set=REQUIRED_MERGED_FOUNDATION - {'PR #112 RTAQ-0029 responsive intake decision guard'},
        ),
        'PR #112 RTAQ-0029 responsive intake decision guard',
    )
    validate_status_text(self_test_status_text('''```yaml
production_ready: "false"
pilot_allowed_to_start:   false
```'''))
    assert_status_invalid(self_test_status_text('''```yaml
production_ready: pending
```'''), 'production_ready: pending')
    assert_status_invalid(self_test_status_text('''```yaml
production_ready: true
```'''), 'production_ready: true')
    assert_status_invalid(
        self_test_status_text().replace(
            'foundation_checkpoint_policy: bounded checkpoints only; not append every merged PR',
            'foundation_checkpoint_policy: append every merged PR',
        ),
        'foundation_checkpoint_policy: bounded checkpoints only; not append every merged PR',
    )
    assert_status_invalid(self_test_status_text('''```yaml
pilot_allowed_to_start: true
```

```yaml
pilot_allowed_to_start: false
```'''), 'pilot_allowed_to_start: true')
    assert_status_invalid(self_test_status_text('''```yaml
pilot_allowed_to_start: "true"
```'''), 'pilot_allowed_to_start: true')
    assert_status_invalid(self_test_status_text('''```yaml
pilot_execution_scope: allowed
```

```yaml
pilot_execution_scope: not_allowed
```'''), 'pilot_execution_scope: allowed')
    validate_status_text(
        self_test_status_text(
            automatic_check_comment='  # comment between key and list must not truncate parsing\n',
        )
    )
    assert_status_invalid(
        self_test_status_text(
            automatic_checks=[check for check in REQUIRED_AUTOMATIC_CHECKS if 'run_task_quality_gate_check.py' not in check],
        ),
        'run_task_quality_gate_check.py',
    )
    assert_status_invalid(
        self_test_status_text(
            automatic_checks=list(reversed(REQUIRED_AUTOMATIC_CHECKS)),
        ),
        'order differs from Validate workflow',
    )


def main() -> int:
    run_self_tests()
    validate_status_text(STATUS.read_text(encoding='utf-8'))
    print('STATUS merged-foundation guard passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
