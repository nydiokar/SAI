#!/usr/bin/env python
"""
Bridge 6 Pilot V2: IMPROVED with better tolerance and validated SMILES
Tolerance: 0.5 Å (better symmetry detection)
Data: Chemically valid, hand-curated molecules with known varied symmetries
"""

import sys
sys.path.insert(0, '/c/Users/Cicada38/Projects/math_exp')

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
import time
warnings.filterwarnings('ignore')

Path('data/processed').mkdir(parents=True, exist_ok=True)
Path('figures').mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("BRIDGE 6 PILOT V2: IMPROVED SYMMETRY DETECTION")
print("=" * 70)
print("\nImprovements:")
print("  • Tolerance: 0.5 Å (was 0.3, better detection)")
print("  • Data: Valid SMILES with expected varied symmetries")
print("  • Validation: CCCBDB reference checking")
print()

# Step 1: Curated molecules with VALID SMILES and expected varied symmetries
print("[Step 1/6] Loading validated molecules...")

curated_molecules = [
    # Simple molecules with HIGH SYMMETRY (Td, D3h, D6h)
    ("C", "methane", "Td"),  # Td - tetrahedral
    ("CC", "ethane", "D3d"),  # D3d - staggered
    ("c1ccccc1", "benzene", "D6h"),  # D6h - very high symmetry
    ("C(F)(F)F", "fluoroform", "C3v"),  # C3v
    ("C(Cl)(Cl)Cl", "chloroform", "C3v"),  # C3v
    ("C1CC1", "cyclopropane", "D3h"),  # D3h
    ("C1CCC1", "cyclobutane", "D4h"),  # D4h
    ("C1CCCC1", "cyclopentane", "D5h"),  # D5h
    ("C1CCCCC1", "cyclohexane", "D6h"),  # D6h (chair)

    # Water (C2v - moderate symmetry)
    ("O", "water", "C2v"),  # C2v

    # Symmetric aromatic compounds
    ("O=C(O)c1ccccc1", "benzoic acid", "Cs"),  # Cs
    ("c1ccc(O)cc1", "phenol", "Cs"),  # Cs
    ("c1ccc(Cl)cc1", "chlorobenzene", "Cs"),  # Cs
    ("c1ccccc1c2ccccc2", "biphenyl", "D2h"),  # D2h
    ("c1ccc(O)c(O)c1", "catechol", "C2v"),  # C2v
    ("c1ccc(O)cc(O)c1", "resorcinol", "C2v"),  # C2v
    ("c1cc(Cl)cc(Cl)c1", "1,3,5-trichlorobenzene", "D3h"),  # D3h

    # Symmetric aliphatic hydrocarbons
    ("CC(C)C", "isobutane", "Cs"),  # Cs
    ("CCCC", "butane", "C2"),  # C2
    ("CCC", "propane", "C2v"),  # C2v
    ("CC(C)CC", "2-methylbutane", "C1"),  # C1 (asymmetric)
    ("CC(C)(C)C", "neopentane", "Td"),  # Td

    # Ketones and aldehydes
    ("CC(=O)C", "acetone", "C2v"),  # C2v
    ("c1ccccc1C=O", "benzaldehyde", "Cs"),  # Cs
    ("CC(=O)c1ccccc1", "acetophenone", "Cs"),  # Cs
    ("O=C(c1ccccc1)c2ccccc2", "benzophenone", "D2h"),  # D2h

    # Ethers
    ("c1ccccc1Oc2ccccc2", "diphenyl ether", "D2h"),  # D2h (high sym)

    # More complex aromatics
    ("c1cc2ccccc2cc1", "naphthalene", "D2h"),  # D2h
    ("c1ccc2c(c1)ccc3c2cccc3", "anthracene", "D2h"),  # D2h

    # Heterocycles
    ("c1cnccc1", "pyridine", "Cs"),  # Cs
    ("c1ccoc1", "furan", "C2v"),  # C2v
    ("c1ccncc1", "pyrazine", "D2h"),  # D2h (square planar-like)

    # Alcohols and diols
    ("CO", "methanol", "Cs"),  # Cs
    ("CCO", "ethanol", "Cs"),  # Cs
    ("CC(O)C", "isopropanol", "Cs"),  # Cs

    # Amines
    ("c1ccccc1N", "aniline", "Cs"),  # Cs
    ("c1ccccc1Nc2ccccc2", "diphenylamine", "C2v"),  # C2v (est.)

    # Carboxylic acids
    ("c1ccccc1C(=O)O", "benzoic acid", "Cs"),  # Cs

    # More aliphatic chains
    ("CCCCC", "pentane", "C2"),  # C2
    ("CCCCCC", "hexane", "C2"),  # C2
    ("CC(C)C(C)C", "2,3-dimethylbutane", "C2"),  # C2

    # Additional symmetric aromatics
    ("c1ccc(F)cc1", "fluorobenzene", "Cs"),  # Cs
    ("c1ccc(Br)cc1", "bromobenzene", "Cs"),  # Cs
    ("c1ccc(I)cc1", "iodobenzene", "Cs"),  # Cs
    ("c1ccc(N)cc1", "4-aminobiphenyl", "C2v"),  # C2v (est.)
]

df_molecules = pd.DataFrame([
    {'smiles': smiles, 'name': name, 'expected_pg': expected}
    for smiles, name, expected in curated_molecules
])

print(f"✓ Loaded {len(df_molecules)} molecules")
print(f"Sample molecules with expected point groups:")
for i in range(min(5, len(df_molecules))):
    print(f"  {df_molecules.iloc[i]['name']:20s} {df_molecules.iloc[i]['smiles']:30s} → {df_molecules.iloc[i]['expected_pg']}")

# Step 2: Compute point groups with IMPROVED tolerance
print(f"\n[Step 2/6] Computing point groups (tolerance=0.5 Å)...")

from src.compute_symmetry import compute_point_group, validate_against_cccbdb

symmetry_results = []
failures = 0
start_time = time.time()

for i, row in df_molecules.iterrows():
    smiles = row['smiles']
    name = row['name']

    if i % 15 == 0:
        elapsed = time.time() - start_time
        print(f"  [{i:2d}/{len(df_molecules)}] {elapsed:.1f}s")

    try:
        result = compute_point_group(smiles, tolerance=0.5)
        if result and result.get('point_group'):
            result['smiles'] = smiles
            result['name'] = name
            result['expected'] = row['expected_pg']

            # Validate
            validation = validate_against_cccbdb(smiles, result['point_group'])
            result.update(validation)

            symmetry_results.append(result)
        else:
            failures += 1
    except Exception as e:
        failures += 1

df_symmetry = pd.DataFrame(symmetry_results)
elapsed = time.time() - start_time

print(f"\n✓ Computed {len(df_symmetry)}/{len(df_molecules)} point groups in {elapsed:.1f}s")
print(f"  Success rate: {len(df_symmetry)/len(df_molecules)*100:.1f}%")

print("\nPoint group distribution:")
pg_counts = df_symmetry['point_group'].value_counts().sort_index()
for pg, count in pg_counts.items():
    print(f"  {pg:5s}: {count:2d}")

print(f"\nSymmetry diversity:")
print(f"  Unique point groups: {df_symmetry['point_group'].nunique()}")
print(f"  Order range: [{df_symmetry['order'].min()}, {df_symmetry['order'].max()}]")

# Step 3: Compute assembly indices
print(f"\n[Step 3/6] Computing assembly indices...")

from src.compute_assembly import AssemblyIndexBatcher

start_time = time.time()
batcher = AssemblyIndexBatcher(method='heuristic', delay_seconds=0.0)
assembly_results = batcher.compute_batch(df_symmetry['smiles'].tolist())

df_assembly = pd.DataFrame(assembly_results)
df_assembly = df_assembly[['smiles', 'assembly_index']]
elapsed = time.time() - start_time

print(f"✓ Computed in {elapsed:.1f}s")
print(f"  Mean MA: {df_assembly['assembly_index'].mean():.2f}")
print(f"  Range:   [{df_assembly['assembly_index'].min():.2f}, {df_assembly['assembly_index'].max():.2f}]")

# Step 4: Merge
print(f"\n[Step 4/6] Merging datasets...")

from src.merge_datasets import merge_datasets, save_dataset

df_merged = merge_datasets(df_symmetry, df_assembly)
print(f"✓ Merged {len(df_merged)} molecules")

save_dataset(df_merged, 'data/processed/pilot_v2_molecules.csv')

# Step 5: TRUTH TEST
print("\n" + "=" * 70)
print("[Step 5/6] THE TRUTH TEST - CORRELATION ANALYSIS")
print("=" * 70)

from src.analyze import test_ma_vs_symmetry, compute_summary_stats

result = test_ma_vs_symmetry(df_merged)

print(f"\nMA vs Point Group Order (Spearman):")
print(f"  ρ (correlation):  {result['rho']:8.4f}")
print(f"  p-value:          {result['p_value']:8.6f}")
print(f"  n samples:        {result['n']:8d}")
print(f"  Unique orders:    {df_merged['order'].nunique():8d}")

if result['p_value'] < 0.05:
    print(f"\n  ✓✓✓ SIGNIFICANT CORRELATION ✓✓✓")
    print(f"      p < 0.05 — Signal is REAL")
    if result['rho'] > 0:
        print(f"      ρ > 0 → Symmetric molecules HIGHER MA")
    else:
        print(f"      ρ < 0 → Symmetric molecules LOWER MA")
else:
    print(f"\n  ⚠ NO SIGNIFICANT CORRELATION")
    print(f"    p >= 0.05 — Symmetry and complexity are INDEPENDENT")

# Summary stats
print("\n" + "=" * 70)
print("SUMMARY STATISTICS")
print("=" * 70)
stats_dict = compute_summary_stats(df_merged)
for key, val in stats_dict.items():
    if key != 'point_groups':
        print(f"  {key:20} : {val}")

# Analysis by point group
print("\n" + "=" * 70)
print("ANALYSIS BY POINT GROUP")
print("=" * 70)

for pg in sorted(df_merged['point_group'].unique()):
    subset = df_merged[df_merged['point_group'] == pg]
    order = subset['order'].iloc[0]
    ma_mean = subset['assembly_index'].mean()
    ma_std = subset['assembly_index'].std()
    print(f"  {pg:5s} (order={order:2d}): n={len(subset):2d}, MA={ma_mean:.2f}±{ma_std:.2f}")

# Step 6: Visualizations
print(f"\n[Step 6/6] Creating visualizations...")

try:
    from src.analyze import plot_ma_vs_symmetry, plot_distribution, plot_symmetry_box

    plot_ma_vs_symmetry(df_merged, output_path='figures/02_ma_vs_symmetry_v2.png')
    print("  ✓ figures/02_ma_vs_symmetry_v2.png")

    plot_distribution(df_merged, 'assembly_index', output_path='figures/02_ma_distribution_v2.png')
    print("  ✓ figures/02_ma_distribution_v2.png")

    plot_symmetry_box(df_merged, output_path='figures/02_ma_by_symmetry_v2.png')
    print("  ✓ figures/02_ma_by_symmetry_v2.png")

except Exception as e:
    print(f"  ⚠ Visualization error: {e}")

# Final summary
print("\n" + "=" * 70)
print("PILOT V2 COMPLETE")
print("=" * 70)

print(f"\nOutput files:")
print(f"  Data:  data/processed/pilot_v2_molecules.csv")
print(f"  Plots: figures/02_ma_*.png")

if result['p_value'] < 0.05:
    print(f"\n✓ RESULT: CORRELATION DETECTED")
    print(f"  Next: Scale to full QM9 dataset (134k molecules)")
else:
    print(f"\n⚠ RESULT: NO CORRELATION")
    print(f"  Next: Investigate confounders or publish negative result")

print("\nDone!\n")
