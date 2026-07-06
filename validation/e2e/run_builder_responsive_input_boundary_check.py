#!/usr/bin/env python3
"""Validate the Builder to Responsive input boundary schema and fixtures."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "ev4-builder-responsive-input.schema.json"
VALID_FIXTURES = (ROOT / "validation" / "fixtures" / "valid" / "builder_responsive_input.valid.json",)
INVALID_DIR = ROOT / "validation" / "fixtures" / "invalid"
INVALID_FIXTURE_GLOB = "builder_responsive_input_*.invalid.json"
REQUIRED_FORBIDDEN_CLAIMS = {
    "production_ready",
    "release_ready",
    "pixel_perfect",
    "live_render_validated",
    "export_json_validated",
    "accessibility_passed",
    "responsive_correctness_validated",
    "ci_success_as_frontend_evidence",
}
CANONICAL_BOUNDARY = "input eligibility only; not responsive correctness evidence"
SHA256_DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
DENIED_INTAKE_REASON_MARKERS = (
    "malformed project gate digest",
    "mobile evidence is missing",
    "claim list is incomplete",
    "not provided",
    "non-verified project gate",
    "must not allow responsive intake",
)


def _load_json(path: Path) -> object:
    if not path.exists():
        raise AssertionError(f"missing required fixture or schema: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def _decision(data: dict[str, object], path: Path) -> dict[str, object]:
    decision = data.get("responsive_intake_decision")
    if not isinstance(decision, dict):
        raise AssertionError(f"{path.relative_to(ROOT)} missing responsive_intake_decision object")
    if decision.get("claim_boundary") != CANONICAL_BOUNDARY:
        raise AssertionError(f"{path.relative_to(ROOT)} has non-canonical claim boundary")
    return decision


def _assert_forbidden_claims(data: dict[str, object], path: Path) -> None:
    claims = data.get("forbidden_claims")
    if not isinstance(claims, list):
        raise AssertionError(f"{path.relative_to(ROOT)} missing forbidden_claims list")
    if len(claims) != len(set(claims)):
        raise AssertionError(f"{path.relative_to(ROOT)} contains duplicate forbidden claims")
    if set(claims) != REQUIRED_FORBIDDEN_CLAIMS:
        missing = REQUIRED_FORBIDDEN_CLAIMS.difference(claims)
        extra = set(claims).difference(REQUIRED_FORBIDDEN_CLAIMS)
        raise AssertionError(
            f"{path.relative_to(ROOT)} forbidden claims mismatch. Missing: {sorted(missing)}, Extra: {sorted(extra)}"
        )


def _has_malformed_digest(data: dict[str, object]) -> bool:
    digests = []
    project_gate = data.get("project_gate_ref")
    builder_output = data.get("builder_output_ref")
    if isinstance(project_gate, dict):
        digests.append(project_gate.get("gate_hash"))
    if isinstance(builder_output, dict):
        digests.append(builder_output.get("artifact_hash"))
    return any(isinstance(digest, str) and not SHA256_DIGEST_PATTERN.fullmatch(digest) for digest in digests)


def _reason_requires_denied_intake(reason: object) -> bool:
    if not isinstance(reason, str):
        return False
    normalized = " ".join(reason.lower().split())
    return any(marker in normalized for marker in DENIED_INTAKE_REASON_MARKERS)


def _assert_valid_fixture(data: dict[str, object], path: Path) -> None:
    decision = _decision(data, path)

    is_allowed_intake = decision.get("intake_allowed") is True
    if path.name == "builder_responsive_input.valid.json" and not is_allowed_intake:
        raise AssertionError(f"{path.relative_to(ROOT)} must exercise allowed intake")

    if is_allowed_intake:
        project_gate = data.get("project_gate_ref")
        if not isinstance(project_gate, dict) or project_gate.get("gate_status") != "verified":
            raise AssertionError(f"{path.relative_to(ROOT)} allowed intake must use a verified project gate")

        viewport_evidence = data.get("viewport_evidence")
        if not isinstance(viewport_evidence, dict):
            raise AssertionError(f"{path.relative_to(ROOT)} missing viewport_evidence object")
        for viewport in ("desktop", "tablet", "mobile"):
            evidence = viewport_evidence.get(viewport)
            if not isinstance(evidence, dict) or evidence.get("evidence_status") != "provided":
                raise AssertionError(f"{path.relative_to(ROOT)} allowed intake must provide {viewport} evidence")

    _assert_forbidden_claims(data, path)


def _assert_invalid_fixture_semantics(data: dict[str, object], path: Path) -> None:
    decision = _decision(data, path)
    intake_allowed = decision.get("intake_allowed")
    reason = decision.get("reason")

    if path.name == "builder_responsive_input_malformed_hash.invalid.json" and intake_allowed is not False:
        raise AssertionError(f"{path.relative_to(ROOT)} malformed-hash fixture must keep intake_allowed=false")

    if _has_malformed_digest(data) and intake_allowed is True:
        raise AssertionError(f"{path.relative_to(ROOT)} malformed digest cannot use intake_allowed=true")

    if _reason_requires_denied_intake(reason) and intake_allowed is True:
        raise AssertionError(f"{path.relative_to(ROOT)} denied-intake reason contradicts intake_allowed=true")


def main() -> int:
    try:
        schema = _load_json(SCHEMA_PATH)
        jsonschema.Draft202012Validator.check_schema(schema)
        validator = jsonschema.Draft202012Validator(schema)

        for fixture in VALID_FIXTURES:
            data = _load_json(fixture)
            validator.validate(data)
            if not isinstance(data, dict):
                raise AssertionError(f"{fixture.relative_to(ROOT)} must be a JSON object")
            _assert_valid_fixture(data, fixture)

        invalid_fixtures = tuple(sorted(INVALID_DIR.glob(INVALID_FIXTURE_GLOB)))
        if not invalid_fixtures:
            raise AssertionError("missing Builder to Responsive invalid fixture coverage")
        for fixture in invalid_fixtures:
            data = _load_json(fixture)
            if not isinstance(data, dict):
                raise AssertionError(f"{fixture.relative_to(ROOT)} must be a JSON object")
            _assert_invalid_fixture_semantics(data, fixture)
            try:
                validator.validate(data)
            except jsonschema.exceptions.ValidationError:
                continue
            raise AssertionError(f"invalid fixture unexpectedly passed schema validation: {fixture.relative_to(ROOT)}")
    except (AssertionError, OSError, json.JSONDecodeError, jsonschema.exceptions.SchemaError, jsonschema.exceptions.ValidationError) as exc:
        print(f"Builder responsive input boundary check failed: {exc}", file=sys.stderr)
        return 1

    print("Builder responsive input boundary check passed: intake eligibility is schema-bound and evidence-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
