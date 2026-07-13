#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "STATUS.md"
COMMAND_INDEX = ROOT / "docs/17_VALIDATION_COMMAND_INDEX.md"
ACTIVE_INDEX = ROOT / "docs/20_ACTIVE_CONTRACT_SCHEMA_VALIDATOR_INDEX.md"
STATUS_GUARD = ROOT / "validation/e2e/run_status_merged_foundation_guard_check.py"

RUNTIME_CONTRACT = "contracts/runtime/RUNTIME_MISMATCH_REOPEN_BOUNDARY.md"
RUNTIME_SCHEMA = "contracts/runtime/runtime-mismatch-reopen-package.v1.schema.json"
RUNTIME_VALIDATOR = "validation/e2e/run_runtime_mismatch_reopen_package_check.py"
RUNTIME_COMMAND = f"python {RUNTIME_VALIDATOR}"
RUNTIME_STATUS_GUARD_ENTRY = '    C("run_runtime_mismatch_reopen_package_check.py"),'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected exactly one anchor, found {count}")
    return text.replace(old, new, 1)


def write_text(path: Path, text: str) -> None:
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def update_status() -> None:
    text = STATUS.read_text(encoding="utf-8")
    if RUNTIME_CONTRACT in text or RUNTIME_SCHEMA in text or RUNTIME_VALIDATOR in text:
        raise AssertionError("STATUS.md already contains partial runtime-mismatch parity; refuse ambiguous update")

    text = replace_once(
        text,
        "  - contracts/RESPONSIVE_HANDOFF_EXPORT_BOUNDARY_MANIFEST.md\n"
        "  - contracts/project-gate/PROMPT_5_ROUTING_BOUNDARY.md",
        "  - contracts/RESPONSIVE_HANDOFF_EXPORT_BOUNDARY_MANIFEST.md\n"
        f"  - {RUNTIME_CONTRACT}\n"
        "  - contracts/project-gate/PROMPT_5_ROUTING_BOUNDARY.md",
        "STATUS active contract parity",
    )
    text = replace_once(
        text,
        "  - schemas/ev4-automation-work-package-catalog.schema.json\n"
        "  - contracts/project-gate/prompt-5-routing-envelope.v1.schema.json",
        "  - schemas/ev4-automation-work-package-catalog.schema.json\n"
        f"  - {RUNTIME_SCHEMA}\n"
        "  - contracts/project-gate/prompt-5-routing-envelope.v1.schema.json",
        "STATUS active schema parity",
    )
    text = replace_once(
        text,
        "  - validation/e2e/run_prompt_5_routing_envelope_check.py\n"
        "  - validation/e2e/run_responsive_contract_drift_sentinel_check.py",
        "  - validation/e2e/run_prompt_5_routing_envelope_check.py\n"
        f"  - {RUNTIME_VALIDATOR}\n"
        "  - validation/e2e/run_responsive_contract_drift_sentinel_check.py",
        "STATUS active validator parity",
    )
    text = replace_once(
        text,
        "  - python validation/e2e/run_prompt_5_routing_envelope_check.py\n"
        "  - python validation/e2e/run_responsive_contract_drift_sentinel_check.py",
        "  - python validation/e2e/run_prompt_5_routing_envelope_check.py\n"
        f"  - {RUNTIME_COMMAND}\n"
        "  - python validation/e2e/run_responsive_contract_drift_sentinel_check.py",
        "STATUS CI command parity",
    )
    write_text(STATUS, text)


def update_command_index() -> None:
    text = COMMAND_INDEX.read_text(encoding="utf-8")
    if RUNTIME_COMMAND in text:
        raise AssertionError("validation command index already contains runtime-mismatch command")

    text = replace_once(
        text,
        "Task: `WP-RESP-008/PR-B`\n"
        "Updated by: `automation/wp-resp-008-pr-b-manifest-fixtures-validator`",
        "Task: `WP-RESP-012/PR-B parity reconciliation`\n"
        "Updated by: `automation/wp-resp-005-pr-b-replenish-after-wp015-a`",
        "command-index identity",
    )
    text = replace_once(
        text,
        "python validation/e2e/run_prompt_5_routing_envelope_check.py\n"
        "python validation/e2e/run_responsive_decision_lineage_sequence_check.py",
        "python validation/e2e/run_prompt_5_routing_envelope_check.py\n"
        f"{RUNTIME_COMMAND}\n"
        "python validation/e2e/run_responsive_decision_lineage_sequence_check.py",
        "primary Validate command parity",
    )
    text = replace_once(
        text,
        "python validation/e2e/run_responsive_kernel_receipt_check.py\n"
        "python validation/e2e/run_decision_escape_routes_schema_check.py",
        "python validation/e2e/run_responsive_kernel_receipt_check.py\n"
        f"{RUNTIME_COMMAND}\n"
        "python validation/e2e/run_decision_escape_routes_schema_check.py",
        "manual Kernel command parity",
    )
    text = replace_once(
        text,
        "- Kernel decision lineage and Wave 5 receipt consistency\n"
        "- viewport inheritance/reset decisions",
        "- Kernel decision lineage and Wave 5 receipt consistency\n"
        "- runtime-mismatch reopen lineage, authority, evidence-reference, and all-false boundary validation\n"
        "- viewport inheritance/reset decisions",
        "manual interpretation parity",
    )
    runtime_section = (
        "## Runtime mismatch reopen package\n\n"
        "```bash\n"
        f"{RUNTIME_COMMAND}\n"
        "```\n\n"
        "Validates the bounded runtime-mismatch reopen package, prior Kernel decision lineage, "
        "authoritative-review action, evidence-reference structure, Responsive observation-only authority, "
        "negative fixtures, and the complete all-false evidence/readiness boundary registry. Success is "
        "repository-check evidence only and does not create submitted evidence, authorize a pilot, execute "
        "Project Gate transport, replace a Kernel decision, or prove production, release, export, accessibility, "
        "pixel-perfect, live-render, or responsive-correctness outcomes.\n\n"
    )
    text = replace_once(
        text,
        "## Project Gate Prompt 5 routing boundary\n",
        runtime_section + "## Project Gate Prompt 5 routing boundary\n",
        "runtime-mismatch command section",
    )
    write_text(COMMAND_INDEX, text)


def update_active_index() -> None:
    text = ACTIVE_INDEX.read_text(encoding="utf-8")
    if RUNTIME_CONTRACT in text or RUNTIME_SCHEMA in text or RUNTIME_VALIDATOR in text:
        raise AssertionError("active index already contains partial runtime-mismatch parity")

    text = replace_once(
        text,
        "Task: `WP-RESP-008/PR-B`\n"
        "Updated by: `automation/wp-resp-008-pr-b-manifest-fixtures-validator`",
        "Task: `WP-RESP-012/PR-B parity reconciliation`\n"
        "Updated by: `automation/wp-resp-005-pr-b-replenish-after-wp015-a`",
        "active-index identity",
    )
    text = replace_once(
        text,
        "  responsive_handoff_export_boundary_manifest:\n"
        "    path: contracts/RESPONSIVE_HANDOFF_EXPORT_BOUNDARY_MANIFEST.md\n"
        "    role: repository-level export eligibility, lineage, artifact-class, and boundary-assertion contract\n"
        "  project_gate_prompt_5_routing_boundary:",
        "  responsive_handoff_export_boundary_manifest:\n"
        "    path: contracts/RESPONSIVE_HANDOFF_EXPORT_BOUNDARY_MANIFEST.md\n"
        "    role: repository-level export eligibility, lineage, artifact-class, and boundary-assertion contract\n"
        "  runtime_mismatch_reopen_boundary:\n"
        f"    path: {RUNTIME_CONTRACT}\n"
        "    role: bounded runtime-observation and authoritative-reopen request boundary without Responsive redecision authority\n"
        "  project_gate_prompt_5_routing_boundary:",
        "active contract index parity",
    )
    text = replace_once(
        text,
        "  automation_work_package_catalog:\n"
        "    path: schemas/ev4-automation-work-package-catalog.schema.json\n"
        "    role: catalog-backed Work Package selection schema\n"
        "  project_gate_prompt_5_routing_envelope:",
        "  automation_work_package_catalog:\n"
        "    path: schemas/ev4-automation-work-package-catalog.schema.json\n"
        "    role: catalog-backed Work Package selection schema\n"
        "  runtime_mismatch_reopen_package:\n"
        f"    path: {RUNTIME_SCHEMA}\n"
        "    role: fail-closed runtime-mismatch reopen package and evidence/readiness boundary schema\n"
        "  project_gate_prompt_5_routing_envelope:",
        "active schema index parity",
    )
    text = replace_once(
        text,
        "    project_gate_prompt_5_routing_envelope:\n"
        "      path: validation/e2e/run_prompt_5_routing_envelope_check.py\n"
        "      role: Prompt 5 schema, semantic coupling, authority, diagnostics, and all-false boundary checks\n"
        "    responsive_contract_drift_sentinel:",
        "    project_gate_prompt_5_routing_envelope:\n"
        "      path: validation/e2e/run_prompt_5_routing_envelope_check.py\n"
        "      role: Prompt 5 schema, semantic coupling, authority, diagnostics, and all-false boundary checks\n"
        "    runtime_mismatch_reopen_package:\n"
        f"      path: {RUNTIME_VALIDATOR}\n"
        "      role: runtime-mismatch schema, lineage, authoritative-review action, authority, negative-fixture, and all-false boundary checks\n"
        "    responsive_contract_drift_sentinel:",
        "primary validator index parity",
    )
    write_text(ACTIVE_INDEX, text)


def update_status_guard() -> None:
    text = STATUS_GUARD.read_text(encoding="utf-8")
    if RUNTIME_STATUS_GUARD_ENTRY in text:
        raise AssertionError("STATUS guard already contains runtime-mismatch command")
    text = replace_once(
        text,
        '    C("run_prompt_5_routing_envelope_check.py"),\n'
        '    C("run_responsive_contract_drift_sentinel_check.py"),',
        '    C("run_prompt_5_routing_envelope_check.py"),\n'
        f"{RUNTIME_STATUS_GUARD_ENTRY}\n"
        '    C("run_responsive_contract_drift_sentinel_check.py"),',
        "STATUS guard primary-chain parity",
    )
    write_text(STATUS_GUARD, text)


def verify() -> None:
    status = STATUS.read_text(encoding="utf-8")
    commands = COMMAND_INDEX.read_text(encoding="utf-8")
    active = ACTIVE_INDEX.read_text(encoding="utf-8")
    guard = STATUS_GUARD.read_text(encoding="utf-8")

    for reference in (RUNTIME_CONTRACT, RUNTIME_SCHEMA, RUNTIME_VALIDATOR, RUNTIME_COMMAND):
        if reference not in status:
            raise AssertionError(f"STATUS.md missing required parity reference: {reference}")
    if commands.count(RUNTIME_COMMAND) < 3:
        raise AssertionError("validation command index must contain primary, manual, and dedicated runtime-mismatch commands")
    for reference in (RUNTIME_CONTRACT, RUNTIME_SCHEMA, RUNTIME_VALIDATOR):
        if reference not in active:
            raise AssertionError(f"active index missing required parity reference: {reference}")
    if RUNTIME_STATUS_GUARD_ENTRY not in guard:
        raise AssertionError("STATUS guard missing runtime-mismatch command")
    for text in (status, commands, active, guard):
        if "production_ready: true" in text or "responsive_correctness_validated: true" in text:
            raise AssertionError("forbidden stronger claim introduced")


def main() -> int:
    update_status()
    update_command_index()
    update_active_index()
    update_status_guard()
    verify()
    print("PR #179 WP-RESP-012 documentation, STATUS, and guard parity repair: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
