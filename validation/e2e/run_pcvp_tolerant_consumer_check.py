#!/usr/bin/env python3
"""Exercise dormant PCVP dual-read behavior at Builder → Responsive intake."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable

import jsonschema

from responsive_pcvp import inspect_optional_pcvp_carrier

ROOT = Path(__file__).resolve().parents[2]
INPUT_SCHEMA = ROOT / "schemas/ev4-builder-responsive-input.schema.json"
OUTPUT_SCHEMA = ROOT / "schemas/ev4-responsive-output.schema.json"
BASE_INPUT = (
    ROOT / "validation/fixtures/valid/builder_responsive_input.valid.json"
)
VALID_PCVP = (
    ROOT / "validation/fixtures/pcvp/valid/builder-to-responsive.valid.json"
)
INVALID_PCVP = (
    ROOT
    / "validation/fixtures/pcvp/invalid/revoked-authorization.invalid.json"
)
LOCK_PATH = ROOT / "contracts/pcvp/pcvp-v1.lock.json"
PROFILE_PATH = ROOT / "contracts/pcvp/responsive.profile.yaml"
VENDORED_ROOT = (
    ROOT / "contracts/pcvp/vendor/decision-kernel/v1.0.0"
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path.relative_to(ROOT)} must be an object")
    return value


def _payload() -> dict[str, Any]:
    value = _load(BASE_INPUT)
    value.pop("$schema_file", None)
    return value


def _codes(result: dict[str, Any]) -> set[str]:
    return {item["code"] for item in result["diagnostics"]}


def _assert_invalid(
    document: dict[str, Any],
    expected_code: str,
) -> None:
    result = inspect_optional_pcvp_carrier(document, ROOT)
    if result["status"] != "invalid" or expected_code not in _codes(result):
        raise AssertionError(
            f"{expected_code} not observed: "
            + json.dumps(result, ensure_ascii=False, indent=2)
        )


def main() -> int:
    input_schema = _load(INPUT_SCHEMA)
    output_schema = _load(OUTPUT_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(input_schema)
    input_validator = jsonschema.Draft202012Validator(input_schema)

    legacy = _payload()
    legacy_before = copy.deepcopy(legacy)
    input_validator.validate(legacy)
    legacy_result = inspect_optional_pcvp_carrier(legacy, ROOT)
    if legacy_result["status"] != "legacy_absent":
        raise AssertionError("legacy Builder intake must remain valid")
    if legacy != legacy_before:
        raise AssertionError("legacy PCVP inspection mutated input")

    valid_carrier_document = _load(VALID_PCVP)
    valid_carrier_before = copy.deepcopy(valid_carrier_document)
    valid_result = inspect_optional_pcvp_carrier(valid_carrier_document, ROOT)
    if valid_result["status"] != "validated":
        raise AssertionError(
            json.dumps(valid_result["diagnostics"], ensure_ascii=False, indent=2)
        )
    if valid_carrier_document != valid_carrier_before:
        raise AssertionError("valid PCVP inspection mutated source carrier")

    combined = _payload()
    combined["continuation_assurance"] = copy.deepcopy(
        valid_carrier_document["continuation_assurance"]
    )
    combined_before = copy.deepcopy(combined)
    input_validator.validate(combined)
    combined_result = inspect_optional_pcvp_carrier(combined, ROOT)
    if combined_result["status"] != "validated":
        raise AssertionError("schema-valid combined input did not validate")
    if combined != combined_before:
        raise AssertionError("combined input was mutated")
    for key, expected in {
        "adoption_status": "not_yet_adopted",
        "activation_effect": "NONE",
        "producer_emission": False,
        "runtime_authority": False,
        "responsive_correctness_proven": False,
    }.items():
        if combined_result.get(key) != expected:
            raise AssertionError(f"{key} must remain {expected!r}")

    _assert_invalid(
        _load(INVALID_PCVP),
        "RESPONSIVE_PCVP_EFFECT_AUTH_NOT_ACTIVE",
    )

    mutations: tuple[
        tuple[str, Callable[[dict[str, Any]], None]], ...
    ] = (
        (
            "RESPONSIVE_PCVP_CARRIER_SCHEMA_INVALID",
            lambda value: value.update(policy_version="2.0.0"),
        ),
        (
            "RESPONSIVE_PCVP_SOURCE_STAGE_MISMATCH",
            lambda value: value.update(source_stage="PROJECT_GATE"),
        ),
        (
            "RESPONSIVE_PCVP_EFFECT_AUTH_STAGE_SCOPE_MISMATCH",
            lambda value: value["authorizations"][0]["stage_scope"].update(
                through="PROJECT_GATE"
            ),
        ),
        (
            "RESPONSIVE_PCVP_EFFECT_CLAIM_REF_UNRESOLVED",
            lambda value: value["effects"][0].update(
                depends_on_claim_ids=["CLM-MISSING"]
            ),
        ),
        (
            "RESPONSIVE_PCVP_ID_NOT_GLOBALLY_UNIQUE",
            lambda value: value["claims"].append(
                {
                    **copy.deepcopy(value["claims"][0]),
                    "statement": "Distinct claim with a duplicate identifier.",
                }
            ),
        ),
        (
            "RESPONSIVE_PCVP_EFFECT_AUTH_NOT_COVERING",
            lambda value: value["authorizations"][0].update(
                allowed_effect_ids=[],
                allowed_effect_classes=["REASONING_ONLY"],
            ),
        ),
        (
            "RESPONSIVE_PCVP_RED_WITH_NON_BLOCKED_EFFECT",
            lambda value: value["stage_summary"].update(
                owner_projection="RED"
            ),
        ),
    )
    for expected_code, mutate in mutations:
        candidate = copy.deepcopy(valid_carrier_document)
        mutate(candidate["continuation_assurance"])
        _assert_invalid(candidate, expected_code)

    if "continuation_assurance" in output_schema.get("properties", {}):
        raise AssertionError(
            "Responsive producer emission must remain dormant in this work unit"
        )

    lock = _load(LOCK_PATH)
    if (
        lock["policy"]["adoption_status"] != "not_yet_adopted"
        or lock["policy"]["activation"] != "NONE"
    ):
        raise AssertionError("PCVP lock activated or claimed adoption")
    if hashlib.sha256(PROFILE_PATH.read_bytes()).hexdigest() != (
        lock["profile"]["sha256"]
    ):
        raise AssertionError("Responsive profile does not match lock")
    observed_schema_hashes = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(VENDORED_ROOT.glob("*.schema.json"))
    }
    expected_schema_hashes = {
        entry["name"]: entry["sha256"] for entry in lock["files"]
    }
    if observed_schema_hashes != expected_schema_hashes:
        raise AssertionError("Vendored canonical schemas do not match lock")

    print(
        json.dumps(
            {
                "result": "PASS",
                "legacy_absence_cases": 1,
                "valid_carrier_cases": 1,
                "invalid_carrier_cases": 1 + len(mutations),
                "compatibility_mode": "DUAL_READ",
                "adoption_status": "not_yet_adopted",
                "activation_effect": "NONE",
                "producer_emission": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        AssertionError,
        OSError,
        ValueError,
        TypeError,
        jsonschema.exceptions.SchemaError,
        jsonschema.exceptions.ValidationError,
    ) as exc:
        print(f"Responsive PCVP tolerant consumer check failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
