"""Compute molecular assembly index.

Strategy:
1. Try to use DaymudeLab/assembly-theory if installed
2. Fallback to molecular-assembly.com API
3. Fallback to simple placeholder based on molecular complexity
"""

import requests
import time
from rdkit import Chem


def compute_ma_via_assembly_theory(smiles: str) -> dict:
    """Compute MA using local assembly-theory package (if installed)."""
    try:
        import assembly_theory
        # This is a placeholder—actual implementation depends on API
        ma = assembly_theory.compute_assembly_index(smiles)
        return {"assembly_index": ma, "source": "assembly_theory_local", "success": True}
    except ImportError:
        return {"success": False, "source": "assembly_theory_local", "error": "not installed"}
    except Exception as e:
        return {"success": False, "source": "assembly_theory_local", "error": str(e)}


def compute_ma_via_api(smiles: str, timeout: int = 10) -> dict:
    """
    Query molecular-assembly.com API for precomputed MA values.

    Note: This requires internet and respects rate limits.
    """
    try:
        url = "https://molecular-assembly.com/api/ma"
        params = {"smiles": smiles}
        response = requests.get(url, params=params, timeout=timeout)

        if response.status_code == 200:
            data = response.json()
            return {
                "assembly_index": data.get("assembly_index"),
                "source": "molecular_assembly_api",
                "success": True
            }
        else:
            return {
                "success": False,
                "source": "molecular_assembly_api",
                "error": f"HTTP {response.status_code}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "source": "molecular_assembly_api",
            "error": str(e)
        }


def compute_ma_simple_heuristic(smiles: str) -> dict:
    """
    Simple heuristic assembly index based on molecular complexity.

    For testing only. Real MA computation requires proper algorithm.

    Formula: MA ≈ log2(num_atoms) + num_rings + num_bonds_complexity
    This is NOT a real assembly index, just a complexity proxy.
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return {"success": False, "source": "heuristic", "error": "invalid SMILES"}

        mol = Chem.AddHs(mol)
        num_atoms = mol.GetNumAtoms()
        num_bonds = mol.GetNumBonds()
        num_rings = Chem.GetSSSR(mol).__len__()

        # Simple heuristic (not real MA)
        complexity = (
            1 + np.log2(max(num_atoms, 2)) +
            num_rings +
            (num_bonds - num_atoms + 1) * 0.5
        )

        return {
            "assembly_index": round(complexity, 2),
            "source": "heuristic_simple",
            "success": True,
            "num_atoms": num_atoms,
            "num_bonds": num_bonds,
            "num_rings": num_rings,
            "note": "Heuristic only—not real assembly index"
        }
    except Exception as e:
        return {
            "success": False,
            "source": "heuristic_simple",
            "error": str(e)
        }


def compute_assembly_index(smiles: str, prefer: str = "api") -> dict:
    """
    Compute molecular assembly index with fallback strategy.

    Args:
        smiles: SMILES string
        prefer: "api" (try API first), "local" (try local first), or "heuristic" (use only heuristic)

    Returns:
        dict with assembly_index, source, and success flag
    """
    if prefer == "local":
        result = compute_ma_via_assembly_theory(smiles)
        if result["success"]:
            return result
        result = compute_ma_via_api(smiles)
        if result["success"]:
            return result
    elif prefer == "api":
        result = compute_ma_via_api(smiles)
        if result["success"]:
            return result
        result = compute_ma_via_assembly_theory(smiles)
        if result["success"]:
            return result
    elif prefer == "heuristic":
        return compute_ma_simple_heuristic(smiles)

    # Final fallback
    return compute_ma_simple_heuristic(smiles)


# For batch operations with rate limiting
class AssemblyIndexBatcher:
    """Batch compute MA with rate limiting for API calls."""

    def __init__(self, method: str = "heuristic", delay_seconds: float = 0.1):
        """
        Args:
            method: "api", "local", or "heuristic"
            delay_seconds: delay between API calls
        """
        self.method = method
        self.delay = delay_seconds
        self.last_call_time = 0

    def compute_batch(self, smiles_list: list[str]) -> list[dict]:
        """Compute MA for multiple SMILES with rate limiting."""
        results = []
        for i, smiles in enumerate(smiles_list):
            if self.method == "api":
                # Rate limiting for API
                elapsed = time.time() - self.last_call_time
                if elapsed < self.delay:
                    time.sleep(self.delay - elapsed)
                self.last_call_time = time.time()

            result = compute_assembly_index(smiles, prefer=self.method)
            result["smiles"] = smiles  # Add SMILES for merging
            result["index"] = i
            results.append(result)

        return results


import numpy as np
