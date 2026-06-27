import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE_FILES = [
    ROOT / 'planning/EV4_ROLLING_QUEUE.json',
    ROOT / 'planning/EV4_RUN_LEDGER.json',
]

MIN_LINE_COUNTS = {
    'planning/EV4_ROLLING_QUEUE.json': 500,
    'planning/EV4_RUN_LEDGER.json': 150,
}


def relative_path(path):
    return path.relative_to(ROOT).as_posix()


def assert_parseable_json(path):
    try:
        json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as error:
        raise ValueError(f'{relative_path(path)} is not valid JSON: {error}') from error


def assert_not_destructively_minified(path):
    text = path.read_text(encoding='utf-8')
    rel = relative_path(path)
    lines = text.splitlines()
    min_lines = MIN_LINE_COUNTS[rel]

    if len(lines) < min_lines:
        raise ValueError(
            f'{rel} appears destructively collapsed: {len(lines)} lines found, '
            f'expected at least {min_lines}. Keep repository state JSON reviewable.'
        )

    if not text.endswith('\n'):
        raise ValueError(f'{rel} must end with a trailing newline.')

    non_empty_lines = [line for line in lines if line.strip()]
    if not non_empty_lines:
        raise ValueError(f'{rel} is empty.')

    one_line_json_markers = sum(1 for line in non_empty_lines if line.count('{') + line.count('[') > 8)
    if one_line_json_markers:
        raise ValueError(f'{rel} contains collapsed JSON structures that are not reviewable.')


def main():
    for path in STATE_FILES:
        if not path.is_file():
            raise ValueError(f'Missing state file: {relative_path(path)}')
        assert_parseable_json(path)
        assert_not_destructively_minified(path)

    print('JSON state file format guard passed.')


if __name__ == '__main__':
    try:
        main()
    except ValueError as error:
        print(error)
        raise SystemExit(1)
