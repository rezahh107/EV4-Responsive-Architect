#!/usr/bin/env python3
"""Reusable Wave 5 formatter and guard for Responsive Kernel decision receipts.

This module is intentionally presentation-layer only. It renders short
human-readable receipts from an existing machine-readable decision_lineage and
rejects green-check claims that are not backed by the required trace fields.
"""
from __future__ import annotations

from collections.abc import Mapping

SUCCESS_MESSAGE = (
    "✅ این Responsive validation به decision card کرنل وصل است؛ "
    "Responsive فقط رفتار responsive/runtime را بررسی کرده و lineage تصمیم حفظ شده است."
)
WARNING_MESSAGE = (
    "⚠️ این Responsive item هنوز رسید معتبر کرنل ندارد؛ بدون machine-readable trace کامل "
    "نباید به‌عنوان تصمیم responsive معتبر عبور کند."
)
RUNTIME_MISMATCH_WARNING_MESSAGE = (
    "⚠️ runtime mismatch دیده شد، اما این رسید تصمیم جدید نیست؛ تصمیم باید با trace معتبر "
    "reopen یا repair شود."
)

REQUIRED_TRACE_FIELDS = (
    "decision_family",
    "decision_card_ref",
    "selected_option",
    "rejected_options",
    "evidence_refs",
    "evidence_state",
    "consumer_stage",
)
LIST_TRACE_FIELDS = {"rejected_options", "evidence_refs"}
SUCCESS_EVIDENCE_STATE = "validated"
RUNTIME_MISMATCH_STAGE = "runtime_evidence_conflict"
RUNTIME_MISMATCH_REQUIRED_OPTION = "blocked_pending_input"
RUNTIME_MISMATCH_REQUIRED_EVIDENCE_STATE = "reopen_required"

FORBIDDEN_RECEIPT_CLAIMS = (
    "redesign_architecture",
    "replace_upstream_Architect_CE_or_Builder_decisions",
    "convert_runtime_mismatch_into_new_design_choice",
    "runtime_monitor_enforced",
    "downstream_contract_enforced",
    "production_ready",
    "production readiness",
    "runtime monitor enforcement",
    "downstream enforcement",
    "new design decision",
    "Responsive redesign",
    "طراحی جدید",
    "بازطراحی",
)


def _is_non_empty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def trace_is_complete(trace: object) -> bool:
    if not isinstance(trace, Mapping):
        return False
    for field in REQUIRED_TRACE_FIELDS:
        if field not in trace:
            return False
        value = trace[field]
        if field in LIST_TRACE_FIELDS:
            if not isinstance(value, list) or not value:
                return False
            if not all(_is_non_empty_text(item) for item in value):
                return False
        elif not _is_non_empty_text(value):
            return False
    return True


def _trace_ref(trace: object) -> str | None:
    return "decision_lineage" if isinstance(trace, Mapping) else None


def _is_runtime_mismatch_trace(trace: object) -> bool:
    return isinstance(trace, Mapping) and trace.get("consumer_stage") == RUNTIME_MISMATCH_STAGE


def _is_runtime_mismatch_reopen_trace(trace: object) -> bool:
    return (
        trace_is_complete(trace)
        and trace.get("selected_option") == RUNTIME_MISMATCH_REQUIRED_OPTION
        and trace.get("evidence_state") == RUNTIME_MISMATCH_REQUIRED_EVIDENCE_STATE
    )


def format_responsive_kernel_receipt(payload: Mapping[str, object], surface: str) -> dict[str, object]:
    """Return the safe user-facing receipt for a Responsive output surface."""
    trace = payload.get("decision_lineage")
    if _is_runtime_mismatch_trace(trace) and _is_runtime_mismatch_reopen_trace(trace):
        return {
            "receipt_state": "runtime_mismatch_warning",
            "message": RUNTIME_MISMATCH_WARNING_MESSAGE,
            "trace_ref": _trace_ref(trace),
            "surface": surface,
        }

    if trace_is_complete(trace) and trace.get("evidence_state") == SUCCESS_EVIDENCE_STATE:
        return {
            "receipt_state": "success",
            "message": SUCCESS_MESSAGE,
            "trace_ref": _trace_ref(trace),
            "surface": surface,
        }

    return {
        "receipt_state": "insufficient_evidence",
        "message": WARNING_MESSAGE,
        "trace_ref": _trace_ref(trace),
        "surface": surface,
    }


def _message_contains_forbidden_claim(message: object) -> bool:
    if not isinstance(message, str):
        return False
    return any(claim in message for claim in FORBIDDEN_RECEIPT_CLAIMS)


def assert_runtime_mismatch_reopen_trace(payload: Mapping[str, object], path: str, receipt_state: object) -> None:
    trace = payload.get("decision_lineage")
    if not _is_runtime_mismatch_trace(trace):
        return
    if not trace_is_complete(trace):
        if receipt_state == "runtime_mismatch_warning":
            raise ValueError(
                "EV4_RESPONSIVE_RUNTIME_MISMATCH_INCOMPLETE_TRACE: "
                f"{path} emitted a runtime mismatch receipt without complete machine-readable lineage"
            )
        return
    if not _is_runtime_mismatch_reopen_trace(trace):
        raise ValueError(
            "EV4_RESPONSIVE_RUNTIME_MISMATCH_REOPEN_REQUIRED: "
            f"{path} must reopen or repair the traced decision instead of emitting a new Responsive choice"
        )


def assert_receipt_matches_trace(payload: Mapping[str, object], path: str, surface: str) -> None:
    """Fail closed when the visible receipt overclaims the available machine trace."""
    receipt = payload.get("kernel_decision_receipt")
    if not isinstance(receipt, Mapping):
        raise ValueError(f"EV4_RESPONSIVE_KERNEL_RECEIPT_MISSING: {path}")

    if _message_contains_forbidden_claim(receipt.get("message")):
        raise ValueError(
            "EV4_RESPONSIVE_KERNEL_RECEIPT_FORBIDDEN_CLAIM: "
            f"{path} receipt claims authority outside Responsive Wave 5"
        )

    trace = payload.get("decision_lineage")
    if receipt.get("receipt_state") == "success":
        if not trace_is_complete(trace):
            raise ValueError(
                "EV4_RESPONSIVE_KERNEL_RECEIPT_GREEN_WITHOUT_TRACE: "
                f"{path} emitted a success receipt without complete machine-readable trace"
            )
        if trace.get("evidence_state") != SUCCESS_EVIDENCE_STATE:
            raise ValueError(
                "EV4_RESPONSIVE_KERNEL_RECEIPT_WEAK_EVIDENCE_GREEN: "
                f"{path} emitted a success receipt without validated evidence_state"
            )
        if trace.get("consumer_stage") == RUNTIME_MISMATCH_STAGE:
            raise ValueError(
                "EV4_RESPONSIVE_RUNTIME_MISMATCH_RECEIPT_OVERCLAIM: "
                f"{path} emitted a success receipt for runtime mismatch"
            )

    assert_runtime_mismatch_reopen_trace(payload, path, receipt.get("receipt_state"))

    expected = format_responsive_kernel_receipt(payload, surface)
    observed = dict(receipt)
    if observed != expected:
        raise ValueError(
            "EV4_RESPONSIVE_KERNEL_RECEIPT_TRACE_MISMATCH: "
            f"{path} receipt={observed!r} expected={expected!r}"
        )
