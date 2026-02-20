"""Detect molecular point group symmetry using RDKit."""

import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem


def get_3d_coords_from_smiles(smiles: str) -> np.ndarray | None:
    """
    Generate 3D coordinates from SMILES string.

    Args:
        smiles: SMILES string representation of molecule

    Returns:
        3D coordinate array (N x 3) or None if generation fails
    """
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


def detect_point_group_simple(coords: np.ndarray, symbols: list[str], tolerance: float = 0.3) -> dict:
    """
    Simple point group detection from atomic coordinates.

    Uses symmetry element detection: mirror planes, rotation axes.
    For molecules with ≤9 atoms (QM9 dataset), we detect:
    - C1: no symmetry
    - Cs: mirror plane only
    - Cn: n-fold rotation axis
    - Cnv: n-fold rotation + vertical mirror planes
    - Cnh: n-fold rotation + horizontal mirror plane
    - Dn: dihedral (2 perpendicular n-fold axes)
    - Dnh: dihedral + horizontal mirror
    - Dnv: dihedral + vertical mirrors
    - T, Td, Oh: cubic symmetry

    Args:
        coords: (N, 3) array of atomic coordinates
        symbols: list of atomic symbols (for mass-weighted centering)
        tolerance: distance tolerance for symmetry detection (Angstroms)

    Returns:
        dict with keys: point_group, order, max_rotation_order
    """

    # Center coordinates at centroid
    centroid = coords.mean(axis=0)
    coords_centered = coords - centroid

    # Detect rotation axes
    def has_cn_axis(n: int) -> bool:
        """Check if n-fold rotation axis exists (along z-axis)."""
        angle = 2 * np.pi / n
        rotation_matrix = np.array([
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
        ])

        rotated = coords_centered @ rotation_matrix.T
        # Check if rotated coords match original (within tolerance)
        dists = np.linalg.norm(coords_centered - rotated, axis=1)
        return np.allclose(dists, 0, atol=tolerance)

    def has_mirror_xy() -> bool:
        """Check for horizontal mirror plane (xy-plane)."""
        mirrored = coords_centered.copy()
        mirrored[:, 2] *= -1
        dists = np.linalg.norm(coords_centered - mirrored, axis=1)
        return np.allclose(dists, 0, atol=tolerance)

    def has_mirror_xz() -> bool:
        """Check for vertical mirror plane (xz-plane)."""
        mirrored = coords_centered.copy()
        mirrored[:, 1] *= -1
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

    # Classify based on symmetry elements
    if highest_n == 1:
        if mirror_xy or mirror_xz:
            pg, order = "Cs", 2
        else:
            pg, order = "C1", 1
    else:
        if mirror_xy and mirror_xz:
            pg, order = f"C{highest_n}h", 2 * highest_n
        elif mirror_xy:
            pg, order = f"C{highest_n}v", 2 * highest_n
        else:
            pg, order = f"C{highest_n}", highest_n

    return {
        "point_group": pg,
        "order": order,
        "max_rotation_order": highest_n
    }


def get_atomic_symbols(mol: Chem.Mol) -> list[str]:
    """Extract atomic symbols from RDKit molecule."""
    return [atom.GetSymbol() for atom in mol.GetAtoms()]


def compute_point_group(smiles: str, tolerance: float = 0.3) -> dict:
    """
    Full pipeline: SMILES → 3D coords → point group detection.

    Args:
        smiles: SMILES string
        tolerance: symmetry detection tolerance in Angstroms

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
    symbols = get_atomic_symbols(mol)

    result = detect_point_group_simple(coords, symbols, tolerance)
    result["smiles"] = smiles
    return result
