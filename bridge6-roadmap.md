# Bridge 6: Molecular Symmetry × Assembly Index
## Research Roadmap & Experimental Plan

**Project Title:** Does Molecular Symmetry Predict Assembly Complexity? A Computational Correlation Study

**Core Question:** Is there a systematic relationship between a molecule's point group symmetry and its molecular assembly index? Do highly symmetric molecules have lower or higher assembly indices than asymmetric ones?

**Why This Matters:** If a correlation exists, it creates an empirical bridge between group theory (symmetry classification) and Assembly Theory (construction complexity) using real chemical data — no abstract algebra needed. If the correlation is absent or non-monotonic, that itself is a finding: it means symmetry anzd constructability are decoupled at the molecular level, which has implications for both drug discovery and origin-of-life research.

**Feasibility:** HIGH. All data sources exist. All tools are open-source. The computation is tractable on a laptop. No lab work required.

---

## Part 0: The Hypothesis in Plain Language

Every molecule has a symmetry — water is C₂ᵥ, methane is Tₓ, benzene is D₆ₕ. This is a group-theoretic classification. Every molecule also has an assembly index — the minimum number of bond-joining steps to build it from basic fragments, allowing reuse. This is an Assembly Theory measure.

Nobody has systematically asked: **are these two properties related?**

Intuition could go either way. Symmetric molecules have repeated substructures, so assembly could reuse those substructures, yielding lower assembly indices. But symmetric molecules might also require more precise construction (more steps to achieve the symmetry), yielding higher indices. Or the two might be completely independent.

This experiment finds out which.

---

## Part 1: Data Sources (All Verified to Exist)

### 1.1 Molecular Assembly Index Data

**Source A: molecular-assembly.com**
- Cronin's team hosts a lookup tool with precomputed MA values for millions of molecules
- Input: SMILES string or mol file → Output: assembly index
- Based on the Reaxys database (~2.5 million molecules computed)
- Paper: Marshall et al. (2021) Nature Communications 12, 3033

**Source B: DaymudeLab/assembly-theory (GitHub)**
- Open-source Rust/Python tool for computing assembly indices from scratch
- Repository: github.com/DaymudeLab/assembly-theory
- Can compute MA from SMILES via RDKit integration
- Actively maintained (Arizona State University)
- This lets us compute MA for any molecule not in the precomputed database

**Source C: croningp/molecular_complexity (GitHub)**
- Cronin's own lab code for the ACS Central Science (2024) paper
- Includes code for inferring MA from NMR, MS/MS, and IR spectra
- Contains experimental validation data

### 1.2 Molecular Symmetry Data

**Source D: RDKit (Python library)**
- Open-source cheminformatics toolkit
- Can detect point group symmetry from 3D molecular geometry
- Can compute SMILES ↔ 3D structure ↔ symmetry elements
- Standard tool in computational chemistry

**Source E: PubChem**
- ~115 million compounds with SMILES, InChI, 3D conformers
- Free API access
- 3D conformers needed for symmetry detection

**Source F: NIST CCCBDB (Computational Chemistry Comparison and Benchmark Database)**
- Contains point group assignments for ~2,000 small molecules
- Pre-labeled symmetry data — useful as validation set
- URL: cccbdb.nist.gov

**Source G: QM9 Dataset**
- 134,000 small organic molecules (up to 9 heavy atoms: C, H, O, N, F)
- 3D geometries optimized at DFT level
- Well-studied benchmark dataset in ML for chemistry
- Downloadable, well-structured

### 1.3 Additional Properties to Enrich the Analysis

From PubChem / RDKit / QM9:
- Molecular weight
- Number of heavy atoms
- Number of bonds
- Number of rotatable bonds
- Number of rings
- Topological polar surface area
- Whether the molecule is a natural product, drug, or synthetic
- Whether the molecule is biological or abiotic in origin

---

## Part 2: The Experimental Pipeline

### Phase 1: Environment Setup

**Tools to install:**
```
Python 3.10+
rdkit          — molecular manipulation, symmetry detection, SMILES handling
assembly_theory — MA computation (from DaymudeLab, Rust backend, Python wrapper)
pandas         — data manipulation
numpy          — numerical computation
scipy          — statistics (correlations, tests)
matplotlib     — plotting
seaborn        — statistical visualization
scikit-learn   — clustering, PCA, dimensionality reduction
requests       — API calls to PubChem / molecular-assembly.com
```

**Repository structure:**
```
bridge6-symmetry-assembly/
├── README.md
├── roadmap.md                    (this document)
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_symmetry_detection.ipynb
│   ├── 03_assembly_computation.ipynb
│   ├── 04_correlation_analysis.ipynb
│   ├── 05_clustering.ipynb
│   └── 06_outlier_investigation.ipynb
├── src/
│   ├── fetch_molecules.py        # PubChem / QM9 data fetching
│   ├── compute_symmetry.py       # Point group detection via RDKit
│   ├── compute_assembly.py       # MA computation via assembly_theory
│   ├── merge_datasets.py         # Join symmetry + MA + properties
│   └── analyze.py                # Statistical analysis
├── data/
│   ├── raw/                      # Downloaded datasets
│   ├── processed/                # Cleaned, merged CSVs
│   └── results/                  # Final analysis outputs
└── figures/                      # Publication-quality plots
```

### Phase 2: Data Collection & Preparation

**Step 2.1: Start with QM9 (the safe bet)**
- Download QM9 dataset (134k molecules, 3D geometries, well-curated)
- These are small organic molecules — manageable, well-understood
- Extract: SMILES, 3D coordinates, molecular weight, atom count

**Step 2.2: Detect point group symmetry for each molecule**
Using RDKit + pymatgen or a custom symmetry detection pipeline:
- Input: 3D geometry of molecule
- Output: Schoenflies symbol (C₁, C₂, Cₛ, C₂ᵥ, C₃ᵥ, D₃ₕ, Tₓ, Oₕ, etc.)
- Also output: order of the point group (number of symmetry operations)
- Also output: highest rotational axis order (n in Cₙ)

**Important detail:** Symmetry detection from optimized 3D geometries requires a tolerance parameter. Use a standard tolerance (e.g., 0.3 Å) and document it. Run sensitivity analysis with tighter/looser tolerances.

**Step 2.3: Compute assembly index for each molecule**
Using DaymudeLab/assembly-theory Python package:
- Input: SMILES string
- Output: molecular assembly index (MA)
- Note: MA computation is NP-hard. For QM9 molecules (≤9 heavy atoms), this should be tractable. For larger molecules, computation time may explode.

**Step 2.4: Merge into a single dataset**
Final CSV columns:
```
molecule_id, smiles, point_group, pg_order, max_rotation_order,
molecular_weight, n_heavy_atoms, n_bonds, n_rings, n_rotatable_bonds,
assembly_index, [any additional properties]
```

**Expected dataset size:** ~134,000 rows (from QM9). May reduce if MA computation is too slow for some molecules.

### Phase 3: Core Analysis

**Analysis 3.1: Distribution of symmetry groups**
- How many molecules in each point group?
- Expectation: most molecules are C₁ (no symmetry). How skewed is this?
- Visualize as bar chart

**Analysis 3.2: Distribution of assembly indices**
- What's the MA distribution across QM9?
- Is there a gap or threshold (Cronin's ~15 threshold)?
- For QM9 (small molecules), MA values will be lower — document the range

**Analysis 3.3: The core correlation — MA vs. point group order**
This is the main experiment.
- Box plot: MA distribution for each point group
- Scatter plot: point group order vs. MA (with molecular weight as color)
- Statistical test: Spearman rank correlation between point group order and MA
- ANOVA or Kruskal-Wallis: do different point groups have significantly different MA distributions?

**Analysis 3.4: Control for molecular size**
Critical confounder: larger molecules tend to have both higher MA and potentially different symmetry distributions. Must control for this.
- Compute MA residuals after regressing on molecular weight / heavy atom count
- Repeat Analysis 3.3 on residuals
- Stratify by molecular size (e.g., 3–5 heavy atoms, 6–7, 8–9) and check correlation within each stratum

**Analysis 3.5: The Generative Asymmetry (from Roadmap 1)**
- Compare point group order (structural symmetry) vs. MA (generative complexity)
- Are they correlated, anti-correlated, or independent?
- Identify outliers: high symmetry + high MA? low symmetry + low MA?
- These outliers are the most interesting molecules

**Analysis 3.6: Clustering**
- Run PCA on the feature space (MA, pg_order, molecular weight, n_bonds, n_rings, etc.)
- Do molecules cluster by symmetry type? By MA range? By both?
- Use t-SNE / UMAP for visualization
- Color by: point group, MA, biological vs synthetic origin (if labeled)

**Analysis 3.7: Family-specific analysis**
- Compare specific chemical families: alkanes, aromatics, amino acids, sugars, drugs
- Do certain families show stronger symmetry-MA correlations?
- Biological molecules vs. synthetic molecules: different relationship?

### Phase 4: Extended Dataset (If Phase 3 Shows Signal)

**Step 4.1: Expand to larger molecules**
- Sample from PubChem: ~10,000 molecules across a range of molecular weights
- Include known natural products, pharmaceuticals, metabolites
- Use molecular-assembly.com for precomputed MA values where available
- Compute symmetry for each

**Step 4.2: Cronin's biotic/abiotic threshold**
- Cronin showed MA ≈ 15 separates biotic from abiotic molecules
- Question: does molecular symmetry also change at this threshold?
- Do abiotic molecules (low MA) have systematically different symmetry profiles than biotic molecules (high MA)?
- This could yield a dual biosignature: MA + symmetry pattern

**Step 4.3: Drug molecules specifically**
- Sample approved drugs from DrugBank (~2,500 approved drugs)
- Compute MA and symmetry for each
- Question: do drugs cluster differently in the MA-symmetry space than non-drug molecules?
- If yes: potential application in drug discovery screening

### Phase 5: Connection Back to Group Theory (The Bridge)

This is where Bridge 6 connects to the abstract Monster Group roadmap (Roadmap 1).

**Step 5.1: Map molecular point groups to the group-theoretic classification**
- Every molecular point group is a finite group
- Classify: which are cyclic? dihedral? symmetric? which contain sporadic subgroups? (none will, at this scale — but the formalism matters)
- Compute the group-theoretic properties of each point group: order, composition series, number of generators, automorphism group size

**Step 5.2: Apply the Symmetry Assembly Index (SAI) from Roadmap 1**
- Compute SAI (from the abstract group theory roadmap) for each point group that appears in the molecular dataset
- Now you have three measures for each molecule: MA (molecular assembly), point group order (structural symmetry), and SAI of its point group (group-theoretic construction complexity)
- Question: does SAI of the point group correlate with MA of the molecule?
- If yes: the abstract assembly-theoretic metric on groups actually predicts something about physical molecules

**Step 5.3: The triple correlation**
- Plot: MA (x-axis) vs. SAI of point group (y-axis), colored by molecular weight
- This is the bridge between molecular chemistry, Assembly Theory, and abstract group theory
- If there's a pattern here, you've empirically connected Cronin's molecular framework to the algebraic framework from Roadmap 1

---

## Part 3: LLM Integration Protocol

### What the LLM Does

| Phase | LLM Role | Example Task |
|---|---|---|
| Data collection | Code generator | "Write Python to fetch 10,000 molecules from PubChem with 3D conformers and compute their point groups using RDKit" |
| Symmetry detection | Debugger / validator | "This molecule is classified as C₁ but visually looks symmetric — is the tolerance too tight?" |
| Analysis | Pattern spotter | "Here are the correlation matrices for the QM9 dataset. What patterns stand out?" |
| Interpretation | Cross-domain translator | "The D₃ₕ point group has order 12 and composition factors [Z₂, Z₃, Z₂]. How does this relate to the MA distribution we see?" |
| Writing | Manuscript assistant | "Draft the results section for the correlation between point group order and MA, controlling for molecular size" |

### What the LLM Does NOT Do

- Does NOT replace RDKit for symmetry computation
- Does NOT replace DaymudeLab code for MA computation
- Does NOT validate statistical claims — use scipy/statsmodels
- Does NOT generate data — it analyzes data that code produces

---

## Part 4: Success Criteria

### The Truth Test (Phase 3 Results)

| Outcome | What It Means | Action |
|---|---|---|
| Strong positive correlation (MA ↑ as symmetry ↑) | Symmetric molecules are harder to build | Surprising and publishable — write up immediately |
| Strong negative correlation (MA ↓ as symmetry ↑) | Symmetry enables efficient construction via reuse | Expected and interesting — investigate mechanism |
| No correlation after size control | Symmetry and construction complexity are independent | Still publishable as a negative result — means these are orthogonal descriptors, useful for dual classification |
| Non-monotonic / complex relationship | The relationship depends on symmetry type, not just amount | Most interesting — investigate which symmetry types associate with which MA ranges |
| Different relationship for biotic vs abiotic | Symmetry-MA coupling changes at the life threshold | Highest impact — dual biosignature potential |

**Every outcome is publishable.** This is not a project that can "fail" — it either confirms or refutes a hypothesis, both of which are contributions.

### Deliverables

**Minimum (Phase 3 complete):**
- Dataset: ~134k molecules with MA and point group symmetry
- Statistical analysis of correlation (or independence)
- Visualization suite (scatter plots, box plots, PCA)
- Clear statement of findings

**Medium (Phase 4 complete):**
- Extended dataset across molecular weight ranges
- Biotic/abiotic symmetry profile comparison
- Drug molecule analysis
- Preprint-ready manuscript

**Maximum (Phase 5 complete):**
- Empirical bridge between molecular MA and abstract group-theoretic SAI
- Triple correlation: molecular complexity × molecular symmetry × algebraic complexity
- Framework connecting Cronin's Assembly Theory to finite group theory through real data

---

## Part 5: Immediate Next Steps (This Week)

### Day 1: Set up environment
- [ ] Create GitHub repository with the structure above
- [ ] Install Python packages: rdkit, pandas, numpy, scipy, matplotlib, seaborn, scikit-learn
- [ ] Install DaymudeLab assembly_theory package (Rust backend, Python wrapper via maturin)
- [ ] Verify: can you compute MA for a simple molecule (e.g., ethanol)?
- [ ] Verify: can you detect the point group of water (should be C₂ᵥ)?

### Day 2: Get the data
- [ ] Download QM9 dataset
- [ ] Parse into a working DataFrame: SMILES, 3D coords, properties
- [ ] Pick 100 molecules as a test set
- [ ] Compute point group for the 100 test molecules
- [ ] Compute MA for the 100 test molecules
- [ ] Sanity check: do the values make sense? (water MA should be low, complex organics higher)

### Day 3: First signal check
- [ ] Run correlation: MA vs. point group order for 100 molecules
- [ ] Make a scatter plot
- [ ] Ask: is there any visible pattern?
- [ ] If yes: scale to full QM9
- [ ] If no: check whether controlling for molecular size reveals a pattern

### Day 4–5: Scale up
- [ ] Compute symmetry for all QM9 molecules (batch processing)
- [ ] Compute MA for all QM9 molecules (may take hours — batch and parallelize)
- [ ] Merge datasets
- [ ] Run full Analysis 3.1 through 3.7

### End of Week 1 Goal
Answer one question: **Is there a statistically significant relationship between molecular point group symmetry and molecular assembly index, after controlling for molecular size?**

If yes → proceed to Phases 4 and 5.
If no → the independence itself is interesting. Write it up as a negative result and consider whether the relationship emerges only for larger molecules (expand dataset) or specific families.

---

## Part 6: Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Most QM9 molecules are C₁ (no symmetry) | HIGH | Reduces statistical power for rare point groups | Supplement with targeted samples: fetch symmetric molecules from PubChem specifically |
| MA computation too slow for 134k molecules | MEDIUM | Delays | Start with subset. Parallelize. Use precomputed values from molecular-assembly.com |
| Symmetry detection sensitive to tolerance | MEDIUM | Noise in data | Run at multiple tolerances. Report sensitivity. Use CCCBDB as validation |
| Correlation is entirely driven by molecular size | MEDIUM | Trivially explained | Control for size rigorously. Report residual correlation after size regression |
| RDKit doesn't natively output Schoenflies symbols | LOW-MEDIUM | Extra work | Use pymatgen PointGroupAnalyzer or implement from RDKit symmetry elements |
| Assembly_theory package installation fails | LOW | Delays | Fall back to molecular-assembly.com API or Cronin's croningp/molecular_complexity code |

---

## Part 7: How This Connects to Roadmap 1

This project (Bridge 6) and the abstract group theory project (Roadmap 1, SAI on finite groups) are **independent but convergent**.

Bridge 6 is empirical: real molecules, real data, measurable quantities.
Roadmap 1 is theoretical: abstract groups, formal invariants, computational algebra.

They converge in Phase 5 of this roadmap, where the point groups appearing in real molecules are analyzed using the SAI metric from Roadmap 1. If both projects produce results, the convergence point is:

**"The assembly-theoretic complexity of a molecule's symmetry group (SAI) correlates with the assembly-theoretic complexity of the molecule itself (MA)."**

This would mean: abstract algebraic structure predicts physical chemical properties. That's a bridge between pure mathematics and experimental chemistry, mediated by Assembly Theory.

If this holds, Cronin's framework becomes a Rosetta Stone between algebra and chemistry — and the Monster Group, as the most complex symmetry atom, becomes the theoretical ceiling of what this framework can describe.

---

## Appendix: Key References

### Assembly Theory (Molecular)
- Marshall, S.M. et al. (2021). Identifying molecules as biosignatures with assembly theory and mass spectrometry. Nature Commun. 12, 3033.
- Sharma, A. et al. (2023). Assembly Theory explains and quantifies selection and evolution. Nature 622, 321–328.
- Jirasek, M. et al. (2024). Investigating and quantifying molecular complexity using Assembly Theory and spectroscopy. ACS Central Science.
- Kahana, A. et al. (2024). Constructing the Molecular Tree of Life using Assembly Theory and Mass Spectrometry. arXiv:2408.09305.
- Rutter, L.A. et al. (2025). Exploring molecular assembly as a biosignature using mass spectrometry and machine learning. arXiv:2507.19057.

### Molecular Symmetry
- Cotton, F.A. Chemical Applications of Group Theory (standard reference)
- RDKit documentation: rdkit.org
- NIST CCCBDB: cccbdb.nist.gov/pg1x.asp

### Tools
- DaymudeLab/assembly-theory: github.com/DaymudeLab/assembly-theory
- croningp/molecular_complexity: github.com/croningp/molecular_complexity
- molecular-assembly.com (precomputed MA lookup)
- QM9 dataset: quantum-machine.org/datasets/
- PubChem API: pubchem.ncbi.nlm.nih.gov
