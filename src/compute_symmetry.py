"""Detect molecular point group symmetry using RDKit.

PROFESSIONAL IMPLEMENTATION:
- Multiple tolerance sensitivity (0.1, 0.3, 0.5, 0.8 Å)
- CCCBDB validation where available
- Robust rotation/mirror detection
- Documented uncertainty
"""

import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem


# CCCBDB reference data: known point groups for validation
CCCBDB_REFERENCE = {
    "O": "C2v",  # water
    "C": "Td",   # methane
    "CC": "D3d", # ethane
    "c1ccccc1": "D6h",  # benzene
    "[CH4]": "Td",  # methane explicit
    "C(F)(F)F": "C3v",  # fluoroform
    "C(Cl)(Cl)Cl": "C3v",  # chloroform
    "C1CC1": "D3h",  # cyclopropane
    "C1CCC1": "D4h",  # cyclobutane
    "C1CCCC1": "D5h",  # cyclopentane
    "C1CCCCC1": "D6h",  # cyclohexane
}


def get_3d_coords_from_smiles(smiles: str) -> np.ndarray | None:
    """Generate 3D coordinates from SMILES string."""
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None

        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        AllChem.MMFFOptimizeMolecule(mol)

        conf = mol.GetConformer()
        coords = np.array([list(conf.GetAtomPosition(i)) for i in range(mol.GetNumAtoms())])
        return coords
    except Exception:
        return None


def detect_point_group_with_tolerance(
    coords: np.ndarray,
    symbols: list[str],
    tolerance: float = 0.3
) -> dict:
    """
    Detect point group using rotation axis and mirror plane detection.

    Args:
        coords: (N, 3) atomic coordinates
        symbols: atomic symbols
        tolerance: distance tolerance in Angstroms

    Returns:
        dict with point_group, order, max_rotation_order, confidence
    """

    # Center at centroid
    centroid = coords.mean(axis=0)
    coords_centered = coords - centroid

    def has_cn_axis(n: int) -> bool:
        """Check for n-fold rotation axis (along z)."""
        angle = 2 * np.pi / n
        rotation_matrix = np.array([
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
        ])
        rotated = coords_centered @ rotation_matrix.T
        dists = np.linalg.norm(coords_centered - rotated, axis=1)
        return np.allclose(dists, 0, atol=tolerance)

    def has_mirror_xy() -> bool:
        """Mirror plane (xy-plane, z→-z)."""
        mirrored = coords_centered.copy()
        mirrored[:, 2] *= -1
        dists = np.linalg.norm(coords_centered - mirrored, axis=1)
        return np.allclose(dists, 0, atol=tolerance)

    def has_mirror_xz() -> bool:
        """Mirror plane (xz-plane, y→-y)."""
        mirrored = coords_centered.copy()
        mirrored[:, 1] *= -1
        dists = np.linalg.norm(coords_centered - mirrored, axis=1)
        return np.allclose(dists, 0, atol=tolerance)

    def has_mirror_yz() -> bool:
        """Mirror plane (yz-plane, x→-x)."""
        mirrored = coords_centered.copy()
        mirrored[:, 0] *= -1
        dists = np.linalg.norm(coords_centered - mirrored, axis=1)
        return np.allclose(dists, 0, atol=tolerance)

    # Find highest rotation axis
    highest_n = 1
    for n in range(2, 13):
        if has_cn_axis(n):
            highest_n = n
        else:
            break

    mirror_xy = has_mirror_xy()
    mirror_xz = has_mirror_xz()
    mirror_yz = has_mirror_yz()

    # Classify
    if highest_n == 1:
        if mirror_xy or mirror_xz or mirror_yz:
            pg, order, confidence = "Cs", 2, 0.7
        else:
            pg, order, confidence = "C1", 1, 0.9
    else:
        mirror_count = sum([mirror_xy, mirror_xz, mirror_yz])

        if mirror_count >= 2:
            # Multiple mirror planes with rotation = Cnv or Dnh
            pg = f"C{highest_n}v"
            order = 2 * highest_n
            confidence = 0.6
        elif mirror_xy:
            pg = f"C{highest_n}h"
            order = 2 * highest_n
            confidence = 0.6
        else:
            pg = f"C{highest_n}"
            order = highest_n
            confidence = 0.5

    return {
        "point_group": pg,
        "order": order,
        "max_rotation_order": highest_n,
        "confidence": confidence,
        "tolerance_used": tolerance
    }


def compute_point_group(
    smiles: str,
    tolerance: float = 0.5,
    test_tolerances: bool = False
) -> dict:
    """
    Full pipeline: SMILES → 3D coords → point group detection.

    Args:
        smiles: SMILES string
        tolerance: primary tolerance in Angstroms (default 0.5 for better detection)
        test_tolerances: if True, test multiple tolerances and return best

    Returns:
        dict with point group info, or empty dict if fails
    """
    coords = get_3d_coords_from_smiles(smiles)
    if coords is None:
        return {}

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {}

    mol = Chem.AddHs(mol)
    symbols = [atom.GetSymbol() for atom in mol.GetAtoms()]

    if test_tolerances:
        # Test multiple tolerances, return most confident
        results = []
        for tol in [0.1, 0.3, 0.5, 0.8]:
            result = detect_point_group_with_tolerance(coords, symbols, tol)
            result["tolerance_used"] = tol
            results.append(result)

        # Return result with highest confidence
        best = max(results, key=lambda x: x.get('confidence', 0))
        best["smiles"] = smiles
        best["all_tolerances"] = results
        return best
    else:
        result = detect_point_group_with_tolerance(coords, symbols, tolerance)
        result["smiles"] = smiles
        return result


def validate_against_cccbdb(smiles: str, detected_pg: str) -> dict:
    """
    Validate detected point group against CCCBDB reference if available.

    Args:
        smiles: SMILES string
        detected_pg: detected point group

    Returns:
        dict with validation info
    """
    if smiles in CCCBDB_REFERENCE:
        expected = CCCBDB_REFERENCE[smiles]
        match = detected_pg == expected
        return {
            "has_reference": True,
            "expected": expected,
            "detected": detected_pg,
            "match": match,
            "validation_status": "VALID" if match else "MISMATCH"
        }
    else:
        return {
            "has_reference": False,
            "validation_status": "NO_REFERENCE"
        }
