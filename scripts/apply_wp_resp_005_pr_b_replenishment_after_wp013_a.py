#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json"
INDEX_PATH = ROOT / "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG_INDEX.json"
PACKAGE_DIR = ROOT / "planning/work-packages"


def load_json(path: Path):
    def no_dupes(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key {key!r} in {path}")
            out[key] = value
        return out
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_dupes)


def canonical_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def false_boundaries():
    return {
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
    }


def false_readiness():
    return {
        "pilot_allowed_to_start": False,
        "production_ready": False,
        "release_ready": False,
        "live_render_validated": False,
        "export_json_validated": False,
        "accessibility_passed": False,
        "pixel_perfect": False,
        "responsive_correctness_validated": False,
    }


def shared_forbidden():
    return [
        "Do not create submitted evidence unless explicitly authorized by the repository owner and current Issue #8 submitted-mode contracts.",
        "Do not mutate Issue #8 or mark Issue #8 evidence as satisfied.",
        "Do not run or authorize real pilot execution.",
        "Do not claim production_ready, release_ready, live_render_validated, export_json_validated, accessibility_passed, pixel_perfect, or responsive_correctness_validated.",
        "Do not treat CI success, merged PRs, catalog completion, Work Package completion, or queue completion as domain evidence.",
    ]


def shared_preserve():
    return [
        "Rolling queue remains a historical reconciled archive, not the execution driver.",
        "Controller selection must come only from planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json.",
        "Quality gates, CI, review, and evidence boundaries remain mandatory.",
        "Technical evidence claims remain false unless real evidence gates pass.",
        "Catalog replenishment is state-driven and must not block active Work Package execution.",
        "Catalog replenishment must respect the single-active-mutation-PR policy.",
    ]


def quality_gates():
    return [
        "python validation/e2e/run_automation_work_package_catalog_check.py",
        "python validation/e2e/run_automation_control_state_check.py",
        "python validation/e2e/run_rolling_queue_check.py",
        "python validation/e2e/run_run_ledger_check.py",
        "python validation/e2e/run_task_quality_gate_check.py",
    ]


def split_rule():
    return {
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
    }


def completion_requirements():
    return [
        "Record selected Work Package ID and PR slice ID in the PR body.",
        "List files changed, validators changed, and CI commands run.",
        "State commands not run and why.",
        "Restate evidence/pilot/readiness/production/release/responsive-correctness boundaries.",
        "Record whether catalog replenishment was checked and whether it was non-mutating, same-PR in-scope, or blocked by single-active-PR policy.",
        "Record remaining risks and the next safe human action.",
    ]


def main() -> None:
    catalog = load_json(CATALOG_PATH)
    policy = catalog["catalog_replenishment_policy"]
    expected_policy = (4, 4, 5)
    actual_policy = (
        policy["ready_work_package_target"],
        policy["refresh_when_ready_below"],
        policy["max_ready_work_packages"],
    )
    if actual_policy != expected_policy:
        raise SystemExit(f"unexpected replenishment policy: {actual_policy}")

    packages = catalog["work_packages"]
    if "WP-RESP-014" in packages:
        raise SystemExit("WP-RESP-014 already exists")

    wp13 = packages["WP-RESP-013"]
    if wp13["ready_state"] != "ready":
        raise SystemExit(f"unexpected WP-RESP-013 state: {wp13['ready_state']}")
    wp13["ready_state"] = "active"
    wp13["current_state"] = (
        "PR #169 merged the authority-preserving Prompt 5 routing contract and schema; "
        "fixture, validator, CI, documentation, and STATUS slices remain incomplete."
    )
    wp13["measurable_current_state"]["statement"] = wp13["current_state"]
    wp13["measurable_current_state"]["measurement"] = (
        "Measured by merged PR #169 plus the absence of completed WP-RESP-013/PR-B and WP-RESP-013/PR-C outcomes."
    )
    wp13["reporting"]["estimated_completion_percentage"] = 35

    wp14 = {
        "id": "WP-RESP-014",
        "title": "Enforce Prompt 5 Cross-Contract Compatibility and Drift Detection",
        "capability_area": "prompt_5_cross_contract_compatibility",
        "current_state": "The local Prompt 5 routing envelope now has a contract and schema, but no deterministic compatibility guard pins its relationship to producer-gate-export.v1 and the vendored Project Gate common contract surfaces.",
        "target_state": "A schema-backed compatibility manifest and fail-closed validator detect identifier, version, hash, lineage, and authority drift across the Prompt 5 routing envelope and its Project Gate contract dependencies.",
        "measurable_current_state": {
            "statement": "The local Prompt 5 routing envelope now has a contract and schema, but no deterministic compatibility guard pins its relationship to producer-gate-export.v1 and the vendored Project Gate common contract surfaces.",
            "measurement": "Measured by the absence of a Prompt 5 compatibility manifest, pinned dependency identities, drift fixtures, and a dedicated compatibility validator in the primary validation chain.",
            "measurable": True,
        },
        "measurable_target_state": {
            "statement": "A schema-backed compatibility manifest and fail-closed validator detect identifier, version, hash, lineage, and authority drift across the Prompt 5 routing envelope and its Project Gate contract dependencies.",
            "measurement": "Accepted only when valid and negative fixtures cover pinned identities, dependency hash drift, schema-version mismatch, lineage incompatibility, authority substitution, and forbidden boundary upgrades under exact-head CI.",
            "measurable": True,
        },
        "target_capability": {
            "statement": "Responsive can prove repository-local compatibility between its Prompt 5 route envelope and pinned Project Gate contract dependencies without executing transport or claiming domain correctness.",
            "measurement": "A canonical compatibility manifest, deterministic diagnostics, negative fixtures, command-index entry, CI wiring, and STATUS parity remain mutually consistent.",
            "measurable": True,
        },
        "expected_project_delta": "Prompt 5 contract evolution becomes fail-closed against cross-contract drift while external Project Gate transport authority and all evidence/readiness boundaries remain unchanged.",
        "selectable": True,
        "ready_state": "ready",
        "priority": 85,
        "reporting": {
            "estimated_completion_percentage": 0,
            "estimated_percentage_is_reporting_only": True,
        },
        "allowed_work": [
            "Define a canonical Prompt 5 compatibility manifest that pins relevant local and vendored contract identities and hashes.",
            "Add valid and negative fixtures for schema-version, hash, lineage, route-target, and authority-boundary drift.",
            "Add a deterministic fail-closed compatibility validator and wire it into CI, command-index, documentation, and STATUS surfaces where directly affected.",
        ],
        "forbidden_work": shared_forbidden(),
        "must_deliver": [
            "Prompt 5 cross-contract compatibility manifest or equivalent schema-backed contract.",
            "Deterministic validator with negative coverage for dependency hash drift, schema/version mismatch, lineage incompatibility, authority substitution, and boundary upgrades.",
            "Primary validation-chain, command-index, documentation, and STATUS parity for the compatibility guard.",
        ],
        "must_preserve": shared_preserve(),
        "evidence_boundary": false_boundaries(),
        "readiness_boundary": false_readiness(),
        "definition_of_done": [
            "The measurable target state is met by schema-backed or validator-backed repository evidence.",
            "The selected PR slice remains reviewable and stays under this Work Package ID.",
            "No submitted evidence, Issue #8 mutation, pilot authorization, or forbidden readiness claim is produced by the Work Package.",
        ],
        "quality_gates": quality_gates(),
        "split_rule": split_rule(),
        "allowed_pr_slices": [
            {
                "slice_id": "WP-RESP-014/PR-A",
                "title": "compatibility manifest and schema",
                "layer": "contract_schema",
                "objective": "Define pinned Prompt 5 dependency identities, compatibility semantics, and fail-closed authority boundaries.",
                "review_boundary": "Reviewable PR slice under the same Work Package ID; no unrelated micro-objective may be introduced.",
            },
            {
                "slice_id": "WP-RESP-014/PR-B",
                "title": "compatibility fixtures, validator, and CI",
                "layer": "fixture_validator_ci",
                "objective": "Add deterministic positive and negative drift coverage plus primary validation-chain wiring.",
                "review_boundary": "Reviewable PR slice under the same Work Package ID; no unrelated micro-objective may be introduced.",
            },
            {
                "slice_id": "WP-RESP-014/PR-C",
                "title": "compatibility documentation and STATUS parity",
                "layer": "docs_status",
                "objective": "Record compatibility guarantees and remaining external transport and evidence limitations.",
                "review_boundary": "Reviewable PR slice under the same Work Package ID; no unrelated micro-objective may be introduced.",
            },
        ],
        "blocked_if": [
            "Required dependency identity or canonical vendored contract hash cannot be determined from repository truth.",
            "The slice would mutate an external Project Gate repository, execute transport, or substitute Responsive for Project Gate authority.",
            "Repository checks would be promoted to production, release, live-render, export, accessibility, pixel, or responsive-correctness evidence.",
        ],
        "completion_record_requirements": completion_requirements(),
        "unblocks_work_package_ids": [],
    }
    packages["WP-RESP-014"] = wp14

    ordered_ids = sorted(packages, key=lambda value: int(value.rsplit("-", 1)[1]))
    catalog["work_packages"] = {wp_id: packages[wp_id] for wp_id in ordered_ids}

    ready = [
        wp_id for wp_id, wp in catalog["work_packages"].items()
        if wp.get("selectable") is True and wp.get("ready_state") == "ready"
    ]
    if ready != ["WP-RESP-010", "WP-RESP-011", "WP-RESP-012", "WP-RESP-014"]:
        raise SystemExit(f"unexpected post-migration ready horizon: {ready}")

    CATALOG_PATH.write_bytes(canonical_bytes(catalog))
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)

    entries = []
    for wp_id in ordered_ids:
        wrapper = {
            "schema": "ev4-automation-work-package-file@1.0.0",
            "id": wp_id,
            "work_package": catalog["work_packages"][wp_id],
        }
        data = canonical_bytes(wrapper)
        path = PACKAGE_DIR / f"{wp_id}.json"
        path.write_bytes(data)
        entries.append({
            "id": wp_id,
            "path": f"planning/work-packages/{wp_id}.json",
            "schema": "ev4-automation-work-package-file@1.0.0",
            "content_sha256": hashlib.sha256(data).hexdigest(),
        })

    index = load_json(INDEX_PATH)
    index["package_entries"] = entries
    index["global_boundaries"] = catalog["global_boundaries"]
    INDEX_PATH.write_bytes(canonical_bytes(index))

    print("WP-RESP-005/PR-B migration complete")
    print("ready horizon:", ", ".join(ready))


if __name__ == "__main__":
    main()
