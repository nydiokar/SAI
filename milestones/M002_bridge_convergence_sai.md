# M002 — Bridge Convergence: SAI Layer on Observed Point Groups

**Status:** 🔵 Next  
**Date Opened:** 2026-03-04  
**Scope:** Convergence of Thread 1 (SAI) with Bridge 6 empirical output

## Target Outcome

Test whether algebraic group-structure complexity (SAI) explains/mediates the observed symmetry-vs-MA signal in real molecules.

## Why This Is the Next Milestone

M001 established a stable empirical signal (symmetry order vs exact MA).  
M002 asks the higher-value scientific question: does the abstract group invariant (SAI) add explanatory power beyond raw group order?

## Definition of Done

- [ ] SAI is formally specified for the molecular point groups observed in Bridge 6.
- [ ] SAI values are computed for those groups and versioned in a reproducible table.
- [ ] Molecule-level dataset is enriched with SAI via point-group mapping.
- [ ] Comparative analysis completed:
  - MA vs group order
  - MA vs SAI
  - Joint/partial analysis (order + SAI)
- [ ] Clear claim produced:
  - `SAI adds explanatory value` OR `SAI does not add value beyond order`

## Deliverables

1. `data/results/point_group_sai_table.csv`
2. `data/results/bridge6_with_sai.csv`
3. `data/results/bridge6_sai_analysis_summary.md`
4. Figure set for manuscript:
   - MA vs order
   - MA vs SAI
   - residual/partial effect comparison

## Acceptance Criteria (Decision Gate)

- Statistical direction/significance reported with effect sizes and CIs.
- Analysis uses the validated native-geometry Bridge 6 baseline from M001.
- Reproducible scripts/notebooks included with fixed random seeds and explicit environment notes.

## Decision Impact

- If SAI adds value: strong convergence claim between algebraic structure and molecular assembly complexity.
- If not: still publishable negative/constraining result with validated empirical baseline.

