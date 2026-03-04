#!/usr/bin/env python
"""Robustness checks for MA-vs-symmetry correlation."""

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import GraphDescriptors
from scipy import stats


VALID_PG_RE = r"^[A-Za-z0-9]+$"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run sanity/robustness checks on pilot/scale output.")
    parser.add_argument("--input", required=True, help="Input CSV (must include smiles, order, assembly_index, point_group).")
    parser.add_argument("--output", default="data/results/sanity_report.md", help="Output markdown report path.")
    parser.add_argument("--bootstrap", type=int, default=1000, help="Bootstrap iterations for rho CI.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    return parser.parse_args()


def spearman(df: pd.DataFrame) -> dict:
    clean = df[["assembly_index", "order"]].dropna()
    if len(clean) < 3:
        return {"rho": np.nan, "p": np.nan, "n": len(clean)}
    rho, p = stats.spearmanr(clean["assembly_index"], clean["order"])
    return {"rho": float(rho), "p": float(p), "n": int(len(clean))}


def bootstrap_rho(df: pd.DataFrame, n_boot: int, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    clean = df[["assembly_index", "order"]].dropna().to_numpy()
    if len(clean) < 10:
        return (np.nan, np.nan)

    rhos = []
    n = len(clean)
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        sample = clean[idx]
        rho, _ = stats.spearmanr(sample[:, 0], sample[:, 1])
        if not math.isnan(rho):
            rhos.append(rho)
    if not rhos:
        return (np.nan, np.nan)
    return (float(np.percentile(rhos, 2.5)), float(np.percentile(rhos, 97.5)))


def add_size_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    heavy_atoms = []
    bertz = []
    rings = []
    for smiles in out["smiles"].astype(str):
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            heavy_atoms.append(np.nan)
            bertz.append(np.nan)
            rings.append(np.nan)
            continue
        heavy_atoms.append(mol.GetNumHeavyAtoms())
        bertz.append(GraphDescriptors.BertzCT(mol))
        rings.append(mol.GetRingInfo().NumRings())
    out["num_heavy_atoms"] = heavy_atoms
    out["bertz_ct"] = bertz
    out["num_rings"] = rings
    return out


def partial_spearman(df: pd.DataFrame, controls: list[str]) -> dict:
    cols = ["assembly_index", "order"] + controls
    d = df[cols].dropna()
    if len(d) < 20:
        return {"r": np.nan, "p": np.nan, "n": len(d)}

    x = stats.rankdata(d["assembly_index"].to_numpy())
    y = stats.rankdata(d["order"].to_numpy())
    z = np.column_stack([stats.rankdata(d[c].to_numpy()) for c in controls])
    z = np.column_stack([np.ones(len(z)), z])  # intercept

    bx, *_ = np.linalg.lstsq(z, x, rcond=None)
    by, *_ = np.linalg.lstsq(z, y, rcond=None)
    rx = x - z @ bx
    ry = y - z @ by
    r, p = stats.pearsonr(rx, ry)
    return {"r": float(r), "p": float(p), "n": int(len(d))}


def size_bin_stats(df: pd.DataFrame) -> pd.DataFrame:
    d = df.dropna(subset=["num_heavy_atoms", "assembly_index", "order"]).copy()
    if len(d) < 50:
        return pd.DataFrame(columns=["bin", "n", "rho", "p"])
    d["size_bin"] = pd.cut(
        d["num_heavy_atoms"],
        bins=[0, 4, 6, 8, 10, 20, 100],
        labels=["1-4", "5-6", "7-8", "9-10", "11-20", "21+"],
        include_lowest=True,
    )
    rows = []
    for b, part in d.groupby("size_bin"):
        if len(part) < 30:
            continue
        rho, p = stats.spearmanr(part["assembly_index"], part["order"])
        rows.append({"bin": str(b), "n": int(len(part)), "rho": float(rho), "p": float(p)})
    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()
    np.random.seed(args.seed)

    df = pd.read_csv(args.input)
    required = {"smiles", "order", "assembly_index", "point_group"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Input missing required columns: {missing}")

    raw = df.copy()
    raw_stats = spearman(raw)
    ci_low, ci_high = bootstrap_rho(raw, args.bootstrap, args.seed)

    clean = raw[raw["point_group"].astype(str).str.match(VALID_PG_RE, na=False)].copy()
    clean_stats = spearman(clean)

    with_features = add_size_features(clean)
    partial = partial_spearman(with_features, ["num_heavy_atoms", "num_rings", "bertz_ct"])
    bins = size_bin_stats(with_features)

    out = []
    out.append("# MA vs Symmetry Sanity Report")
    out.append("")
    out.append(f"- Input: `{args.input}`")
    out.append(f"- Rows: {len(raw)}")
    out.append("")
    out.append("## Baseline")
    out.append(f"- Spearman rho: {raw_stats['rho']:.6f}")
    out.append(f"- p-value: {raw_stats['p']:.6g}")
    out.append(f"- n: {raw_stats['n']}")
    out.append(f"- 95% bootstrap CI for rho: [{ci_low:.6f}, {ci_high:.6f}]")
    out.append("")
    out.append("## Label Cleaning")
    out.append(f"- Rows after dropping nonstandard point groups: {len(clean)}")
    out.append(f"- Spearman rho (clean): {clean_stats['rho']:.6f}")
    out.append(f"- p-value (clean): {clean_stats['p']:.6g}")
    out.append("")
    out.append("## Size/Complexity Controls")
    out.append("- Partial correlation (rank-residualized) controlling for:")
    out.append("  `num_heavy_atoms`, `num_rings`, `bertz_ct`")
    out.append(f"- Partial r: {partial['r']:.6f}")
    out.append(f"- p-value: {partial['p']:.6g}")
    out.append(f"- n: {partial['n']}")
    out.append("")
    out.append("## Size Bin Stability")
    if len(bins) == 0:
        out.append("- Not enough data for size-bin analysis.")
    else:
        out.append("| Bin | n | rho | p |")
        out.append("|---|---:|---:|---:|")
        for _, r in bins.iterrows():
            out.append(f"| {r['bin']} | {int(r['n'])} | {r['rho']:.6f} | {r['p']:.6g} |")
    out.append("")
    out.append("## Interpretation")
    out.append("- Stable rho across these checks supports a real association.")
    out.append("- Large shifts after controls/cleaning indicate proxy or labeling bias.")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(out))
    print(f"Saved report: {output_path}")


if __name__ == "__main__":
    main()
