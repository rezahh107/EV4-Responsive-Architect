#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json"
INDEX = ROOT / "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG_INDEX.json"
PACKAGE_DIR = ROOT / "planning/work-packages"
SELF = ROOT / "scripts/apply_wp_resp_005_pr_b_replenishment_after_wp012_a.py"
WORKFLOW = ROOT / ".github/workflows/apply-wp-resp-005-pr-b-after-wp012-a.yml"


def reject_duplicates(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates)


def canonical_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_json(path: Path, value) -> bytes:
    payload = canonical_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return payload


def package_015() -> dict:
    forbidden_claims = [
        "production_ready", "release_ready", "live_render_validated",
        "export_json_validated", "accessibility_passed", "pixel_perfect",
        "responsive_correctness_validated",
    ]
    return {
        "id": "WP-RESP-015",
        "title": "Enforce Runtime-Mismatch Reopen Routing Compatibility",
        "capability_area": "runtime_mismatch_reopen_routing_compatibility",
        "current_state": "PR #174 added the runtime-mismatch reopen contract and schema, while Prompt 5 routing is locally validation-backed; no deterministic compatibility contract currently proves that reopen requests preserve routing lineage, authority, and fail-closed boundary semantics across both surfaces.",
        "target_state": "A schema-backed compatibility manifest and deterministic validator bind runtime-mismatch reopen packages to Prompt 5 routing lineage, action, diagnostics, and authority rules without executing transport or replacing Kernel decisions.",
        "measurable_current_state": {
            "statement": "The runtime-mismatch reopen schema and Prompt 5 routing schema exist independently, but no pinned compatibility manifest, cross-contract fixtures, or validator covers their shared lineage and authority invariants.",
            "measurement": "Measured by the absence of a canonical compatibility manifest, dependency identity pins, cross-contract fixtures, dedicated diagnostics, CI wiring, and STATUS or command-index parity.",
            "measurable": True,
        },
        "measurable_target_state": {
            "statement": "Runtime-mismatch reopen packages and Prompt 5 routing envelopes are deterministically compatible or fail closed on lineage, action, diagnostic, authority, and boundary drift.",
            "measurement": "Accepted only when valid and negative fixtures cover missing or divergent lineage, unsupported action, diagnostic mismatch, authority substitution, schema-version drift, and forbidden boundary upgrades under exact-head CI.",
            "measurable": True,
        },
        "target_capability": {
            "statement": "Responsive can validate repository-local compatibility between reopen requests and Prompt 5 routing without executing Project Gate transport or authoring replacement Kernel decisions.",
            "measurement": "A canonical compatibility contract, deterministic diagnostics, positive and negative fixtures, primary CI wiring, documentation, command-index, and STATUS parity remain mutually consistent.",
            "measurable": True,
        },
        "expected_project_delta": "Runtime mismatch escalation becomes fail-closed across the local routing boundary, preventing lineage or authority drift while all evidence, pilot, readiness, release, export, accessibility, pixel, and responsive-correctness claims remain false.",
        "selectable": True,
        "ready_state": "ready",
        "priority": 88,
        "reporting": {"estimated_completion_percentage": 0, "estimated_percentage_is_reporting_only": True},
        "allowed_work": [
            "Define a canonical compatibility manifest that pins the runtime-mismatch reopen and Prompt 5 routing contract identities and shared lineage semantics.",
            "Add valid and negative cross-contract fixtures for lineage, action, diagnostics, authority ownership, version drift, and boundary upgrades.",
            "Add a deterministic fail-closed compatibility validator and align primary CI, command-index, documentation, and STATUS where directly affected.",
        ],
        "forbidden_work": [
            "Do not create submitted evidence unless explicitly authorized by the repository owner and current Issue #8 submitted-mode contracts.",
            "Do not mutate Issue #8 or mark Issue #8 evidence as satisfied.",
            "Do not run or authorize real pilot execution.",
            "Do not execute Project Gate transport or let Responsive author, replace, or reinterpret Kernel decisions.",
            "Do not claim production_ready, release_ready, live_render_validated, export_json_validated, accessibility_passed, pixel_perfect, or responsive_correctness_validated.",
            "Do not treat CI success, merged PRs, catalog completion, Work Package completion, or queue completion as domain evidence.",
        ],
        "must_deliver": [
            "Runtime-mismatch reopen to Prompt 5 routing compatibility manifest or equivalent schema-backed contract.",
            "Deterministic validator with positive and negative coverage for lineage, action, diagnostics, authority, version drift, and boundary upgrades.",
            "Primary validation-chain, command-index, documentation, and STATUS parity for the compatibility boundary.",
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
            "forbidden_claims_without_real_evidence": forbidden_claims,
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
            "No submitted evidence, Issue #8 mutation, pilot authorization, external transport execution, replacement decision, or forbidden readiness claim is produced by the Work Package.",
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
                "invent_unrelated_rtaq_tasks", "guard_only_task_without_named_work_package_unblock",
                "checkpoint_only_pr_after_every_merge", "artificial_reserve_task_to_keep_task_count_high",
                "queue_refresh_loop_as_execution_driver", "fixed_ordinal_refresh",
            ],
        },
        "allowed_pr_slices": [
            {"slice_id": "WP-RESP-015/PR-A", "title": "reopen-routing compatibility contract", "layer": "contract_schema", "objective": "Define pinned contract identities, shared lineage, action, diagnostic, and authority compatibility semantics.", "review_boundary": "Reviewable PR slice under the same Work Package ID; no unrelated micro-objective may be introduced."},
            {"slice_id": "WP-RESP-015/PR-B", "title": "compatibility fixtures, validator, and CI", "layer": "fixture_validator_ci", "objective": "Add deterministic positive and negative cross-contract coverage plus primary validation-chain wiring.", "review_boundary": "Reviewable PR slice under the same Work Package ID; no unrelated micro-objective may be introduced."},
            {"slice_id": "WP-RESP-015/PR-C", "title": "compatibility documentation and STATUS parity", "layer": "docs_status", "objective": "Record compatibility guarantees and remaining Kernel, Project Gate, evidence, and readiness limitations.", "review_boundary": "Reviewable PR slice under the same Work Package ID; no unrelated micro-objective may be introduced."},
        ],
        "blocked_if": [
            "Required contract identity, schema version, or canonical lineage field cannot be determined from repository truth.",
            "The slice would execute external Project Gate transport or let Responsive author, replace, or reinterpret Kernel decisions.",
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
    catalog = load_json(CATALOG)
    index = load_json(INDEX)
    policy = catalog["catalog_replenishment_policy"]
    assert (policy["ready_work_package_target"], policy["refresh_when_ready_below"], policy["max_ready_work_packages"]) == (4, 4, 5)
    packages = catalog["work_packages"]
    assert "WP-RESP-015" not in packages
    wp12 = packages["WP-RESP-012"]
    assert wp12["selectable"] is True and wp12["ready_state"] == "ready"
    assert (ROOT / "contracts/runtime/runtime-mismatch-reopen-package.v1.schema.json").exists()
    assert (ROOT / "contracts/runtime/RUNTIME_MISMATCH_REOPEN_BOUNDARY.md").exists()

    wp12["current_state"] = "PR #174 merged the authority-preserving runtime-mismatch reopen contract and schema; fixture, validator, CI, documentation, STATUS, and command-index slices remain incomplete."
    wp12["measurable_current_state"] = {
        "statement": wp12["current_state"],
        "measurement": "Measured by merged PR #174 plus the absence of completed WP-RESP-012/PR-B and documentation or STATUS parity outcomes.",
        "measurable": True,
    }
    wp12["ready_state"] = "active"
    wp12["reporting"]["estimated_completion_percentage"] = 35
    packages["WP-RESP-015"] = package_015()

    ordered_ids = sorted(packages, key=lambda value: int(value.rsplit("-", 1)[1]))
    catalog["work_packages"] = {package_id: packages[package_id] for package_id in ordered_ids}
    write_json(CATALOG, catalog)

    entries = []
    for package_id in ordered_ids:
        wrapper = {"schema": "ev4-automation-work-package-file@1.0.0", "id": package_id, "work_package": catalog["work_packages"][package_id]}
        path = PACKAGE_DIR / f"{package_id}.json"
        payload = write_json(path, wrapper)
        entries.append({
            "id": package_id,
            "path": f"planning/work-packages/{package_id}.json",
            "schema": "ev4-automation-work-package-file@1.0.0",
            "content_sha256": hashlib.sha256(payload).hexdigest(),
        })

    index["package_entries"] = entries
    index["global_boundaries"] = catalog["global_boundaries"]
    write_json(INDEX, index)

    ready_ids = [package_id for package_id, package in catalog["work_packages"].items() if package.get("selectable") is True and package.get("ready_state") == "ready"]
    assert ready_ids == ["WP-RESP-010", "WP-RESP-011", "WP-RESP-014", "WP-RESP-015"], ready_ids
    assert all(value is False for key, value in catalog["global_boundaries"].items() if key != "catalog_completion_is_evidence_validation" or True)

    SELF.unlink()
    WORKFLOW.unlink()


if __name__ == "__main__":
    main()
