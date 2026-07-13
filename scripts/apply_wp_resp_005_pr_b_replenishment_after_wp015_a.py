#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json"
INDEX_PATH = ROOT / "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG_INDEX.json"
PACKAGE_DIR = ROOT / "planning/work-packages"

BOUNDARY_FALSE_KEYS = {
    "production_ready",
    "release_ready",
    "live_render_validated",
    "export_json_validated",
    "accessibility_passed",
    "pixel_perfect",
    "responsive_correctness_validated",
}


def load_json(path: Path):
    def reject_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate key {key!r} in {path}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates)


def canonical_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def assert_false_boundaries(package: dict) -> None:
    evidence = package["evidence_boundary"]
    readiness = package["readiness_boundary"]
    assert evidence["submitted_evidence_created_by_package"] is False
    assert evidence["issue_8_mutation_allowed"] is False
    assert evidence["real_pilot_execution_allowed"] is False
    assert evidence["ci_success_is_domain_evidence"] is False
    assert evidence["merged_pr_is_domain_evidence"] is False
    assert evidence["catalog_completion_is_evidence_validation"] is False
    assert evidence["claims_require_real_evidence_gates"] is True
    assert set(readiness) == {"pilot_allowed_to_start", *BOUNDARY_FALSE_KEYS}
    assert all(value is False for value in readiness.values())


def package_016() -> dict:
    return {
        "id": "WP-RESP-016",
        "title": "Bind Prompt 5 Routing to Downstream Decision Receipt Correlation",
        "capability_area": "routing_receipt_correlation",
        "current_state": "Prompt 5 routing and downstream decision-receipt boundaries exist as separate planned or implemented surfaces, but no canonical correlation contract binds their shared decision lineage, routing outcome, receipt identity, and authority semantics.",
        "target_state": "A schema-backed correlation envelope and deterministic validator bind Prompt 5 routing outcomes to downstream decision receipts while preserving Kernel authority and rejecting missing, divergent, misleading, or boundary-upgrading correlations.",
        "measurable_current_state": {
            "statement": "Routing envelopes and downstream receipt semantics are not yet connected by a canonical correlation identity or deterministic cross-surface validation path.",
            "measurement": "Measured by the absence of a routing-to-receipt correlation schema, shared lineage pins, positive and negative fixtures, dedicated diagnostics, CI wiring, and documentation or STATUS parity.",
            "measurable": True,
        },
        "measurable_target_state": {
            "statement": "Every supported Prompt 5 route or rejection can be correlated to a downstream receipt or fail closed on lineage, outcome, receipt identity, authority, and boundary drift.",
            "measurement": "Accepted only when valid and negative fixtures cover missing or divergent lineage, route/receipt outcome mismatch, misleading success text, authority substitution, duplicate receipt identity, version drift, and forbidden boundary upgrades under exact-head CI.",
            "measurable": True,
        },
        "target_capability": {
            "statement": "Responsive can validate repository-local correlation between Prompt 5 routing decisions and downstream receipts without treating receipt prose as Kernel authority or executing external transport.",
            "measurement": "A canonical correlation contract, deterministic diagnostics, positive and negative fixtures, primary CI wiring, documentation, command-index, and STATUS parity remain mutually consistent.",
            "measurable": True,
        },
        "expected_project_delta": "Routing and downstream receipt artifacts gain a deterministic correlation boundary that prevents lineage, outcome, or authority ambiguity while all evidence, pilot, readiness, release, export, accessibility, pixel, and responsive-correctness claims remain false.",
        "selectable": True,
        "ready_state": "ready",
        "priority": 86,
        "reporting": {
            "estimated_completion_percentage": 0,
            "estimated_percentage_is_reporting_only": True,
        },
        "allowed_work": [
            "Define a canonical correlation envelope that pins Prompt 5 routing identity, downstream receipt identity, shared Kernel lineage, routing outcome, and authority semantics.",
            "Add valid and negative fixtures for lineage divergence, outcome mismatch, misleading receipt text, duplicate identity, authority substitution, version drift, and boundary upgrades.",
            "Add a deterministic fail-closed validator and align primary CI, command-index, documentation, and STATUS where directly affected.",
        ],
        "forbidden_work": [
            "Do not create submitted evidence unless explicitly authorized by the repository owner and current Issue #8 submitted-mode contracts.",
            "Do not mutate Issue #8 or mark Issue #8 evidence as satisfied.",
            "Do not run or authorize real pilot execution.",
            "Do not execute Project Gate transport or treat human-readable receipt text as canonical Kernel authority.",
            "Do not claim production_ready, release_ready, live_render_validated, export_json_validated, accessibility_passed, pixel_perfect, or responsive_correctness_validated.",
            "Do not treat CI success, merged PRs, catalog completion, Work Package completion, or queue completion as domain evidence.",
        ],
        "must_deliver": [
            "Prompt 5 routing to downstream decision-receipt correlation envelope or equivalent schema-backed contract.",
            "Deterministic validator with positive and negative coverage for lineage, outcome, receipt identity, misleading text, authority, version drift, and boundary upgrades.",
            "Primary validation-chain, command-index, documentation, and STATUS parity for the correlation boundary.",
        ],
        "must_preserve": [
            "Rolling queue remains a historical reconciled archive, not the execution driver.",
            "Controller selection must come only from planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json.",
            "Quality gates, CI, review, and evidence boundaries remain mandatory.",
            "Technical evidence claims remain false unless real evidence gates pass.",
            "Catalog replenishment is state-driven and must not block active Work Package execution.",
            "Catalog replenishment must respect the single-active-mutation-PR policy.",
        ],
        "evidence_boundary": {
            "submitted_evidence_created_by_package": False,
            "issue_8_mutation_allowed": False,
            "real_pilot_execution_allowed": False,
            "ci_success_is_domain_evidence": False,
            "merged_pr_is_domain_evidence": False,
            "catalog_completion_is_evidence_validation": False,
            "claims_require_real_evidence_gates": True,
            "forbidden_claims_without_real_evidence": [
                "production_ready",
                "release_ready",
                "live_render_validated",
                "export_json_validated",
                "accessibility_passed",
                "pixel_perfect",
                "responsive_correctness_validated",
            ],
        },
        "readiness_boundary": {
            "pilot_allowed_to_start": False,
            "production_ready": False,
            "release_ready": False,
            "live_render_validated": False,
            "export_json_validated": False,
            "accessibility_passed": False,
            "pixel_perfect": False,
            "responsive_correctness_validated": False,
        },
        "definition_of_done": [
            "The measurable target state is met by schema-backed or validator-backed repository evidence.",
            "The selected PR slice remains reviewable and stays under this Work Package ID.",
            "No submitted evidence, Issue #8 mutation, pilot authorization, external transport execution, Kernel-authority substitution, or forbidden readiness claim is produced by the Work Package.",
        ],
        "quality_gates": [
            "python validation/e2e/run_automation_work_package_catalog_check.py",
            "python validation/e2e/run_automation_control_state_check.py",
            "python validation/e2e/run_rolling_queue_check.py",
            "python validation/e2e/run_run_ledger_check.py",
            "python validation/e2e/run_task_quality_gate_check.py",
        ],
        "split_rule": {
            "principle": "A Work Package may be large in objective, but each PR must remain reviewable.",
            "split_by": "implementation_layer_under_same_work_package_id",
            "requires_slice_id_prefix": "<WORK_PACKAGE_ID>/PR-",
            "forbidden_splits": [
                "invent_unrelated_rtaq_tasks",
                "guard_only_task_without_named_work_package_unblock",
                "checkpoint_only_pr_after_every_merge",
                "artificial_reserve_task_to_keep_task_count_high",
                "queue_refresh_loop_as_execution_driver",
                "fixed_ordinal_refresh",
            ],
        },
        "allowed_pr_slices": [
            {
                "slice_id": "WP-RESP-016/PR-A",
                "title": "routing-receipt correlation contract",
                "layer": "contract_schema",
                "objective": "Define pinned routing and receipt identities, shared lineage, outcome, and authority correlation semantics.",
                "review_boundary": "Reviewable PR slice under the same Work Package ID; no unrelated micro-objective may be introduced.",
            },
            {
                "slice_id": "WP-RESP-016/PR-B",
                "title": "correlation fixtures, validator, and CI",
                "layer": "fixture_validator_ci",
                "objective": "Add deterministic positive and negative correlation coverage plus primary validation-chain wiring.",
                "review_boundary": "Reviewable PR slice under the same Work Package ID; no unrelated micro-objective may be introduced.",
            },
            {
                "slice_id": "WP-RESP-016/PR-C",
                "title": "correlation documentation and STATUS parity",
                "layer": "docs_status",
                "objective": "Record correlation guarantees and remaining Kernel, Project Gate, evidence, and readiness limitations.",
                "review_boundary": "Reviewable PR slice under the same Work Package ID; no unrelated micro-objective may be introduced.",
            },
        ],
        "blocked_if": [
            "Required routing identity, receipt identity, shared Kernel lineage, or schema version cannot be determined from repository truth.",
            "The slice would execute external Project Gate transport or treat human-readable receipt text as canonical Kernel authority.",
            "Repository checks would be promoted to submitted evidence, pilot authorization, production, release, live-render, export, accessibility, pixel, or responsive-correctness evidence.",
        ],
        "completion_record_requirements": [
            "Record selected Work Package ID and PR slice ID in the PR body.",
            "List files changed, validators changed, and CI commands run.",
            "State commands not run and why.",
            "Restate evidence/pilot/readiness/production/release/responsive-correctness boundaries.",
            "Record whether catalog replenishment was checked and whether it was non-mutating, same-PR in-scope, or blocked by single-active-PR policy.",
            "Record remaining risks and the next safe human action.",
        ],
        "unblocks_work_package_ids": [],
    }


def main() -> None:
    catalog = load_json(CATALOG_PATH)
    index = load_json(INDEX_PATH)
    policy = catalog["catalog_replenishment_policy"]
    assert policy["ready_work_package_target"] == 4
    assert policy["refresh_when_ready_below"] == 4
    assert policy["max_ready_work_packages"] == 5

    packages = catalog["work_packages"]
    assert "WP-RESP-016" not in packages
    assert packages["WP-RESP-012"]["ready_state"] == "active"
    assert packages["WP-RESP-013"]["ready_state"] == "active"
    assert packages["WP-RESP-015"]["ready_state"] == "ready"

    wp12 = packages["WP-RESP-012"]
    wp12["current_state"] = "PR #174 and PR #177 completed the authority-preserving runtime-mismatch reopen contract, schema, fixtures, deterministic validator, negative coverage, and primary CI wiring."
    wp12["measurable_current_state"]["statement"] = wp12["current_state"]
    wp12["measurable_current_state"]["measurement"] = "Measured by merged PR #174 and PR #177 plus exact-head repository validation outcomes; completion remains repository-check evidence only."
    wp12["ready_state"] = "completed"
    wp12["reporting"]["estimated_completion_percentage"] = 100

    wp13 = packages["WP-RESP-013"]
    wp13["current_state"] = "PR #169, PR #172, and PR #173 completed the authority-preserving Prompt 5 routing contract, schema, fixtures, deterministic validator, negative coverage, primary CI wiring, documentation, command-index, and STATUS parity."
    wp13["measurable_current_state"]["statement"] = wp13["current_state"]
    wp13["measurable_current_state"]["measurement"] = "Measured by merged PR #169, PR #172, and PR #173 plus exact-head repository validation outcomes; completion remains repository-check evidence only."
    wp13["ready_state"] = "completed"
    wp13["reporting"]["estimated_completion_percentage"] = 100

    wp15 = packages["WP-RESP-015"]
    wp15["current_state"] = "PR #178 merged the pinned reopen-routing compatibility contract and schema; fixtures, deterministic validator diagnostics, CI wiring, documentation, command-index, and STATUS parity remain incomplete."
    wp15["measurable_current_state"]["statement"] = wp15["current_state"]
    wp15["measurable_current_state"]["measurement"] = "Measured by merged PR #178 plus the absence of completed WP-RESP-015/PR-B and WP-RESP-015/PR-C outcomes."
    wp15["ready_state"] = "active"
    wp15["reporting"]["estimated_completion_percentage"] = 35

    packages["WP-RESP-016"] = package_016()

    ordered_ids = sorted(packages, key=lambda item: int(item.rsplit("-", 1)[1]))
    catalog["work_packages"] = {package_id: packages[package_id] for package_id in ordered_ids}
    packages = catalog["work_packages"]
    active = [p["id"] for p in packages.values() if p["ready_state"] == "active"]
    assert active == ["WP-RESP-015"]
    ready = [p["id"] for p in packages.values() if p.get("selectable") and p["ready_state"] == "ready"]
    assert ready == ["WP-RESP-010", "WP-RESP-011", "WP-RESP-014", "WP-RESP-016"]

    global_boundaries = catalog["global_boundaries"]
    assert set(global_boundaries) == {
        "submitted_evidence_created_by_catalog",
        "issue_8_mutation_allowed_by_catalog",
        "real_pilot_execution_allowed_by_catalog",
        "catalog_completion_is_evidence_validation",
        "ci_success_is_responsive_correctness_evidence",
        *BOUNDARY_FALSE_KEYS,
    }
    assert all(value is False for value in global_boundaries.values())
    for package in packages.values():
        assert_false_boundaries(package)

    CATALOG_PATH.write_bytes(canonical_bytes(catalog))

    entries_by_id = {entry["id"]: entry for entry in index["package_entries"]}
    for package_id in ("WP-RESP-012", "WP-RESP-013", "WP-RESP-015", "WP-RESP-016"):
        wrapper = {
            "schema": "ev4-automation-work-package-file@1.0.0",
            "id": package_id,
            "work_package": packages[package_id],
        }
        payload = canonical_bytes(wrapper)
        package_path = PACKAGE_DIR / f"{package_id}.json"
        package_path.write_bytes(payload)
        digest = hashlib.sha256(payload).hexdigest()
        entry = entries_by_id.get(package_id)
        if entry is None:
            entry = {
                "id": package_id,
                "path": f"planning/work-packages/{package_id}.json",
                "schema": "ev4-automation-work-package-file@1.0.0",
                "content_sha256": digest,
            }
            index["package_entries"].append(entry)
            entries_by_id[package_id] = entry
        else:
            entry["content_sha256"] = digest

    index["package_entries"].sort(key=lambda entry: int(entry["id"].rsplit("-", 1)[1]))
    assert [entry["id"] for entry in index["package_entries"]] == ordered_ids
    assert index["global_boundaries"] == global_boundaries
    INDEX_PATH.write_bytes(canonical_bytes(index))


if __name__ == "__main__":
    main()
