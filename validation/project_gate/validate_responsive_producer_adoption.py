#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
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
    required_modes={'design_to_responsive_tree','responsive_repair'}
    if {m['id'] for m in manifest['modes']}!=required_modes: raise AssertionError('mode separation missing')
    rules='\n'.join(manifest['rules'])
    for term in ['Classify first.','Route second.','Validate only with matching viewport evidence.','Export machine truth last.']:
        if term not in rules: raise AssertionError(f'missing rule {term}')
    pin=manifest['project_gate_pin']
    if pin['silent_fallback_allowed'] is not False or pin['acquisition_mode']!='producer_emitted_gate_artifact': raise AssertionError('bad acquisition mode')
    lock=load('contracts/project-gate/producer-gate-export.v1.lock.json')
    if lock['locked_contracts'][0]['sha256']!='c556bb9deeccdcafeb885a1c8b3dbd660e4e06f452b8ac3c7040d21377465fcc': raise AssertionError('producer lock sha mismatch')
    if lock['separately_verified_stage_bundle']['covered_by_common_lock'] is not False: raise AssertionError('stage bundle must not be lock-covered')
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
    if not any(p['id']=='elementor_v4_default_unverified' and p['allows_responsive_correctness_claim'] is False for p in registry['profiles']): raise AssertionError('breakpoint registry boundary missing')
    caps=load('registries/elementor-responsive-capabilities.v1.json')
    if any(c.get('may_infer_hidden_values_from_screenshot') for c in caps['capabilities']): raise AssertionError('hidden screenshot inference allowed')
    wf=ROOT/'.github/workflows/verify-vendored-common-contract.yml'
    if not wf.exists(): raise AssertionError('missing vendored contract workflow')
    text=wf.read_text()
    if 'ea19c22c32458068e167b267da8b819e9263cdf7' not in text: raise AssertionError('workflow not pinned')
    print('Responsive Producer Adoption Prompt 4 validation passed')
if __name__=='__main__': main()
