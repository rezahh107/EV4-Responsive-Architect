#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "STATUS.md"
GUARD = ROOT / "validation" / "e2e" / "run_status_merged_foundation_guard_check.py"

old_status = (
    "The snapshot below is derived from the canonical monolithic catalog and is validator-enforced. "
    "It explicitly supersedes the former `WP-RESP-009` through `WP-RESP-012` ready-horizon statement."
)
new_status = (
    "The snapshot below is derived from the canonical monolithic catalog, is validator-enforced, "
    "and supersedes earlier prose horizons."
)

status_text = STATUS.read_text(encoding="utf-8")
if status_text.count(old_status) != 1:
    raise SystemExit("PRF-005 STATUS preimage mismatch")
status_text = status_text.replace(old_status, new_status, 1)

guard_text = GUARD.read_text(encoding="utf-8")

old_extraction = '''    trailing = section[match.end():]
    for fenced in ANY_FENCE_RE.finditer(trailing):
        if CATALOG_BLOCK_MARKERS.search(fenced.group("body")):
            raise AssertionError(
                "STATUS.md catalog status section contains another machine-readable catalog-state block"
            )

    prose_only = ANY_FENCE_RE.sub("", trailing)
    if CONTRADICTORY_CATALOG_PROSE.search(prose_only):
        raise AssertionError("STATUS.md catalog status section contains contradictory catalog-state prose after snapshot")
    return payload
'''
new_extraction = '''    outside_snapshot = section[: match.start()] + section[match.end() :]
    for fenced in ANY_FENCE_RE.finditer(outside_snapshot):
        if CATALOG_BLOCK_MARKERS.search(fenced.group("body")):
            raise AssertionError(
                "STATUS.md catalog status section contains another machine-readable catalog-state block"
            )

    prose_only = ANY_FENCE_RE.sub("", outside_snapshot)
    if CONTRADICTORY_CATALOG_PROSE.search(prose_only):
        raise AssertionError(
            "STATUS.md catalog status section contains contradictory catalog-state prose outside canonical snapshot"
        )
    return payload
'''
if guard_text.count(old_extraction) != 1:
    raise SystemExit("PRF-005 extraction preimage mismatch")
guard_text = guard_text.replace(old_extraction, new_extraction, 1)

old_section_helper = '''def json_section(*payloads: dict[str, Any], trailing: str = "") -> str:
    fences = "\\n\\n".join(
        "```json\\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\\n```"
        for payload in payloads
    )
    return f"{STATUS_CATALOG_HEADING}\\n\\n{fences}\\n{trailing}"
'''
new_section_helper = '''def json_section(
    *payloads: dict[str, Any],
    leading: str = "",
    trailing: str = "",
) -> str:
    fences = "\\n\\n".join(
        "```json\\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\\n```"
        for payload in payloads
    )
    return f"{STATUS_CATALOG_HEADING}\\n\\n{leading}{fences}\\n{trailing}"
'''
if guard_text.count(old_section_helper) != 1:
    raise SystemExit("PRF-005 json_section preimage mismatch")
guard_text = guard_text.replace(old_section_helper, new_section_helper, 1)

anchor = '''    snapshot = expected_catalog_status_snapshot(catalog)
    assert_invalid(
        status_fixture(catalog, expected_checks, catalog_section=f"{STATUS_CATALOG_HEADING}\\n\\nNo snapshot.\\n"),
'''
insert = '''    snapshot = expected_catalog_status_snapshot(catalog)

    assert_invalid(
        status_fixture(
            catalog,
            expected_checks,
            catalog_section=json_section(
                snapshot,
                leading="Selectable ready horizon: `WP-RESP-009` through `WP-RESP-012`.\\n\\n",
            ),
        ),
        catalog,
        workflow_text,
        "contradictory catalog-state prose outside canonical snapshot",
    )
    assert_invalid(
        status_fixture(
            catalog,
            expected_checks,
            catalog_section=json_section(
                snapshot,
                leading=(
                    "```yaml\\n"
                    "selectable_ready_horizon:\\n"
                    "  - WP-RESP-009\\n"
                    "  - WP-RESP-010\\n"
                    "  - WP-RESP-011\\n"
                    "  - WP-RESP-012\\n"
                    "```\\n\\n"
                ),
            ),
        ),
        catalog,
        workflow_text,
        "another machine-readable catalog-state block",
    )
    assert_invalid(
        status_fixture(
            catalog,
            expected_checks,
            catalog_section=json_section(
                snapshot,
                leading="Active work packages: `WP-RESP-013`.\\n\\n",
            ),
        ),
        catalog,
        workflow_text,
        "contradictory catalog-state prose outside canonical snapshot",
    )
    assert_invalid(
        status_fixture(
            catalog,
            expected_checks,
            catalog_section=json_section(
                snapshot,
                leading="Completed work packages exclude `WP-RESP-012`.\\n\\n",
            ),
        ),
        catalog,
        workflow_text,
        "contradictory catalog-state prose outside canonical snapshot",
    )

    assert_invalid(
        status_fixture(catalog, expected_checks, catalog_section=f"{STATUS_CATALOG_HEADING}\\n\\nNo snapshot.\\n"),
'''
if guard_text.count(anchor) != 1:
    raise SystemExit("PRF-005 self-test insertion anchor mismatch")
guard_text = guard_text.replace(anchor, insert, 1)

STATUS.write_text(status_text, encoding="utf-8")
GUARD.write_text(guard_text, encoding="utf-8")
print("PRF-005 bounded STATUS/guard repair materialized")
