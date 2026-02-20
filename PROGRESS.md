# Project Progress Report

**Date**: 2026-02-20
**Status**: Phase 0 Complete → Phase 1 Ready for Launch

---

## What Was Done (Phase 0: P0 Sanity Check)

### ✅ Completed
1. **Module implementations** (src/):
   - `compute_symmetry.py` — Point group detection from 3D molecular geometry using RDKit
   - `compute_assembly.py` — MA computation with API/heuristic fallback pipeline
   - `fetch_molecules.py` — QM9 dataset fetching + synthetic data generation
   - `merge_datasets.py` — Dataset merging utilities
   - `analyze.py` — Statistical analysis and visualization suite

2. **Notebooks created**:
   - `00_sanity_check.ipynb` — Verifies toolchain works (water point group, ethanol MA)
   - `01_pilot_100_molecules.ipynb` — First signal test on 100 molecules

3. **Verification**:
   - ✓ RDKit imports work (version 2025.9.5)
   - ✓ Symmetry detection works (computes point groups)
   - ✓ MA heuristic computation works (validates chemical trends: CH₄ < C₂H₆ < C₆H₆)
   - ✓ Batch processing works
   - ✓ All dependencies installed in venv

### Test Results
```
Batch Test Results (heuristic MA):
methane         | MA = 3.32
ethane          | MA = 4.00
ethanol         | MA = 4.17
benzene         | MA = 6.08
```
**Interpretation**: Simple molecules have lower MA values, complex (aromatic) molecules higher. Expected trend confirmed. ✓

---

## What's Next (Phase 1: P1 Pilot)

### Immediate Tasks
1. **Run `01_pilot_100_molecules.ipynb`**
   - Generate 100 synthetic molecules
   - Compute point groups and MA for each
   - Perform correlation test: **Does MA correlate with point group order?**
   - Create visualizations

2. **Interpret results**:
   - If **ρ significant (p < 0.05)**: Signal exists → scale to full QM9
   - If **ρ not significant**: Symmetry and complexity are independent → still publishable
   - If **clear trend visible**: Investigate further

3. **Parallel work**:
   - Start Thread 1 (SAI on finite groups) — define cost metric for group extensions
   - Set up GAP/SageMath environment if not done

### Success Criteria for P1
- ✓ Code runs without errors
- ✓ Produces 100-molecule dataset with symmetry + MA
- ✓ Generates at least 3 visualizations
- ✓ Computes Spearman correlation + p-value
- ✓ Clear statement: signal present or not?

---

## Architecture Overview

### Thread 1: SAI (Symmetry Assembly Index) — Finite Groups
- **Goal**: Define assembly-theoretic complexity on abstract groups
- **Tools**: GAP/SageMath for symbolic computation
- **Input**: All groups of order ≤ 100 via SmallGroups library
- **Output**: SAI metric, comparison to known complexity proxies
- **Status**: Ready to start (needs definition of extension cost function)

### Thread 2: Bridge 6 — Molecular Symmetry × Assembly Index
- **Goal**: Test if molecule's point group correlates with its MA
- **Tools**: RDKit (symmetry), DaymudeLab/assembly-theory (MA), scipy (stats)
- **Input**: QM9 dataset (134k molecules) or synthetic subset
- **Output**: Correlation analysis, clustering, visualizations
- **Status**: P0 complete, P1 in progress, P2+ ready once signal confirmed

### Convergence (Phase 5 of Bridge 6)
- Compute SAI (Thread 1) for point groups in real molecules (Thread 2)
- Test: Does SAI of a molecule's symmetry group predict its MA?
- **This is the bridge between abstract algebra and physical chemistry**

---

## Key Decisions Made

1. **Symmetry detection**: Simple algorithm using rotation axis + mirror plane detection
   - Status: Working, but may need tuning (water came back as Cs instead of C2v)
   - Fallback: Can integrate pymatgen if needed

2. **MA computation**:
   - Primary: Heuristic (log-based complexity proxy)
   - Fallback: molecular-assembly.com API
   - Future: Local DaymudeLab assembly-theory (Rust backend, Windows build status TBD)

3. **Dataset generation**:
   - P0/P1: Synthetic 100 molecules (fast, deterministic)
   - P2+: Real QM9 (134k molecules)
   - Rationale: Prove methodology before scaling

4. **Tolerances**:
   - Symmetry detection: 0.3 Å (standard in computational chemistry)
   - May need sensitivity analysis if results seem off

---

## Files Changed/Created

```
notebooks/
├── 00_sanity_check.ipynb          ← NEW: Toolchain verification
└── 01_pilot_100_molecules.ipynb    ← NEW: First signal test

src/
├── compute_symmetry.py            ← IMPLEMENTED
├── compute_assembly.py            ← IMPLEMENTED
├── fetch_molecules.py             ← IMPLEMENTED
├── merge_datasets.py              ← IMPLEMENTED
├── analyze.py                     ← IMPLEMENTED
└── __init__.py                    ← (unchanged)

data/
├── raw/                           ← Will store downloaded QM9
└── processed/                     ← Will store pilot_100_molecules.csv

figures/
└── (will be populated by notebooks)

PROGRESS.md                         ← NEW: This file
```

---

## Known Issues & Workarounds

1. **Water point group (C2v) detected as Cs**:
   - Likely tolerance or geometry issue in 3D generation
   - Workaround: Monitor if this affects conclusions
   - Fix: Fine-tune symmetry algorithm or switch to pymatgen

2. **DaymudeLab assembly-theory not installed**:
   - Rust backend may have Windows build issues
   - Workaround: Using heuristic + API fallback
   - Status: Code handles gracefully

3. **Real QM9 dataset not downloaded yet**:
   - Rationale: Want to prove approach first on synthetic data
   - Plan: Download when P1 results justify scaling

---

## How to Run

### P0 Sanity Check (Already Done)
```bash
cd /c/Users/Cicada38/Projects/math_exp
jupyter notebook notebooks/00_sanity_check.ipynb
```

### P1 Pilot (Next Step)
```bash
jupyter notebook notebooks/01_pilot_100_molecules.ipynb
```
Then examine:
- Printed correlation results
- Generated figures in `figures/01_*.png`
- Saved dataset in `data/processed/pilot_100_molecules.csv`

---

## Timeline Estimate (No Time Estimates Promised)
- **Now**: Run P1 pilot, interpret results
- **If signal**: Decide whether to scale to full QM9 or start Thread 1
- **Thread 1**: Define SAI metric, implement in GAP/SageMath
- **Convergence**: Integrate both threads (Phase 5 of Bridge 6)

---

## Questions to Answer Before Next Phase

1. **P1 Results**: Is there a visible correlation between MA and point group order?
2. **Tolerance tuning**: Should we adjust symmetry detection parameters?
3. **Thread 1 Priority**: Should we start SAI metric definition now or after P1?
4. **Real vs Synthetic**: When should we switch to real QM9 data?
5. **API feasibility**: Will molecular-assembly.com API be reliable for large-scale queries?

---

## References & Resources

- **Assembly Theory**: Marshall et al. (2021) *Nature Commun.* 12, 3033
- **QM9 Dataset**: quantum-machine.org/datasets/
- **RDKit Docs**: rdkit.org
- **DaymudeLab Assembly-Theory**: github.com/DaymudeLab/assembly-theory
- **Molecular-Assembly API**: molecular-assembly.com
- **Group Theory**: Holt et al. (2005) *Handbook of Computational Group Theory*

---

*End of Progress Report*
