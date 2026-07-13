#!/usr/bin/env python3
"""Apply the bounded WP-RESP-005/PR-B catalog replenishment.

This one-shot migration reconciles consumed WP-RESP-009 and adds one real,
material selectable package for the documented Project Gate Prompt 5 routing
gap. It also regenerates modular package wrappers and their canonical index.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json"
INDEX_PATH = ROOT / "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG_INDEX.json"
PACKAGE_DIR = ROOT / "planning/work-packages"


def load_json(path: Path) -> dict:
    def reject_duplicate(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key in {path}: {key}")
            result[key] = value
        return result

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle, object_pairs_hook=reject_duplicate)


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def numeric_suffix(work_package_id: str) -> int:
    prefix = "WP-RESP-"
    if not work_package_id.startswith(prefix):
        raise ValueError(f"unexpected Work Package id: {work_package_id}")
    return int(work_package_id.removeprefix(prefix))


def ready_depth(packages: dict[str, dict]) -> int:
    return sum(
        package.get("selectable") is True and package.get("ready_state") == "ready"
        for package in packages.values()
    )


def make_wp_013(template: dict) -> dict:
    package = copy.deepcopy(template)
    package.update(
        {
            "id": "WP-RESP-013",
            "title": "Implement Project Gate Prompt 5 Routing Boundary",
            "capability_area": "project_gate_prompt_5_routing",
            "current_state": (
                "STATUS records prompt_5_project_gate_routing as not_implemented; Responsive has guarded "
                "producer artifacts but no schema-backed, fail-closed routing package for verified Project Gate transport."
            ),
            "target_state": (
                "A deterministic Prompt 5 routing boundary validates Project Gate transport inputs, routing decisions, "
                "lineage, and rejection states without letting Responsive execute Project Gate authority or claim responsive correctness."
            ),
            "expected_project_delta": (
                "The documented Prompt 5 routing gap becomes a bounded contract, fixture, validator, CI, and documentation objective "
                "while Project Gate remains the transport authority and all evidence/readiness claims remain false."
            ),
            "selectable": True,
            "ready_state": "ready",
            "priority": 100,
            "reporting": {
                "estimated_completion_percentage": 0,
                "estimated_percentage_is_reporting_only": True,
            },
        }
    )
    package["measurable_current_state"] = {
        "statement": package["current_state"],
        "measurement": (
            "Measured by STATUS prompt_5_project_gate_routing state and the absence of a dedicated routing contract, schema, fixtures, and validator."
        ),
        "measurable": True,
    }
    package["measurable_target_state"] = {
        "statement": package["target_state"],
        "measurement": (
            "Accepted only when contract/schema, positive and negative fixtures, deterministic diagnostics, docs/STATUS parity, "
            "and exact-head CI pass without upgrading evidence or readiness claims."
        ),
        "measurable": True,
    }
    package["target_capability"] = {
        "statement": (
            "Responsive can validate and package the Prompt 5 Project Gate routing boundary while remaining non-executing and authority-preserving."
        ),
        "measurement": (
            "Schema-backed route envelopes and fail-closed validators cover accepted transport, missing lineage, unsupported route, "
            "authority substitution, and forbidden readiness-upgrade states."
        ),
        "measurable": True,
    }
    package["allowed_work"] = [
        "Define the local Prompt 5 routing envelope and Project Gate authority boundary.",
        "Add positive and negative fixtures for lineage, route selection, transport eligibility, and rejection diagnostics.",
        "Wire deterministic validators into CI and align directly affected documentation and STATUS records.",
    ]
    package["must_deliver"] = [
        "Prompt 5 routing boundary contract and schema or schema reference.",
        "Deterministic validator with valid fixtures and negative coverage for missing lineage, unsupported routes, authority substitution, and boundary upgrades.",
        "CI, documentation, command-index, and STATUS parity where directly affected.",
    ]
    package["allowed_pr_slices"] = [
        {
            "slice_id": "WP-RESP-013/PR-A",
            "title": "Prompt 5 routing contract and schema",
            "layer": "contract_schema",
            "objective": "Define the authority-preserving route envelope, inputs, outputs, and rejection semantics.",
            "review_boundary": "Reviewable PR slice under the same Work Package ID; no unrelated micro-objective may be introduced.",
        },
        {
            "slice_id": "WP-RESP-013/PR-B",
            "title": "routing fixtures, validator, and CI",
            "layer": "fixture_validator_ci",
            "objective": "Add deterministic accepted/rejected route coverage and primary validation-chain wiring.",
            "review_boundary": "Reviewable PR slice under the same Work Package ID; no unrelated micro-objective may be introduced.",
        },
        {
            "slice_id": "WP-RESP-013/PR-C",
            "title": "routing documentation and STATUS parity",
            "layer": "docs_status",
            "objective": "Record the implemented local routing boundary and remaining external transport and evidence limitations.",
            "review_boundary": "Reviewable PR slice under the same Work Package ID; no unrelated micro-objective may be introduced.",
        },
    ]
    package["blocked_if"] = [
        "The slice would implement or mutate Project Gate runtime behavior in an external repository.",
        "Responsive would be allowed to authorize transport, replace Project Gate decisions, or execute the real pilot.",
        "Repository checks would be promoted to production, release, live-render, export, accessibility, pixel, or responsive-correctness evidence.",
    ]
    package["unblocks_work_package_ids"] = []
    return package


def main() -> None:
    catalog = load_json(CATALOG_PATH)
    packages = catalog["work_packages"]
    policy = catalog["catalog_replenishment_policy"]

    assert policy["ready_work_package_target"] == 4
    assert policy["refresh_when_ready_below"] == 4
    assert policy["max_ready_work_packages"] == 5
    assert ready_depth(packages) == 4, "raw catalog preimage must contain WP-RESP-009 through WP-RESP-012 as ready"
    assert packages["WP-RESP-009"]["ready_state"] == "ready"
    assert "WP-RESP-013" not in packages

    wp009 = packages["WP-RESP-009"]
    completed_state = (
        "Completed by PR #166 and PR #167: modular catalog contracts, package projection, canonical index, "
        "hash parity, deterministic reassembly, negative self-test coverage, and read-only exact-head CI validation are present."
    )
    wp009["current_state"] = completed_state
    wp009["target_state"] = (
        "The deterministic modular catalog projection is implemented and validation-backed while the monolithic catalog remains canonical."
    )
    wp009["measurable_current_state"]["statement"] = completed_state
    wp009["measurable_target_state"]["statement"] = wp009["target_state"]
    wp009["ready_state"] = "completed"
    wp009["reporting"]["estimated_completion_percentage"] = 100

    packages["WP-RESP-013"] = make_wp_013(packages["WP-RESP-012"])
    catalog["work_packages"] = dict(
        sorted(packages.items(), key=lambda item: numeric_suffix(item[0]))
    )

    assert ready_depth(catalog["work_packages"]) == 4
    assert [
        package_id
        for package_id, package in catalog["work_packages"].items()
        if package.get("selectable") is True and package.get("ready_state") == "ready"
    ] == ["WP-RESP-010", "WP-RESP-011", "WP-RESP-012", "WP-RESP-013"]

    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    entries = []
    for package_id, package in catalog["work_packages"].items():
        wrapper = {
            "schema": "ev4-automation-work-package-file@1.0.0",
            "id": package_id,
            "work_package": package,
        }
        package_bytes = canonical_bytes(wrapper)
        package_path = PACKAGE_DIR / f"{package_id}.json"
        package_path.write_bytes(package_bytes)
        entries.append(
            {
                "id": package_id,
                "path": f"planning/work-packages/{package_id}.json",
                "schema": "ev4-automation-work-package-file@1.0.0",
                "content_sha256": hashlib.sha256(package_bytes).hexdigest(),
            }
        )

    index = load_json(INDEX_PATH)
    index["package_entries"] = entries
    index["global_boundaries"] = copy.deepcopy(catalog["global_boundaries"])

    CATALOG_PATH.write_bytes(canonical_bytes(catalog))
    INDEX_PATH.write_bytes(canonical_bytes(index))

    reparsed = load_json(CATALOG_PATH)
    assert reparsed == catalog
    assert ready_depth(reparsed["work_packages"]) == 4
    assert all(value is False for key, value in reparsed["global_boundaries"].items() if key != "catalog_completion_is_evidence_validation")
    assert reparsed["global_boundaries"]["catalog_completion_is_evidence_validation"] is False


if __name__ == "__main__":
    main()
