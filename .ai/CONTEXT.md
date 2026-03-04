# Assembly Theory × Group Theory — Project Context

**Repo:** `nydiokar/SAI`  **Branch:** `master`  **Last Updated:** 2026-03-04  **Status:** P1 Full Exact-QM9 Run Complete; Post-Run Validation In Progress

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
| 🟢 | Scaffold + portability fixes | Both | Cross-platform path fixes and WSL-ready pipeline complete |
| 🟢 | Exact MA pipeline migration | B6 | Heuristic path removed from active runners; exact-only baseline active |
| 🟢 | Full QM9 exact scale run | B6 | `run_scale_qm9.py` completed at `n=131970` with checkpointing |
| 🔵 | Symmetry validity gate | B6 | Confirm point-group fidelity using trusted 3D geometries (not only RDKit-generated conformers) |
| 🔵 | Definitive Bridge 6 claim package | B6 | Lock final correlation claim only after symmetry-validity check passes |
| ⚪ | Define SAI formally | T1 | Ready to start in parallel with B6 reporting |
| ⚪ | Compute SAI for observed point groups | T1 | Start after formal SAI definition |

---

## Current Snapshot (2026-03-04)

### What Just Happened (Full Exact Run)
- Completed full exact-scale execution in `run_scale_qm9.py` with checkpoint resume:
  - `rows_total=131970`
  - `rows_usable=126892` (96.15%)
  - `rho=+0.103632`, `p=6.55037e-300`, `n=126892`
  - `ma_success=131930`, `ma_fail=40` (0.03%)
  - `sym_success=126932`, `sym_fail=5038` (3.82%)
- Final output saved to `data/processed/qm9_exact_scaled_results_full.csv`.

### Evaluation
- The run itself is operationally successful: near-complete MA success and stable throughput (~8.4 rows/s in final batches).
- Compared with earlier heuristic-negative results, the exact pipeline now shows a **small positive** MA-vs-symmetry-order association on the full dataset.
- MA reliability is now high (exact method). Symmetry validity has now been benchmarked directly against native QM9 geometries.
- `DtypeWarning` at final CSV read is non-fatal and caused by mixed `ma_error` values (mostly empty + string error labels).

### Immediate Next Steps (Priority Order)
1. **Lock Bridge 6 wording with explicit caveat:** symmetry is stable for directional/statistical claims; residual mismatch is concentrated in `C1` vs `Cs` boundary cases.
2. **For publication-grade final table:** regenerate final correlation once using native-geometry symmetry labels (reuse exact MA already computed; no need to rerun exact MA end-to-end).
3. **Declare completion criteria:** if native-geometry rerun preserves positive small effect (`rho` direction unchanged, small delta), mark Bridge 6 empirical phase complete.
4. **Move to convergence:** map observed point groups to Thread-1 SAI and test SAI-vs-MA mediation hypothesis.

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

### 2026-03-03 (Session 4) — WSL Execution, Portability Fixes, and QM9 URL Correction

| ID | Type | Description |
|:--:|:----:|:------------|
| 03.01 | ENV | Verified imports in WSL venv: `rdkit`, `pymatgen`, `ase` all import successfully. |
| 03.02 | FIX | Removed hardcoded Windows repo path from `run_pilot.py`, `run_pilot_v2.py`, `run_pilot_fast.py`. |
| 03.03 | FIX | Updated `src/compute_symmetry.py` to use `pymatgen PointGroupAnalyzer` with multi-conformer RDKit generation + legacy fallback. |
| 03.04 | TEST | `run_pilot_v2.py` now yields diverse groups (14 unique), not only `C1/Cs`; output is now meaningful for P1. |
| 03.05 | FIX | Added fail-fast controls to PubChem fetch (`max_seconds`, `max_consecutive_errors`) to avoid long hangs. |
| 03.06 | FIX | Corrected merge inflation bug in `src/merge_datasets.py` (duplicate SMILES no longer cause cartesian row explosion). |
| 03.07 | TEST | `run_pilot.py` now completes reliably; fallback synthetic run reports correct `n=500` after merge fix. |
| 03.08 | DIAG | Confirmed legacy QM9 URL `https://quantum-machine.org/datasets/qm9.tar.gz` now returns **404** (obsolete). |
| 03.09 | FIX | Updated QM9 downloader in `src/fetch_molecules.py` to modern mirrors: DeepChem zip (primary) + Figshare file mirror (fallback). |

**Current Blocker (as of 2026-03-03):**
- External data acquisition can still fail due network/DNS/remote mirror availability.
- This is no longer a code-path blocker in pilots; it is now an external download reliability issue.

**Current Status:**
- P1 execution pipeline is unblocked and producing meaningful results on curated/synthetic datasets.
- Full "real QM9" run depends on successfully downloading current QM9 artifacts from active mirrors.

### 2026-03-03 (Session 5) — First Real-QM9 Pilot Success

| ID | Type | Description |
|:--:|:----:|:------------|
| 03.10 | DATA | Downloaded QM9 mirror archive: `data/raw/qm9.zip` (~43MB, includes `gdb9.sdf` + `gdb9.sdf.csv`). |
| 03.11 | FIX | Updated loader to prioritize local QM9 and parse SDF when SMILES columns are absent in CSV. |
| 03.12 | FIX | Reordered data-source priority: local QM9 -> QM9 mirror download -> PubChem -> synthetic fallback. |
| 03.13 | TEST | Ran `run_pilot.py` using local QM9-derived molecules (no PubChem dependency). |
| 03.14 | RESULT | P1 pilot (`n=500`) produced **16 point groups**, Spearman **ρ=-0.1931**, **p=0.000014** (significant, negative correlation). |

**Interpretation (current):**
- P1 is no longer blocked.
- Initial signal exists: higher symmetry order tends to associate with lower MA in this pilot subset.
- Effect size is modest; scale-up on larger QM9 subsets is the next validation step.

**Immediate Next Step:**
- Run larger sample (e.g., 5k-10k QM9 molecules) to verify stability of ρ and p-value.

### 2026-03-03 (Session 6) — Robustness / Sanity Phase Before Full-Scale Claim

| ID | Type | Description |
|:--:|:----:|:------------|
| 03.15 | SCALE | Added checkpointed scaler `run_scale_qm9.py` and ran 20k target (`19480` valid rows). |
| 03.16 | RESULT | 20k-scale summary: **ρ=-0.164517**, **p=3.05e-118**, `point_groups=20`, `orders=10`. |
| 03.17 | SANITY | Added `run_sanity_checks.py` for robustness diagnostics (bootstrap CI, label cleaning, partial correlation, size-bin stability, optional API benchmark). |
| 03.18 | SANITY | Sanity report on 5k set: baseline ρ=-0.1925; partial (size/complexity controlled) r=-0.1382; effect remains negative/significant. |
| 03.19 | SANITY | Sanity report on 20k set: baseline ρ=-0.1645; partial (size/complexity controlled) r=-0.1594; effect remains negative/significant. |
| 03.20 | DIAG | Tried heuristic-vs-API benchmark (`molecular-assembly.com` endpoint currently returns no usable matches in this environment / endpoint likely stale). |

**Current Interpretation (scientific):**
- The negative association appears **stable across sample size, cleaning, and basic confound controls**.
- Effect size remains **modest**, not dominant.
- Core remaining risk is **proxy fidelity**:
  - MA values are still heuristic, not guaranteed to match canonical Assembly Index values from original method.
  - Some symmetry labels remain noisy/rare in long tails, though not driving the main result.

**Decision Gate Before Final 130k Claim:**
1. Full 130k run is useful and technically ready (checkpointed) for high-confidence effect-size estimate.
2. But final scientific wording should remain cautious until MA proxy is benchmarked against a trusted MA source on a representative subset.

### 2026-03-03 (Session 7) — Exact MA Benchmark Changes Interpretation

| ID | Type | Description |
|:--:|:----:|:------------|
| 03.21 | TOOL | Installed `assembly-theory==0.6.1` (DaymudeLab exact MA implementation). |
| 03.22 | VALID | Verified canonical references via exact MA: aspirin=8, anthracene=6, ethanol=1 (matches published examples). |
| 03.23 | FIX | Added exact-MA path in `src/compute_assembly.py` (`source=assembly_theory_exact`) and wired `prefer='exact'`. |
| 03.24 | BENCH | Exact-vs-heuristic benchmark (QM9 subset 2000): weak agreement (`ρ≈0.05`), indicating substantial proxy mismatch. |
| 03.25 | BENCH | MA-vs-symmetry on exact MA (subset 5000 from 20k symmetry pool): small **positive** effect (`ρ≈+0.056`, p<1e-4), opposite sign to heuristic pipeline. |
| 03.26 | RISK | Attempted full 20k exact MA encountered long-tail hard molecules; exact call can stall on rare cases without robust process-level timeout. |

**Updated Interpretation:**
- The heuristic MA proxy is not reliable enough for directional claims (it can flip effect sign vs exact MA).
- Previous negative-correlation conclusions from heuristic MA should be treated as provisional / proxy-driven.
- Research baseline must now prioritize exact MA (or validated proxy with quantified calibration error).

**Immediate Next Actions:**
1. Build a process-timeout exact MA batch runner (worker-process timeout/skip) to avoid rare stalls.
2. Run exact MA on stratified QM9 subsets (by heavy-atom bins) and report effect sizes with CIs.
3. Only then run full 130k exact MA (checkpointed), and treat heuristic outputs as auxiliary diagnostics.

### 2026-03-03 (Session 8) — Exact-Only Refactor + Smart Batch Runner

| ID | Type | Description |
|:--:|:----:|:------------|
| 03.27 | REFACTOR | Rebuilt `src/compute_assembly.py` as exact-only MA module (`compute_ma_exact`), removed heuristic execution paths and fake local placeholder API calls. |
| 03.28 | REFACTOR | Updated pilot scripts (`run_pilot.py`, `run_pilot_v2.py`, `run_pilot_fast.py`) to use `AssemblyIndexBatcher(method='exact')`. |
| 03.29 | REFACTOR | Replaced `run_scale_qm9.py` with exact-MA-first scalable runner: checkpoint/resume, per-molecule MA timeout, explicit success/error columns. |
| 03.30 | ROBUSTNESS | Added worker-process mode with `maxtasksperchild` recycling and automatic serial fallback when multiprocessing semaphores are unavailable in restricted environments. |
| 03.31 | TEST | Smoke-tested new scaler on QM9 (`n=300`): completed end-to-end, produced usable rows and correlation output without heuristic fallback. |

**Current Execution Baseline:**
- MA computation path is now **exact-first and exact-only in active scripts**.
- Failures/timeouts are explicitly tracked (`ma_success`, `ma_error`) instead of silently replaced by heuristic values.
- Full-scale runs should use `run_scale_qm9.py` with checkpointing and timeout parameters.

### 2026-03-04 (Session 9) — Full Exact-QM9 Completion (131,970 Rows)

| ID | Type | Description |
|:--:|:----:|:------------|
| 03.32 | SCALE | Completed resumed final batches in `run_scale_qm9.py` (from `101,500/101,970` pending to `101,970/101,970` pending complete). |
| 03.33 | RESULT | Final exact run summary: `rows_total=131970`, `rows_usable=126892`, Spearman `ρ=+0.103632`, `p=6.55037e-300`, `n=126892`. |
| 03.34 | RESULT | Status counts: `ma_success=131930`, `ma_fail=40`; `sym_success=126932`, `sym_fail=5038`. |
| 03.35 | DIAG | `ma_error` composition (40 fails): `hard_timeout=20`, `child_panic_canonize_unwrap=17`, `invalid_or_overflow=3`. |
| 03.36 | DIAG | Observed pandas warning on final read: mixed-type `ma_error` column; non-fatal and expected from nullable/error-string field mix. |
| 03.37 | DATA | Full exact output persisted to `data/processed/qm9_exact_scaled_results_full.csv`. |

**Interpretation Update:**
- Full exact-scale evidence now supports a **small positive** monotonic association between symmetry order and exact MA on usable QM9 rows.
- Prior heuristic-negative direction is now formally superseded by exact-only results.
- Residual uncertainty is now concentrated in **symmetry-label validity**, not in the exact-MA compute path.

**Execution Next Actions:**
1. Execute symmetry-validity benchmark against trusted geometry-derived labels.
2. Apply explicit pass/fail gate for “definitive Bridge 6” status based on agreement + correlation stability.
3. Finalize write-up wording only after gate result; otherwise mark current run as provisional and rerun with corrected symmetry path.

### 2026-03-04 (Session 10) — Symmetry Validity Gate (Native QM9 Geometry, 10k)

| ID | Type | Description |
|:--:|:----:|:------------|
| 03.38 | SCRIPT | Rebuilt `scripts/symmetry_validity_gate.py` to use index-aligned native QM9 SDF geometries with alignment QA and tolerance-stability diagnostics. |
| 03.39 | VALID | Alignment check passed strongly: `126792/126892` usable rows aligned by `mol_index` (`99.92%`). |
| 03.40 | RESULT | Primary tolerance (`0.5`) strict metrics: label match `0.9020`, order match `0.8955`, rho current `0.1063`, rho trusted `0.0955`, rho delta `0.0109`. |
| 03.41 | RESULT | Strict gate status: **FAIL** (fails only on high bar for exact order match and order stability across tolerances). |
| 03.42 | RESULT | Practical stability metrics (C1/Cs ambiguity-aware): coarse label match `0.9952`, coarse order match `0.9965`, coarse tolerance stability `0.9949` => **practical gate PASS**. |
| 03.43 | ANALYSIS | Main disagreement mass is `C1 <-> Cs`, i.e., low-symmetry boundary sensitivity, not broad high-symmetry collapse. Directional effect remains positive and stable. |

**Interpretation Update:**
- Symmetry signal is sufficiently stable for the Bridge 6 directional claim (small positive association) when accounting for known `C1/Cs` boundary ambiguity.
- Remaining uncertainty is mostly categorical granularity at the low-symmetry edge, not a sign flip or full-method invalidation.

**Decision (Current):**
1. Treat Bridge 6 as **scientifically supportable with explicit C1/Cs caveat** now.
2. For final manuscript table, run one native-geometry symmetry pass across the full exact-MA rows and report that as canonical final result.

### 2026-03-04 (Session 11) — Full Native-Geometry Symmetry Pass (All Aligned Rows)

| ID | Type | Description |
|:--:|:----:|:------------|
| 03.44 | RUN | Executed full native-geometry gate run using `scripts/symmetry_validity_gate.py` with `--n 0 --tolerances 0.5` on all aligned exact-MA rows. |
| 03.45 | VALID | Alignment remained strong at full scale: `126792/126892` (`99.92%`). |
| 03.46 | RESULT | Full-scale strict metrics (`tol=0.5`): exact label match `0.9027`, order match `0.8934`, rho current `0.10422`, rho trusted `0.09432`, rho delta `0.00990`. |
| 03.47 | RESULT | Full-scale practical stability (C1/Cs-aware): coarse label match `0.9964`, coarse order match `0.9975`; practical gate **PASS**. |
| 03.48 | INTERP | Positive association remains after native-geometry validation, with similar small effect size; remaining mismatch is concentrated in low-symmetry C1/Cs boundary. |

**Bridge 6 Status After Full Native Pass:**
- Directional claim is stable and supported: higher symmetry order associates with slightly higher exact MA (small positive effect).
- Strict categorical identity of low-symmetry labels (`C1` vs `Cs`) remains tolerance-sensitive; this should be reported as a caveat, not treated as result-invalidating.
- Empirical Bridge 6 phase can be considered **complete for decision/reporting**, with canonical numbers sourced from native-geometry validated outputs.
