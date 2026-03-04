# MA vs Symmetry Sanity Report

- Input: `data/processed/pilot_real_molecules_5000.csv`
- Rows: 4943

## Baseline
- Spearman rho: -0.192487
- p-value: 1.8193e-42
- n: 4943
- 95% bootstrap CI for rho: [-0.219073, -0.166473]

## Label Cleaning
- Rows after dropping nonstandard point groups: 4934
- Spearman rho (clean): -0.192329
- p-value (clean): 2.52509e-42

## Size/Complexity Controls
- Partial correlation (rank-residualized) controlling for:
  `num_heavy_atoms`, `num_rings`, `bertz_ct`
- Partial r: -0.138215
- p-value: 1.792e-22
- n: 4934

## Size Bin Stability
| Bin | n | rho | p |
|---|---:|---:|---:|
| 1-4 | 44 | -0.006281 | 0.967723 |
| 5-6 | 734 | -0.102203 | 0.00558043 |
| 7-8 | 4147 | -0.175166 | 6.26354e-30 |

## API Benchmark (Heuristic vs Molecular-Assembly API)
- Skipped (`--api-benchmark-n 0`).

## Interpretation
- Stable rho across these checks supports a real association.
- Large shifts after controls/cleaning indicate proxy or labeling bias.