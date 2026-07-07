#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
VALID_BRIDGE = ROOT / "validation" / "fixtures" / "valid" / "issue_to_packet_bridge.valid.json"
INVALID_TEXT_PROOF = ROOT / "validation" / "fixtures" / "invalid" / "issue_to_packet_bridge.text_as_visual_proof.invalid.json"

REQUIRED_BLOCKED_STATES = {
    "MISSING_ATTACHMENT",
    "MISSING_HASH",
    "MALFORMED_HASH",
    "PRIVACY_NOT_ACKED",
    "CONFLICTING_SOURCE",
    "SAMPLE_MARKER_PRESENT",
}

EXPECTED_BLOCKED_STATE_ACTIONS = {
    "MISSING_ATTACHMENT": "request_missing_evidence",
    "MISSING_HASH": "request_hashes",
    "MALFORMED_HASH": "request_hashes",
    "PRIVACY_NOT_ACKED": "request_privacy_review",
    "CONFLICTING_SOURCE": "resolve_conflict",
    "SAMPLE_MARKER_PRESENT": "reject_sample_marker",
}


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    payload.pop("$schema_file", None)
    return payload


def fail(message: str) -> None:
    raise AssertionError(message)


def assert_real_pilot_blocked(payload: dict[str, Any], label: str) -> None:
    verdict = payload["bridge_verdict"]
    if verdict["real_pilot_allowed_to_start"] is not False:
        fail(f"{label}: bridge must never authorize the real pilot")


def assert_blocked_bridge_is_safe(payload: dict[str, Any]) -> None:
    assert_real_pilot_blocked(payload, "valid blocked bridge")

    policy = payload["mapping_policy"]
    if policy["may_infer_missing_evidence"] is not False:
        fail("bridge must not infer missing evidence")
    if policy["may_treat_text_as_visual_proof"] is not False:
        fail("bridge must not treat text as visual proof")
    if policy["sample_markers_allowed"] is not False:
        fail("bridge must reject sample markers")
    if policy["requires_payload_identity_hash"] is not True:
        fail("bridge must require payload identity hashes")
    if policy["requires_privacy_acknowledgement"] is not True:
        fail("bridge must require privacy acknowledgement")

    hash_mappings = [
        mapping
        for mapping in payload["field_mappings"]
        if mapping["packet_field"] == "main_ev4_handoff.payload_identity_hash"
    ]
    if len(hash_mappings) != 1:
        fail("bridge must carry exactly one payload identity hash mapping")
    if hash_mappings[0]["evidence_kind"] != "hash":
        fail("payload identity mapping must be hash evidence")
    if "sha256:<64 lowercase hex>" not in hash_mappings[0]["source_requirement"]:
        fail("payload identity mapping must require sha256:<64 lowercase hex> format")

    blocked_state_ids = {state["state_id"] for state in payload["blocked_states"]}
    missing = REQUIRED_BLOCKED_STATES - blocked_state_ids
    if missing:
        fail(f"bridge missing required blocked states: {sorted(missing)}")

    unexpected = blocked_state_ids - REQUIRED_BLOCKED_STATES
    if unexpected:
        fail(f"bridge contains unexpected blocked states: {sorted(unexpected)}")

    for state in payload["blocked_states"]:
        state_id = state["state_id"]
        if state["pilot_allowed_to_start"] is not False:
            fail(f"blocked state {state_id} must keep pilot_allowed_to_start=false")
        expected_action = EXPECTED_BLOCKED_STATE_ACTIONS[state_id]
        if state["required_action"] != expected_action:
            fail(f"blocked state {state_id} must require action {expected_action}")

    verdict = payload["bridge_verdict"]
    if verdict["status"] != "blocked_missing_evidence":
        fail("current valid fixture must remain blocked_missing_evidence")
    if verdict["packet_creation_allowed"] is not False:
        fail("blocked bridge must not allow packet creation")
    if not verdict["blocking_reasons"]:
        fail("blocked bridge must carry visible blocking reasons")


def assert_text_only_visual_proof_rejected(payload: dict[str, Any]) -> None:
    assert_real_pilot_blocked(payload, "text-only visual proof fixture")

    policy = payload["mapping_policy"]
    if policy["may_treat_text_as_visual_proof"] is True:
        return

    visual_text_mappings = [
        mapping
        for mapping in payload.get("field_mappings", [])
        if mapping.get("packet_field", "").startswith("desktop_baseline")
        and mapping.get("evidence_kind") == "structured_text"
        and mapping.get("missing_state") != "block_packet_creation"
    ]
    if visual_text_mappings:
        return

    verdict = payload["bridge_verdict"]
    if verdict["packet_creation_allowed"] is True and not verdict["blocking_reasons"]:
        return

    fail("invalid fixture no longer demonstrates unsafe text-only visual proof mapping")


def main() -> None:
    valid_payload = load(VALID_BRIDGE)
    invalid_payload = load(INVALID_TEXT_PROOF)

    assert_blocked_bridge_is_safe(valid_payload)
    assert_text_only_visual_proof_rejected(invalid_payload)

    print("Issue-to-packet bridge semantic validation passed")


if __name__ == "__main__":
    main()
