#!/usr/bin/env python3
"""Validate Decision Escape Routes state and Wave 4 carrier strictness."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "planning" / "DECISION_ESCAPE_ROUTES.yml"
SCHEMA = ROOT / "planning" / "decision-escape-routes.schema.json"
SEQUENCE_CARRIER_FIELDS = (
    "sequence_CI_step",
    "test_command",
    "positive_fixture",
    "negative_fixture",
    "validator_rule",
    "validator_diagnostic",
)


def load_yaml_via_ruby(path: Path) -> dict[str, object]:
    result = subprocess.run(
        ["ruby", "-rjson", "-ryaml", "-e", "puts JSON.generate(YAML.load_file(ARGV[0]))", str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Ruby YAML parse failed for {path.relative_to(ROOT)}: {result.stderr.strip()}")
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must parse to an object")
    return payload


def assert_null_sequence_carriers_rejected(state: dict[str, object], validator: Draft202012Validator) -> None:
    records = state.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("DECISION_ESCAPE_ROUTES.yml must contain at least one Wave 4 record")
    for field in SEQUENCE_CARRIER_FIELDS:
        mutated = copy.deepcopy(state)
        mutated["records"][0]["carriers"][field] = None
        try:
            validator.validate(mutated)
        except ValidationError:
            continue
        raise ValueError(f"sequence_ci_enforced record accepted null carrier: {field}")
    for field in SEQUENCE_CARRIER_FIELDS:
        mutated = copy.deepcopy(state)
        mutated["records"][0]["carriers"][field] = ""
        try:
            validator.validate(mutated)
        except ValidationError:
            continue
        raise ValueError(f"sequence_ci_enforced record accepted empty carrier: {field}")


def main() -> int:
    try:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        state = load_yaml_via_ruby(STATE)
        validator.validate(state)
        assert_null_sequence_carriers_rejected(state, validator)
    except (OSError, json.JSONDecodeError, RuntimeError, ValueError, ValidationError) as exc:
        print(f"Decision escape routes schema check failed: {exc}", file=sys.stderr)
        return 1
    print("Decision escape routes schema check passed: state validates and sequence_ci_enforced carriers are non-empty")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
