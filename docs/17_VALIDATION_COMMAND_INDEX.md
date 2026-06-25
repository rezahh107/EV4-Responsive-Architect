# Validation Command Index

Task: `RTAQ-0003`

This index lists repository validation commands for controlled manual use. Command success is repository-check evidence only; it is not responsive correctness evidence and does not authorize production, release, real pilot, export, live-render, accessibility, or pixel-validation claims.

## Dependency setup

```bash
python -m pip install -r requirements.txt
```

## Active validation commands

```bash
python validation/e2e/run_responsive_tree_architecture_refactor_check.py
python validation/e2e/run_submitted_packet_eligibility_gate_check.py
```

## Automatic workflow boundary

The GitHub Actions workflow runs repository checks for pull requests and pushes to `main`. Its success means the configured repository checks passed. It does not prove that a real submitted packet exists, that Issue #8 has real evidence, or that the responsive output is production/release ready.

## Manual-only interpretation

The commands can be used to inspect deterministic repository behavior:

- responsive-tree architecture contracts, schema, and route fixtures
- invalid fixture rejection
- submitted-packet eligibility failure modes
- boundary text preservation

They must not be used to bypass the real submitted-packet gate or pilot-readiness gate.

## Required stop conditions

Stop and do not upgrade claims if:

- real submitted evidence is absent
- Issue #8 remains evidence-pending
- the run would treat fixture or sample behavior as real evidence
- the run would rely on CI success as responsive validation
- any validation command fails or is not run

## Boundary

This command index is documentation only. It does not create evidence, mutate Issue #8, run the pilot, or change readiness state.
