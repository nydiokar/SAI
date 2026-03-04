#!/usr/bin/env python
"""Scale QM9 analysis with exact MA and hard per-molecule subprocess timeout."""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

from src.analyze import test_ma_vs_symmetry
from src.compute_symmetry import compute_point_group
from src.fetch_molecules import get_qm9_sample


EXACT_MA_SNIPPET = r"""
from rdkit import Chem
import assembly_theory as at
import sys

smi = sys.argv[1]
mol = Chem.MolFromSmiles(smi)
if mol is None:
    print("ERR:invalid_smiles")
    raise SystemExit(2)
mb = Chem.MolToMolBlock(mol)
ma = int(at.index(mb))
if ma >= (2**32 - 1):
    print("ERR:invalid_or_overflow")
    raise SystemExit(3)
print(ma)
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run scalable exact-MA QM9 analysis.")
    parser.add_argument("--n", type=int, default=131970, help="Number of molecules to process.")
    parser.add_argument("--batch-size", type=int, default=500, help="Checkpoint batch size.")
    parser.add_argument("--workers", type=int, default=8, help="Thread workers (subprocess orchestrators).")
    parser.add_argument("--tolerance", type=float, default=0.5, help="Symmetry tolerance.")
    parser.add_argument("--ma-timeout", type=int, default=6, help="Hard timeout seconds for exact MA subprocess.")
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/qm9_exact_scaled_results.csv",
        help="Output CSV path (checkpoint and final dataset).",
    )
    return parser.parse_args()


def compute_exact_ma_subprocess(smiles: str, timeout_seconds: int) -> tuple[bool, int | None, str, str | None]:
    """Compute exact MA in isolated subprocess with hard timeout."""
    try:
        proc = subprocess.run(
            [sys.executable, "-c", EXACT_MA_SNIPPET, smiles],
            capture_output=True,
            text=True,
            timeout=max(int(timeout_seconds), 1),
        )
    except subprocess.TimeoutExpired:
        return False, None, "assembly_theory_exact", "hard_timeout"
    except Exception as exc:
        return False, None, "assembly_theory_exact", f"subprocess_error:{exc}"

    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()

    if proc.returncode == 0:
        try:
            return True, int(out), "assembly_theory_exact", None
        except ValueError:
            return False, None, "assembly_theory_exact", f"parse_error:{out}"

    if out.startswith("ERR:"):
        return False, None, "assembly_theory_exact", out.replace("ERR:", "", 1)

    return False, None, "assembly_theory_exact", f"child_exit_{proc.returncode}:{err[:120]}"


def process_task(task: tuple[int, str, str, float, int]) -> dict:
    mol_index, mol_id, smiles, tolerance, ma_timeout = task

    sym = compute_point_group(smiles, tolerance=tolerance)
    if sym and sym.get("point_group"):
        sym_ok = True
        point_group = sym.get("point_group")
        order = sym.get("order")
        max_rotation_order = sym.get("max_rotation_order")
        symmetry_confidence = sym.get("confidence")
        symmetry_method = sym.get("method")
    else:
        sym_ok = False
        point_group = None
        order = None
        max_rotation_order = None
        symmetry_confidence = None
        symmetry_method = None

    ma_ok, ma_value, ma_source, ma_error = compute_exact_ma_subprocess(smiles, ma_timeout)
    return {
        "mol_index": mol_index,
        "id": mol_id,
        "smiles": smiles,
        "symmetry_success": sym_ok,
        "point_group": point_group,
        "order": order,
        "max_rotation_order": max_rotation_order,
        "symmetry_confidence": symmetry_confidence,
        "symmetry_method": symmetry_method,
        "ma_success": ma_ok,
        "assembly_index": ma_value,
        "ma_source": ma_source,
        "ma_error": ma_error,
    }


def load_resume_state(output_path: Path) -> tuple[set[int], int]:
    if not output_path.exists():
        return set(), 0
    try:
        existing = pd.read_csv(output_path, usecols=["mol_index"])
        done = set(existing["mol_index"].dropna().astype(int).tolist())
        return done, len(done)
    except Exception:
        return set(), 0


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading QM9 sample n={args.n}...")
    df = get_qm9_sample(n=args.n, use_real_data=True, data_dir="data/raw")
    if len(df) == 0:
        raise RuntimeError("No molecules loaded from QM9/local sources.")

    df = df.reset_index(drop=True)
    if "id" not in df.columns:
        df["id"] = df.index.astype(str)
    df["mol_index"] = df.index
    n_total = min(args.n, len(df))
    df = df.iloc[:n_total].copy()

    done_indices, n_done = load_resume_state(output_path)
    print(f"Resume state: {n_done} rows already processed")

    remaining_df = df[~df["mol_index"].isin(done_indices)].copy()
    if len(remaining_df) == 0:
        print("Nothing to do. Existing output already covers requested range.")
        return

    run_start = time.time()
    print(
        f"Starting exact scale run: pending={len(remaining_df)} workers={args.workers} "
        f"ma_timeout={args.ma_timeout}s"
    )

    for batch_start in range(0, len(remaining_df), args.batch_size):
        batch = remaining_df.iloc[batch_start: batch_start + args.batch_size].copy()
        tasks = [
            (int(r.mol_index), str(r.id), str(r.smiles), args.tolerance, args.ma_timeout)
            for r in batch.itertuples(index=False)
        ]

        t0 = time.time()
        rows = []
        with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = [ex.submit(process_task, task) for task in tasks]
            for i, fut in enumerate(cf.as_completed(futures), start=1):
                rows.append(fut.result())
                if i % 250 == 0:
                    print(f"  batch_progress {i}/{len(tasks)}")

        out_df = pd.DataFrame(rows).sort_values("mol_index")
        write_header = not output_path.exists()
        out_df.to_csv(output_path, mode="a", header=write_header, index=False)

        elapsed = time.time() - t0
        processed_now = min(batch_start + args.batch_size, len(remaining_df))
        overall_elapsed = time.time() - run_start
        rate = processed_now / overall_elapsed if overall_elapsed > 0 else 0.0
        eta = (len(remaining_df) - processed_now) / rate if rate > 0 else 0.0
        print(
            f"[{processed_now}/{len(remaining_df)} pending] wrote {len(out_df)} rows "
            f"in {elapsed:.1f}s | rate {rate:.1f}/s | ETA {eta:.0f}s"
        )

    final_df = pd.read_csv(output_path)
    usable = final_df[(final_df["symmetry_success"] == True) & (final_df["ma_success"] == True)].copy()

    print("\nExact scale run complete")
    print(f"rows_total={len(final_df)} rows_usable={len(usable)}")
    if len(usable) >= 3:
        result = test_ma_vs_symmetry(usable[["assembly_index", "order"]])
        print(f"rho={result['rho']:.6f}, p={result['p_value']:.6g}, n={result['n']}")
    else:
        print("Not enough usable rows for correlation.")

    print(
        "status_counts "
        f"ma_success={int((final_df['ma_success'] == True).sum())} "
        f"ma_fail={int((final_df['ma_success'] != True).sum())} "
        f"sym_success={int((final_df['symmetry_success'] == True).sum())} "
        f"sym_fail={int((final_df['symmetry_success'] != True).sum())}"
    )
    print(f"saved={output_path}")


if __name__ == "__main__":
    main()
