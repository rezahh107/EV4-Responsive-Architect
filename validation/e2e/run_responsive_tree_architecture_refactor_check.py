import json
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


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def expected_invalid_reason(path):
    name = path.name
    if name.startswith('responsive_output_missing_'):
        return 'Schema validation failed'
    if name == 'responsive_output_empty_steps.invalid.json':
        return 'builder_handoff.steps cannot be empty'
    if name == 'responsive_output_duplicate_step_id.invalid.json':
        return 'Duplicate step_ids'
    if name == 'responsive_output_route_mode_mismatch.invalid.json':
        return 'Route/mode mismatch'
    raise ValueError(f'No expected invalid failure registered for {path}')


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

    for index, step_id in enumerate(step_ids, start=1):
        prefix, sep, suffix = step_id.partition('-')
        if not prefix or sep != '-' or not suffix.isdigit():
            raise ValueError(f'Invalid step_id format: {step_id} in {path}')
        if int(suffix) != index:
            raise ValueError(f'Non-sequential step_id: {step_id} in {path}')


def assert_route_mode(payload, path):
    route = payload.get('selected_route')
    mode = payload.get('responsive_tree_output', {}).get('mode')
    expected = ROUTE_TO_MODE.get(route)
    if mode != expected:
        raise ValueError(f'Route/mode mismatch in {path}: route={route}, mode={mode}, expected={expected}')


def validate_payload(payload, path, validator):
    if list(validator.iter_errors(payload)):
        raise ValueError(f'Schema validation failed for {path}')
    assert_step_integrity(payload, path)
    assert_route_mode(payload, path)


def main():
    for path in [SCHEMA, *VALID_FIXTURES]:
        if not path.is_file():
            raise ValueError(f'Missing file: {path.relative_to(ROOT)}')

    schema = load_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    seen_routes = set()
    for path in VALID_FIXTURES:
        payload = load_json(path)
        validate_payload(payload, path.relative_to(ROOT), validator)
        seen_routes.add(payload['selected_route'])

    if seen_routes != EXPECTED_ROUTES:
        raise ValueError(f'Route fixture coverage mismatch: {sorted(seen_routes)}')

    invalid_paths = sorted(INVALID_DIR.glob('responsive_output_*.invalid.json'))
    if not invalid_paths:
        raise ValueError('No invalid responsive output fixtures found')

    for path in invalid_paths:
        expected = expected_invalid_reason(path)
        try:
            validate_payload(load_json(path), path.relative_to(ROOT), validator)
        except ValueError as error:
            if expected not in str(error):
                raise ValueError(
                    f'Invalid fixture failed for wrong reason: {path.relative_to(ROOT)}; '
                    f'expected={expected}; actual={error}'
                ) from error
        else:
            raise ValueError(f'Invalid fixture unexpectedly passed: {path.relative_to(ROOT)}')

    print('Responsive tree architecture refactor check passed.')


if __name__ == '__main__':
    try:
        main()
    except ValueError as error:
        print(error)
        raise SystemExit(1)
