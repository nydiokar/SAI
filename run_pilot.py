#!/usr/bin/env python
"""
Bridge 6 Pilot: Real Molecules Test
Run this script to test if molecular symmetry correlates with assembly index.
WITH PROGRESS LOGGING
"""

import sys
sys.path.insert(0, '/c/Users/Cicada38/Projects/math_exp')

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
import time
warnings.filterwarnings('ignore')

# Create directories
Path('data/processed').mkdir(parents=True, exist_ok=True)
Path('figures').mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("BRIDGE 6 PILOT: REAL MOLECULES TEST")
print("=" * 70)

# Step 1: Fetch real molecules from PubChem
print("\n[Step 1/6] Fetching real molecules from PubChem...")
print("Expected time: 2-3 minutes (500 molecules @ 10ms per API call)\n")

from src.fetch_molecules import get_qm9_sample

start_time = time.time()
df_molecules = get_qm9_sample(n=500, use_real_data=True)
elapsed = time.time() - start_time

print(f"\n✓ Fetched {len(df_molecules)} molecules in {elapsed:.1f}s")
print("Sample SMILES:")
for i, row in df_molecules.head(3).iterrows():
    print(f"  {row['smiles']}")

# Step 2: Compute point group symmetry
print("\n[Step 2/6] Computing point groups...")
print(f"Expected time: 10-15 minutes ({len(df_molecules)} molecules @ ~1s per molecule)\n")

from src.compute_symmetry import compute_point_group

symmetry_results = []
failures = 0
start_time = time.time()

for i, smiles in enumerate(df_molecules['smiles']):
    if i % 25 == 0:
        elapsed = time.time() - start_time
        rate = (i + 1) / elapsed if elapsed > 0 else 0
        eta = (len(df_molecules) - i) / rate if rate > 0 else 0
        print(f"  [{i:3d}/{len(df_molecules)}] {rate:.1f} mol/s | ETA {eta:.0f}s")

    try:
        result = compute_point_group(smiles, tolerance=0.3)
        if result and result.get('point_group'):
            result['smiles'] = smiles
            symmetry_results.append(result)
        else:
            failures += 1
    except Exception as e:
        failures += 1

df_symmetry = pd.DataFrame(symmetry_results)
elapsed = time.time() - start_time
print(f"\n✓ Computed {len(df_symmetry)} point groups in {elapsed:.1f}s")
print(f"  Success rate: {len(df_symmetry)/len(df_molecules)*100:.1f}%")

print("\nPoint group distribution:")
pg_dist = df_symmetry['point_group'].value_counts()
for pg, count in pg_dist.items():
    print(f"  {pg:5s}: {count:3d}")

# Step 3: Compute assembly indices
print("\n[Step 3/6] Computing assembly indices...")
print(f"Expected time: 1-2 minutes ({len(df_symmetry)} molecules)\n")

from src.compute_assembly import AssemblyIndexBatcher

start_time = time.time()
batcher = AssemblyIndexBatcher(method='heuristic', delay_seconds=0.0)
assembly_results = batcher.compute_batch(df_symmetry['smiles'].tolist())

df_assembly = pd.DataFrame(assembly_results)
df_assembly = df_assembly[['smiles', 'assembly_index']]
elapsed = time.time() - start_time

print(f"\n✓ Computed {len(df_assembly)} assembly indices in {elapsed:.1f}s")
print(f"  Mean MA: {df_assembly['assembly_index'].mean():.2f}")
print(f"  Std MA:  {df_assembly['assembly_index'].std():.2f}")
print(f"  Range:   [{df_assembly['assembly_index'].min():.2f}, {df_assembly['assembly_index'].max():.2f}]")

# Step 4: Merge datasets
print("\n[Step 4/6] Merging datasets...")

from src.merge_datasets import merge_datasets, save_dataset

df_merged = merge_datasets(df_symmetry, df_assembly)
print(f"✓ Merged {len(df_merged)} molecules")

save_dataset(df_merged, 'data/processed/pilot_real_molecules.csv')
print(f"✓ Saved to: data/processed/pilot_real_molecules.csv")

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
    print(f"    (Still publishable as orthogonal descriptors)")

# Summary stats
print("\n" + "=" * 70)
print("SUMMARY STATISTICS")
print("=" * 70)
stats_dict = compute_summary_stats(df_merged)
for key, val in stats_dict.items():
    if key != 'point_groups':
        print(f"  {key:20} : {val}")

# Detailed analysis by point group
print("\n" + "=" * 70)
print("ANALYSIS BY POINT GROUP")
print("=" * 70)

pg_analysis = df_merged.groupby('point_group').agg({
    'assembly_index': ['count', 'mean', 'std'],
    'order': 'first'
}).round(3)

for pg, row in pg_analysis.iterrows():
    count = int(row[('assembly_index', 'count')])
    mean = row[('assembly_index', 'mean')]
    std = row[('assembly_index', 'std')]
    order = int(row[('order', 'first')])
    print(f"  {pg:5s} (order={order:2d}): n={count:3d}, MA={mean:.2f}±{std:.2f}")

# Step 6: Visualizations
print("\n[Step 6/6] Creating visualizations...")

try:
    from src.analyze import plot_ma_vs_symmetry, plot_distribution, plot_symmetry_box

    print("  Creating scatter plot...")
    plot_ma_vs_symmetry(df_merged, output_path='figures/01_ma_vs_symmetry_real.png')
    print("  ✓ figures/01_ma_vs_symmetry_real.png")

    print("  Creating distribution histogram...")
    plot_distribution(df_merged, 'assembly_index', output_path='figures/01_ma_distribution_real.png')
    print("  ✓ figures/01_ma_distribution_real.png")

    print("  Creating box plot...")
    plot_symmetry_box(df_merged, output_path='figures/01_ma_by_symmetry_real.png')
    print("  ✓ figures/01_ma_by_symmetry_real.png")

except Exception as e:
    print(f"  ⚠ Visualization failed: {e}")

# Final summary
print("\n" + "=" * 70)
print("PILOT COMPLETE ✓")
print("=" * 70)

print(f"\nOutput files:")
print(f"  Data:    data/processed/pilot_real_molecules.csv")
print(f"  Plots:   figures/01_ma_vs_symmetry_real.png")
print(f"           figures/01_ma_distribution_real.png")
print(f"           figures/01_ma_by_symmetry_real.png")

if result['p_value'] < 0.05:
    print(f"\n✓ RESULT: CORRELATION DETECTED")
    print(f"  p-value = {result['p_value']:.6f} < 0.05")
    print(f"  Next step: Scale to full QM9 (134k molecules) for validation")
else:
    print(f"\n⚠ RESULT: NO CORRELATION")
    print(f"  p-value = {result['p_value']:.6f} >= 0.05")
    print(f"  Next step: Investigate confounders or publish as negative result")

print("\n" + "=" * 70)
