import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / 'schemas/ev4-responsive-output.schema.json'
VALID_DIR = ROOT / 'validation/fixtures/valid'
INVALID_DIR = ROOT / 'validation/fixtures/invalid'

VALID_FIXTURES = [
    VALID_DIR / 'responsive_output_same_tree.valid.json',
    VALID_DIR / 'responsive_output_viewport_tree.valid.json',
    VALID_DIR / 'responsive_output_hybrid.valid.json',
]

INVALID_FIXTURES = [
    INVALID_DIR / 'responsive_output_missing_forbidden_claims.invalid.json',
    INVALID_DIR / 'responsive_output_empty_steps.invalid.json',
    INVALID_DIR / 'responsive_output_duplicate_step_id.invalid.json',
    INVALID_DIR / 'responsive_output_route_mode_mismatch.invalid.json',
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
}

QUEUE_CHECKS = [
    'validation/e2e/run_rolling_queue_check.py',
    'validation/e2e/run_run_ledger_check.py',
    'validation/e2e/run_task_quality_gate_check.py',
    'validation/e2e/run_submitted_packet_eligibility_gate_check.py',
    'validation/e2e/run_json_state_file_format_guard.py',
]


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


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
    steps = payload.get('builder_handoff', {}).get('steps', [])
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
    mode = payload.get('responsive_tree_output', {}).get('mode')
    expected = ROUTE_TO_MODE.get(route)
    if mode != expected:
        raise ValueError(f'Route/mode mismatch in {path}: route={route}, mode={mode}, expected={expected}')


def validate_payload(payload, path, validator):
    errors = list(validator.iter_errors(payload))
    if errors:
        details = '; '.join(
            f"{'/'.join(str(part) for part in error.path)}: {error.message}" for error in errors
        )
        raise ValueError(f'Schema validation failed for {path}: {details}')
    assert_step_integrity(payload, path)
    assert_route_mode(payload, path)


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

    seen_routes = set()
    for path in VALID_FIXTURES:
        payload = load_json(path)
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
            validate_payload(load_json(path), relative_path(path), validator)
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
