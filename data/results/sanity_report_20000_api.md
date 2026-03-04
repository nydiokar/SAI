# MA vs Symmetry Sanity Report

- Input: `data/processed/qm9_scaled_results_20000.csv`
- Rows: 19480

## Baseline
- Spearman rho: -0.164517
- p-value: 3.05243e-118
- n: 19480
- 95% bootstrap CI for rho: [-0.176686, -0.148434]

## Label Cleaning
- Rows after dropping nonstandard point groups: 19467
- Spearman rho (clean): -0.163754
- p-value (clean): 4.48926e-117

## Size/Complexity Controls
- Partial correlation (rank-residualized) controlling for:
  `num_heavy_atoms`, `num_rings`, `bertz_ct`
- Partial r: -0.159356
- p-value: 6.79412e-111
- n: 19467

## Size Bin Stability
| Bin | n | rho | p |
|---|---:|---:|---:|
| 1-4 | 44 | -0.006281 | 0.967723 |
| 5-6 | 734 | -0.102203 | 0.00558043 |
| 7-8 | 18680 | -0.137908 | 5.57095e-80 |

## API Benchmark (Heuristic vs Molecular-Assembly API)
- Requested rows: 10
- Matched API rows: 0
- Not enough API matches for a stable comparison.

## Interpretation
- Stable rho across these checks supports a real association.
- Large shifts after controls/cleaning indicate proxy or labeling bias.