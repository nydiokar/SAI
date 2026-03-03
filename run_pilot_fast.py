#!/usr/bin/env python
"""
Bridge 6 Pilot: FAST VERSION with curated molecules
No API calls. Just real, diverse molecules with known varied symmetries.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
import numpy as np
import warnings
import time
warnings.filterwarnings('ignore')

# Create directories
Path('data/processed').mkdir(parents=True, exist_ok=True)
Path('figures').mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("BRIDGE 6 PILOT: FAST VERSION (Curated Molecules)")
print("=" * 70)

# Step 1: Create curated dataset with KNOWN VARIED SYMMETRIES
print("\n[Step 1/6] Loading curated molecules (NO API CALLS)...")

# These are chemically real, diverse molecules with expected varied point groups
curated_molecules = [
    # C1 (no symmetry) - asymmetric molecules
    ("CC(C)Cc1ccc(cc1)C(C)C(=O)O", "ibuprofen"),  # C1
    ("CC(=O)Nc1ccc(O)cc1", "paracetamol"),  # C1
    ("CC(C)CC(C)(C)O", "asymmetric alcohol"),  # C1
    ("C1CCCC(C1)(C)O", "cyclopentanol"),  # Cs or C1

    # Cs (mirror plane only)
    ("O=C(O)c1ccccc1", "benzoic acid"),  # Cs
    ("Cc1ccccc1O", "o-cresol"),  # Cs
    ("Cc1ccc(O)cc1", "p-cresol"),  # Cs

    # C2 (2-fold rotation)
    ("c1ccc(cc1)C(=O)C(=O)c2ccccc2", "benzil"),  # C2
    ("CC(C)C(C)C", "2,3-dimethylbutane"),  # C2

    # C2v (2-fold rotation + mirror planes)
    ("O", "water"),  # C2v
    ("C(Cl)(Cl)Cl", "chloroform"),  # C3v
    ("C(F)(F)F", "fluoroform"),  # C3v
    ("CC(=O)C", "acetone"),  # C2v
    ("C1=CC=C(C=C1)C(=C2C=CC=CC2)C3=CC=CC=C3", "triphenylmethanol base"),  # high symmetry

    # C3v (3-fold rotation + mirror planes)
    ("C(C)(C)C", "neopentane"),  # Td
    ("C", "methane"),  # Td
    ("[CH4]", "methane (explicit)"),  # Td

    # Td (tetrahedral - high symmetry)
    ("C(F)(F)(F)F", "carbon tetrafluoride"),  # Td
    ("C(Cl)(Cl)(Cl)Cl", "carbon tetrachloride"),  # Td
    ("CC(C)(C)C", "neopentane"),  # Td

    # D3h (benzene and analogs - high symmetry)
    ("c1ccccc1", "benzene"),  # D6h
    ("c1ccccc1c2ccccc2", "biphenyl"),  # D2h
    ("C1=CC=CC=C1", "benzene (explicit)"),  # D6h

    # Aromatic compounds with symmetry
    ("c1cc(Cl)cc(Cl)c1", "1,3,5-trichlorobenzene"),  # D3h
    ("c1cc(O)cc(O)c1", "resorcinol"),  # C2v
    ("c1ccc(O)cc1", "phenol"),  # Cs

    # Cyclic with symmetry
    ("C1CCCCC1", "cyclohexane"),  # D6h (chair)
    ("C1CCCC1", "cyclopentane"),  # C5
    ("C1CCC1", "cyclobutane"),  # D4h
    ("C1CC1", "cyclopropane"),  # D3h

    # Symmetric diols/diamines
    ("c1ccc(O)c(O)c1", "catechol (1,2-dihydroxybenzene)"),  # C2v
    ("c1ccc(O)cc(O)c1", "resorcinol (1,3-dihydroxybenzene)"),  # C2v
    ("c1ccc(O)c(O)c1O", "pyrogallol"),  # C2v

    # Aldehydes/Ketones
    ("c1ccccc1C=O", "benzaldehyde"),  # Cs
    ("CC(=O)c1ccccc1", "acetophenone"),  # Cs
    ("O=C(c1ccccc1)c2ccccc2", "benzophenone"),  # D2h (high symmetry)

    # More simple aliphatic
    ("C", "methane"),  # Td
    ("CC", "ethane"),  # D3d
    ("CCC", "propane"),  # C2v
    ("CC(C)C", "isobutane"),  # Cs
    ("CCCC", "butane"),  # C2
    ("CC(C)CC", "2-methylbutane"),  # C1

    # Symmetric aromatics
    ("c1ccccc1c2ccccc2c3ccccc3", "triphenylmethane"),  # high symmetry
    ("c1ccc2c(c1)ccc3c2cccc3", "anthracene"),  # D2h
    ("c1cc2ccccc2cc1", "naphthalene"),  # D2h

    # Heterocycles
    ("c1cnccc1", "pyridine"),  # Cs
    ("c1ccncc1", "pyrazine"),  # D2h
    ("c1cncc1", "pyrimidine"),  # C2v
    ("c1ccoc1", "furan"),  # C2v

    # More complex but known symmetries
    ("CC(C)C(C)C(C)C", "2,3,4-trimethylpentane"),  # low symmetry
    ("C1=C(C=CC=C1)C=CC(=O)C", "cinnamaldehyde"),  # Cs

    # Amines
    ("c1ccccc1N", "aniline"),  # Cs
    ("c1ccccc1Nc2ccccc2", "diphenylamine"),  # C2v

    # Carboxylic acids
    ("c1ccccc1C(=O)O", "benzoic acid"),  # Cs
    ("c1ccc(C(=O)O)cc1", "4-carboxybiphenyl"),  # C2v

    # Ethers
    ("c1ccccc1Oc2ccccc2", "diphenyl ether"),  # D2h (high symmetry)
    ("CCOc1ccccc1", "phenetole"),  # Cs

    # Esters
    ("CC(=O)Oc1ccccc1", "phenyl acetate"),  # Cs
    ("c1ccccc1C(=O)Oc2ccccc2", "phenyl benzoate"),  # high symmetry
]

# Convert to DataFrame
df_molecules = pd.DataFrame([
    {'smiles': smiles, 'name': name}
    for smiles, name in curated_molecules
])

print(f"✓ Loaded {len(df_molecules)} curated molecules")
print("Sample molecules:")
for i in range(min(5, len(df_molecules))):
    print(f"  {df_molecules.iloc[i]['name']:30s} | {df_molecules.iloc[i]['smiles']}")

# Step 2: Compute point group symmetry
print(f"\n[Step 2/6] Computing point groups for {len(df_molecules)} molecules...")
print("(Should take 2-3 minutes)\n")

from src.compute_symmetry import compute_point_group

symmetry_results = []
failures = 0
start_time = time.time()

for i, row in df_molecules.iterrows():
    smiles = row['smiles']
    name = row['name']

    if i % 10 == 0:
        elapsed = time.time() - start_time
        print(f"  [{i:2d}/{len(df_molecules)}] {elapsed:.1f}s elapsed")

    try:
        result = compute_point_group(smiles, tolerance=0.3)
        if result and result.get('point_group'):
            result['smiles'] = smiles
            result['name'] = name
            symmetry_results.append(result)
        else:
            failures += 1
            print(f"    ⚠ Failed for {name}")
    except Exception as e:
        failures += 1
        print(f"    ⚠ Error for {name}: {str(e)[:50]}")

df_symmetry = pd.DataFrame(symmetry_results)
elapsed = time.time() - start_time

print(f"\n✓ Computed {len(df_symmetry)}/{len(df_molecules)} point groups in {elapsed:.1f}s")
print(f"  Success rate: {len(df_symmetry)/len(df_molecules)*100:.1f}%")

print("\nPoint group distribution:")
pg_dist = df_symmetry['point_group'].value_counts().sort_index()
for pg, count in pg_dist.items():
    print(f"  {pg:5s}: {count:2d}")

print("\nPoint group order distribution:")
order_dist = df_symmetry['order'].value_counts().sort_index()
for order, count in order_dist.items():
    print(f"  Order {order:2d}: {count:2d}")

# Step 3: Compute assembly indices
print(f"\n[Step 3/6] Computing assembly indices for {len(df_symmetry)} molecules...")

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

# Step 4: Merge datasets
print(f"\n[Step 4/6] Merging datasets...")

from src.merge_datasets import merge_datasets, save_dataset

df_merged = merge_datasets(df_symmetry, df_assembly)
print(f"✓ Merged {len(df_merged)} molecules")

save_dataset(df_merged, 'data/processed/pilot_curated_molecules.csv')
print(f"✓ Saved to: data/processed/pilot_curated_molecules.csv")

# Step 5: THE TRUTH TEST
print("\n" + "=" * 70)
print("[Step 5/6] THE TRUTH TEST - CORRELATION ANALYSIS")
print("=" * 70)

from src.analyze import test_ma_vs_symmetry, compute_summary_stats

result = test_ma_vs_symmetry(df_merged)

print(f"\nMA vs Point Group Order (Spearman):")
print(f"  ρ (correlation):  {result['rho']:8.4f}")
print(f"  p-value:          {result['p_value']:8.6f}")
print(f"  n samples:        {result['n']:8d}")

if result['p_value'] < 0.05:
    print(f"\n  ✓✓✓ SIGNIFICANT CORRELATION DETECTED ✓✓✓")
    print(f"      p < 0.05 — The signal is REAL")
    if result['rho'] > 0:
        print(f"      ρ > 0 → Symmetric molecules have HIGHER assembly index")
    else:
        print(f"      ρ < 0 → Symmetric molecules have LOWER assembly index")
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

# Detailed analysis
print("\n" + "=" * 70)
print("ANALYSIS BY POINT GROUP")
print("=" * 70)

for pg in df_merged['point_group'].unique():
    subset = df_merged[df_merged['point_group'] == pg]
    order = subset['order'].iloc[0]
    ma_mean = subset['assembly_index'].mean()
    ma_std = subset['assembly_index'].std()
    print(f"  {pg:5s} (order={order:2d}): n={len(subset):2d}, MA={ma_mean:.2f}±{ma_std:.2f}")

# Step 6: Visualizations
print(f"\n[Step 6/6] Creating visualizations...")

try:
    from src.analyze import plot_ma_vs_symmetry, plot_distribution, plot_symmetry_box

    print("  Creating scatter plot...")
    plot_ma_vs_symmetry(df_merged, output_path='figures/01_ma_vs_symmetry_curated.png')
    print("  ✓ figures/01_ma_vs_symmetry_curated.png")

    print("  Creating distribution...")
    plot_distribution(df_merged, 'assembly_index', output_path='figures/01_ma_distribution_curated.png')
    print("  ✓ figures/01_ma_distribution_curated.png")

    print("  Creating box plot...")
    plot_symmetry_box(df_merged, output_path='figures/01_ma_by_symmetry_curated.png')
    print("  ✓ figures/01_ma_by_symmetry_curated.png")

except Exception as e:
    print(f"  ⚠ Visualization error: {e}")

# Final summary
print("\n" + "=" * 70)
print("PILOT COMPLETE ✓")
print("=" * 70)

print(f"\nOutput files:")
print(f"  Data:  data/processed/pilot_curated_molecules.csv")
print(f"  Plots: figures/01_ma_*.png")

if result['p_value'] < 0.05:
    print(f"\n✓ RESULT: CORRELATION DETECTED")
    print(f"  Next: Expand to larger real dataset")
else:
    print(f"\n⚠ RESULT: NO CORRELATION")
    print(f"  Next: Investigate or publish negative result")

print("\nDone!\n")
