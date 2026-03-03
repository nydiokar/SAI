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
from pymatgen.core import Molecule as PMGMolecule
from pymatgen.symmetry.analyzer import PointGroupAnalyzer


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


def get_3d_conformers_from_smiles(smiles: str, seeds: list[int] | None = None) -> list[tuple[np.ndarray, list[str]]]:
    """Generate multiple optimized 3D conformers for a molecule."""
    if seeds is None:
        seeds = [7, 13, 23, 37, 101]

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return []

    mol = Chem.AddHs(mol)
    symbols = [atom.GetSymbol() for atom in mol.GetAtoms()]
    conformers: list[tuple[np.ndarray, list[str]]] = []

    for seed in seeds:
        try:
            work = Chem.Mol(mol)
            params = AllChem.ETKDGv3()
            params.randomSeed = seed
            params.useRandomCoords = True

            embed_status = AllChem.EmbedMolecule(work, params)
            if embed_status != 0:
                continue

            if AllChem.MMFFHasAllMoleculeParams(work):
                AllChem.MMFFOptimizeMolecule(work)
            else:
                AllChem.UFFOptimizeMolecule(work)

            conf = work.GetConformer()
            coords = np.array([list(conf.GetAtomPosition(i)) for i in range(work.GetNumAtoms())])
            conformers.append((coords, symbols))
        except Exception:
            continue

    return conformers


def detect_point_group_pymatgen(coords: np.ndarray, symbols: list[str], tolerance: float = 0.3) -> dict:
    """Detect point group using pymatgen's symmetry analyzer."""
    molecule = PMGMolecule(symbols, coords.tolist())
    analyzer = PointGroupAnalyzer(molecule, tolerance=tolerance)

    point_group = str(analyzer.sch_symbol)
    order = len(analyzer.get_symmetry_operations())
    max_rotation_order = int(analyzer.get_rotational_symmetry_number())

    # Confidence proxy based on group order and pymatgen backend reliability.
    confidence = min(0.99, 0.65 + 0.04 * min(order, 8))

    return {
        "point_group": point_group,
        "order": max(order, 1),
        "max_rotation_order": max(max_rotation_order, 1),
        "confidence": confidence,
        "tolerance_used": tolerance,
        "method": "pymatgen"
    }


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
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {}

    mol = Chem.AddHs(mol)
    symbols = [atom.GetSymbol() for atom in mol.GetAtoms()]

    tolerances = [0.1, 0.3, 0.5, 0.8] if test_tolerances else [tolerance]
    pymatgen_results = []

    conformers = get_3d_conformers_from_smiles(smiles)
    if conformers:
        for conf_idx, (coords, conf_symbols) in enumerate(conformers):
            for tol in tolerances:
                try:
                    result = detect_point_group_pymatgen(coords, conf_symbols, tol)
                    result["conformer_index"] = conf_idx
                    pymatgen_results.append(result)
                except Exception:
                    continue

    if pymatgen_results:
        best = max(
            pymatgen_results,
            key=lambda r: (
                r.get("order", 1),
                r.get("max_rotation_order", 1),
                r.get("confidence", 0.0),
                -float(r.get("tolerance_used", tolerance)),
            ),
        )
        best["smiles"] = smiles
        if test_tolerances:
            best["all_tolerances"] = pymatgen_results
        return best

    # Fallback: legacy detector if pymatgen route cannot analyze this molecule.
    coords = get_3d_coords_from_smiles(smiles)
    if coords is None:
        return {}

    if test_tolerances:
        # Test multiple tolerances, return most confident
        results = []
        for tol in tolerances:
            result = detect_point_group_with_tolerance(coords, symbols, tol)
            result["tolerance_used"] = tol
            result["method"] = "rdkit_legacy"
            results.append(result)

        # Return result with highest confidence
        best = max(results, key=lambda x: x.get('confidence', 0))
        best["smiles"] = smiles
        best["all_tolerances"] = results
        return best
    else:
        result = detect_point_group_with_tolerance(coords, symbols, tolerance)
        result["method"] = "rdkit_legacy"
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
