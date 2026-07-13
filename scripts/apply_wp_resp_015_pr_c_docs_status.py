#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "STATUS.md"
COMMAND_INDEX = ROOT / "docs/17_VALIDATION_COMMAND_INDEX.md"
ACTIVE_INDEX = ROOT / "docs/20_ACTIVE_CONTRACT_SCHEMA_VALIDATOR_INDEX.md"
DOC = ROOT / "docs/49_RUNTIME_MISMATCH_PROMPT_5_ROUTING_COMPATIBILITY.md"

EXPECTED_BLOBS = {
    STATUS: "59318b68c1bfff25c27a06751e8e204a41cb1902",
    COMMAND_INDEX: "c13303fc7077f8fad1ae67f144add45149d7aaf3",
    ACTIVE_INDEX: "a3caca79467b8b73121745c63025bf4289cfe659",
}


def blob_sha(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], cwd=ROOT, text=True).strip()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected exactly one anchor, found {count}")
    return text.replace(old, new, 1)


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


for path, expected in EXPECTED_BLOBS.items():
    actual = blob_sha(path)
    if actual != expected:
        raise AssertionError(f"preimage drift for {path.relative_to(ROOT)}: {actual} != {expected}")
if DOC.exists():
    raise AssertionError(f"unexpected existing document: {DOC.relative_to(ROOT)}")

status = STATUS.read_text(encoding="utf-8")
status = replace_once(
    status,
    "  - contracts/project-gate/PROMPT_5_ROUTING_BOUNDARY.md\n",
    "  - contracts/project-gate/PROMPT_5_ROUTING_BOUNDARY.md\n"
    "  - contracts/compatibility/RUNTIME_MISMATCH_PROMPT_5_ROUTING_COMPATIBILITY.md\n",
    "STATUS active contract",
)
status = replace_once(
    status,
    "  - contracts/project-gate/prompt-5-routing-envelope.v1.schema.json\n",
    "  - contracts/project-gate/prompt-5-routing-envelope.v1.schema.json\n"
    "  - contracts/compatibility/runtime-mismatch-prompt-5-routing-compatibility.v1.schema.json\n",
    "STATUS active schema",
)
status = replace_once(
    status,
    "  - validation/e2e/run_runtime_mismatch_reopen_package_check.py\n",
    "  - validation/e2e/run_runtime_mismatch_reopen_package_check.py\n"
    "  - validation/e2e/run_runtime_mismatch_prompt_5_compatibility_check.py\n",
    "STATUS active validator",
)
status = replace_once(
    status,
    "  - docs/48_PROMPT_5_PROJECT_GATE_ROUTING_BOUNDARY.md\n",
    "  - docs/48_PROMPT_5_PROJECT_GATE_ROUTING_BOUNDARY.md\n"
    "  - docs/49_RUNTIME_MISMATCH_PROMPT_5_ROUTING_COMPATIBILITY.md\n",
    "STATUS controlled-use document",
)
status = replace_once(
    status,
    "  prompt_5_routing_fixtures: validation/fixtures/prompt05\n",
    "  prompt_5_routing_fixtures: validation/fixtures/prompt05\n"
    "  runtime_mismatch_prompt_5_compatibility: implemented_repository_local_fail_closed\n"
    "  runtime_mismatch_prompt_5_compatibility_contract: contracts/compatibility/RUNTIME_MISMATCH_PROMPT_5_ROUTING_COMPATIBILITY.md\n"
    "  runtime_mismatch_prompt_5_compatibility_schema: contracts/compatibility/runtime-mismatch-prompt-5-routing-compatibility.v1.schema.json\n"
    "  runtime_mismatch_prompt_5_compatibility_validator: validation/e2e/run_runtime_mismatch_prompt_5_compatibility_check.py\n"
    "  runtime_mismatch_prompt_5_compatibility_ci_path: invoked_by_runtime_mismatch_reopen_package_validator\n",
    "STATUS Prompt 5 compatibility block",
)
write(STATUS, status)

command_index = COMMAND_INDEX.read_text(encoding="utf-8")
command_index = replace_once(
    command_index,
    "Task: `WP-RESP-012/PR-B parity reconciliation`\nUpdated by: `automation/wp-resp-005-pr-b-replenish-after-wp015-a`\n",
    "Task: `WP-RESP-015/PR-C compatibility documentation and STATUS parity`\n"
    "Updated by: `automation/wp-resp-015-pr-c-compatibility-docs-status`\n",
    "command-index header",
)
compat_section = """

## Runtime-mismatch reopen to Prompt 5 routing compatibility

```bash
python validation/e2e/run_runtime_mismatch_prompt_5_compatibility_check.py
```

Validates the repository-local compatibility contract between `runtime-mismatch-reopen-package.v1` and `prompt-5-routing-envelope.v1`. It checks pinned dependency identities, shared Kernel and producer-export lineage, the exact `reopen_for_authoritative_review` action, eligible routing to `ev4-project-gate`, empty rejection diagnostics for a compatible route, authority ownership, negative drift cases, and the complete all-false evidence/readiness boundary registry.

The primary `Validate` workflow reaches this check transitively through `run_runtime_mismatch_reopen_package_check.py`; the direct command above is supported for focused manual diagnosis. Success is repository-check evidence only. It does not execute Project Gate transport, replace or reinterpret a Kernel decision, create submitted evidence, authorize a pilot, or prove production, release, live-render, export, accessibility, pixel-perfect, or responsive-correctness outcomes.
"""
command_index = replace_once(
    command_index,
    "\n## Project Gate Prompt 04 Responsive Producer Adoption\n",
    compat_section + "\n## Project Gate Prompt 04 Responsive Producer Adoption\n",
    "command-index compatibility section",
)
write(COMMAND_INDEX, command_index)

active_index = ACTIVE_INDEX.read_text(encoding="utf-8")
active_index = replace_once(
    active_index,
    "Task: `WP-RESP-012/PR-B parity reconciliation`\nUpdated by: `automation/wp-resp-005-pr-b-replenish-after-wp015-a`\n",
    "Task: `WP-RESP-015/PR-C compatibility documentation and STATUS parity`\n"
    "Updated by: `automation/wp-resp-015-pr-c-compatibility-docs-status`\n",
    "active-index header",
)
active_index = replace_once(
    active_index,
    "  project_gate_prompt_5_routing_boundary:\n    path: contracts/project-gate/PROMPT_5_ROUTING_BOUNDARY.md\n    role: non-executing local route/reject and Project Gate authority boundary\n",
    "  project_gate_prompt_5_routing_boundary:\n    path: contracts/project-gate/PROMPT_5_ROUTING_BOUNDARY.md\n    role: non-executing local route/reject and Project Gate authority boundary\n"
    "  runtime_mismatch_prompt_5_routing_compatibility:\n"
    "    path: contracts/compatibility/RUNTIME_MISMATCH_PROMPT_5_ROUTING_COMPATIBILITY.md\n"
    "    role: repository-local compatibility boundary for authoritative reopen routing without transport execution or Kernel authority substitution\n",
    "active-index contract",
)
active_index = replace_once(
    active_index,
    "  project_gate_prompt_5_routing_envelope:\n    path: contracts/project-gate/prompt-5-routing-envelope.v1.schema.json\n    role: fail-closed Prompt 5 route/reject envelope and boundary-claim schema\n",
    "  project_gate_prompt_5_routing_envelope:\n    path: contracts/project-gate/prompt-5-routing-envelope.v1.schema.json\n    role: fail-closed Prompt 5 route/reject envelope and boundary-claim schema\n"
    "  runtime_mismatch_prompt_5_routing_compatibility:\n"
    "    path: contracts/compatibility/runtime-mismatch-prompt-5-routing-compatibility.v1.schema.json\n"
    "    role: pinned dependency, lineage, action, diagnostic, authority, and all-false boundary compatibility schema\n",
    "active-index schema",
)
active_index = replace_once(
    active_index,
    "    runtime_mismatch_reopen_package:\n      path: validation/e2e/run_runtime_mismatch_reopen_package_check.py\n      role: runtime-mismatch schema, lineage, authoritative-review action, authority, negative-fixture, and all-false boundary checks\n",
    "    runtime_mismatch_reopen_package:\n      path: validation/e2e/run_runtime_mismatch_reopen_package_check.py\n      role: runtime-mismatch schema, lineage, authoritative-review action, authority, negative-fixture, and all-false boundary checks; invokes the Prompt 5 compatibility validator\n"
    "    runtime_mismatch_prompt_5_routing_compatibility:\n"
    "      path: validation/e2e/run_runtime_mismatch_prompt_5_compatibility_check.py\n"
    "      role: focused dependency-pin, shared-lineage, action, route, diagnostic, authority, drift, and boundary compatibility checks\n"
    "      ci_path: transitively invoked by runtime_mismatch_reopen_package in the primary Validate chain\n",
    "active-index validator",
)
active_index = replace_once(
    active_index,
    "  prompt_5_project_gate_routing_boundary:\n    path: docs/48_PROMPT_5_PROJECT_GATE_ROUTING_BOUNDARY.md\n    role: WP-RESP-013 local routing capability, external transport limitation, and evidence/readiness boundary\n",
    "  prompt_5_project_gate_routing_boundary:\n    path: docs/48_PROMPT_5_PROJECT_GATE_ROUTING_BOUNDARY.md\n    role: WP-RESP-013 local routing capability, external transport limitation, and evidence/readiness boundary\n"
    "  runtime_mismatch_prompt_5_routing_compatibility:\n"
    "    path: docs/49_RUNTIME_MISMATCH_PROMPT_5_ROUTING_COMPATIBILITY.md\n"
    "    role: WP-RESP-015 compatibility guarantees, validator path, authority ownership, and preserved evidence/readiness limitations\n",
    "active-index controlled-use doc",
)
write(ACTIVE_INDEX, active_index)

doc = """# Runtime-Mismatch Reopen to Prompt 5 Routing Compatibility

Work Package: `WP-RESP-015`
Slice: `WP-RESP-015/PR-C`

## Purpose

This document records the repository-local compatibility boundary between a runtime-mismatch authoritative-reopen request and the Prompt 5 Project Gate routing envelope. It documents implemented contract, schema, fixture, validator, and CI behavior; it does not execute external transport or establish domain correctness.

## Active artifacts

| Surface | Path | Role |
|---|---|---|
| Compatibility contract | `contracts/compatibility/RUNTIME_MISMATCH_PROMPT_5_ROUTING_COMPATIBILITY.md` | Human-readable authority and compatibility boundary |
| Compatibility schema | `contracts/compatibility/runtime-mismatch-prompt-5-routing-compatibility.v1.schema.json` | Pinned dependency, lineage, action, route, diagnostic, authority, and boundary shape |
| Positive fixture | `validation/fixtures/compatibility/runtime-mismatch-prompt5/valid/runtime_mismatch_prompt5_compatibility.valid.json` | Canonical compatible reopen-to-route example |
| Negative fixture | `validation/fixtures/compatibility/runtime-mismatch-prompt5/invalid/runtime_mismatch_prompt5_missing_lineage.invalid.json` | Persistent missing-lineage rejection example |
| Focused validator | `validation/e2e/run_runtime_mismatch_prompt_5_compatibility_check.py` | Schema and semantic compatibility checks plus deterministic negative self-tests |
| Primary CI entry | `validation/e2e/run_runtime_mismatch_reopen_package_check.py` | Invokes the focused compatibility validator from the primary `Validate` workflow |

## Compatibility guarantees

A compatible package must:

1. pin the runtime-mismatch and Prompt 5 dependency identities, versions, blob identities, and schema hashes;
2. preserve shared Kernel decision lineage and producer-export lineage;
3. request exactly `reopen_for_authoritative_review`;
4. map to `decision=route`, `transport_eligible=true`, and target `ev4-project-gate`;
5. carry no rejection diagnostic for the compatible route;
6. keep EV4 Decision Kernel as decision owner and EV4 Project Gate as transport owner;
7. forbid Responsive from replacing or reinterpreting the Kernel decision or executing Project Gate transport; and
8. keep every evidence, pilot, readiness, release, export, accessibility, pixel, and responsive-correctness claim false.

The validator also fails closed on missing lineage, rejected-option drift, invalid evidence references, unsupported action, diagnostic mismatch, authority substitution, dependency schema-version drift, and boundary upgrades.

## Validation

Focused command:

```bash
python validation/e2e/run_runtime_mismatch_prompt_5_compatibility_check.py
```

Primary-chain command:

```bash
python validation/e2e/run_runtime_mismatch_reopen_package_check.py
```

The primary command runs the runtime-mismatch package checks and then invokes the focused compatibility validator. `.github/workflows/validate.yml` runs the primary command on the supported Python matrix.

## Authority boundary

| Concern | Authority |
|---|---|
| Original or replacement technical decision | EV4 Decision Kernel |
| Local route eligibility | EV4 Responsive Architect |
| Transport execution and downstream gate behavior | EV4 Project Gate |

Responsive may observe a mismatch and package an authoritative-review request. It may not claim that transport occurred, author a replacement decision, or treat receipt or diagnostic prose as Kernel authority.

## Evidence and readiness boundary

Validation success, schema validity, fixture acceptance, CI success, PR review, or merge are repository-check evidence only. They do not:

- create submitted evidence or mutate Issue #8;
- authorize or run a real pilot;
- prove production or release readiness;
- prove live-render or export validity;
- prove accessibility conformance or pixel-perfect output; or
- prove responsive correctness.

All corresponding claims remain false until separate real-evidence gates and explicit authority permit an upgrade.
"""
write(DOC, doc)

# Parse all touched JSON-adjacent sources indirectly through their validators and
# run the targeted parity boundary before committing.
subprocess.run(["python", "validation/e2e/run_runtime_mismatch_prompt_5_compatibility_check.py"], cwd=ROOT, check=True)
subprocess.run(["python", "validation/e2e/run_runtime_mismatch_reopen_package_check.py"], cwd=ROOT, check=True)
subprocess.run(["python", "validation/e2e/run_responsive_contract_drift_sentinel_check.py"], cwd=ROOT, check=True)
subprocess.run(["python", "validation/e2e/run_status_merged_foundation_guard_check.py"], cwd=ROOT, check=True)
