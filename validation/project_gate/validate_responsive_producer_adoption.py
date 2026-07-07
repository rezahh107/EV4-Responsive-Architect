#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[2]
def load(p): return json.loads((ROOT/p).read_text())
def errors(schema,payload): return list(Draft202012Validator(schema).iter_errors(payload))
def assert_no_errors(label,schema,payload):
    es=errors(schema,payload)
    if es: raise AssertionError(f"{label}: {es[0].message}")
def assert_has_errors(label,schema,payload):
    if not errors(schema,payload): raise AssertionError(f"{label}: expected validation failure")
def main():
    manifest=load('manifests/ev4-responsive-pipeline-manifest.v1.json')
    if manifest['schema']!='ev4-responsive-pipeline-manifest@1.0.0': raise AssertionError('manifest schema mismatch')
    expected_sequences={
        'design_to_responsive_tree':[
            'architect_baseline_intake','builder_responsive_intake','viewport_source_ledger',
            'relationship_classification','strategy_routing','route_specific_output','display_contract',
            'content_accessibility_duplication_gate','responsive_output_package','responsive_stage_payload',
            'producer_gate_export'
        ],
        'responsive_repair':[
            'builder_responsive_intake','viewport_source_ledger','responsive_failure_map','repair_ownership',
            'atomic_repair_plan','architecture_mutation_veto','responsive_final_audit','responsive_stage_payload',
            'producer_gate_export'
        ],
    }
    modes={mode.get('id'): mode.get('stage_sequence') for mode in manifest.get('modes', []) if isinstance(mode, dict)}
    if set(modes) != set(expected_sequences): raise AssertionError('mode separation missing or mismatched')
    for mode_id, expected_sequence in expected_sequences.items():
        if modes.get(mode_id) != expected_sequence: raise AssertionError(f'exact stage sequence mismatch for {mode_id}')
    rules='\n'.join(manifest['rules'])
    for term in ['Classify first.','Route second.','Validate only with matching viewport evidence.','Export machine truth last.']:
        if term not in rules: raise AssertionError(f'missing rule {term}')
    pin=manifest['project_gate_pin']
    if pin['silent_fallback_allowed'] is not False or pin['acquisition_mode']!='producer_emitted_gate_artifact': raise AssertionError('bad acquisition mode')
    lock=load('contracts/project-gate/producer-gate-export.v1.lock.json')
    if lock.get('lock_schema')!='project-gate-common-contract-lock.v1': raise AssertionError('lock schema mismatch')
    if lock.get('contract_owner')!='rezahh107/EV4-Project-Gate': raise AssertionError('contract owner mismatch')
    if lock.get('contract_id')!='producer-gate-export.v1': raise AssertionError('contract id mismatch')
    canonical=lock.get('canonical')
    vendored=lock.get('vendored')
    verification=lock.get('verification')
    if not isinstance(canonical, dict) or not isinstance(vendored, dict) or not isinstance(verification, dict): raise AssertionError('official lock sections missing')
    expected_sha='c556bb9deeccdcafeb885a1c8b3dbd660e4e06f452b8ac3c7040d21377465fcc'
    if canonical.get('file_sha256')!=expected_sha or vendored.get('file_sha256')!=expected_sha: raise AssertionError('producer lock sha mismatch')
    if vendored.get('local_copy_authoritative') is not False: raise AssertionError('vendored local copy must not be authoritative')
    if verification.get('byte_equality_required') is not True or verification.get('compare_against_moving_default_branch') is not False: raise AssertionError('verification policy mismatch')
    forbidden_lock_keys={'schema_version','locked_contracts','source_commit_sha','source_repository','separately_verified_stage_bundle'}
    if forbidden_lock_keys.intersection(lock): raise AssertionError('lock file still uses custom Prompt 4 lock shape')
    payload_schema=load('schemas/ev4-responsive-stage-payload.v1.schema.json')
    valid_payload=load('validation/fixtures/prompt04/valid/responsive_stage_payload.valid.json')
    invalid_payload=load('validation/fixtures/prompt04/invalid/responsive_stage_payload_cross_viewport.invalid.json')
    assert_no_errors('valid responsive payload',payload_schema,valid_payload)
    assert_has_errors('invalid cross viewport payload',payload_schema,invalid_payload)
    producer_schema=load('contracts/project-gate/producer-gate-export.v1.schema.json')
    valid_export=load('validation/fixtures/prompt04/valid/responsive_producer_gate_export.valid.json')
    invalid_export=load('validation/fixtures/prompt04/invalid/responsive_producer_gate_export_silent_fallback.invalid.json')
    assert_no_errors('valid producer export',producer_schema,valid_export)
    assert_has_errors('invalid silent fallback export',producer_schema,invalid_export)
    registry=load('registries/breakpoint-profiles.v1.json')
    if not any(profile.get('id')=='elementor_v4_default_unverified' and profile.get('allows_responsive_correctness_claim') is False for profile in registry.get('profiles', [])): raise AssertionError('breakpoint registry boundary missing')
    caps=load('registries/elementor-responsive-capabilities.v1.json')
    if any(capability.get('may_infer_hidden_values_from_screenshot') for capability in caps.get('capabilities', [])): raise AssertionError('hidden screenshot inference allowed')
    wf=ROOT/'.github/workflows/verify-vendored-common-contract.yml'
    if not wf.exists(): raise AssertionError('missing vendored contract workflow')
    text=wf.read_text()
    if 'ea19c22c32458068e167b267da8b819e9263cdf7' not in text: raise AssertionError('workflow not pinned')
    if 'lock_path: contracts/project-gate/producer-gate-export.v1.lock.json' not in text: raise AssertionError('workflow must pass lock_path')
    if 'lock-file:' in text or 'vendored-contract:' in text: raise AssertionError('workflow still passes unsupported inputs')
    print('Responsive Producer Adoption Prompt 4 validation passed')
if __name__=='__main__': main()
