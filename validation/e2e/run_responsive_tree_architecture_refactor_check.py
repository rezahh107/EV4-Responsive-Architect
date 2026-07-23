import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / 'schemas/ev4-responsive-output.schema.json'
VALID_DIR = ROOT / 'validation/fixtures/valid'
INVALID_DIR = ROOT / 'validation/fixtures/invalid'
OWNERSHIP_INVENTORY = ROOT / 'validation/fixtures/fixture_schema_ownership.json'

VALID_FIXTURES = [
    VALID_DIR / 'responsive_output_same_tree.valid.json',
    VALID_DIR / 'responsive_output_viewport_tree.valid.json',
    VALID_DIR / 'responsive_output_hybrid.valid.json',
    VALID_DIR / 'responsive_output_blocked.valid.json',
]

INVALID_FIXTURES = [
    INVALID_DIR / 'responsive_output_missing_forbidden_claims.invalid.json',
    INVALID_DIR / 'responsive_output_empty_steps.invalid.json',
    INVALID_DIR / 'responsive_output_duplicate_step_id.invalid.json',
    INVALID_DIR / 'responsive_output_route_mode_mismatch.invalid.json',
    INVALID_DIR / 'responsive_output_builder_mode_mismatch.invalid.json',
    INVALID_DIR / 'responsive_output_noncanonical_breakpoint_scope.invalid.json',
    INVALID_DIR / 'responsive_output_unresolved_ready_mismatch.invalid.json',
    INVALID_DIR / 'responsive_output_dropped_decision_lineage.invalid.json',
    INVALID_DIR / 'responsive_output_replaced_decision_lineage.invalid.json',
    INVALID_DIR / 'responsive_output_runtime_conflict_redesign.invalid.json',
    INVALID_DIR / 'responsive_output_evidence_state_insufficient.invalid.json',
    INVALID_DIR / 'responsive_output_evidence_state_provided.invalid.json',
    INVALID_DIR / 'responsive_output_missing_evidence_state.invalid.json',
]

REQUIRED_FILES = [
    ROOT / 'docs/RESPONSIVE_TREE_ARCHITECTURE_REFACTOR_v0.3.0.md',
    ROOT / 'contracts/EV4_RESPONSIVE_TREE_ARCHITECTURE_CONTRACT.md',
    ROOT / 'contracts/EV4_VIEWPORT_RELATIONSHIP_CLASSIFICATION_CONTRACT.md',
    ROOT / 'contracts/EV4_RESPONSIVE_STRATEGY_ROUTING_CONTRACT.md',
    ROOT / 'contracts/EV4_VIEWPORT_DISPLAY_CONTRACT.md',
    ROOT / 'contracts/EV4_RESPONSIVE_HANDOFF_EXPORT_CONTRACT.md',
    ROOT / 'stages/00_RESPONSIVE_START_PACKET_INGEST.md',
    ROOT / 'stages/01_RESPONSIVE_DESIGN_INTAKE.md',
    ROOT / 'stages/02_VIEWPORT_SOURCE_LEDGER.md',
    ROOT / 'stages/03_SECTION_RELATIONSHIP_CLASSIFICATION.md',
    ROOT / 'stages/04_ELEMENTOR_STRATEGY_ROUTING.md',
    ROOT / 'stages/05_RESPONSIVE_TREE_OWNERSHIP_CONTRACT.md',
    ROOT / 'stages/06A_SAME_TREE_RESPONSIVE_DERIVATION.md',
    ROOT / 'stages/06B_VIEWPORT_TREE_ARCHITECTURE.md',
    ROOT / 'stages/06C_COMPOSITE_RESPONSIVE_PLAN.md',
    ROOT / 'stages/07_DISPLAY_AND_BREAKPOINT_CONTRACT.md',
    ROOT / 'stages/08_CONTENT_ACCESSIBILITY_DUPLICATION_GATE.md',
    ROOT / 'stages/09_RESPONSIVE_BUILDER_HANDOFF.md',
    ROOT / 'stages/10_RESPONSIVE_VALIDATION_PLAN.md',
    ROOT / 'stages/11_RESPONSIVE_FINAL_REVIEW.md',
    ROOT / 'stages/12_RESPONSIVE_OUTPUT_PACKAGE.md',
    SCHEMA,
    OWNERSHIP_INVENTORY,
    ROOT / 'manifests/ev4-responsive-pipeline-manifest.v1.json',
    ROOT / 'schemas/ev4-responsive-stage-payload.v1.schema.json',
    ROOT / 'schemas/ev4-responsive-viewport-source-ledger.v1.schema.json',
    ROOT / 'contracts/project-gate/producer-gate-export.v1.lock.json',
    ROOT / 'registries/breakpoint-profiles.v1.json',
    *VALID_FIXTURES,
    *INVALID_FIXTURES,
]

REQUIRED_TERMS = [
    'design_to_responsive_tree',
    'same_tree_responsive_overrides',
    'viewport_specific_variant_tree',
    'hybrid_split_architecture',
    'blocked_pending_input',
]

ROUTE_TO_MODE = {
    'same_tree_responsive_overrides': 'same_tree',
    'viewport_specific_variant_tree': 'viewport_tree',
    'hybrid_split_architecture': 'hybrid',
    'blocked_pending_input': 'blocked',
}

EXPECTED_ROUTES = {
    'same_tree_responsive_overrides',
    'viewport_specific_variant_tree',
    'hybrid_split_architecture',
    'blocked_pending_input',
}

EXPECTED_BREAKPOINT_SCOPE = {
    'desktop': '>=1025px',
    'tablet': '768px-1024px',
    'mobile': '<=767px',
}

QUEUE_CHECKS = [
    'validation/e2e/run_rolling_queue_check.py',
    'validation/e2e/run_run_ledger_check.py',
    'validation/e2e/run_task_quality_gate_check.py',
    'validation/e2e/run_submitted_packet_eligibility_gate_check.py',
    'validation/e2e/run_rtaq_ssot_guard_check.py',
]


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def load_ownership_inventory():
    inventory = load_json(OWNERSHIP_INVENTORY)
    if not isinstance(inventory, dict):
        raise ValueError('Fixture ownership inventory must be a JSON object')
    for fixture_path, schema_file in inventory.items():
        if not isinstance(fixture_path, str) or not fixture_path:
            raise ValueError('Fixture ownership inventory has an invalid fixture path')
        if not isinstance(schema_file, str) or not schema_file or '/' in schema_file or '\\' in schema_file:
            raise ValueError(f'Fixture ownership inventory has an invalid schema reference: {fixture_path}')
    return inventory


def load_fixture_payload(path, ownership_inventory):
    raw = load_json(path)
    if not isinstance(raw, dict):
        raise ValueError(f'Fixture must be a JSON object: {relative_path(path)}')

    payload = dict(raw)
    if '$schema_files' in payload:
        raise ValueError(f'Forbidden duplicate-owner $schema_files metadata: {relative_path(path)}')

    metadata_schema = payload.pop('$schema_file', None)
    rel = relative_path(path).as_posix()
    sidecar_schema = ownership_inventory.get(rel)
    if metadata_schema is not None and sidecar_schema is not None:
        raise ValueError(f'Duplicate fixture ownership metadata: {relative_path(path)}')

    schema_file = metadata_schema if metadata_schema is not None else sidecar_schema
    if not isinstance(schema_file, str) or not schema_file:
        raise ValueError(f'Missing or malformed fixture ownership metadata: {relative_path(path)}')
    if '/' in schema_file or '\\' in schema_file:
        raise ValueError(f'Noncanonical fixture ownership schema reference: {relative_path(path)}')
    if schema_file != SCHEMA.name:
        raise ValueError(
            f'Wrong fixture ownership schema for {relative_path(path)}: '
            f'expected={SCHEMA.name}, actual={schema_file}'
        )
    return payload


def relative_path(path):
    return path.relative_to(ROOT)


def expected_invalid_reason(path):
    name = path.name
    if name == 'responsive_output_missing_forbidden_claims.invalid.json':
        return 'Schema validation failed'
    if name == 'responsive_output_empty_steps.invalid.json':
        return 'builder_handoff.steps cannot be empty'
    if name == 'responsive_output_duplicate_step_id.invalid.json':
        return 'Duplicate step_ids'
    if name == 'responsive_output_route_mode_mismatch.invalid.json':
        return 'Route/mode mismatch'
    if name == 'responsive_output_builder_mode_mismatch.invalid.json':
        return 'Builder handoff mode mismatch'
    if name == 'responsive_output_noncanonical_breakpoint_scope.invalid.json':
        return 'Noncanonical breakpoint scope'
    if name == 'responsive_output_unresolved_ready_mismatch.invalid.json':
        return 'Final review readiness mismatch'
    if name == 'responsive_output_dropped_decision_lineage.invalid.json':
        return 'Schema validation failed'
    if name == 'responsive_output_replaced_decision_lineage.invalid.json':
        return 'EV4_RESPONSIVE_DECISION_LINEAGE_REPLACED'
    if name == 'responsive_output_runtime_conflict_redesign.invalid.json':
        return 'EV4_RESPONSIVE_RUNTIME_CONFLICT_REDESIGN_FORBIDDEN'
    if name in {
        'responsive_output_evidence_state_insufficient.invalid.json',
        'responsive_output_evidence_state_provided.invalid.json',
    }:
        return 'EV4_RESPONSIVE_DECISION_LINEAGE_EVIDENCE_STATE_WEAKENED'
    if name == 'responsive_output_missing_evidence_state.invalid.json':
        return 'Schema validation failed'
    raise ValueError(f'No expected invalid failure registered for {relative_path(path)}')


def assert_required_files():
    missing = [str(relative_path(path)) for path in REQUIRED_FILES if not path.is_file()]
    if missing:
        raise ValueError('Missing responsive tree files: ' + ', '.join(missing))


def assert_required_terms():
    combined_text = '\n'.join(path.read_text(encoding='utf-8') for path in REQUIRED_FILES)
    missing_terms = [term for term in REQUIRED_TERMS if term not in combined_text]
    if missing_terms:
        raise ValueError('Missing required responsive tree terms: ' + ', '.join(missing_terms))


def assert_step_integrity(payload, path):
    steps = (payload.get('builder_handoff') or {}).get('steps', [])
    if not steps:
        raise ValueError(f'builder_handoff.steps cannot be empty: {path}')

    step_ids = []
    for index, step in enumerate(steps, start=1):
        step_id = step.get('step_id')
        if not step_id:
            raise ValueError(f'Missing step_id at index {index} in {path}')
        step_ids.append(step_id)

    if len(step_ids) != len(set(step_ids)):
        raise ValueError(f'Duplicate step_ids in {path}')

    first_prefix = None
    for index, step_id in enumerate(step_ids, start=1):
        prefix, sep, suffix = step_id.partition('-')
        if not prefix or sep != '-' or not suffix.isdigit():
            raise ValueError(f'Invalid step_id format: {step_id} in {path}')
        if first_prefix is None:
            first_prefix = prefix
        elif prefix != first_prefix:
            raise ValueError(f'Inconsistent step_id prefix: expected {first_prefix}, got {prefix} in {path}')
        if int(suffix) != index:
            raise ValueError(f'Non-sequential step_id: {step_id} in {path}')


def assert_route_mode(payload, path):
    route = payload.get('selected_route')
    mode = (payload.get('responsive_tree_output') or {}).get('mode')
    expected = ROUTE_TO_MODE.get(route)
    if mode != expected:
        raise ValueError(f'Route/mode mismatch in {path}: route={route}, mode={mode}, expected={expected}')


def assert_builder_handoff_mode(payload, path):
    route = payload.get('selected_route')
    handoff_mode = (payload.get('builder_handoff') or {}).get('mode')
    if handoff_mode != route:
        raise ValueError(
            f'Builder handoff mode mismatch in {path}: route={route}, builder_handoff.mode={handoff_mode}'
        )


def assert_breakpoint_scope(payload, path):
    scope = (payload.get('display_contract') or {}).get('breakpoint_scope', {})
    if scope != EXPECTED_BREAKPOINT_SCOPE:
        raise ValueError(
            f'Noncanonical breakpoint scope in {path}: expected={EXPECTED_BREAKPOINT_SCOPE}, actual={scope}'
        )


def assert_final_review_consistency(payload, path):
    final_review = payload.get('final_review') or {}
    handoff_ready = final_review.get('handoff_ready')
    unresolved_unknowns = payload.get('unresolved_unknowns') or []
    classification = (payload.get('relationship_classification_ref') or {}).get('classification')
    blocked_route = payload.get('selected_route') == 'blocked_pending_input'
    unresolved_classification = classification == 'unresolved_requires_designer_input'

    if handoff_ready and (blocked_route or unresolved_classification or unresolved_unknowns):
        raise ValueError(
            f'Final review readiness mismatch in {path}: handoff_ready=true cannot coexist with '
            f'blocked_route={blocked_route}, unresolved_classification={unresolved_classification}, '
            f'unresolved_unknowns={len(unresolved_unknowns)}'
        )


def assert_decision_lineage(payload, path):
    lineage = payload.get('decision_lineage') or {}
    if lineage.get('consumer_stage') not in {'responsive_validation_output', 'runtime_evidence_conflict'}:
        raise ValueError(f'EV4_RESPONSIVE_DECISION_LINEAGE_STAGE_INVALID in {path}')
    if lineage.get('selected_option') != payload.get('selected_route'):
        raise ValueError(
            f'EV4_RESPONSIVE_DECISION_LINEAGE_REPLACED in {path}: '
            f"selected_option={lineage.get('selected_option')} selected_route={payload.get('selected_route')}"
        )
    if not lineage.get('decision_card_ref', '').startswith('kernel-decision-card:'):
        raise ValueError(f'EV4_RESPONSIVE_DECISION_LINEAGE_REPLACED in {path}: non-Kernel decision card ref')
    if lineage.get('consumer_stage') == 'runtime_evidence_conflict' and payload.get('selected_route') != 'blocked_pending_input':
        raise ValueError(
            f'EV4_RESPONSIVE_RUNTIME_CONFLICT_REDESIGN_FORBIDDEN in {path}: '
            'runtime conflicts must flag/reopen instead of selecting a new Responsive architecture decision'
        )
    if lineage.get('consumer_stage') == 'responsive_validation_output' and lineage.get('evidence_state') != 'validated':
        raise ValueError(
            f'EV4_RESPONSIVE_DECISION_LINEAGE_EVIDENCE_STATE_WEAKENED in {path}: '
            'responsive validation output must preserve validated upstream decision lineage unless explicitly blocked/reopened'
        )


def validate_payload(payload, path, validator):
    errors = list(validator.iter_errors(payload))
    if errors:
        details = '; '.join(
            f"{'/'.join(str(part) for part in error.path)}: {error.message}" for error in errors
        )
        raise ValueError(f'Schema validation failed for {path}: {details}')
    assert_step_integrity(payload, path)
    assert_route_mode(payload, path)
    assert_builder_handoff_mode(payload, path)
    assert_breakpoint_scope(payload, path)
    assert_final_review_consistency(payload, path)
    assert_decision_lineage(payload, path)


def run_queue_checks():
    for check in QUEUE_CHECKS:
        result = subprocess.run([sys.executable, check], cwd=ROOT, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            raise ValueError(f'{check} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}')


def main():
    assert_required_files()
    assert_required_terms()
    run_queue_checks()

    schema = load_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    ownership_inventory = load_ownership_inventory()

    seen_routes = set()
    for path in VALID_FIXTURES:
        payload = load_fixture_payload(path, ownership_inventory)
        validate_payload(payload, relative_path(path), validator)
        seen_routes.add(payload['selected_route'])

    if seen_routes != EXPECTED_ROUTES:
        raise ValueError(f'Route fixture coverage mismatch: {sorted(seen_routes)}')

    discovered_invalid_paths = sorted(INVALID_DIR.glob('responsive_output_*.invalid.json'))
    missing_invalid = [
        str(relative_path(path)) for path in INVALID_FIXTURES if path not in discovered_invalid_paths
    ]
    if missing_invalid:
        raise ValueError('Missing required invalid fixtures: ' + ', '.join(missing_invalid))

    for path in discovered_invalid_paths:
        expected = expected_invalid_reason(path)
        try:
            validate_payload(load_fixture_payload(path, ownership_inventory), relative_path(path), validator)
        except ValueError as error:
            if expected not in str(error):
                raise ValueError(
                    f'Invalid fixture failed for wrong reason: {relative_path(path)}; '
                    f'expected={expected}; actual={error}'
                ) from error
        else:
            raise ValueError(f'Invalid fixture unexpectedly passed: {relative_path(path)}')

    print('Responsive tree architecture refactor check passed.')


if __name__ == '__main__':
    try:
        main()
    except ValueError as error:
        print(error)
        raise SystemExit(1)
