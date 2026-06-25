import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]

files = [
    'docs/RESPONSIVE_TREE_ARCHITECTURE_REFACTOR_v0.3.0.md',
    'contracts/EV4_RESPONSIVE_TREE_ARCHITECTURE_CONTRACT.md',
    'contracts/EV4_VIEWPORT_RELATIONSHIP_CLASSIFICATION_CONTRACT.md',
    'contracts/EV4_RESPONSIVE_STRATEGY_ROUTING_CONTRACT.md',
    'contracts/EV4_VIEWPORT_DISPLAY_CONTRACT.md',
    'contracts/EV4_RESPONSIVE_HANDOFF_EXPORT_CONTRACT.md',
    'stages/00_RESPONSIVE_START_PACKET_INGEST.md',
    'stages/01_RESPONSIVE_DESIGN_INTAKE.md',
    'stages/02_VIEWPORT_SOURCE_LEDGER.md',
    'stages/03_SECTION_RELATIONSHIP_CLASSIFICATION.md',
    'stages/04_ELEMENTOR_STRATEGY_ROUTING.md',
    'stages/05_RESPONSIVE_TREE_OWNERSHIP_CONTRACT.md',
    'stages/06A_SAME_TREE_RESPONSIVE_DERIVATION.md',
    'stages/06B_VIEWPORT_TREE_ARCHITECTURE.md',
    'stages/06C_COMPOSITE_RESPONSIVE_PLAN.md',
    'stages/07_DISPLAY_AND_BREAKPOINT_CONTRACT.md',
    'stages/08_CONTENT_ACCESSIBILITY_DUPLICATION_GATE.md',
    'stages/09_RESPONSIVE_BUILDER_HANDOFF.md',
    'stages/10_RESPONSIVE_VALIDATION_PLAN.md',
    'stages/11_RESPONSIVE_FINAL_REVIEW.md',
    'stages/12_RESPONSIVE_OUTPUT_PACKAGE.md',
    'schemas/ev4-responsive-output.schema.json',
    'validation/fixtures/valid/responsive_output_same_tree.valid.json',
    'validation/fixtures/valid/responsive_output_viewport_tree.valid.json',
    'validation/fixtures/valid/responsive_output_hybrid.valid.json',
]

terms = [
    'design_to_responsive_tree',
    'same_tree_responsive_overrides',
    'viewport_specific_variant_tree',
    'hybrid_split_architecture',
    'blocked_pending_input',
]

fixture_paths = [
    'validation/fixtures/valid/responsive_output_same_tree.valid.json',
    'validation/fixtures/valid/responsive_output_viewport_tree.valid.json',
    'validation/fixtures/valid/responsive_output_hybrid.valid.json',
]

missing = [p for p in files if not (ROOT / p).is_file()]
if missing:
    print('Missing responsive tree files:')
    for item in missing:
        print(item)
    raise SystemExit(1)

text = '\n'.join((ROOT / p).read_text(encoding='utf-8') for p in files)
for term in terms:
    if term not in text:
        print('Missing term:', term)
        raise SystemExit(1)

schema_path = ROOT / 'schemas/ev4-responsive-output.schema.json'
schema = json.loads(schema_path.read_text(encoding='utf-8'))
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema)

seen_routes = set()
for fixture_path in fixture_paths:
    payload = json.loads((ROOT / fixture_path).read_text(encoding='utf-8'))
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))
    if errors:
        print('Fixture failed schema validation:', fixture_path)
        for error in errors:
            print('-', '/'.join(str(part) for part in error.path), error.message)
        raise SystemExit(1)
    seen_routes.add(payload['selected_route'])

expected_routes = {
    'same_tree_responsive_overrides',
    'viewport_specific_variant_tree',
    'hybrid_split_architecture',
}
if seen_routes != expected_routes:
    print('Route fixture coverage mismatch:', sorted(seen_routes))
    raise SystemExit(1)

print('Responsive tree architecture refactor check passed.')
