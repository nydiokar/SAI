#!/usr/bin/env python3
"""Bridge 6 symmetry validity/stability gate.

This script answers one question:
"Are current symmetry labels trustworthy enough to support a definitive claim?"

Method:
1) Align run results to native QM9 SDF molecules by index (mol_index).
2) Validate index mapping quality via canonical no-H SMILES agreement.
3) Compare current labels vs trusted labels from native 3D coordinates.
4) Check correlation stability (MA vs symmetry order) on same molecule set.
5) Emit pass/fail gate outputs.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from scipy.stats import spearmanr

from src.compute_symmetry import detect_point_group_pymatgen


@dataclass
class NativeMol:
    mol_index: int
    mol: Chem.Mol
    smiles_raw: str
    smiles_noh: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run symmetry validity gate against native QM9 geometries.")
    parser.add_argument("--results", type=str, default="data/processed/qm9_exact_scaled_results_full.csv")
    parser.add_argument("--qm9-sdf", type=str, default="data/raw/qm9/gdb9.sdf")
    parser.add_argument("--out-dir", type=str, default="data/results")
    parser.add_argument("--n", type=int, default=10000, help="Sample size; use <=0 for all eligible rows.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--tolerances", type=str, default="0.1,0.3,0.5,0.8")
    parser.add_argument("--primary-tol", type=float, default=0.5)
    parser.add_argument("--progress-every", type=int, default=1000)

    # Gate thresholds
    parser.add_argument("--min-align-rate", type=float, default=0.98)
    parser.add_argument("--min-order-match", type=float, default=0.95)
    parser.add_argument("--min-label-match", type=float, default=0.85)
    parser.add_argument("--max-rho-delta", type=float, default=0.02)
    parser.add_argument("--min-tol-order-stability", type=float, default=0.95)
    parser.add_argument("--allow-low-align", action="store_true")
    parser.add_argument("--rdkit-verbose", action="store_true")
    return parser.parse_args()


def parse_tolerances(raw: str) -> list[float]:
    vals = [v.strip() for v in raw.split(",") if v.strip()]
    if not vals:
        raise ValueError("No tolerances provided.")
    return [float(v) for v in vals]


def smiles_noh_from_smiles(smiles: str) -> str | None:
    mol = Chem.MolFromSmiles(str(smiles))
    if mol is None:
        return None
    return Chem.MolToSmiles(Chem.RemoveHs(mol), canonical=True)


def build_native_indexed(sdf_path: Path) -> list[NativeMol]:
    """Build index-ordered native mol list using same strict behavior as loader fallback."""
    supplier = Chem.SDMolSupplier(str(sdf_path), removeHs=False, sanitize=False, strictParsing=False)
    out: list[NativeMol] = []
    seen = 0
    skipped = 0
    for mol in supplier:
        seen += 1
        if mol is None:
            skipped += 1
            continue
        try:
            work = Chem.Mol(mol)
            Chem.SanitizeMol(work)  # strict, same semantics as loader fallback
            raw = Chem.MolToSmiles(work, canonical=True)
            noh = Chem.MolToSmiles(Chem.RemoveHs(work), canonical=True)
        except Exception:
            skipped += 1
            continue
        out.append(NativeMol(mol_index=len(out), mol=work, smiles_raw=raw, smiles_noh=noh))
    print(f"SDF parse summary: seen={seen} kept={len(out)} skipped={skipped}")
    return out


def compute_trusted_symmetry(mol: Chem.Mol, tolerance: float) -> tuple[str, int] | None:
    try:
        conf = mol.GetConformer()
        coords = []
        symbols = []
        for i, atom in enumerate(mol.GetAtoms()):
            pos = conf.GetAtomPosition(i)
            coords.append([float(pos.x), float(pos.y), float(pos.z)])
            symbols.append(atom.GetSymbol())
        out = detect_point_group_pymatgen(np.array(coords), symbols, tolerance=tolerance)
        return str(out.get("point_group")), int(out.get("order", 0))
    except Exception:
        return None


def nearest_tolerance(target: float, values: list[float]) -> float:
    return sorted(values, key=lambda x: abs(x - target))[0]


def coarse_pg(pg: str) -> str:
    v = (pg or "").strip()
    if v in {"C1", "Cs"}:
        return "LOW_SYM"
    return v


def main() -> None:
    args = parse_args()
    if not args.rdkit_verbose:
        RDLogger.DisableLog("rdApp.error")
        RDLogger.DisableLog("rdApp.warning")

    results_path = Path(args.results)
    sdf_path = Path(args.qm9_sdf)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not results_path.exists():
        raise FileNotFoundError(f"Missing results CSV: {results_path}")
    if not sdf_path.exists():
        raise FileNotFoundError(f"Missing QM9 SDF: {sdf_path}")

    tolerances = parse_tolerances(args.tolerances)
    primary_tol = nearest_tolerance(args.primary_tol, tolerances)

    results = pd.read_csv(results_path, low_memory=False)
    needed = ["mol_index", "smiles", "point_group", "order", "assembly_index", "ma_success", "symmetry_success"]
    missing = [c for c in needed if c not in results.columns]
    if missing:
        raise ValueError(f"Missing required columns in results CSV: {missing}")

    usable = results[(results["ma_success"] == True) & (results["symmetry_success"] == True)].copy()
    usable["mol_index"] = usable["mol_index"].astype(int)
    usable["smiles_noh"] = usable["smiles"].map(smiles_noh_from_smiles)
    usable = usable[usable["smiles_noh"].notna()].copy()
    print(f"Usable rows from results: {len(usable)}")

    print(f"Building native indexed molecule list from {sdf_path}...")
    native = build_native_indexed(sdf_path)
    if len(native) == 0:
        raise RuntimeError("No native molecules parsed from SDF.")
    max_native_idx = len(native) - 1

    aligned = usable[(usable["mol_index"] >= 0) & (usable["mol_index"] <= max_native_idx)].copy()
    aligned["native_smiles_noh"] = aligned["mol_index"].map(lambda i: native[int(i)].smiles_noh)
    aligned["index_align_match"] = aligned["smiles_noh"] == aligned["native_smiles_noh"]

    align_rate = float(aligned["index_align_match"].mean()) if len(aligned) else 0.0
    print(f"Index alignment check: matched={int(aligned['index_align_match'].sum())}/{len(aligned)} ({align_rate:.4f})")
    if (align_rate < args.min_align_rate) and (not args.allow_low_align):
        raise RuntimeError(
            f"Alignment rate {align_rate:.4f} below threshold {args.min_align_rate:.4f}. "
            "Abort to avoid invalid symmetry comparison."
        )

    eval_base = aligned[aligned["index_align_match"] == True].copy()
    if len(eval_base) == 0:
        raise RuntimeError("No aligned rows available for evaluation.")

    if args.n > 0 and args.n < len(eval_base):
        eval_base = eval_base.sample(n=args.n, random_state=args.seed).copy()
    eval_base = eval_base.reset_index(drop=True)
    print(f"Evaluation rows: {len(eval_base)}")

    trusted_rows = []
    for i, row in enumerate(eval_base.itertuples(index=False), start=1):
        mol = native[int(row.mol_index)].mol
        for tol in tolerances:
            trusted = compute_trusted_symmetry(mol, tolerance=tol)
            if trusted is None:
                continue
            pg, order = trusted
            trusted_rows.append(
                {
                    "mol_index": int(row.mol_index),
                    "smiles": row.smiles,
                    "assembly_index": float(row.assembly_index),
                    "current_pg": str(row.point_group),
                    "current_order": int(row.order),
                    "trusted_pg": pg,
                    "trusted_order": int(order),
                    "tolerance": float(tol),
                }
            )
        if args.progress_every > 0 and (i % args.progress_every == 0):
            print(f"  progress {i}/{len(eval_base)}")

    trusted_df = pd.DataFrame(trusted_rows)
    if len(trusted_df) == 0:
        raise RuntimeError("No trusted symmetry values were computed.")

    trusted_df["exact_label_match"] = trusted_df["current_pg"] == trusted_df["trusted_pg"]
    trusted_df["order_match"] = trusted_df["current_order"] == trusted_df["trusted_order"]
    trusted_df["order_abs_delta"] = (trusted_df["current_order"] - trusted_df["trusted_order"]).abs()
    trusted_df["current_pg_coarse"] = trusted_df["current_pg"].map(coarse_pg)
    trusted_df["trusted_pg_coarse"] = trusted_df["trusted_pg"].map(coarse_pg)
    trusted_df["coarse_label_match"] = trusted_df["current_pg_coarse"] == trusted_df["trusted_pg_coarse"]
    trusted_df["coarse_order_match"] = trusted_df["order_match"] | (
        (trusted_df["current_pg_coarse"] == "LOW_SYM") & (trusted_df["trusted_pg_coarse"] == "LOW_SYM")
    )

    # Per-tolerance metrics.
    metrics = []
    for tol, g in trusted_df.groupby("tolerance", sort=True):
        rho_current, p_current = spearmanr(g["assembly_index"], g["current_order"])
        rho_trusted, p_trusted = spearmanr(g["assembly_index"], g["trusted_order"])
        metrics.append(
            {
                "tolerance": float(tol),
                "n_eval": int(len(g)),
                "exact_label_match_rate": float(g["exact_label_match"].mean()),
                "order_match_rate": float(g["order_match"].mean()),
                "coarse_label_match_rate": float(g["coarse_label_match"].mean()),
                "coarse_order_match_rate": float(g["coarse_order_match"].mean()),
                "rho_current": float(rho_current),
                "p_current": float(p_current),
                "rho_trusted": float(rho_trusted),
                "p_trusted": float(p_trusted),
                "rho_delta": float(abs(rho_trusted - rho_current)),
            }
        )
    metrics_df = pd.DataFrame(metrics).sort_values("tolerance").reset_index(drop=True)

    # Tolerance stability of trusted order per molecule.
    tol_order_stability = (
        trusted_df.groupby("mol_index")["trusted_order"]
        .nunique()
        .pipe(lambda s: float((s == 1).mean()) if len(s) else 0.0)
    )
    tol_coarse_stability = (
        trusted_df.groupby("mol_index")["trusted_pg_coarse"]
        .nunique()
        .pipe(lambda s: float((s == 1).mean()) if len(s) else 0.0)
    )

    primary = metrics_df.loc[metrics_df["tolerance"] == primary_tol].iloc[0]
    practical_pass = bool(
        (align_rate >= args.min_align_rate)
        and (float(primary["coarse_order_match_rate"]) >= 0.97)
        and (float(primary["coarse_label_match_rate"]) >= 0.90)
        and (float(primary["rho_delta"]) <= args.max_rho_delta)
        and (float(primary["rho_current"]) * float(primary["rho_trusted"]) >= 0)
        and (tol_coarse_stability >= args.min_tol_order_stability)
    )
    gate_pass = bool(
        (align_rate >= args.min_align_rate)
        and (float(primary["order_match_rate"]) >= args.min_order_match)
        and (float(primary["exact_label_match_rate"]) >= args.min_label_match)
        and (float(primary["rho_delta"]) <= args.max_rho_delta)
        and (float(primary["rho_current"]) * float(primary["rho_trusted"]) >= 0)
        and (tol_order_stability >= args.min_tol_order_stability)
    )

    gate_df = pd.DataFrame(
        [
            {
                "results_csv": str(results_path),
                "qm9_sdf": str(sdf_path),
                "sample_n": int(len(eval_base)),
                "alignment_rate": align_rate,
                "primary_tolerance": float(primary_tol),
                "primary_n_eval": int(primary["n_eval"]),
                "primary_exact_label_match_rate": float(primary["exact_label_match_rate"]),
                "primary_order_match_rate": float(primary["order_match_rate"]),
                "primary_coarse_label_match_rate": float(primary["coarse_label_match_rate"]),
                "primary_coarse_order_match_rate": float(primary["coarse_order_match_rate"]),
                "primary_rho_current": float(primary["rho_current"]),
                "primary_rho_trusted": float(primary["rho_trusted"]),
                "primary_rho_delta": float(primary["rho_delta"]),
                "tol_order_stability_rate": float(tol_order_stability),
                "tol_coarse_stability_rate": float(tol_coarse_stability),
                "pass_align": bool(align_rate >= args.min_align_rate),
                "pass_order_match": bool(float(primary["order_match_rate"]) >= args.min_order_match),
                "pass_label_match": bool(float(primary["exact_label_match_rate"]) >= args.min_label_match),
                "pass_rho_delta": bool(float(primary["rho_delta"]) <= args.max_rho_delta),
                "pass_direction": bool(float(primary["rho_current"]) * float(primary["rho_trusted"]) >= 0),
                "pass_tol_stability": bool(tol_order_stability >= args.min_tol_order_stability),
                "practical_gate_pass": practical_pass,
                "gate_pass": gate_pass,
            }
        ]
    )

    primary_eval = trusted_df[trusted_df["tolerance"] == primary_tol].copy()
    confusion = (
        primary_eval.groupby(["current_pg", "trusted_pg"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
        .sort_values("count", ascending=False)
    )
    disagreements = primary_eval[primary_eval["exact_label_match"] == False].copy()
    disagreements = disagreements.sort_values("order_abs_delta", ascending=False).head(500)

    # Save outputs.
    metrics_path = out_dir / "symmetry_gate_metrics.csv"
    gate_path = out_dir / "symmetry_gate_decision.csv"
    rho_path = out_dir / "bridge6_rho_comparison.csv"
    confusion_path = out_dir / "symmetry_confusion_top.csv"
    disagreement_path = out_dir / "symmetry_disagreement_samples.csv"
    align_path = out_dir / "symmetry_alignment_metrics.csv"
    summary_path = out_dir / "symmetry_validity_gate_summary.md"

    metrics_df.to_csv(metrics_path, index=False)
    metrics_df[["tolerance", "n_eval", "rho_current", "p_current", "rho_trusted", "p_trusted", "rho_delta"]].to_csv(
        rho_path, index=False
    )
    gate_df.to_csv(gate_path, index=False)
    confusion.head(250).to_csv(confusion_path, index=False)
    disagreements.to_csv(disagreement_path, index=False)
    pd.DataFrame([{"aligned_rows": int(len(aligned)), "alignment_rate": align_rate}]).to_csv(align_path, index=False)

    summary_lines = [
        "# Symmetry Validity Gate Summary",
        "",
        f"- sample_n: {int(len(eval_base))}",
        f"- alignment_rate: {align_rate:.4f}",
        f"- primary_tolerance: {primary_tol}",
        f"- primary_exact_label_match_rate: {float(primary['exact_label_match_rate']):.4f}",
        f"- primary_order_match_rate: {float(primary['order_match_rate']):.4f}",
        f"- primary_coarse_label_match_rate: {float(primary['coarse_label_match_rate']):.4f}",
        f"- primary_coarse_order_match_rate: {float(primary['coarse_order_match_rate']):.4f}",
        f"- primary_rho_current: {float(primary['rho_current']):.6f}",
        f"- primary_rho_trusted: {float(primary['rho_trusted']):.6f}",
        f"- primary_rho_delta: {float(primary['rho_delta']):.6f}",
        f"- tol_order_stability_rate: {tol_order_stability:.4f}",
        f"- tol_coarse_stability_rate: {tol_coarse_stability:.4f}",
        f"- practical_gate_pass: {practical_pass}",
        f"- gate_pass: {gate_pass}",
        "",
        "## Criteria",
        f"- alignment_rate >= {args.min_align_rate}",
        f"- order_match_rate >= {args.min_order_match}",
        f"- exact_label_match_rate >= {args.min_label_match}",
        f"- abs(rho_trusted - rho_current) <= {args.max_rho_delta}",
        "- direction unchanged (rho_current * rho_trusted >= 0)",
        f"- tolerance order stability >= {args.min_tol_order_stability}",
    ]
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")

    print(f"Saved: {metrics_path}")
    print(f"Saved: {gate_path}")
    print(f"Saved: {rho_path}")
    print(f"Saved: {confusion_path}")
    print(f"Saved: {disagreement_path}")
    print(f"Saved: {align_path}")
    print(f"Saved: {summary_path}")
    print(f"Gate pass: {gate_pass}")


if __name__ == "__main__":
    main()
