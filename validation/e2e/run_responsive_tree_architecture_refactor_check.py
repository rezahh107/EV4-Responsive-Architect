from pathlib import Path

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
]

missing = [p for p in files if not (ROOT / p).is_file()]
if missing:
    print('Missing responsive tree files:')
    for item in missing:
        print(item)
    raise SystemExit(1)

text = '\n'.join((ROOT / p).read_text(encoding='utf-8') for p in files)
for term in ['design_to_responsive_tree', 'same_tree_responsive_overrides', 'viewport_specific_variant_tree', 'hybrid_split_architecture', 'blocked_pending_input']:
    if term not in text:
        print('Missing term:', term)
        raise SystemExit(1)

print('Responsive tree architecture refactor check passed.')
