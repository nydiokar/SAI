"""Exact molecular Assembly Index (MA) computation utilities."""

from __future__ import annotations

import signal
import time
from dataclasses import dataclass

from rdkit import Chem


class ExactMATimeoutError(Exception):
    """Raised when an exact MA call exceeds the configured timeout."""


def _timeout_handler(signum, frame):
    raise ExactMATimeoutError("exact_ma_timeout")


def compute_ma_exact(smiles: str, timeout_seconds: int = 3) -> dict:
    """
    Compute exact MA via DaymudeLab's `assembly-theory` package.

    Returns a dict with standardized status fields.
    """
    try:
        import assembly_theory as at
    except ImportError:
        return {"success": False, "source": "assembly_theory_exact", "error": "not_installed"}

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"success": False, "source": "assembly_theory_exact", "error": "invalid_smiles"}

    mol_block = Chem.MolToMolBlock(mol)

    old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(max(int(timeout_seconds), 1))
    try:
        ma = int(at.index(mol_block))
    except ExactMATimeoutError:
        return {"success": False, "source": "assembly_theory_exact", "error": "timeout"}
    except Exception as exc:
        return {"success": False, "source": "assembly_theory_exact", "error": str(exc)}
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

    # `assembly_theory` can return u32::MAX as an invalid sentinel.
    if ma >= (2**32 - 1):
        return {"success": False, "source": "assembly_theory_exact", "error": "invalid_or_overflow"}

    return {"assembly_index": ma, "source": "assembly_theory_exact", "success": True}


def compute_assembly_index(smiles: str, prefer: str = "exact", timeout_seconds: int = 3) -> dict:
    """
    Compute MA with exact algorithm only.

    `prefer` is kept for backward compatibility but only `"exact"` is accepted.
    """
    if prefer != "exact":
        return {
            "success": False,
            "source": "assembly_theory_exact",
            "error": f"unsupported_method:{prefer}",
        }
    return compute_ma_exact(smiles, timeout_seconds=timeout_seconds)


@dataclass
class AssemblyIndexBatcher:
    """Batch exact MA computation with optional per-call timeout."""

    method: str = "exact"
    timeout_seconds: int = 3
    delay_seconds: float = 0.0

    def compute_batch(self, smiles_list: list[str]) -> list[dict]:
        if self.method != "exact":
            raise ValueError(f"Unsupported method '{self.method}'. Use 'exact'.")

        results = []
        for i, smiles in enumerate(smiles_list):
            if self.delay_seconds > 0:
                time.sleep(self.delay_seconds)
            result = compute_assembly_index(
                smiles,
                prefer="exact",
                timeout_seconds=self.timeout_seconds,
            )
            result["smiles"] = smiles
            result["index"] = i
            results.append(result)
        return results
