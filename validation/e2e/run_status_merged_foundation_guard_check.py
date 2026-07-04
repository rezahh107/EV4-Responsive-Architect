#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "STATUS.md"

# This list is a bounded foundation checkpoint, not a requirement to append every
# future merged PR. It prevents verified foundation drift while avoiding
# status-only merge-final loops.
REQUIRED_MERGED_FOUNDATION = {
    'PR #101 evidence intake fixture matrix hardening',
    'PR #102 pilot readiness boundary hardening',
    'PR #103 Issue 8 submitted-packet preflight guide',
    'PR #104 backlog boundary refresh after preflight guide',
    'PR #105 Issue 8 preflight boundary validation',
    'PR #106 RTAQ-0024 preflight boundary status reconciliation',
    'PR #107 RTAQ-0025 active STATUS guard validation',
    'PR #108 RTAQ-0026 STATUS foundation guard refresh',
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

        if not inside_block or ':' not in line or line.startswith('-'):
            continue

        key, value = line.split(':', 1)
        key = key.strip()
        value = normalize_claim_value(value)
        claims.append((key, value))

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
            conflicting_boundaries.append(
                f'{key}: {value} (expected {key}: {expected})'
            )
    if conflicting_boundaries:
        raise AssertionError(
            'STATUS.md contains conflicting boundary entries; expected only: '
            + ', '.join(sorted(set(conflicting_boundaries)))
        )

    present_forbidden_claims = []
    for key, value in claim_occurrences:
        if FORBIDDEN_CLAIMS.get(key) == value:
            present_forbidden_claims.append(f'{key}: {value}')
    if present_forbidden_claims:
        raise AssertionError('STATUS.md upgrades forbidden claims: ' + ', '.join(present_forbidden_claims))


def self_test_status_text(extra_yaml_blocks: str = '') -> str:
    foundation_entries = '\n'.join(
        f'  - "{entry}"'
        for entry in sorted(REQUIRED_MERGED_FOUNDATION)
    )
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

    validate_status_text(self_test_status_text('''```yaml
production_ready: "false"
pilot_allowed_to_start:   false
```'''))

    assert_status_invalid(
        self_test_status_text('''```yaml
production_ready: pending
```'''),
        'production_ready: pending',
    )

    assert_status_invalid(
        self_test_status_text('''```yaml
production_ready: true
```'''),
        'production_ready: true',
    )

    assert_status_invalid(
        self_test_status_text().replace(
            'foundation_checkpoint_policy: bounded checkpoints only; not append every merged PR',
            'foundation_checkpoint_policy: append every merged PR',
        ),
        'foundation_checkpoint_policy: bounded checkpoints only; not append every merged PR',
    )

    assert_status_invalid(
        self_test_status_text('''```yaml
pilot_allowed_to_start: true
```

```yaml
pilot_allowed_to_start: false
```'''),
        'pilot_allowed_to_start: true',
    )

    assert_status_invalid(
        self_test_status_text('''```yaml
pilot_allowed_to_start: "true"
```'''),
        'pilot_allowed_to_start: true',
    )

    assert_status_invalid(
        self_test_status_text('''```yaml
pilot_allowed_to_start:  true
```'''),
        'pilot_allowed_to_start: true',
    )

    assert_status_invalid(
        self_test_status_text('''```yaml
pilot_execution_scope: allowed
```

```yaml
pilot_execution_scope: not_allowed
```'''),
        'pilot_execution_scope: allowed',
    )


def main() -> int:
    run_self_tests()
    status_text = STATUS.read_text(encoding='utf-8')
    validate_status_text(status_text)
    print('STATUS merged-foundation guard passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
