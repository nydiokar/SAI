# Assembly Theory × Finite Group Theory
## Research Roadmap & Experimental Plan

**Project Title:** Symmetry Assembly Index — Applying Assembly-Theoretic Measures to Finite Group Construction

**Core Question:** Can an assembly-theory-inspired metric, applied to finite groups, reveal structure that neither group theory nor Assembly Theory sees alone?

**Status:** Conceptually coherent, mathematically natural (partially), computationally feasible. The entire project hinges on defining an assembly cost that is mathematically principled rather than ad hoc.

---

## Part 0: The Thesis in One Paragraph

Assembly Theory measures the minimal generative history of objects (molecules). Finite group theory studies the structural decomposability of symmetry via composition series, extensions, generators, and representations. Both frameworks ask the same fundamental question: *What is the minimal sequence of allowed operations that produces the object?* This project applies assembly-theoretic measures to finite groups to determine whether this lens produces a novel invariant — one that separates structural simplicity from generative depth — or collapses to known complexity proxies.

---

## Part 1: Structural Foundations

### 1.1 The Clean Correspondences (Validated)

These mappings are mathematically natural and form the backbone of the project.

| Assembly Theory Concept | Group Theory Analogue | Strength |
|---|---|---|
| Assembly index | Generative complexity of a group | Core metric to define |
| Primitive building blocks | Finite simple groups | Strong (but weighting matters — see 1.2) |
| Assembly steps / joining operations | Group extensions (direct, semidirect, non-split) | Strongest bridge — extensions ARE construction histories |
| Assembly tree / pathway | Composition series / extension tree | Clean |
| Reuse of intermediates | Shared subgroups, quotient reuse | Natural |
| Construction program | Group presentation ⟨S \| R⟩ | Gives computable proxy immediately |

**Key insight from feedback:** Composition series as assembly backbone is the strongest structural bridge. Every finite group admits G₀ ⊲ G₁ ⊲ … ⊲ Gₙ with simple quotients. This is directly interpretable as: base primitives = simple groups, assembly steps = extensions.

### 1.2 Forced or Dangerous Mappings (Caution Required)

These require careful handling. Ignoring these warnings will compromise the project.

**Warning 1: Symmetry ≠ assembly depth.**
Highly symmetric objects can be structurally simple OR generatively deep, or vice versa. Do NOT assume monotonic relations between symmetry richness and assembly cost. This decoupling is actually the most interesting thing to test.

**Warning 2: Finite simple groups are NOT obviously equal-cost "atoms."**
In Assembly Theory, primitives are domain-dependent. Treating all simple groups as equal-cost atoms is likely wrong. The project MUST explore weighted primitives:
- Weight by order (|G|)
- Weight by Lie rank (for groups of Lie type)
- Weight by presentation complexity (number of generators + total relator length)
- Weight by representation dimension (smallest faithful representation)

**Warning 3: Representation theory may not map cleanly.**
Representations describe how a group *acts*, not how it is *constructed*. They are useful but second-order relative to extensions and presentations. Do not build the core metric on representation theory.

### 1.3 What Connects to the Monster Group

The Monster Group is the extreme test case. Key properties relevant to this project:
- Order: ~8.08 × 10⁵³ (the number)
- Smallest faithful representation: 196,883 dimensions
- Composition series: trivial (it IS simple — composition length 1)
- But its *internal structure* is enormously complex
- Contains 20 of the 26 sporadic groups as subquotients (the "Happy Family")
- Connected to modular forms via Monstrous Moonshine (196,884 = 196,883 + 1)
- Connected to the Leech lattice (24D sphere packing)
- Connected to vertex operator algebras / conformal field theory
- Connected to string theory (bosonic string on 24D torus)
- Witten's conjecture: symmetry of 3D pure quantum gravity

**Critical note:** The Monster has composition length 1 (it's simple), so a naive assembly index = 0. This immediately shows that composition length alone is insufficient. The assembly metric must capture *internal complexity of atoms*, not just the number of assembly steps. This is the first non-trivial design decision.

---

## Part 2: Three Candidate Invariants to Test

These come directly from the feedback and represent the novel contributions this project could make.

### Candidate Invariant 1: Assembly Depth of a Group

**Definition (to refine):** The minimal cost to construct G from chosen primitives via:
- Direct products
- Semidirect products
- General extensions (non-split)
- Presentations

**What makes this potentially new:** Closest known relatives are minimal presentation length, subgroup growth metrics, and profinite complexity. But this version incorporates *reuse* (assembly-theoretic) and *weighted primitives* — which is distinct.

**Design decisions required:**
- [ ] Choice of primitive set (all finite simple groups? cyclic p-groups? both as separate experiments?)
- [ ] Cost model (unit per operation? log(|G|) penalty? weighted by extension type?)
- [ ] Whether non-split extensions cost more than split ones (they should — they encode more "information")
- [ ] How to handle the internal complexity of simple groups themselves

### Candidate Invariant 2: Extension Entropy

**Definition:** Measure the branching complexity of extension paths leading to G.

Finite groups often admit MANY different extension realizations (different composition series, different extension types at each step). Quantifying the *size and structure* of this space is potentially interesting.

**Analogy:** In Assembly Theory, a molecule has one assembly index but potentially many assembly pathways. The number and diversity of pathways is itself informative. Same idea here.

**Computation:** For each group G, enumerate distinct composition series. For each series, enumerate possible extension types at each step. Measure:
- Total number of distinct construction paths
- Shannon entropy of the path distribution
- Whether certain paths are "preferred" (shorter, more symmetric)

### Candidate Invariant 3: Generative Asymmetry Index

**Definition:** Compare structural symmetry (automorphism group size |Aut(G)|) with generative complexity (assembly cost).

**Why this matters:** If these two quantities are *strongly decoupled* — if there exist groups that are highly symmetric but generatively deep, or generatively simple but structurally asymmetric — that is a genuinely new observation. The feedback explicitly states: "If strongly decoupled, that is publishable territory."

**Computation:**
- For each G: compute |Aut(G)| and assembly depth
- Plot and look for correlation (or lack thereof)
- Identify outlier families where the two diverge sharply

---

## Part 3: Experimental Plan

### Phase 1: Environment Setup

**Tools required:**
- GAP (Groups, Algorithms, Programming) — the symbolic algebra engine. This is NON-NEGOTIABLE as the mathematical core.
- Python / SageMath — for data analysis, visualization, clustering
- LLM (Claude via API or chat) — for hypothesis generation, code writing, pattern detection, cross-domain translation
- Git repository — for version control and reproducibility

**Architecture (from feedback — critical):**
```
LLM (planner / hypothesis generator)
  → GAP / SageMath (exact symbolic computation)
    → Metric computation (assembly index, extension entropy, etc.)
      → Result clustering & visualization (Python)
        → Conjecture surfacing (LLM)
```

**The LLM is the planner. GAP is the engine. If you invert this, the project collapses into noise.**

**Setup steps:**
- [ ] Install GAP 4.x with packages: SmallGroups, ATLAS, Cohomolo (for extension computation)
- [ ] Set up Python environment with: numpy, scipy, matplotlib, seaborn, pandas, networkx
- [ ] Create GitHub repository with structure:
  ```
  assembly-symmetry/
  ├── README.md
  ├── docs/
  │   ├── roadmap.md (this document)
  │   ├── references/
  │   │   ├── monster-group/        # Key papers, ATLAS data
  │   │   ├── assembly-theory/      # Cronin-Walker papers, responses
  │   │   └── group-theory/         # Classification, extensions, presentations
  │   └── hypotheses/               # LLM-generated conjectures, evolving
  ├── gap/
  │   ├── compute_composition.g     # Composition series for all groups
  │   ├── compute_presentations.g   # Minimal presentations
  │   ├── compute_automorphisms.g   # Aut(G) sizes
  │   └── compute_assembly.g        # The assembly index computation
  ├── python/
  │   ├── analysis.py               # Correlation, clustering, outlier detection
  │   ├── visualize.py              # Plots and diagrams
  │   └── compare_invariants.py     # Compare assembly index to known measures
  ├── data/
  │   ├── raw/                      # GAP output files
  │   ├── processed/                # Cleaned CSVs
  │   └── results/                  # Final analysis outputs
  └── notebooks/
      └── exploration.ipynb         # Interactive analysis
  ```

### Phase 2: Knowledge Base Construction

**Monster Group corpus — collect and organize:**
- [ ] ATLAS of Finite Groups data (character tables, subgroup structure, maximal subgroups)
- [ ] Online ATLAS (Robert Wilson's group) — machine-readable data
- [ ] Conway-Norton (1979) — Monstrous Moonshine conjecture
- [ ] Borcherds (1992) — Proof of Moonshine
- [ ] Frenkel-Lepowsky-Meurman (1988) — Moonshine Module / vertex operator algebra
- [ ] Griess (1982) — Construction of the Monster
- [ ] Witten (2007) — Monster and 3D gravity
- [ ] Umbral Moonshine papers (2012–present)
- [ ] Viazovska (2016) — Leech lattice optimality

**Assembly Theory corpus — collect and organize:**
- [ ] Cronin & Walker (2021) Nature paper — core Assembly Theory
- [ ] Cronin et al. — molecular assembly index experiments (mass spectrometry)
- [ ] Walker & Cronin — Assembly Theory as fundamental physics
- [ ] Response papers (critics arguing redundancy with Kolmogorov complexity)
- [ ] Cronin's rebuttal (physical measurability argument)
- [ ] Any formalization papers on assembly spaces / assembly graphs

**Group theory foundations:**
- [ ] Jordan-Hölder theorem (uniqueness of composition factors)
- [ ] Schreier's theorem (refinement of series)
- [ ] Extension theory (Schur-Zassenhaus, cohomological classification)
- [ ] Presentation theory (Tietze transformations, Andrews-Curtis conjecture)

**LLM task for this phase:** Read both corpuses and produce a structured translation document — mapping every core concept in Assembly Theory to its closest group-theoretic analogue, flagging where the mapping is clean vs. forced (per the feedback in Section 1.2).

### Phase 3: Define the Metric (The Critical Step)

This is where the project succeeds or fails. The metric must be:
1. Mathematically principled (not ad hoc)
2. Computable (at least for groups up to moderate order)
3. Distinct from known complexity measures (or the project is redundant)

**Proposed Definition — Symmetry Assembly Index (SAI):**

Given:
- A set P of primitive groups (finite simple groups, with assigned costs)
- A set O of allowed operations: {direct product, semidirect product, non-split extension}
- A cost function c(op) for each operation type
- A primitive cost function w(S) for each simple group S ∈ P

The SAI of a group G is the minimum total cost of any construction tree T that:
- Has leaves labeled by elements of P
- Has internal nodes labeled by operations from O
- Produces G at the root
- May reuse any intermediate node (assembly-theoretic reuse)

**Cost model options to test (run all three, compare):**

Model A — Unit cost:
- w(S) = 1 for all simple groups
- c(op) = 1 for all operations
- SAI = minimum number of operations

Model B — Order-weighted:
- w(S) = log₂(|S|) for each simple group
- c(direct product) = 1
- c(semidirect product) = 2
- c(non-split extension) = 3
- SAI = sum of w(leaves) + sum of c(operations) along minimum-cost tree

Model C — Presentation-weighted:
- w(S) = minimal presentation length of S (number of generators + total relator length)
- c(op) = as in Model B
- SAI = sum of w(leaves) + sum of c(operations)

**Why three models:** If all three produce the same ranking, the metric is robust. If they diverge, the divergence itself is informative — it tells you which aspect of "complexity" matters.

**Design decision log (track all choices and alternatives):**
- [ ] Document why each cost model was chosen
- [ ] Document alternatives considered and why they were rejected
- [ ] For each design decision, note what changes if you chose differently

### Phase 4: Minimum Viable Experiment (The Truth Test)

**This is the fastest signal check. If nothing interesting appears here, the larger vision is weak. If strong separation appears, the project has teeth.**

**Dataset:** All groups in GAP's SmallGroups library up to order N.
- Start with N = 100 (manageable, ~1,048 groups)
- Extend to N = 500 if results are promising
- Extend to N = 2000 if results are strong (this is ~49 billion groups — will need sampling)

**For each group G, compute:**

| Metric | Tool | Notes |
|---|---|---|
| Group order \|G\| | GAP: `Size(G)` | Baseline |
| Composition length | GAP: `CompositionSeries(G)` | Number of simple factors |
| Composition factors | GAP: `CompositionSeries(G)` | Which simple groups appear |
| Minimal number of generators | GAP: `RankPGroup(G)` or search | Known complexity proxy |
| Presentation length proxy | GAP: present and count | Generators + relator lengths |
| Automorphism group size \|Aut(G)\| | GAP: `AutomorphismGroup(G)` | Structural symmetry measure |
| SAI Model A | Custom GAP code | Unit-cost assembly index |
| SAI Model B | Custom GAP code | Order-weighted |
| SAI Model C | Custom GAP code | Presentation-weighted |

**Then test:**

1. **Correlations:** Compute pairwise correlations between all metrics. If SAI correlates >0.95 with composition length or presentation length, it's probably redundant. If correlation is moderate (0.4–0.8), there's signal.

2. **Clustering:** Use dimensionality reduction (PCA, t-SNE) on the multi-metric space. Do groups cluster in interesting ways? Do known families (cyclic, dihedral, symmetric, PSL) form distinct clusters?

3. **Outliers:** Identify groups where SAI diverges sharply from other measures — especially where:
   - High structural symmetry (large Aut) + high SAI (generatively deep)
   - Low structural symmetry + low SAI
   - These are the "generative asymmetry" cases from Candidate Invariant 3

4. **The Cronin Threshold:** Is there an SAI value below which groups are "trivially constructible" and above which they require more structured/rare operations? Plot the distribution of SAI values — is it smooth or does it have a gap?

**Success criteria for Phase 4:**
- ✅ SAI is computable for the dataset within reasonable time
- ✅ SAI does NOT collapse to a single known measure (correlation < 0.9 with all known proxies)
- ✅ At least one of: interesting clustering, sharp outliers, or a distributional gap
- ❌ If SAI correlates >0.95 with composition length, rethink the metric
- ❌ If no outliers or structure appears, the larger vision is weak

### Phase 5: Monster Group Probe

Only proceed here if Phase 4 shows signal.

The Monster is too large to compute directly, but we can probe it indirectly:

**5.1 The Happy Family:**
20 of the 26 sporadic groups sit inside the Monster as subquotients. Compute SAI for the smaller sporadics that are computationally accessible (Mathieu groups M₁₁, M₁₂, M₂₂, M₂₃, M₂₄ — these are in GAP). Compare their SAI profiles to non-sporadic groups of similar order.

**Hypothesis to test:** Sporadic groups have anomalous SAI profiles — their assembly depth is qualitatively different from groups in infinite families of comparable order.

**5.2 Moonshine Connection:**
The j-function coefficients encode dimensions of Monster representations:
j(q) = q⁻¹ + 744 + 196884q + 21493760q² + ...

Each coefficient decomposes into Monster representations. Ask: is there a correlation between the assembly-theoretic complexity of the coefficient's decomposition and the position in the q-expansion?

**This is speculative but high-reward.** If the assembly framework reveals structure in the Moonshine coefficients that pure representation theory doesn't see, that's a significant finding.

**5.3 The Leech Lattice Path:**
The Conway group Co₁ (symmetries of the Leech lattice) sits inside the Monster. Co₁ is large but more tractable than the Monster. Compute what we can about its extension structure and compare to the broader SAI landscape.

### Phase 6: Chaos and Order Connection

**6.1 Assembly Index as Order-Chaos Measure:**
Groups with low SAI → simple construction → "ordered"
Groups with high SAI → complex construction → "on the edge of chaos"

Test whether SAI correlates with known measures of "complexity" in dynamical systems associated with groups (e.g., growth rates of Cayley graphs, properties of random walks on groups).

**6.2 Modular Forms Bridge:**
Both the Monster (via Moonshine) and chaotic dynamical systems connect to modular forms. If SAI reveals structure in the Moonshine coefficients, and those same modular forms appear in chaos theory, then SAI becomes a bridge between algebraic complexity and dynamical complexity.

**This is the long-range vision — do not attempt until Phases 4 and 5 produce results.**

---

## Part 4: LLM Integration Protocol

### What the LLM Does (Correct Use)

| Phase | LLM Role | Example |
|---|---|---|
| Knowledge base | Cross-domain translator | "Map Assembly Theory's 'copy number' to group theory" |
| Metric design | Hypothesis generator | "What if non-split extensions cost more because they encode cohomological data?" |
| Code generation | Write GAP and Python scripts | "Write a GAP function to compute composition series and output as CSV" |
| Analysis | Pattern detector | "Given these 1000 data points, what clusters or outliers do you see?" |
| Conjecture | Formal statement drafter | "The data suggests SAI and Aut(G) are decoupled for nilpotent groups. State this precisely." |
| Debugging | Sanity checker | "This result says a cyclic group has higher SAI than S₅. Is that plausible?" |

### What the LLM Does NOT Do (Critical Boundary)

- **NOT** the mathematical engine — all exact computation goes through GAP/SageMath
- **NOT** a proof system — if a pattern is found, proving it requires formal methods (Lean) or human mathematicians
- **NOT** a source of truth for group-theoretic facts — always verify against ATLAS/GAP
- **NOT** a replacement for understanding — the human must understand what the metrics mean

### Prompt Templates for Each Phase

**Translation prompt:**
"I have two concepts. In Assembly Theory: [concept]. In finite group theory: [concept]. Are these structurally analogous? Where does the analogy hold and where does it break? Be precise about the failure modes."

**Hypothesis generation prompt:**
"Given these computed SAI values for groups of order ≤ 100: [data]. And these known properties: [composition length, |Aut|, etc.]. What patterns do you see? Propose 3 testable hypotheses, ranked by how surprising they would be if true."

**Code generation prompt:**
"Write a GAP function that takes a finite group G and returns: (1) its composition series as a list of simple factor names, (2) the number of generators in a minimal generating set, (3) the size of Aut(G). Output as tab-separated values."

**Sanity check prompt:**
"I computed SAI = 7 for the dihedral group D₁₂ and SAI = 3 for PSL(2,7). Is this plausible given that PSL(2,7) is simple and D₁₂ is a semidirect product of Z₆ and Z₂? If not, what's likely wrong with my computation?"

---

## Part 5: Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| SAI collapses to composition length | Medium | Fatal | Test multiple cost models. If all collapse, the metric is redundant — stop and report that finding. |
| SAI collapses to presentation length | Medium | Fatal | Same as above. |
| Computation explodes for moderate N | Medium | Delays | Start with N = 100. Sample for larger N. Focus on specific families rather than exhaustive enumeration. |
| Sporadic groups show no anomaly | Low-Medium | Major | Would weaken the Monster connection specifically, but the general invariant could still be interesting. |
| Moonshine connection is noise | Medium | Reduces scope | This is the speculative part. The core experiment (Phase 4) stands independently. |
| LLM hallucinates group-theoretic "facts" | High | Corrupts results | ALWAYS verify LLM claims against GAP computation. Never trust LLM arithmetic or algebra. |

---

## Part 6: Success Criteria & Deliverables

### Minimum Success (Phase 4 complete)
- A computable metric (SAI) defined on finite groups
- Evidence it is or is not distinct from known measures
- A dataset of SAI values for groups up to order 100+
- Clear statement of whether the approach has "teeth"

### Medium Success (Phase 5 partial)
- SAI is distinct from known measures
- Sporadic groups show anomalous profiles
- At least one surprising pattern identified
- A preprint-ready write-up of findings

### Maximum Success (Phases 4–6)
- SAI reveals structure in Moonshine coefficients
- A new invariant accepted as non-trivial by group theorists
- A bridge between Assembly Theory and algebra that Cronin/Walker find interesting
- Connection to chaos/dynamics established

---

## Part 7: Immediate Next Steps (This Week)

1. **Set up the GAP environment** — install GAP, load SmallGroups library, verify it works by computing composition series of a few known groups.

2. **Write the first GAP script** — compute composition series, number of generators, and |Aut(G)| for all groups of order ≤ 50. Export as CSV. This is your baseline dataset.

3. **Implement SAI Model A** (unit cost) — the simplest version. Compute for the same groups. Check: does it just equal composition length? If yes, move to Model B.

4. **Build the repository** — create the GitHub structure, commit this roadmap, start the reference collection.

5. **Collect the papers** — gather the Monster Group and Assembly Theory corpuses listed in Phase 2.

6. **First analysis** — correlations, scatter plots, outlier identification on whatever data you have from steps 2–3.

**The goal for week 1 is to answer one question: does SAI Model A collapse to composition length? If no, you have a project. If yes, you iterate the metric.**

---

## Appendix A: Key References

### Assembly Theory
- Sharma, A., Czégel, D., Lachmann, M., Kempes, C.P., Walker, S.I. & Cronin, L. (2023). Assembly Theory explains and quantifies selection and evolution. *Nature*, 622, 321–328.
- Marshall, S.M., Murray, A.R.G., Cronin, L. (2021). A probabilistic framework for identifying biosignatures using Pathway Complexity. *Phil. Trans. R. Soc. A*, 379.
- Liu, Y. et al. — molecular assembly mass spectrometry experiments

### Monster Group & Moonshine
- Conway, J.H. & Norton, S.P. (1979). Monstrous Moonshine. *Bull. London Math. Soc.*, 11, 308–339.
- Borcherds, R.E. (1992). Monstrous moonshine and monstrous Lie superalgebras. *Invent. Math.*, 109, 405–444.
- Frenkel, I., Lepowsky, J. & Meurman, A. (1988). *Vertex Operator Algebras and the Monster*.
- Griess, R.L. (1982). The Friendly Giant. *Invent. Math.*, 69, 1–102.
- Witten, E. (2007). Three-Dimensional Gravity Revisited. arXiv:0706.3359.
- Gannon, T. (2006). *Moonshine beyond the Monster*.
- Duncan, J.F.R., Griffin, M.J. & Ono, K. (2015). Moonshine. *Research in the Mathematical Sciences*, 2.

### Computational Group Theory
- GAP System: https://www.gap-system.org/
- Wilson, R.A. et al. ATLAS of Finite Group Representations: https://atlas.math.rwth-aachen.de/
- Holt, D.F., Eick, B. & O'Brien, E.A. (2005). *Handbook of Computational Group Theory*.

---

## Appendix B: The Feedback (Preserved Verbatim)

> Short answer: the idea is intellectually legitimate and technically plausible. It is nontrivial, but not crackpot. The value will depend entirely on how precisely you define the assembly metric on algebraic objects.

> Final judgment: The proposal is structurally sound and worth a tightly scoped computational probe. The risk is not conceptual incoherence; the risk is producing a metric that collapses to known group-complexity proxies. The entire project hinges on defining an assembly cost that is mathematically principled rather than ad hoc.
