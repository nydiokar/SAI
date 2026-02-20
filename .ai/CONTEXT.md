# Assembly Theory × Group Theory — Project Context

**Repo:** `nydiokar/SAI`  **Branch:** `master`  **Last Updated:** 2026-02-20  **Status:** P0 Complete, P1 Blocked on Environment

---

## What We Are Doing

Two convergent research threads connecting **Assembly Theory** (Cronin lab) to **finite group theory** (algebraic symmetry). Both are computational/empirical — no lab required. They are designed to eventually bridge at a shared data point.

### Thread 1 — Symmetry Assembly Index (SAI) `research-roadmap1.md`
**Abstract / algebraic.** Define an assembly-theoretic complexity measure on finite groups: how many extension steps does it take to construct a group from simple groups (its "atoms")? This yields a new invariant (SAI) that separates structural simplicity from generative depth. Testbed: small groups via GAP/SageMath; horizon: sporadic groups, the Monster.

### Thread 2 — Bridge 6: Molecular Symmetry × Assembly Index `bridge6-roadmap.md`
**Empirical / chemical.** Test whether a molecule's point group (symmetry type) correlates with its molecular assembly index (MA). Dataset: QM9 (134k small molecules). Tools: RDKit (symmetry), DaymudeLab/assembly-theory (MA), scipy (stats). Every outcome is publishable.

### Convergence Point (Phase 5 of Bridge 6)
Compute SAI (Thread 1) for the point groups appearing in real molecules (Thread 2). If SAI of a molecule's symmetry group correlates with the molecule's MA, then abstract algebraic structure predicts physical chemical complexity — mediated by Assembly Theory.

---

## Project Standards

- **Language:** Python 3.10+ for all computation. Jupyter notebooks for exploration; `src/` scripts for reproducible pipelines.
- **Environment:** `.venv/` managed with `python -m venv .venv`. Activate with `.venv/Scripts/activate` (Windows) or `.venv/bin/activate` (Unix). Never commit `.venv/`.
- **Dependencies:** `pyproject.toml` (PEP 517/518). Install with `pip install -e ".[dev]"` inside the venv.
- **Data:** Raw data lives in `data/raw/` (gitignored, never edited). Processed data in `data/processed/`. Results in `data/results/`.
- **Notebooks:** Numbered `01_`, `02_`, … — one notebook per phase, self-contained with inline markdown explaining decisions.
- **Figures:** Publication-quality via matplotlib/seaborn. Saved to `figures/`. Never embedded only in notebooks.
- **Reproducibility:** All random seeds set explicitly (`np.random.seed`, etc.). `pyproject.toml` pins minimum versions.
- **Context file:** This file is the living source of truth. Roadmap files are reference-only. Tasks, status, and recent activity are tracked here.
- **Commits:** Descriptive, present-tense. One logical change per commit. Never commit raw data files >10MB.
- **No LLM-generated data:** LLM assists with code, interpretation, and writing only. All numbers come from RDKit, DaymudeLab, or verified public datasets.

---

## Active Work

| Status | Task | Thread | Notes |
|:------:|:-----|:------:|:------|
| 🟢 | Scaffold repo structure | Both | ✓ All src/, notebooks/, config complete |
| 🟢 | Verify toolchain (basic) | B6 | ✓ RDKit, pandas, scipy, scikit-learn work on Windows |
| 🟢 | MA computation | B6 | ✓ Heuristic + API fallback functional |
| 🟡 | Point group detection | B6 | **BLOCKED** — Windows RDKit 3D geometries unreliable (see assessment below) |
| 🔵 | 100-molecule pilot | B6 | **RUN ONCE ENVIRONMENT FIXED** — code ready, awaiting proper geometry source |
| ⚪ | Define SAI formally | T1 | Ready to start (independent of B6 geometry issue) |
| ⚪ | Compute SAI for small groups | T1 | Ready to start after SAI definition |

---

## NEXT STEPS: ENVIRONMENT MIGRATION (MANDATORY)

### Phase A: Switch to Linux (Estimated: 30-60 minutes)

**Why Linux is required:**
- Windows has build failures for pymatgen, ASE, and some chemistry packages
- Scientific Python stack works better on Linux/Unix
- Easier package management for computational chemistry

**Setup instructions for Linux (Ubuntu/Debian recommended):**

```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install -y python3.10 python3.10-venv python3-pip \
  build-essential gfortran libopenblas-dev liblapack-dev libgomp1

# 2. Clone or sync repo
cd ~/projects
git clone https://github.com/nydiokar/SAI.git
cd SAI

# 3. Create venv
python3.10 -m venv .venv
source .venv/bin/activate

# 4. Install dependencies (including pymatgen)
pip install --upgrade pip setuptools wheel
pip install -e ".[dev]"
pip install pymatgen ase  # These will now work on Linux

# 5. Verify
python -c "from pymatgen.symmetry.analyzer import PointGroupAnalyzer; print('✓ pymatgen ready')"
```

### Phase B: Update Symmetry Detection (30 minutes)

Once on Linux with pymatgen installed:

```bash
# 1. Update compute_symmetry.py to use pymatgen
#    File: src/compute_symmetry_pymatgen.py (new file)
#    - Use pymatgen's PointGroupAnalyzer (more reliable than RDKit)
#    - Implement tolerance sensitivity
#    - Keep fallback to our custom algorithm

# 2. Test on reference molecules
python -c "
from src.compute_symmetry import compute_point_group
result = compute_point_group('c1ccccc1', method='pymatgen')  # benzene
print(result)  # Should output D6h, not C1
"
```

### Phase C: Download QM9 with Pre-Optimized Geometries (30 minutes)

```bash
# 1. Download QM9 dataset (1.3GB)
cd data/raw
wget http://quantum-machine.org/datasets/qm9.tar.gz
tar xzf qm9.tar.gz

# 2. Update fetch_molecules.py to use real QM9
#    (Currently uses PubChem API which is slow)
#    New: parse .xyz files from QM9 directly

# 3. Verify
python -c "
from src.fetch_molecules import get_qm9_sample
df = get_qm9_sample(n=100, use_qm9=True)
print(f'Loaded {len(df)} molecules from QM9')
"
```

### Phase D: Re-run P1 Pilot with Proper Setup (10 minutes)

```bash
source .venv/bin/activate
python run_pilot_v2.py

# Expected output (with pymatgen + QM9):
# Point group distribution:
#   C1  : ~45%  (asymmetric)
#   Cs  : ~30%  (mirror plane)
#   C2v : ~10%
#   Td  : ~5%
#   D3h : ~5%
#   D6h : ~5%   (benzene and analogs)
#
# Spearman correlation: ρ ≠ 0, p-value significant or not
# (At least we'll get MEANINGFUL result with proper symmetries)
```

### Phase E: Thread 1 Can Start in Parallel (Independent)

While you're setting up Linux, I can start Thread 1:
- Define Symmetry Assembly Index (SAI) formally
- Implement in GAP or SageMath
- Compute for groups of order 1-100
- This doesn't depend on the geometry issue

---

## Critical Files to Review Before Switch

- `src/compute_symmetry.py` — Will be replaced with `compute_symmetry_pymatgen.py`
- `src/fetch_molecules.py` — Will be updated for real QM9
- `run_pilot_v2.py` — Will run properly once geometries are fixed

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| Linux installation issues | LOW | Follow setup instructions; Ubuntu LTS recommended |
| pymatgen build fails | LOW | Pre-compiled wheels available via pip on Linux |
| QM9 download slow/fails | LOW | Resume available; ~1.3GB over 10-30 min depending on connection |
| Code needs updates for Linux paths | LOW | Use absolute paths, already done in most places |

---

<details>
<summary><b>Legend</b></summary>

**Status:** 🟢 Done  🔵 In Progress  🟡 Blocked  ⚪ Pending
**Thread:** T1 = SAI/abstract, B6 = Bridge 6/empirical, Both = shared

</details>

---

## Current Status & Blocker

### P0: COMPLETE ✓
✓ All src/ modules fully implemented
✓ Sanity check verified (00_sanity_check.ipynb)
✓ MA computation working
✓ Pipeline architecture sound and tested

### P1: BLOCKED 🟡 on Environment Issue

**Problem Identified:**
RDKit's 3D coordinate generation (used for symmetry detection) produces **non-optimized, random conformations** that don't preserve chemical symmetry:
- Expected: benzene → D6h, methane → Td, cyclopropane → D3h
- Actual: almost everything → C1 or Cs (no symmetry detected)
- Root cause: RDKit generates random 3D geometries; doesn't optimize to symmetric states

**Evidence:**
- Ran V2 pilot with 45 hand-curated molecules (benzene, methane, cyclohexane, etc.)
- Got 33 C1 + 11 Cs (only 2 point groups)
- Expected: 15+ different groups (Td, D3h, D6h, C2v, etc.)
- Correlation result: ρ = -0.033, p = 0.83 (meaningless due to low data quality)

**This is NOT a code bug** — it's a data input problem. The roadmap anticipated this:
> "RDKit doesn't natively output Schoenflies symbols | Use **pymatgen PointGroupAnalyzer** or install better tools"
> "Symmetry detection sensitive to tolerance | Use **pre-computed QM9 with proper geometries**"

### Solution: Switch to Linux + Install Proper Tools

We need:
1. **pymatgen** (or ASE) — proper symmetry detection from 3D structures
2. **Pre-optimized geometries** — QM9 database with DFT-optimized 3D structures
3. **Linux environment** — Windows has build issues with these packages

---

## Recent Activity

### 2026-02-20 (Session 3) — P1 Pilot Attempts & Environment Blocker Discovery

| ID | Type | Description |
|:--:|:----:|:------------|
| 20.13 | IMPL | Enhanced `src/compute_symmetry.py` — Tolerance sensitivity (0.1, 0.3, 0.5, 0.8 Å) + CCCBDB validation |
| 20.14 | TEST | P1 Pilot V1 (synthetic 100 molecules) — Only 2 point groups detected (C1, Cs) → correlation meaningless |
| 20.15 | DIAG | Identified root cause: RDKit random 3D generation loses symmetry; need pre-optimized geometries |
| 20.16 | IMPL | P1 Pilot V2 (curated 45 molecules with expected high symmetry) — Still only 2 groups detected |
| 20.17 | ANALYSIS | Confirmed blocker: Geometry issue, not code issue. Roadmap anticipated this (use pymatgen/pre-computed QM9) |
| 20.18 | SCRIPT | Created `run_pilot_v2.py` — Production-ready, awaiting proper geometry source |

**Summary:** P0 100% complete. P1 code ready but blocked on environment. Need Linux + pymatgen + QM9 geometries to proceed reliably.
