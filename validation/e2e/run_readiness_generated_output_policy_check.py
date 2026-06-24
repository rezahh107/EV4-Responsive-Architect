#!/usr/bin/env python3
"""Check readiness generated-output policy.

Generated pilot readiness reports are runtime validation products. They must not
be committed under the repository as .generated.json evidence. Validators may
write explicit temporary outputs outside the repository, such as /tmp paths.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ALLOWED_GENERATED_DIRS = {
    ROOT / "validation" / "fixtures" / "valid",
    ROOT / "validation" / "fixtures" / "invalid",
}

FORBIDDEN_RUNTIME_PATTERNS = [
    "**/*.generated.json",
]


def is_allowed_fixture(path: Path) -> bool:
    resolved = path.resolve()
    return any(resolved.is_relative_to(directory.resolve()) for directory in ALLOWED_GENERATED_DIRS)


def assert_no_committed_runtime_generated_reports() -> None:
    offenders: list[str] = []
    for pattern in FORBIDDEN_RUNTIME_PATTERNS:
        for path in ROOT.glob(pattern):
            if path.is_file() and not is_allowed_fixture(path):
                offenders.append(str(path.relative_to(ROOT)))
    if offenders:
        joined = "\n  - ".join(offenders)
        raise AssertionError(
            "Committed runtime generated readiness/report outputs are forbidden:\n"
            f"  - {joined}\n"
            "Write generated reports to explicit temporary paths such as /tmp instead."
        )


def assert_output_path_policy() -> None:
    repo_generated = ROOT / "examples" / "smart-home-connector" / "readiness" / "PILOT_READINESS_REPORT.generated.json"
    tmp_generated = Path("/tmp/PILOT_READINESS_REPORT.generated.json")

    if not repo_generated.resolve().is_relative_to(ROOT.resolve()):
        raise AssertionError("repository generated-output probe must resolve inside the repo")
    if tmp_generated.resolve().is_relative_to(ROOT.resolve()):
        raise AssertionError("temporary generated-output probe must resolve outside the repo")


def main() -> int:
    try:
        assert_no_committed_runtime_generated_reports()
        assert_output_path_policy()
    except AssertionError as exc:
        print(f"Readiness generated-output policy check failed: {exc}", file=sys.stderr)
        return 1
    print("Readiness generated-output policy check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
