#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json"
CONTROL = ROOT / "planning/EV4_AUTOMATION_CONTROL_STATE.json"
STATUS = ROOT / "STATUS.md"
VALIDATE = ROOT / ".github/workflows/validate.yml"


def load_json(path: Path):
    seen = set()
    def hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate key {key!r} in {path}")
            out[key] = value
        return out
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=hook)


def write_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def package_from(template, *, wp_id, title, area, current, target, delta, priority, allowed, deliver, blocked, slices):
    pkg = copy.deepcopy(template)
    pkg["id"] = wp_id
    pkg["title"] = title
    pkg["capability_area"] = area
    pkg["current_state"] = current
    pkg["target_state"] = target
    pkg["measurable_current_state"] = {
        "statement": current,
        "measurement": f"Measured by repository contracts, schemas, fixtures, validators, CI, documentation, and STATUS signals for {wp_id}.",
        "measurable": True,
    }
    pkg["measurable_target_state"] = {
        "statement": target,
        "measurement": f"Accepted only when the approved slices for {wp_id} pass deterministic repository validators and exact-head CI without upgrading evidence or readiness claims.",
        "measurable": True,
    }
    pkg["target_capability"] = {
        "statement": target,
        "measurement": f"Measured by explicit contract, schema, fixture, validator, CI, docs, and STATUS parity for {wp_id}.",
        "measurable": True,
    }
    pkg["expected_project_delta"] = delta
    pkg["selectable"] = True
    pkg["ready_state"] = "ready"
    pkg["priority"] = priority
    pkg["reporting"] = {
        "estimated_completion_percentage": 0,
        "estimated_percentage_is_reporting_only": True,
    }
    pkg["allowed_work"] = allowed
    pkg["must_deliver"] = deliver
    pkg["allowed_pr_slices"] = [
        {
            "slice_id": f"{wp_id}/{slice_id}",
            "title": slice_title,
            "layer": layer,
            "objective": objective,
            "review_boundary": "Reviewable PR slice under the same Work Package ID; no unrelated micro-objective may be introduced.",
        }
        for slice_id, slice_title, layer, objective in slices
    ]
    pkg["blocked_if"] = blocked
    pkg["unblocks_work_package_ids"] = []
    return pkg


def main():
    catalog = load_json(CATALOG)
    control = load_json(CONTROL)
    packages = catalog["work_packages"]

    policy = catalog["catalog_replenishment_policy"]
    policy["ready_work_package_target"] = 4
    policy["refresh_when_ready_below"] = 4
    policy["max_ready_work_packages"] = 5

    outcomes = {
        "WP-RESP-006": ("Responsive contract drift sentinel is implemented and CI-visible through PR #158 and PR #159.", ["PR #158", "PR #159"]),
        "WP-RESP-007": ("Viewport inheritance/reset decision matrix, fixtures, validator, documentation, and CI wiring are completed through PR #160 and PR #161.", ["PR #160", "PR #161"]),
        "WP-RESP-008": ("Responsive handoff export-boundary manifest contract, fixtures, validator, documentation, and CI wiring are completed through PR #162 and PR #163.", ["PR #162", "PR #163"]),
    }
    for wp_id, (statement, refs) in outcomes.items():
        pkg = packages[wp_id]
        pkg["current_state"] = statement
        pkg["measurable_current_state"]["statement"] = statement
        pkg["ready_state"] = "completed"
        pkg["reporting"]["estimated_completion_percentage"] = 100
        pkg["material_outcome_references"] = refs

    template = packages["WP-RESP-006"]
    new_packages = {
        "WP-RESP-009": package_from(
            template,
            wp_id="WP-RESP-009",
            title="Split Work Package Catalog into Deterministic Index and Package Files",
            area="catalog_modularity",
            current="The approved Work Package Catalog is canonical and readable but remains a single large file whose whole-file mutation path is operationally fragile.",
            target="An index plus one schema-validated file per Work Package can be deterministically reassembled and checked for duplicate IDs, ordering, parity, and boundary preservation.",
            delta="Catalog maintenance becomes reviewable and patch-safe without changing catalog authority, execution semantics, or evidence boundaries.",
            priority=60,
            allowed=[
                "Define an index and package-file layout while preserving the catalog as the sole approved objective source.",
                "Add deterministic reassembly, duplicate-ID, ordering, parity, and canonical-format validation.",
                "Migrate existing package records without changing their truthful state or boundary claims.",
            ],
            deliver=[
                "Schema-backed catalog index and package-file contracts.",
                "Deterministic reassembly and duplicate/parity validators with negative fixtures.",
                "CI, docs, STATUS, and controller-path updates required by the migration.",
            ],
            blocked=[
                "The migration would create two competing catalog authorities.",
                "Reassembly cannot preserve canonical ordering, metadata, and all false evidence/readiness claims.",
            ],
            slices=[
                ("PR-A", "index and package-file contracts", "schema_contract", "Define the modular catalog representation and deterministic authority rules."),
                ("PR-B", "migration and reassembly validator", "migration_validator", "Migrate package records and add deterministic reassembly, parity, and negative coverage."),
            ],
        ),
        "WP-RESP-010": package_from(
            template,
            wp_id="WP-RESP-010",
            title="Close Repository-Wide Schema Fixture Metadata Parity",
            area="schema_fixture_parity",
            current="Repository-specific validators pass, but the repository-wide schema validator has a known fixture metadata mismatch around required schema ownership markers.",
            target="Every active valid and invalid fixture has deterministic owning-schema metadata and the repository-wide schema validator passes without weakening focused validators.",
            delta="Schema ownership becomes uniform across fixtures and the broad validation path stops failing on metadata drift.",
            priority=70,
            allowed=[
                "Inventory active fixtures and their owning schemas.",
                "Add or normalize schema ownership metadata and deterministic negative coverage.",
                "Align the repository-wide schema validator, focused validators, command index, and CI when required.",
            ],
            deliver=[
                "Fixture-to-schema ownership inventory or contract.",
                "Metadata normalization with malformed, missing, and wrong-owner negative fixtures.",
                "Repository-wide schema validation wired to exact-head CI with docs parity.",
            ],
            blocked=[
                "The change would bypass focused semantic validators or silently reclassify invalid fixtures as valid.",
                "Owning schema cannot be identified without inventing a new authority boundary.",
            ],
            slices=[
                ("PR-A", "fixture ownership inventory and contract", "inventory_contract", "Define deterministic fixture-to-schema ownership and migration rules."),
                ("PR-B", "metadata migration and CI parity", "fixture_validator_ci", "Normalize metadata, add negative coverage, and close broad-validator parity."),
            ],
        ),
        "WP-RESP-011": package_from(
            template,
            wp_id="WP-RESP-011",
            title="Define Downstream Decision Receipt Rejection Boundary",
            area="downstream_receipt_boundary",
            current="Responsive emits guarded human-readable Kernel decision receipts, but the outbound contract does not yet define deterministic downstream rejection conditions for incomplete or misleading receipts.",
            target="Responsive outbound artifacts expose a schema-backed receipt envelope and fail-closed rejection diagnostics that downstream consumers can enforce without treating receipt text as Kernel authority.",
            delta="Downstream consumers receive a deterministic, machine-checkable rejection boundary while Kernel lineage remains the source of truth.",
            priority=80,
            allowed=[
                "Define the Responsive outbound decision-receipt envelope and rejection diagnostics.",
                "Add fixtures for incomplete lineage, misleading success text, runtime mismatch, and forbidden authority claims.",
                "Document downstream consumer expectations without mutating external repositories.",
            ],
            deliver=[
                "Outbound receipt envelope contract or schema.",
                "Deterministic validator and positive/negative fixture coverage.",
                "Documentation and CI-visible checks preserving Kernel authority and consumer boundaries.",
            ],
            blocked=[
                "The slice would implement or claim enforcement inside Project Gate or another external repository.",
                "Human-readable receipt text would be treated as canonical decision evidence.",
            ],
            slices=[
                ("PR-A", "outbound receipt boundary contract", "contract_schema", "Define machine-readable outbound receipt and fail-closed rejection semantics."),
                ("PR-B", "receipt rejection fixtures and validator", "fixture_validator_ci", "Add deterministic acceptance/rejection coverage and CI wiring."),
            ],
        ),
        "WP-RESP-012": package_from(
            template,
            wp_id="WP-RESP-012",
            title="Harden Runtime Mismatch Reopen Package",
            area="runtime_mismatch_reopen",
            current="Runtime mismatch warnings require lineage, but there is no standalone schema-backed reopen package covering observed mismatch, prior decision lineage, evidence references, and fail-closed routing.",
            target="A deterministic runtime-mismatch reopen package preserves prior Kernel lineage, records observations without redesign authority, and rejects incomplete or readiness-upgrading reopen requests.",
            delta="Runtime mismatch handling becomes a bounded, validator-backed reopen path rather than an informal warning or Responsive-side redesign escape route.",
            priority=90,
            allowed=[
                "Define the runtime mismatch reopen package and allowed observation fields.",
                "Require prior decision lineage, evidence references, consumer stage, and explicit reopen reason.",
                "Add negative fixtures for missing lineage, replacement decisions, unsupported observations, and boundary upgrades.",
            ],
            deliver=[
                "Runtime mismatch reopen package schema or contract.",
                "Valid and invalid fixtures plus deterministic validator diagnostics.",
                "CI, documentation, STATUS, and command-index parity where directly affected.",
            ],
            blocked=[
                "The package would let Responsive author or replace Kernel decisions.",
                "Runtime observations would be promoted to production, release, accessibility, pixel, export, or responsive-correctness evidence.",
            ],
            slices=[
                ("PR-A", "runtime mismatch reopen contract", "contract_schema", "Define the bounded reopen package and authority-preserving fields."),
                ("PR-B", "reopen fixtures, validator, and CI", "fixture_validator_ci", "Add deterministic fail-closed coverage and validation-chain parity."),
            ],
        ),
    }
    packages.update(new_packages)

    governance = packages["WP-RESP-005"]
    governance["current_state"] = "Catalog governance supports the preferred 4/4/5 replenishment policy and records truthful completed outcomes before restoring a four-package selectable horizon."
    governance["measurable_current_state"]["statement"] = governance["current_state"]
    governance["reporting"]["estimated_completion_percentage"] = 100
    governance["unblocks_work_package_ids"] = ["WP-RESP-001", "WP-RESP-009", "WP-RESP-010", "WP-RESP-011", "WP-RESP-012"]
    governance["material_outcome_references"] = ["PR #158", "PR #159", "PR #160", "PR #161", "PR #162", "PR #163", "PR #164"]

    control["latest_material_checkpoint"] = "PR #164 WP-RESP-005/PR-A replenishment-policy transition governance"
    control["catalog_replenishment_policy"] = "state_driven_target_4_refresh_below_4_max_5_single_active_pr"

    validate_text = VALIDATE.read_text(encoding="utf-8")
    diagnostic = "          test -f validation/e2e/run_catalog_replenishment_policy_transition_check.py\n"
    if diagnostic.strip() not in validate_text:
        validate_text = validate_text.replace(
            "          test -f validation/e2e/run_automation_work_package_catalog_check.py\n",
            "          test -f validation/e2e/run_automation_work_package_catalog_check.py\n" + diagnostic,
        )
    step = "      - name: Catalog replenishment policy transition\n        run: python validation/e2e/run_catalog_replenishment_policy_transition_check.py\n"
    if step.strip() not in validate_text:
        validate_text = validate_text.replace(
            "      - name: Automation work package catalog\n        run: python validation/e2e/run_automation_work_package_catalog_check.py\n",
            "      - name: Automation work package catalog\n        run: python validation/e2e/run_automation_work_package_catalog_check.py\n" + step,
        )
    VALIDATE.write_text(validate_text, encoding="utf-8")

    status_text = STATUS.read_text(encoding="utf-8")
    marker = "## WP-RESP-005/PR-B — State-driven catalog replenishment"
    if marker not in status_text:
        status_text = status_text.rstrip() + f"\n\n{marker}\n\n- Preferred catalog policy: `target=4`, `refresh_when_ready_below=4`, `max=5`.\n- `WP-RESP-006`, `WP-RESP-007`, and `WP-RESP-008` are reconciled as completed with merged outcome references.\n- Selectable ready horizon: `WP-RESP-009` through `WP-RESP-012`.\n- No submitted evidence was created; Issue #8 was not mutated; no pilot was run or authorized.\n- Production, release, live-render, export, accessibility, pixel-perfect, and responsive-correctness claims remain false.\n- CI and catalog completion remain repository-check evidence only.\n"
        STATUS.write_text(status_text, encoding="utf-8")

    write_json(CATALOG, catalog)
    write_json(CONTROL, control)

    reloaded = load_json(CATALOG)
    ready = [
        wp_id for wp_id, pkg in reloaded["work_packages"].items()
        if pkg.get("selectable") is True and pkg.get("ready_state") == "ready"
    ]
    assert ready == ["WP-RESP-009", "WP-RESP-010", "WP-RESP-011", "WP-RESP-012"], ready
    assert reloaded["catalog_replenishment_policy"]["ready_work_package_target"] == 4
    assert reloaded["catalog_replenishment_policy"]["refresh_when_ready_below"] == 4
    assert reloaded["catalog_replenishment_policy"]["max_ready_work_packages"] == 5
    for wp_id in ("WP-RESP-006", "WP-RESP-007", "WP-RESP-008"):
        assert reloaded["work_packages"][wp_id]["ready_state"] == "completed"
    for pkg in reloaded["work_packages"].values():
        for key in ("production_ready", "release_ready", "live_render_validated", "accessibility_passed", "pixel_perfect", "responsive_correctness_validated"):
            if key in pkg.get("readiness_boundary", {}):
                assert pkg["readiness_boundary"][key] is False


if __name__ == "__main__":
    main()
