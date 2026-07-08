#!/usr/bin/env python3
"""
Pretty-print EV4 Work Package Catalog without changing semantic content.

Run from the repository root:
    python scripts_local_pretty_print_catalog.py

Optional:
    python scripts_local_pretty_print_catalog.py planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json
"""

from __future__ import annotations

import json
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any


class DuplicateKeyError(ValueError):
    pass


def no_duplicate_object_pairs_hook(pairs: list[tuple[str, Any]]) -> OrderedDict[str, Any]:
    obj: OrderedDict[str, Any] = OrderedDict()
    for key, value in pairs:
        if key in obj:
            raise DuplicateKeyError(f"Duplicate JSON key found: {key!r}")
        obj[key] = value
    return obj


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json"
    )

    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        print("Run this from the repository root, or pass the file path explicitly.", file=sys.stderr)
        return 2

    original = path.read_text(encoding="utf-8")

    try:
        data = json.loads(original, object_pairs_hook=no_duplicate_object_pairs_hook)
    except DuplicateKeyError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}", file=sys.stderr)
        return 4

    formatted = json.dumps(data, indent=2, ensure_ascii=False) + "\n"

    if original == formatted:
        print("OK: catalog is already canonical pretty-printed JSON.")
        return 0

    backup = path.with_suffix(path.suffix + ".before-pretty-print")
    backup.write_text(original, encoding="utf-8")
    path.write_text(formatted, encoding="utf-8")

    print(f"Updated: {path}")
    print(f"Backup:  {backup}")
    print("Next: inspect git diff, then run repository validators.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
