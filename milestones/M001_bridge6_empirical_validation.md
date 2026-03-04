# M001 — Bridge 6 Empirical Validation (Exact MA + Native Symmetry Gate)

**Status:** ✅ Complete  
**Date:** 2026-03-04  
**Scope:** QM9 empirical thread (Bridge 6)

## Why This Milestone Existed

Initial objective was to test whether molecular symmetry is associated with assembly complexity, but with trustworthy methods:
- MA had to be exact (not heuristic proxy).
- Symmetry had to be validated against native QM9 3D geometries.

## What Was Done

1. Migrated MA pipeline to exact computation (`assembly-theory`) and ran full scale.
2. Completed full exact run output at:
   - `data/processed/qm9_exact_scaled_results_full.csv`
3. Built and ran native-geometry symmetry validity gate:
   - `scripts/symmetry_validity_gate.py`
   - Full native pass at:
     - `data/results/full_native_symmetry/`

## What Was Achieved

### Full exact-MA run (pipeline output)
- `rows_total=131970`
- `rows_usable=126892`
- `rho=+0.103632` (small positive association)

### Native-geometry validated full pass (canonical)
- alignment_rate: `0.9992` (index alignment quality is strong)
- exact_label_match_rate: `0.9027`
- order_match_rate: `0.8934`
- coarse label/order match (C1/Cs-aware): `0.9964 / 0.9975`
- `rho_current=0.10422`
- `rho_trusted=0.09432`
- `rho_delta=0.00990`

## Interpretation

- The directional finding is stable: symmetry-order vs exact MA remains **small positive** after native-geometry validation.
- The main mismatch is low-symmetry boundary behavior (`C1` vs `Cs`), not a collapse of the relationship.
- This converts Bridge 6 empirical result from provisional to decision-grade, with an explicit caveat on C1/Cs granularity.

## Added Value

1. Eliminated MA-proxy risk (exact MA is now baseline).
2. Eliminated major symmetry-validity uncertainty (native geometry benchmark complete).
3. Established robust claim quality for reporting:
   - Association exists
   - Effect is modest
   - Caveat is known and bounded

## Definition of Done (Met)

- [x] Exact MA at full scale completed.
- [x] Native-geometry symmetry validation completed on full aligned dataset.
- [x] Correlation direction stable under trusted symmetry labels.
- [x] Canonical artifact set saved and reproducible.

## Canonical Artifacts

- `data/processed/qm9_exact_scaled_results_full.csv`
- `data/results/full_native_symmetry/symmetry_validity_gate_summary.md`
- `data/results/full_native_symmetry/symmetry_gate_decision.csv`
- `data/results/full_native_symmetry/bridge6_rho_comparison.csv`
- `data/results/full_native_symmetry/symmetry_confusion_top.csv`

