import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / 'schemas/ev4-responsive-reference-family.schema.json'
VALID_DIR = ROOT / 'validation/fixtures/valid'
INVALID_DIR = ROOT / 'validation/fixtures/invalid'

VALID_FIXTURES = [
    VALID_DIR / 'responsive_reference_family.valid.json',
]

INVALID_FIXTURES = [
    INVALID_DIR / 'responsive_reference_family_missing_scope.invalid.json',
    INVALID_DIR / 'responsive_reference_family_raw_screenshot_authority.invalid.json',
]


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def relative_path(path):
    return path.relative_to(ROOT)


def validate_payload(payload, path, validator):
    errors = list(validator.iter_errors(payload))
    if errors:
        details = '; '.join(
            f"{'/'.join(str(part) for part in error.path)}: {error.message}" for error in errors
        )
        raise ValueError(f'Schema validation failed for {path}: {details}')

    if payload.get('raw_screenshot_authority') is not False:
        raise ValueError(f'raw screenshot used as authority: {path}')
    if payload.get('desktop_screenshot_proves_mobile_or_tablet') is not False:
        raise ValueError(f'desktop screenshot inferred mobile/tablet behavior: {path}')

    authorization = payload.get('per_viewport_reference_authorization', {})
    scope = payload.get('golden_reference_scope')
    if scope in {'tablet', 'mobile'} and authorization.get(scope) != 'authorized':
        raise ValueError(f'{scope} reference behavior lacks scoped authorization: {path}')


def main():
    if not SCHEMA.is_file():
        raise ValueError(f'Missing schema: {relative_path(SCHEMA)}')

    schema = load_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    for path in VALID_FIXTURES:
        if not path.is_file():
            raise ValueError(f'Missing valid fixture: {relative_path(path)}')
        validate_payload(load_json(path), relative_path(path), validator)

    for path in INVALID_FIXTURES:
        if not path.is_file():
            raise ValueError(f'Missing invalid fixture: {relative_path(path)}')
        try:
            validate_payload(load_json(path), relative_path(path), validator)
        except ValueError:
            continue
        raise ValueError(f'Invalid reference-family fixture unexpectedly passed: {relative_path(path)}')

    print('Responsive reference family check passed.')


if __name__ == '__main__':
    try:
        main()
    except ValueError as error:
        print(error)
        raise SystemExit(1)
