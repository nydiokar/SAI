# Legacy Archive — 2026-03-04

This archive stores superseded artifacts that were removed from active working paths to keep the repository lean and unambiguous.

## What Was Archived

- `data_processed/`
  - Older intermediate scale outputs superseded by full exact run + native-geometry validation.
  - Pilot/smoke outputs and exploratory subsets not needed for canonical reporting.
- `data_results/`
  - Earlier gate outputs in `data/results/` superseded by canonical outputs in `data/results/full_native_symmetry/`.
  - Heuristic-vs-exact benchmark files retained for historical traceability.
  - Sanity report markdown files moved out of active results root.
- `docs/`
  - Older migration/progress docs superseded by:
    - `.ai/CONTEXT.md`
    - `milestones/`
- `notebooks_data/`
  - Notebook-local processed pilot artifact archived for cleanliness.

## Canonical Active Artifacts (Not Archived)

- `data/processed/qm9_exact_scaled_results_full.csv`
- `data/results/full_native_symmetry/*`
- `scripts/symmetry_validity_gate.py`
- `milestones/*`
- `.ai/CONTEXT.md`
