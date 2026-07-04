#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "STATUS.md"

REQUIRED_MERGED_FOUNDATION = {
    'PR #101 evidence intake fixture matrix hardening',
    'PR #102 pilot readiness boundary hardening',
    'PR #103 Issue 8 submitted-packet preflight guide',
    'PR #104 backlog boundary refresh after preflight guide',
    'PR #105 Issue 8 preflight boundary validation',
    'PR #106 RTAQ-0024 preflight boundary status reconciliation',
}

REQUIRED_BOUNDARIES = [
    'production_ready: false',
    'prompt_pack_release_ready: false',
    'real_submitted_packet_present: false',
    'pilot_allowed_to_start: false',
    'readiness_claims_upgraded: false',
    'ci_success_claim_boundary: repository checks only; not responsive correctness evidence',
    'pilot_execution_scope: not_allowed',
]

FORBIDDEN_CLAIMS = [
    'production_ready: true',
    'prompt_pack_release_ready: true',
    'real_submitted_packet_present: true',
    'pilot_allowed_to_start: true',
    'readiness_claims_upgraded: true',
    'pilot_execution_scope: allowed',
]


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


def main() -> int:
    status_text = STATUS.read_text(encoding='utf-8')
    merged_foundation = extract_merged_foundation(status_text)

    missing_foundation = sorted(REQUIRED_MERGED_FOUNDATION - merged_foundation)
    if missing_foundation:
        raise AssertionError('STATUS.md missing merged_foundation entries: ' + ', '.join(missing_foundation))

    missing_boundaries = [item for item in REQUIRED_BOUNDARIES if item not in status_text]
    if missing_boundaries:
        raise AssertionError('STATUS.md missing boundary entries: ' + ', '.join(missing_boundaries))

    present_forbidden_claims = [item for item in FORBIDDEN_CLAIMS if item in status_text]
    if present_forbidden_claims:
        raise AssertionError('STATUS.md upgrades forbidden claims: ' + ', '.join(present_forbidden_claims))

    print('STATUS merged-foundation guard passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
