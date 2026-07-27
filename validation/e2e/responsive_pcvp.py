"""Pinned, dormant EV4-PCVP reader for the Builder → Responsive boundary."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

POLICY_ID = "EV4-PCVP"
POLICY_VERSION = "1.0.0"
ARCHITECTURE_LOCK_ID = "EV4-PCVP-ROLL-LOCK-20260727-R1"
CANONICAL_REPOSITORY = "rezahh107/EV4-Decision-Kernel"
CANONICAL_COMMIT = "069a50fa243b01fa578a7c1bcb8864d9e796d34b"
LOCK_PATH = Path("contracts/pcvp/pcvp-v1.lock.json")
PROFILE_PATH = Path("contracts/pcvp/responsive.profile.yaml")
VENDORED_ROOT = Path("contracts/pcvp/vendor/decision-kernel/v1.0.0")
PROFILE_SHA256 = "92a316af37a3f85afe3ca917e62b2a4017fb9dfaa7190370e7a6529e554ced1e"
EXPECTED_SOURCE_STAGE = "BUILDER_ASSISTANT"
EXPECTED_CONSUMER_STAGE = "RESPONSIVE_ARCHITECT"
SCHEMA_HASHES = {
    "authorization.schema.json": "8eba853834bc3881ae836857a5bef3d8cc8e7c9edecd535ba22fb58a26fa5ff9",
    "claim.schema.json": "7d4c686b983330c454d76ebc34ef97ca4c595dd77b221de194e6a75e41859a72",
    "effect.schema.json": "59c201b7277f3bf3488eb43afbd04f686efae25b9a143c73f97aca5f65a1bbeb",
    "handoff.schema.json": "dcc3189ef4662b27e440aee3d3c698d503e265f81fb71d5d1904972cfe8728da",
}


def _diagnostic(code: str, message: str, path: str = "$") -> dict[str, str]:
    return {"code": code, "severity": "error", "message": message, "path": path}


def _projection(status: str, **extra: Any) -> dict[str, Any]:
    result = {
        "status": status,
        "compatibility_mode": "DUAL_READ",
        "canonical_owner": CANONICAL_REPOSITORY,
        "canonical_commit": CANONICAL_COMMIT,
        "architecture_lock_id": ARCHITECTURE_LOCK_ID,
        "adoption_status": "not_yet_adopted",
        "activation_effect": "NONE",
        "producer_emission": False,
        "runtime_authority": False,
        "responsive_correctness_proven": False,
    }
    result.update(extra)
    return result


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_path(parts: list[Any]) -> str:
    result = "$"
    for part in parts:
        result += f"[{part}]" if isinstance(part, int) else f".{part}"
    return result


def _load_pinned_schemas(
    root: Path,
) -> tuple[dict[str, dict[str, Any]] | None, list[dict[str, str]]]:
    diagnostics: list[dict[str, str]] = []
    try:
        lock = _load_json(root / LOCK_PATH)
    except (OSError, ValueError, TypeError) as exc:
        return None, [
            _diagnostic(
                "RESPONSIVE_PCVP_LOCK_UNAVAILABLE",
                f"Pinned contract lock could not be loaded ({type(exc).__name__}).",
                "$.continuation_assurance",
            )
        ]

    if not isinstance(lock, dict):
        return None, [
            _diagnostic(
                "RESPONSIVE_PCVP_LOCK_INVALID",
                "Pinned contract lock must be an object.",
                "$.continuation_assurance",
            )
        ]

    if (
        lock.get("schema_version") != "ev4-pcvp-contract-lock.v1"
        or lock.get("architecture_lock_id") != ARCHITECTURE_LOCK_ID
    ):
        diagnostics.append(
            _diagnostic(
                "RESPONSIVE_PCVP_LOCK_IDENTITY_MISMATCH",
                "Contract lock identity drifted.",
                "$.architecture_lock_id",
            )
        )

    expected_policy = {
        "id": POLICY_ID,
        "version": POLICY_VERSION,
        "adoption_status": "not_yet_adopted",
        "activation": "NONE",
    }
    if lock.get("policy") != expected_policy:
        diagnostics.append(
            _diagnostic(
                "RESPONSIVE_PCVP_LOCK_IDENTITY_MISMATCH",
                "Policy identity or dormant state drifted.",
                "$.policy",
            )
        )

    canonical = lock.get("canonical")
    if not isinstance(canonical, dict) or (
        canonical.get("repository") != CANONICAL_REPOSITORY
        or canonical.get("commit_sha") != CANONICAL_COMMIT
    ):
        diagnostics.append(
            _diagnostic(
                "RESPONSIVE_PCVP_LOCK_IDENTITY_MISMATCH",
                "Canonical owner or immutable commit drifted.",
                "$.canonical",
            )
        )

    expected_profile = {
        "profile_id": "EV4-PCVP-PROFILE-RESPONSIVE",
        "profile_version": "1.0.0",
        "repository": "rezahh107/EV4-Responsive-Architect",
        "stage_id": EXPECTED_CONSUMER_STAGE,
        "consumes_from": [
            "ARCHITECT",
            "CONSTRUCTABILITY_ENGINEER",
            EXPECTED_SOURCE_STAGE,
        ],
        "path": PROFILE_PATH.as_posix(),
        "sha256": PROFILE_SHA256,
        "local_copy_authoritative": False,
    }
    if lock.get("profile") != expected_profile:
        diagnostics.append(
            _diagnostic(
                "RESPONSIVE_PCVP_PROFILE_IDENTITY_MISMATCH",
                "Responsive profile identity drifted.",
                "$.profile",
            )
        )
    try:
        profile_hash = hashlib.sha256((root / PROFILE_PATH).read_bytes()).hexdigest()
    except OSError as exc:
        diagnostics.append(
            _diagnostic(
                "RESPONSIVE_PCVP_PROFILE_UNAVAILABLE",
                f"Responsive profile could not be loaded ({type(exc).__name__}).",
                "$.profile.path",
            )
        )
    else:
        if profile_hash != PROFILE_SHA256:
            diagnostics.append(
                _diagnostic(
                    "RESPONSIVE_PCVP_PROFILE_HASH_MISMATCH",
                    "Responsive profile bytes differ from the immutable lock.",
                    "$.profile.sha256",
                )
            )

    vendored = lock.get("vendored")
    verification = lock.get("verification")
    if not isinstance(vendored, dict) or (
        vendored.get("root") != VENDORED_ROOT.as_posix()
        or vendored.get("local_copy_authoritative") is not False
    ):
        diagnostics.append(
            _diagnostic(
                "RESPONSIVE_PCVP_LOCK_IDENTITY_MISMATCH",
                "Vendored schemas must remain non-authoritative.",
                "$.vendored",
            )
        )
    if not isinstance(verification, dict) or (
        verification.get("byte_equality_required") is not True
        or verification.get("compare_against_moving_default_branch") is not False
    ):
        diagnostics.append(
            _diagnostic(
                "RESPONSIVE_PCVP_LOCK_IDENTITY_MISMATCH",
                "Verification must remain bound to immutable bytes.",
                "$.verification",
            )
        )

    entries = lock.get("files")
    by_name = {
        entry.get("name"): entry.get("sha256")
        for entry in entries
        if isinstance(entry, dict)
        and isinstance(entry.get("name"), str)
    } if isinstance(entries, list) else {}
    if by_name != SCHEMA_HASHES:
        diagnostics.append(
            _diagnostic(
                "RESPONSIVE_PCVP_LOCK_FILE_SET_INVALID",
                "Lock must cover exactly the four canonical carrier schemas.",
                "$.files",
            )
        )

    schemas: dict[str, dict[str, Any]] = {}
    for name, expected_hash in SCHEMA_HASHES.items():
        schema_path = root / VENDORED_ROOT / name
        try:
            content = schema_path.read_bytes()
            observed_hash = hashlib.sha256(content).hexdigest()
            parsed = json.loads(content.decode("utf-8"))
        except (OSError, UnicodeError, ValueError, TypeError) as exc:
            diagnostics.append(
                _diagnostic(
                    "RESPONSIVE_PCVP_SCHEMA_UNAVAILABLE",
                    f"Pinned {name} could not be loaded ({type(exc).__name__}).",
                    f"$.files.{name}",
                )
            )
            continue
        if observed_hash != expected_hash or not isinstance(parsed, dict):
            diagnostics.append(
                _diagnostic(
                    "RESPONSIVE_PCVP_SCHEMA_HASH_MISMATCH",
                    f"Pinned {name} bytes differ from the immutable source.",
                    f"$.files.{name}.sha256",
                )
            )
            continue
        schemas[name] = parsed

    if diagnostics or set(schemas) != set(SCHEMA_HASHES):
        return None, diagnostics
    return schemas, diagnostics


def _mechanical_diagnostics(document: dict[str, Any]) -> list[dict[str, str]]:
    carrier = document["continuation_assurance"]
    claims = carrier["claims"]
    effects = carrier["effects"]
    authorizations = carrier["authorizations"]
    summary = carrier["stage_summary"]
    diagnostics: list[dict[str, str]] = []

    if carrier["source_stage"] != EXPECTED_SOURCE_STAGE:
        diagnostics.append(
            _diagnostic(
                "RESPONSIVE_PCVP_SOURCE_STAGE_MISMATCH",
                "source_stage must identify the Builder input edge.",
                "$.continuation_assurance.source_stage",
            )
        )

    claims_by_id = {item["claim_id"]: item for item in claims}
    effects_by_id = {item["effect_id"]: item for item in effects}
    authorizations_by_id = {
        item["authorization_id"]: item for item in authorizations
    }
    all_ids = [
        *(item["claim_id"] for item in claims),
        *(item["effect_id"] for item in effects),
        *(item["authorization_id"] for item in authorizations),
    ]
    if len(all_ids) != len(set(all_ids)):
        diagnostics.append(
            _diagnostic(
                "RESPONSIVE_PCVP_ID_NOT_GLOBALLY_UNIQUE",
                "Claim, Effect and Authorization IDs must be globally unique.",
                "$.continuation_assurance",
            )
        )

    for index, claim in enumerate(claims):
        for dependency_id in claim["dependency_refs"]:
            if dependency_id not in claims_by_id:
                diagnostics.append(
                    _diagnostic(
                        "RESPONSIVE_PCVP_CLAIM_DEPENDENCY_UNRESOLVED",
                        f"Claim dependency is unresolved: {dependency_id}.",
                        f"$.continuation_assurance.claims[{index}].dependency_refs",
                    )
                )

    for index, effect in enumerate(effects):
        effect_path = f"$.continuation_assurance.effects[{index}]"
        for claim_id in effect["depends_on_claim_ids"]:
            if claim_id not in claims_by_id:
                diagnostics.append(
                    _diagnostic(
                        "RESPONSIVE_PCVP_EFFECT_CLAIM_REF_UNRESOLVED",
                        f"Effect dependency is unresolved: {claim_id}.",
                        f"{effect_path}.depends_on_claim_ids",
                    )
                )

        auth_ref = effect["authorization_ref"]
        authorization = (
            authorizations_by_id.get(auth_ref)
            if auth_ref is not None
            else None
        )
        if auth_ref is not None and authorization is None:
            diagnostics.append(
                _diagnostic(
                    "RESPONSIVE_PCVP_EFFECT_AUTH_REF_UNRESOLVED",
                    f"Authorization reference is unresolved: {auth_ref}.",
                    f"{effect_path}.authorization_ref",
                )
            )
        if authorization is not None:
            stage_scope = authorization["stage_scope"]
            if (
                stage_scope["from"] != EXPECTED_SOURCE_STAGE
                or stage_scope["through"] != EXPECTED_CONSUMER_STAGE
            ):
                diagnostics.append(
                    _diagnostic(
                        "RESPONSIVE_PCVP_EFFECT_AUTH_STAGE_SCOPE_MISMATCH",
                        "Authorization must cover Builder through Responsive.",
                        f"{effect_path}.authorization_ref",
                    )
                )
            if authorization["status"] != "ACTIVE":
                diagnostics.append(
                    _diagnostic(
                        "RESPONSIVE_PCVP_EFFECT_AUTH_NOT_ACTIVE",
                        "Referenced Authorization is not ACTIVE.",
                        f"{effect_path}.authorization_ref",
                    )
                )
            covered = (
                effect["effect_id"] in authorization["allowed_effect_ids"]
                or effect["effect_class"]
                in authorization["allowed_effect_classes"]
            )
            if not covered:
                diagnostics.append(
                    _diagnostic(
                        "RESPONSIVE_PCVP_EFFECT_AUTH_NOT_COVERING",
                        "Referenced Authorization does not cover the Effect.",
                        f"{effect_path}.authorization_ref",
                    )
                )
            if authorization["permitted_scope"] != effect["permitted_scope"]:
                diagnostics.append(
                    _diagnostic(
                        "RESPONSIVE_PCVP_EFFECT_AUTH_SCOPE_MISMATCH",
                        "Effect and Authorization scopes differ.",
                        f"{effect_path}.permitted_scope",
                    )
                )
            if (
                authorization["basis"] == "SAFE_REVERSIBLE_DEFAULT"
                and effect["effect_class"]
                in {"EXTERNAL_MUTATION", "IRREVERSIBLE_OR_AUTHORITY_BEARING"}
            ):
                diagnostics.append(
                    _diagnostic(
                        "RESPONSIVE_PCVP_SAFE_DEFAULT_FORBIDDEN_EFFECT",
                        "SAFE_REVERSIBLE_DEFAULT cannot cover this Effect class.",
                        effect_path,
                    )
                )

        dependent = [
            claims_by_id[claim_id]
            for claim_id in effect["depends_on_claim_ids"]
            if claim_id in claims_by_id
        ]
        contradicted_critical = any(
            claim["criticality"] == "CRITICAL"
            and claim["applicability_state"] == "APPLICABLE"
            and claim["verification_state"] == "CONTRADICTED"
            for claim in dependent
        )
        if contradicted_critical and effect["continuation_state"] != "BLOCKED":
            diagnostics.append(
                _diagnostic(
                    "RESPONSIVE_PCVP_CONTRADICTED_CRITICAL_EFFECT_NOT_BLOCKED",
                    "A contradicted critical dependency must block the Effect.",
                    f"{effect_path}.continuation_state",
                )
            )

    current_effect = effects_by_id.get(summary["current_effect_id"])
    if current_effect is None:
        diagnostics.append(
            _diagnostic(
                "RESPONSIVE_PCVP_SUMMARY_EFFECT_REF_UNRESOLVED",
                "stage_summary.current_effect_id is unresolved.",
                "$.continuation_assurance.stage_summary.current_effect_id",
            )
        )
        return diagnostics

    current_dependencies = set(current_effect["depends_on_claim_ids"])
    for claim_id in summary["derived_from_claim_ids"]:
        if claim_id not in claims_by_id:
            diagnostics.append(
                _diagnostic(
                    "RESPONSIVE_PCVP_SUMMARY_CLAIM_REF_UNRESOLVED",
                    f"Summary claim reference is unresolved: {claim_id}.",
                    "$.continuation_assurance.stage_summary.derived_from_claim_ids",
                )
            )
        elif claim_id not in current_dependencies:
            diagnostics.append(
                _diagnostic(
                    "RESPONSIVE_PCVP_SUMMARY_CLAIM_NOT_EFFECT_DEPENDENCY",
                    f"Summary claim is not a current-effect dependency: {claim_id}.",
                    "$.continuation_assurance.stage_summary.derived_from_claim_ids",
                )
            )

    dependent = [
        claims_by_id[claim_id]
        for claim_id in current_effect["depends_on_claim_ids"]
        if claim_id in claims_by_id
    ]
    critical_contradicted = any(
        claim["criticality"] == "CRITICAL"
        and claim["applicability_state"] == "APPLICABLE"
        and claim["verification_state"] == "CONTRADICTED"
        for claim in dependent
    )
    any_contradicted = any(
        claim["verification_state"] == "CONTRADICTED" for claim in dependent
    )
    critical_not_verified = any(
        claim["criticality"] == "CRITICAL"
        and claim["applicability_state"] == "APPLICABLE"
        and claim["verification_state"] != "VERIFIED"
        for claim in dependent
    )
    undetermined_material = any(
        claim["criticality"] in {"CRITICAL", "MATERIAL"}
        and claim["applicability_state"] == "UNDETERMINED"
        for claim in dependent
    )
    applicable_unverified = any(
        claim["applicability_state"] == "APPLICABLE"
        and claim["verification_state"] == "UNVERIFIED"
        for claim in dependent
    )
    projection = summary["owner_projection"]

    if projection == "GREEN" and (
        current_effect["continuation_state"] != "CONTINUE"
        or critical_not_verified
        or any_contradicted
        or undetermined_material
    ):
        diagnostics.append(
            _diagnostic(
                "RESPONSIVE_PCVP_GREEN_PROJECTION_INVALID",
                "GREEN is inconsistent with the current Effect dependencies.",
                "$.continuation_assurance.stage_summary",
            )
        )
    if projection == "YELLOW":
        expected_substate = (
            "CONTINUATION_AVAILABLE"
            if current_effect["continuation_state"] == "CONTINUE"
            else (
                "OWNER_CHOICE_REQUIRED"
                if current_effect["continuation_state"] == "AUTHORIZATION_REQUIRED"
                else None
            )
        )
        if (
            expected_substate is None
            or summary["yellow_substate"] != expected_substate
            or (
                not applicable_unverified
                and current_effect["continuation_state"]
                != "AUTHORIZATION_REQUIRED"
            )
            or critical_contradicted
        ):
            diagnostics.append(
                _diagnostic(
                    "RESPONSIVE_PCVP_YELLOW_PROJECTION_INVALID",
                    "YELLOW is inconsistent with the current Effect dependencies.",
                    "$.continuation_assurance.stage_summary",
                )
            )
    if projection == "RED" and current_effect["continuation_state"] != "BLOCKED":
        diagnostics.append(
            _diagnostic(
                "RESPONSIVE_PCVP_RED_WITH_NON_BLOCKED_EFFECT",
                "RED requires a BLOCKED current Effect.",
                "$.continuation_assurance.stage_summary",
            )
        )
    if (
        current_effect["continuation_state"] == "BLOCKED"
        or critical_contradicted
    ) and projection != "RED":
        diagnostics.append(
            _diagnostic(
                "RESPONSIVE_PCVP_REQUIRED_RED_PROJECTION_MISSING",
                "A blocked or contradicted critical Effect requires RED.",
                "$.continuation_assurance.stage_summary",
            )
        )
    return diagnostics


def inspect_optional_pcvp_carrier(
    artifact: Any,
    repository_root: str | Path,
) -> dict[str, Any]:
    """Validate an optional Builder-authored carrier without activating PCVP."""
    if not isinstance(artifact, dict) or "continuation_assurance" not in artifact:
        return _projection("legacy_absent", diagnostics=[])

    root = Path(repository_root)
    document = {
        "continuation_assurance": copy.deepcopy(
            artifact.get("continuation_assurance")
        )
    }
    schemas, diagnostics = _load_pinned_schemas(root)
    if schemas is not None:
        runtime_schema = copy.deepcopy(schemas["handoff.schema.json"])
        carrier_properties = runtime_schema["properties"][
            "continuation_assurance"
        ]["properties"]
        carrier_properties["claims"]["items"] = schemas["claim.schema.json"]
        carrier_properties["effects"]["items"] = schemas["effect.schema.json"]
        carrier_properties["authorizations"]["items"] = schemas[
            "authorization.schema.json"
        ]
        validator = jsonschema.Draft202012Validator(runtime_schema)
        for error in sorted(
            validator.iter_errors(document),
            key=lambda item: (_json_path(list(item.absolute_path)), item.message),
        ):
            diagnostics.append(
                _diagnostic(
                    "RESPONSIVE_PCVP_CARRIER_SCHEMA_INVALID",
                    error.message,
                    _json_path(list(error.absolute_path)),
                )
            )

    if not diagnostics:
        diagnostics.extend(_mechanical_diagnostics(document))
    diagnostics = sorted(
        {
            (item["code"], item["path"], item["message"]): item
            for item in diagnostics
        }.values(),
        key=lambda item: (item["path"], item["code"], item["message"]),
    )
    if diagnostics:
        return _projection("invalid", diagnostics=diagnostics)

    carrier = document["continuation_assurance"]
    return _projection(
        "validated",
        diagnostics=[],
        policy_id=carrier["policy_id"],
        policy_version=carrier["policy_version"],
        source_stage=carrier["source_stage"],
        canonical_sha256=_canonical_sha256(document),
        carrier=copy.deepcopy(document),
    )


__all__ = [
    "ARCHITECTURE_LOCK_ID",
    "CANONICAL_COMMIT",
    "CANONICAL_REPOSITORY",
    "POLICY_ID",
    "POLICY_VERSION",
    "inspect_optional_pcvp_carrier",
]
