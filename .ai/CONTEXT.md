# Assembly Theory × Group Theory — Project Context

**Repo:** `nydiokar/SAI`  **Branch:** `master`  **Last Updated:** 2026-02-20  **Status:** Active — Scaffolding

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
| 🔵 | Scaffold repo structure | Both | Create `src/`, `data/`, `notebooks/`, `figures/` with placeholder files |
| ⚪ | Environment setup | B6 | Install rdkit, assembly-theory (DaymudeLab), pandas, scipy, seaborn, scikit-learn |
| ⚪ | Verify toolchain | B6 | Compute MA for ethanol; detect point group of water (C₂ᵥ) |
| ⚪ | Download QM9 dataset | B6 | 134k molecules, 3D geometries, ~1.3GB |
| ⚪ | 100-molecule pilot | B6 | Compute MA + point group for test set; first scatter plot |
| ⚪ | Define SAI formally | T1 | Choose extension cost function; implement in SageMath/GAP |
| ⚪ | Compute SAI for small groups | T1 | Orders 1–100 via GAP; validate against known complexity proxies |

<details>
<summary><b>Legend</b></summary>

**Status:** 🟢 Done  🔵 In Progress  🟡 Blocked  ⚪ Pending
**Thread:** T1 = SAI/abstract, B6 = Bridge 6/empirical, Both = shared

</details>

---

## Current Focus

### P0: Repo scaffold + environment (now)

Get the repo to a runnable state:
1. Directory structure created (src/, data/, notebooks/, figures/)
2. `.venv/` created (`python -m venv .venv`)
3. `pyproject.toml` with all dependencies; install via `pip install -e ".[dev]"`
4. `notebooks/00_sanity_check.ipynb` — imports rdkit, runs one MA computation, detects one point group
5. All roadmap files committed

### P1: Bridge 6 — 100-molecule pilot

First real signal check. QM9 subset → point group + MA → scatter plot → is there a visible pattern?

---

## Recent Activity

### 2026-02-20 — Project initialized

| ID | Type | Description |
|:--:|:----:|:------------|
| 20.1 | PLAN | `research-roadmap1.md` created — SAI on finite groups (Thread 1) |
| 20.2 | PLAN | `bridge6-roadmap.md` created — molecular symmetry × MA correlation (Bridge 6) |
| 20.3 | SETUP | Repo initialized, context file written, scaffold started |

**Summary:** Research design complete for both threads. All data sources verified (QM9, molecular-assembly.com, DaymudeLab/assembly-theory, RDKit). Convergence strategy defined. Repo pushed to `nydiokar/SAI`.
