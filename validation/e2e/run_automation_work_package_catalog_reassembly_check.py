#!/usr/bin/env python3
"""Deterministically generate and validate the modular Work Package Catalog."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MONOLITH = ROOT / "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json"
INDEX = ROOT / "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG_INDEX.json"
PACKAGE_DIR = ROOT / "planning/work-packages"
ID_RE = re.compile(r"^WP-RESP-(\d{3})$")
FALSE_BOUNDARIES = {
    "submitted_evidence_created_by_catalog",
    "issue_8_mutation_allowed_by_catalog",
    "real_pilot_execution_allowed_by_catalog",
    "catalog_completion_is_evidence_validation",
    "ci_success_is_responsive_correctness_evidence",
    "production_ready",
    "release_ready",
    "live_render_validated",
    "export_json_validated",
    "accessibility_passed",
    "pixel_perfect",
    "responsive_correctness_validated",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicates)


def _reject_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def canonical_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def ordered_ids(work_packages: dict) -> list[str]:
    ids = list(work_packages)
    for package_id in ids:
        if not ID_RE.fullmatch(package_id):
            raise ValueError(f"invalid Work Package ID: {package_id}")
    ordered = sorted(ids, key=lambda item: int(ID_RE.fullmatch(item).group(1)))
    if ids != ordered:
        raise ValueError("monolith Work Package order is not canonical ascending numeric order")
    return ordered


def expected_projection(catalog: dict):
    boundaries = catalog.get("global_boundaries", {})
    if set(boundaries) != FALSE_BOUNDARIES or any(boundaries.values()):
        raise ValueError("global evidence/readiness boundaries must remain complete and false")
    package_files = {}
    entries = []
    for package_id in ordered_ids(catalog["work_packages"]):
        record = catalog["work_packages"][package_id]
        if record.get("id") != package_id:
            raise ValueError(f"monolith key/id mismatch: {package_id}")
        wrapper = {
            "schema": "ev4-automation-work-package-file@1.0.0",
            "id": package_id,
            "work_package": record,
        }
        data = canonical_bytes(wrapper)
        relative = f"planning/work-packages/{package_id}.json"
        package_files[relative] = data
        entries.append({
            "id": package_id,
            "path": relative,
            "schema": "ev4-automation-work-package-file@1.0.0",
            "content_sha256": hashlib.sha256(data).hexdigest(),
        })
    index = {
        "schema": "ev4-automation-work-package-catalog-index@1.0.0",
        "project": catalog["project"],
        "authority_mode": "monolith_canonical_modular_shadow",
        "canonical_catalog_path": "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json",
        "package_directory": "planning/work-packages",
        "ordering": {
            "key": "work_package_id_numeric_suffix",
            "direction": "ascending",
            "duplicate_ids_forbidden": True,
            "missing_entries_forbidden": True,
            "unindexed_files_forbidden": True,
        },
        "package_entries": entries,
        "global_boundaries": boundaries,
    }
    return index, package_files


def validate_projection(root: Path = ROOT) -> None:
    catalog = load_json(root / MONOLITH.relative_to(ROOT))
    expected_index, expected_files = expected_projection(catalog)
    actual_index_path = root / INDEX.relative_to(ROOT)
    if actual_index_path.read_bytes() != canonical_bytes(expected_index):
        raise ValueError("catalog index file is not canonical or has drifted from deterministic monolith projection")
    actual_index = load_json(actual_index_path)
    indexed_paths = [entry["path"] for entry in actual_index["package_entries"]]
    if len(indexed_paths) != len(set(indexed_paths)):
        raise ValueError("duplicate indexed package path")
    package_directory = root / PACKAGE_DIR.relative_to(ROOT)
    actual_paths = sorted(
        str(path.relative_to(root)).replace("\\", "/")
        for path in package_directory.iterdir()
        if path.is_file()
    )
    if actual_paths != sorted(expected_files):
        raise ValueError("missing indexed package file or unindexed package file")
    reassembled = copy.deepcopy(catalog)
    reassembled["work_packages"] = {}
    for entry in actual_index["package_entries"]:
        path = root / entry["path"]
        raw = path.read_bytes()
        if raw != expected_files[entry["path"]]:
            raise ValueError(f"non-canonical or drifted package file: {entry['path']}")
        if hashlib.sha256(raw).hexdigest() != entry["content_sha256"]:
            raise ValueError(f"content hash mismatch: {entry['path']}")
        wrapper = load_json(path)
        filename_id = path.stem
        if not (entry["id"] == filename_id == wrapper["id"] == wrapper["work_package"]["id"]):
            raise ValueError(f"ID/path/wrapper mismatch: {entry['path']}")
        reassembled["work_packages"][entry["id"]] = wrapper["work_package"]
    if reassembled != catalog:
        raise ValueError("round-trip reassembly differs from canonical catalog")


def write_projection() -> None:
    catalog = load_json(MONOLITH)
    index, package_files = expected_projection(catalog)
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    for stale in PACKAGE_DIR.iterdir():
        if stale.is_file() and str(stale.relative_to(ROOT)).replace("\\", "/") not in package_files:
            stale.unlink()
    for relative, data in package_files.items():
        (ROOT / relative).write_bytes(data)
    INDEX.write_bytes(canonical_bytes(index))
    validate_projection()


def assert_rejected(root: Path, message: str) -> None:
    try:
        validate_projection(root)
    except ValueError:
        return
    raise AssertionError(message)


def self_test() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "planning/work-packages").mkdir(parents=True)
        catalog = load_json(MONOLITH)
        index, files = expected_projection(catalog)
        index_path = root / "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG_INDEX.json"
        (root / "planning/EV4_AUTOMATION_WORK_PACKAGE_CATALOG.json").write_bytes(canonical_bytes(catalog))
        index_path.write_bytes(canonical_bytes(index))
        for relative, data in files.items():
            (root / relative).write_bytes(data)
        validate_projection(root)

        first_relative = index["package_entries"][0]["path"]
        first = root / first_relative
        first.write_bytes(first.read_bytes() + b" ")
        assert_rejected(root, "negative non-canonical package fixture was accepted")
        first.write_bytes(files[first_relative])

        index_path.write_bytes(index_path.read_bytes() + b" ")
        assert_rejected(root, "negative non-canonical index was accepted")
        index_path.write_bytes(canonical_bytes(index))

        extra = root / "planning/work-packages/EXTRA.json"
        extra.write_text("{}\n", encoding="utf-8")
        assert_rejected(root, "negative unindexed package-directory file was accepted")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.write:
        write_projection()
    else:
        validate_projection()
    if args.self_test:
        self_test()
    print("automation work package catalog reassembly: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
