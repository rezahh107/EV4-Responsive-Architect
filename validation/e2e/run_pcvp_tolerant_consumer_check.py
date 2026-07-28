#!/usr/bin/env python3
"""Exercise dormant EV4-PCVP dual-read behavior at Builder -> Responsive intake."""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

import jsonschema

from responsive_pcvp import (
    CROSS_RECORD,
    JSON_SCHEMA,
    RESPONSIVE_INTEGRATION,
    SEMANTIC_POLICY,
    inspect_optional_pcvp_carrier,
)

ROOT = Path(__file__).resolve().parents[2]
INPUT_SCHEMA = ROOT / "schemas" / "ev4-builder-responsive-input.schema.json"
OUTPUT_SCHEMA = ROOT / "schemas" / "ev4-responsive-output.schema.json"
BASE_INPUT = ROOT / "validation" / "fixtures" / "valid" / "builder_responsive_input.valid.json"
VALID_PCVP = ROOT / "validation" / "fixtures" / "pcvp" / "valid" / "builder-to-responsive.valid.json"
REVOKED_PCVP = ROOT / "validation" / "fixtures" / "pcvp" / "invalid" / "revoked-authorization.invalid.json"
LOCK_PATH = ROOT / "contracts" / "pcvp" / "pcvp-v1.lock.json"
PROFILE_PATH = ROOT / "contracts" / "pcvp" / "responsive.profile.yaml"
VENDORED_ROOT = ROOT / "contracts" / "pcvp" / "vendor" / "decision-kernel" / "v1.0.0"

EXPECTED_COMMON_FACTS = {
    "compatibility_mode": "DUAL_READ",
    "adoption_status": "not_yet_adopted",
    "activation_effect": "NONE",
    "producer_emission_enabled": False,
    "runtime_authority_created": False,
    "responsive_authority_created": False,
    "responsive_correctness_proven": False,
    "project_gate_pass_created": False,
    "production_ready": False,
}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path.relative_to(ROOT)} must be an object")
    return value


def _payload() -> dict[str, Any]:
    value = _load(BASE_INPUT)
    value.pop("$schema_file", None)
    return value


def _codes_by_layer(result: dict[str, Any]) -> set[tuple[str, str]]:
    return {(item["layer"], item["code"]) for item in result["diagnostics"]}


def _assert_common_facts(result: dict[str, Any]) -> None:
    for key, expected in EXPECTED_COMMON_FACTS.items():
        if result.get(key) != expected:
            raise AssertionError(f"{key} must remain {expected!r}; got {result.get(key)!r}")


def _assert_invalid(
    document: dict[str, Any],
    expected_layer: str,
    expected_code: str,
    *,
    repository_root: Path = ROOT,
) -> None:
    result = inspect_optional_pcvp_carrier(document, repository_root)
    if result["status"] != "invalid":
        raise AssertionError(f"expected invalid result for {expected_code}: {result}")
    observed = _codes_by_layer(result)
    if (expected_layer, expected_code) not in observed:
        raise AssertionError(
            f"{expected_layer}/{expected_code} not observed: "
            + json.dumps(result, ensure_ascii=False, indent=2)
        )
    _assert_common_facts(result)


def _mutated_valid(
    mutate: Callable[[dict[str, Any]], None],
) -> dict[str, Any]:
    candidate = _load(VALID_PCVP)
    mutate(candidate["continuation_assurance"])
    return candidate


def _pcvp_sandbox() -> tempfile.TemporaryDirectory[str]:
    temp = tempfile.TemporaryDirectory(prefix="responsive-pcvp-")
    root = Path(temp.name)
    source = ROOT / "contracts" / "pcvp"
    destination = root / "contracts" / "pcvp"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    return temp


def _assert_local_pin_drift_fail_closed(valid_document: dict[str, Any]) -> None:
    with _pcvp_sandbox() as temp_path:
        root = Path(temp_path)
        profile = root / "contracts" / "pcvp" / "responsive.profile.yaml"
        profile.write_text(profile.read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")
        _assert_invalid(
            valid_document,
            RESPONSIVE_INTEGRATION,
            "RESPONSIVE_PCVP_PROFILE_HASH_MISMATCH",
            repository_root=root,
        )

    with _pcvp_sandbox() as temp_path:
        root = Path(temp_path)
        schema = (
            root
            / "contracts"
            / "pcvp"
            / "vendor"
            / "decision-kernel"
            / "v1.0.0"
            / "claim.schema.json"
        )
        schema.write_text(schema.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        _assert_invalid(
            valid_document,
            RESPONSIVE_INTEGRATION,
            "RESPONSIVE_PCVP_SCHEMA_HASH_MISMATCH",
            repository_root=root,
        )


def _assert_lossless_and_legacy() -> None:
    input_schema = _load(INPUT_SCHEMA)
    output_schema = _load(OUTPUT_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(input_schema)
    input_validator = jsonschema.Draft202012Validator(input_schema)

    legacy = _payload()
    legacy_before = copy.deepcopy(legacy)
    input_validator.validate(legacy)
    # Absent PCVP must not need a Kernel checkout, lock, profile, or vendored schema.
    legacy_result = inspect_optional_pcvp_carrier(
        legacy,
        ROOT / "validation" / "fixtures" / "__pcvp_dependency_must_not_exist__",
    )
    if legacy_result["status"] != "legacy_absent":
        raise AssertionError("legacy Builder intake must remain valid")
    if legacy != legacy_before:
        raise AssertionError("legacy PCVP inspection mutated input")
    _assert_common_facts(legacy_result)

    valid_document = _load(VALID_PCVP)
    valid_before = copy.deepcopy(valid_document)
    valid_result = inspect_optional_pcvp_carrier(valid_document, ROOT)
    if valid_result["status"] != "validated":
        raise AssertionError(json.dumps(valid_result["diagnostics"], indent=2))
    if valid_document != valid_before:
        raise AssertionError("valid PCVP inspection mutated source carrier")
    if valid_result["carrier"] != valid_before:
        raise AssertionError("validated carrier was not preserved losslessly")
    _assert_common_facts(valid_result)

    combined = _payload()
    combined["continuation_assurance"] = copy.deepcopy(
        valid_document["continuation_assurance"]
    )
    combined_before = copy.deepcopy(combined)
    input_validator.validate(combined)
    combined_result = inspect_optional_pcvp_carrier(combined, ROOT)
    if combined_result["status"] != "validated":
        raise AssertionError("schema-valid combined input did not validate")
    if combined != combined_before:
        raise AssertionError("combined Builder input was mutated")
    if combined_result["carrier"]["continuation_assurance"] != combined["continuation_assurance"]:
        raise AssertionError("combined carrier was not retained losslessly")
    _assert_common_facts(combined_result)

    if "continuation_assurance" in output_schema.get("properties", {}):
        raise AssertionError("Responsive output must not emit continuation_assurance")


def _assert_negative_matrix() -> int:
    cases: list[tuple[str, str, dict[str, Any]]] = []

    cases.append((
        JSON_SCHEMA,
        "PCVP_SCHEMA_REQUIRED",
        _mutated_valid(lambda c: c.pop("policy_id")),
    ))
    cases.append((
        JSON_SCHEMA,
        "PCVP_SCHEMA_CONST",
        _mutated_valid(lambda c: c.update(policy_version="2.0.0")),
    ))
    cases.append((
        RESPONSIVE_INTEGRATION,
        "RESPONSIVE_PCVP_SOURCE_STAGE_MISMATCH",
        _mutated_valid(lambda c: c.update(source_stage="PROJECT_GATE")),
    ))
    cases.append((
        RESPONSIVE_INTEGRATION,
        "RESPONSIVE_PCVP_AUTH_STAGE_SCOPE_MISMATCH",
        _mutated_valid(lambda c: c["authorizations"][0]["stage_scope"].update(through="PROJECT_GATE")),
    ))

    def duplicate_global_id(carrier: dict[str, Any]) -> None:
        duplicate = copy.deepcopy(carrier["claims"][0])
        duplicate["statement"] = "Distinct claim body sharing the same global identifier."
        carrier["claims"].append(duplicate)

    cases.append((CROSS_RECORD, "PCVP_ID_NOT_GLOBALLY_UNIQUE", _mutated_valid(duplicate_global_id)))
    cases.append((
        CROSS_RECORD,
        "PCVP_CLAIM_DEPENDENCY_UNRESOLVED",
        _mutated_valid(lambda c: c["claims"][0].update(dependency_refs=["CLM-MISSING"])),
    ))
    cases.append((
        CROSS_RECORD,
        "PCVP_EFFECT_CLAIM_REF_UNRESOLVED",
        _mutated_valid(lambda c: c["effects"][0].update(depends_on_claim_ids=["CLM-MISSING"])),
    ))
    cases.append((
        CROSS_RECORD,
        "PCVP_SUMMARY_EFFECT_REF_UNRESOLVED",
        _mutated_valid(lambda c: c["stage_summary"].update(current_effect_id="EFF-MISSING")),
    ))
    cases.append((
        CROSS_RECORD,
        "PCVP_EFFECT_AUTH_REF_UNRESOLVED",
        _mutated_valid(lambda c: c["effects"][0].update(authorization_ref="AUTH-MISSING")),
    ))
    cases.append((CROSS_RECORD, "PCVP_EFFECT_AUTH_NOT_ACTIVE", _load(REVOKED_PCVP)))

    def non_covering(carrier: dict[str, Any]) -> None:
        carrier["authorizations"][0]["allowed_effect_ids"] = []
        carrier["authorizations"][0]["allowed_effect_classes"] = ["REASONING_ONLY"]

    cases.append((CROSS_RECORD, "PCVP_EFFECT_AUTH_NOT_COVERING", _mutated_valid(non_covering)))
    cases.append((
        CROSS_RECORD,
        "PCVP_EFFECT_AUTH_SCOPE_MISMATCH",
        _mutated_valid(lambda c: c["authorizations"][0].update(permitted_scope="different scope")),
    ))

    def unsafe_default(carrier: dict[str, Any]) -> None:
        carrier["effects"][0]["effect_class"] = "EXTERNAL_MUTATION"
        carrier["authorizations"][0]["basis"] = "SAFE_REVERSIBLE_DEFAULT"
        carrier["authorizations"][0]["allowed_effect_classes"] = ["EXTERNAL_MUTATION"]

    cases.append((SEMANTIC_POLICY, "PCVP_SAFE_DEFAULT_FORBIDDEN_EFFECT", _mutated_valid(unsafe_default)))
    cases.append((
        SEMANTIC_POLICY,
        "PCVP_CONTRADICTED_CRITICAL_EFFECT_NOT_BLOCKED",
        _mutated_valid(lambda c: c["claims"][0].update(verification_state="CONTRADICTED")),
    ))
    cases.append((
        SEMANTIC_POLICY,
        "PCVP_RED_WITH_NON_BLOCKED_EFFECT",
        _mutated_valid(lambda c: c["stage_summary"].update(owner_projection="RED")),
    ))

    def dependency_projection_drift(carrier: dict[str, Any]) -> None:
        carrier["claims"].append({
            "claim_id": "CLM-BUILDER-002",
            "statement": "A material dependency remains applicability-undetermined.",
            "criticality": "MATERIAL",
            "applicability_state": "UNDETERMINED",
            "verification_state": "UNVERIFIED",
            "lifecycle_state": "ACTIVE",
            "evidence_refs": [],
            "dependency_refs": [],
            "assumption_refs": [],
        })
        carrier["effects"][0]["depends_on_claim_ids"].append("CLM-BUILDER-002")
        carrier["stage_summary"]["derived_from_claim_ids"].append("CLM-BUILDER-002")

    cases.append((SEMANTIC_POLICY, "PCVP_GREEN_PROJECTION_INVALID", _mutated_valid(dependency_projection_drift)))

    authority_statements = (
        "Responsive correctness validated and proven.",
        "Project Gate PASS verified.",
        "Production readiness ready and validated.",
    )
    for statement in authority_statements:
        cases.append((
            RESPONSIVE_INTEGRATION,
            "RESPONSIVE_PCVP_FORBIDDEN_AUTHORITY_CLAIM",
            _mutated_valid(lambda c, statement=statement: c["claims"][0].update(statement=statement)),
        ))

    for layer, code, document in cases:
        _assert_invalid(document, layer, code)
    return len(cases)


def _assert_lock_integrity() -> None:
    lock = _load(LOCK_PATH)
    if (
        lock["policy"]["adoption_status"] != "not_yet_adopted"
        or lock["policy"]["activation"] != "NONE"
    ):
        raise AssertionError("PCVP lock activated or claimed adoption")
    if hashlib.sha256(PROFILE_PATH.read_bytes()).hexdigest() != lock["profile"]["sha256"]:
        raise AssertionError("Responsive profile does not match immutable lock")
    observed = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(VENDORED_ROOT.glob("*.schema.json"))
    }
    expected = {entry["name"]: entry["sha256"] for entry in lock["files"]}
    if observed != expected:
        raise AssertionError("Vendored canonical schemas do not match immutable lock")


def main() -> int:
    _assert_lossless_and_legacy()
    valid_document = _load(VALID_PCVP)
    _assert_local_pin_drift_fail_closed(valid_document)
    negative_cases = _assert_negative_matrix()
    _assert_lock_integrity()
    print(json.dumps({
        "result": "PASS",
        "legacy_absence_cases": 1,
        "valid_carrier_cases": 1,
        "negative_cases": negative_cases + 2,
        "compatibility_mode": "DUAL_READ",
        "adoption_status": "not_yet_adopted",
        "activation_effect": "NONE",
        "producer_emission_enabled": False,
    }, indent=2))
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
