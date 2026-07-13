#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one marker, found {count}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def require_contains(path: Path, needle: str) -> None:
    if needle not in path.read_text(encoding="utf-8"):
        raise SystemExit(f"{path}: required content missing: {needle!r}")


def write_doc() -> None:
    path = ROOT / "docs/48_PROMPT_5_PROJECT_GATE_ROUTING_BOUNDARY.md"
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing {path}")
    path.write_text(
        "# Prompt 5 Project Gate Routing Boundary\n\n"
        "Work Package: `WP-RESP-013`  \n"
        "Slice: `WP-RESP-013/PR-C`\n\n"
        "## Implemented local boundary\n\n"
        "Responsive now owns a deterministic, repository-local validation boundary for Prompt 5 routing envelopes. The implementation consists of:\n\n"
        "- contract: `contracts/project-gate/PROMPT_5_ROUTING_BOUNDARY.md`;\n"
        "- schema: `contracts/project-gate/prompt-5-routing-envelope.v1.schema.json`;\n"
        "- validator: `validation/e2e/run_prompt_5_routing_envelope_check.py`;\n"
        "- positive fixtures: `validation/fixtures/prompt05/valid/*.valid.json`;\n"
        "- negative fixtures: `validation/fixtures/prompt05/invalid/*.invalid.json`;\n"
        "- CI path: `.github/workflows/validate.yml`.\n\n"
        "The validator checks Draft 2020-12 schema conformance plus explicit policy semantics for route/reject coupling, diagnostic behavior, transport eligibility, authority ownership, exact boundary-claim registry, and all-false boundary values.\n\n"
        "## Authority boundary\n\n"
        "Responsive may decide only whether a locally produced routing envelope is eligible or rejected. Responsive does not execute transport, mutate EV4 Project Gate runtime state, replace Project Gate decisions, or authorize downstream progression. EV4 Project Gate remains the transport and downstream gate authority.\n\n"
        "## Fail-closed behavior\n\n"
        "The routing boundary rejects, at minimum:\n\n"
        "- missing or incomplete source lineage;\n"
        "- unsupported routing targets;\n"
        "- authority substitution or Responsive-owned transport execution;\n"
        "- inconsistent route/reject and `transport_eligible` states;\n"
        "- forbidden submitted-evidence, pilot, production, release, live-render, export, accessibility, pixel-perfect, or responsive-correctness upgrades.\n\n"
        "## Current limitations\n\n"
        "This repository-local implementation does not prove that external Project Gate transport is deployed, exercised, or accepted. It does not create submitted evidence, satisfy Issue #8, run a pilot, validate a live render or export, or establish responsive correctness. Exact-head CI success is repository-check evidence only.\n\n"
        "## Validation\n\n"
        "```bash\n"
        "python validation/e2e/run_prompt_5_routing_envelope_check.py\n"
        "```\n\n"
        "The command is also part of the primary `Validate` workflow. Its success must not be interpreted as production readiness, release readiness, transport execution, or domain evidence.\n",
        encoding="utf-8",
    )


def patch_status() -> None:
    path = ROOT / "STATUS.md"
    replace_once(
        path,
        "  - contracts/RESPONSIVE_HANDOFF_EXPORT_BOUNDARY_MANIFEST.md\nactive_schema:",
        "  - contracts/RESPONSIVE_HANDOFF_EXPORT_BOUNDARY_MANIFEST.md\n"
        "  - contracts/project-gate/PROMPT_5_ROUTING_BOUNDARY.md\nactive_schema:",
    )
    replace_once(
        path,
        "  - schemas/ev4-automation-work-package-catalog.schema.json\nactive_validation:",
        "  - schemas/ev4-automation-work-package-catalog.schema.json\n"
        "  - contracts/project-gate/prompt-5-routing-envelope.v1.schema.json\nactive_validation:",
    )
    replace_once(
        path,
        "  - validation/e2e/run_builder_responsive_input_boundary_check.py\n  - validation/e2e/run_responsive_contract_drift_sentinel_check.py",
        "  - validation/e2e/run_builder_responsive_input_boundary_check.py\n"
        "  - validation/e2e/run_prompt_5_routing_envelope_check.py\n"
        "  - validation/e2e/run_responsive_contract_drift_sentinel_check.py",
    )
    replace_once(
        path,
        "  - docs/47_RESPONSIVE_CONTRACT_DRIFT_SENTINEL.md\n  - docs/AUTOMATION_WORK_PACKAGE_CATALOG.md",
        "  - docs/47_RESPONSIVE_CONTRACT_DRIFT_SENTINEL.md\n"
        "  - docs/48_PROMPT_5_PROJECT_GATE_ROUTING_BOUNDARY.md\n"
        "  - docs/AUTOMATION_WORK_PACKAGE_CATALOG.md",
    )
    replace_once(
        path,
        "  - python validation/e2e/run_builder_responsive_input_boundary_check.py\n  - python validation/e2e/run_responsive_contract_drift_sentinel_check.py",
        "  - python validation/e2e/run_builder_responsive_input_boundary_check.py\n"
        "  - python validation/e2e/run_prompt_5_routing_envelope_check.py\n"
        "  - python validation/e2e/run_responsive_contract_drift_sentinel_check.py",
    )
    replace_once(
        path,
        "  prompt_5_project_gate_routing: not_implemented\n  responsive_correctness: not_claimed",
        "  prompt_5_project_gate_routing: implemented_local_validation_non_executing\n"
        "  prompt_5_routing_contract: contracts/project-gate/PROMPT_5_ROUTING_BOUNDARY.md\n"
        "  prompt_5_routing_schema: contracts/project-gate/prompt-5-routing-envelope.v1.schema.json\n"
        "  prompt_5_routing_validator: validation/e2e/run_prompt_5_routing_envelope_check.py\n"
        "  prompt_5_routing_fixtures: validation/fixtures/prompt05\n"
        "  project_gate_transport_execution_owner: EV4 Project Gate\n"
        "  external_project_gate_transport_implemented_here: false\n"
        "  submitted_evidence_created: false\n"
        "  pilot_authorized: false\n"
        "  responsive_correctness: not_claimed",
    )


def patch_command_index() -> None:
    path = ROOT / "docs/17_VALIDATION_COMMAND_INDEX.md"
    replace_once(
        path,
        "python validation/e2e/run_builder_responsive_input_boundary_check.py\npython validation/e2e/run_responsive_decision_lineage_sequence_check.py",
        "python validation/e2e/run_builder_responsive_input_boundary_check.py\n"
        "python validation/e2e/run_prompt_5_routing_envelope_check.py\n"
        "python validation/e2e/run_responsive_decision_lineage_sequence_check.py",
    )
    replace_once(
        path,
        "## Project Gate Prompt 04 Responsive Producer Adoption\n",
        "## Project Gate Prompt 5 routing boundary\n\n"
        "```bash\n"
        "python validation/e2e/run_prompt_5_routing_envelope_check.py\n"
        "```\n\n"
        "Validates the repository-local Prompt 5 route/reject envelope, lineage, transport eligibility, diagnostics, authority ownership, and all-false evidence/readiness boundary registry. Responsive remains non-executing; EV4 Project Gate retains transport and downstream gate authority. Success is repository-check evidence only and does not prove external transport, pilot readiness, production/release readiness, export, accessibility, pixel-perfect output, or responsive correctness.\n\n"
        "## Project Gate Prompt 04 Responsive Producer Adoption\n",
    )


def patch_active_index() -> None:
    path = ROOT / "docs/20_ACTIVE_CONTRACT_SCHEMA_VALIDATOR_INDEX.md"
    replace_once(
        path,
        "  responsive_handoff_export_boundary_manifest:\n    path: contracts/RESPONSIVE_HANDOFF_EXPORT_BOUNDARY_MANIFEST.md\n    role: repository-level export eligibility, lineage, artifact-class, and boundary-assertion contract\n",
        "  responsive_handoff_export_boundary_manifest:\n"
        "    path: contracts/RESPONSIVE_HANDOFF_EXPORT_BOUNDARY_MANIFEST.md\n"
        "    role: repository-level export eligibility, lineage, artifact-class, and boundary-assertion contract\n"
        "  project_gate_prompt_5_routing_boundary:\n"
        "    path: contracts/project-gate/PROMPT_5_ROUTING_BOUNDARY.md\n"
        "    role: non-executing local route/reject and Project Gate authority boundary\n",
    )
    replace_once(
        path,
        "  automation_work_package_catalog:\n    path: schemas/ev4-automation-work-package-catalog.schema.json\n    role: catalog-backed Work Package selection schema\n",
        "  automation_work_package_catalog:\n"
        "    path: schemas/ev4-automation-work-package-catalog.schema.json\n"
        "    role: catalog-backed Work Package selection schema\n"
        "  project_gate_prompt_5_routing_envelope:\n"
        "    path: contracts/project-gate/prompt-5-routing-envelope.v1.schema.json\n"
        "    role: fail-closed Prompt 5 route/reject envelope and boundary-claim schema\n",
    )
    replace_once(
        path,
        "    builder_responsive_input_boundary:\n      path: validation/e2e/run_builder_responsive_input_boundary_check.py\n      role: Builder -> Responsive input boundary checks\n",
        "    builder_responsive_input_boundary:\n"
        "      path: validation/e2e/run_builder_responsive_input_boundary_check.py\n"
        "      role: Builder -> Responsive input boundary checks\n"
        "    project_gate_prompt_5_routing_envelope:\n"
        "      path: validation/e2e/run_prompt_5_routing_envelope_check.py\n"
        "      role: Prompt 5 schema, semantic coupling, authority, diagnostics, and all-false boundary checks\n",
    )
    replace_once(
        path,
        "  responsive_contract_drift_sentinel:\n    path: docs/47_RESPONSIVE_CONTRACT_DRIFT_SENTINEL.md\n    role: WP-RESP-006 sentinel behavior, fixtures, CI path, and non-domain-evidence boundary\n",
        "  responsive_contract_drift_sentinel:\n"
        "    path: docs/47_RESPONSIVE_CONTRACT_DRIFT_SENTINEL.md\n"
        "    role: WP-RESP-006 sentinel behavior, fixtures, CI path, and non-domain-evidence boundary\n"
        "  prompt_5_project_gate_routing_boundary:\n"
        "    path: docs/48_PROMPT_5_PROJECT_GATE_ROUTING_BOUNDARY.md\n"
        "    role: WP-RESP-013 local routing capability, external transport limitation, and evidence/readiness boundary\n",
    )


def verify() -> None:
    checks = {
        ROOT / "STATUS.md": [
            "prompt_5_project_gate_routing: implemented_local_validation_non_executing",
            "external_project_gate_transport_implemented_here: false",
            "responsive_correctness: not_claimed",
            "validation/e2e/run_prompt_5_routing_envelope_check.py",
        ],
        ROOT / "docs/17_VALIDATION_COMMAND_INDEX.md": [
            "## Project Gate Prompt 5 routing boundary",
            "python validation/e2e/run_prompt_5_routing_envelope_check.py",
        ],
        ROOT / "docs/20_ACTIVE_CONTRACT_SCHEMA_VALIDATOR_INDEX.md": [
            "project_gate_prompt_5_routing_boundary",
            "project_gate_prompt_5_routing_envelope",
            "validation/e2e/run_prompt_5_routing_envelope_check.py",
        ],
        ROOT / "docs/48_PROMPT_5_PROJECT_GATE_ROUTING_BOUNDARY.md": [
            "Responsive does not execute transport",
            "responsive correctness",
        ],
    }
    for path, needles in checks.items():
        for needle in needles:
            require_contains(path, needle)


if __name__ == "__main__":
    write_doc()
    patch_status()
    patch_command_index()
    patch_active_index()
    verify()
