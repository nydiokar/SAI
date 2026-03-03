"""Merge symmetry, assembly index, and molecular property datasets."""

import pandas as pd
from pathlib import Path


def compute_molecular_properties(mol_obj) -> dict:
    """
    Compute additional molecular properties from RDKit molecule object.

    Args:
        mol_obj: RDKit Mol object

    Returns:
        dict with properties: num_atoms, num_bonds, num_rings, num_rotatable_bonds,
                              molecular_weight, polar_surface_area
    """
    from rdkit.Chem import Descriptors, Crippen

    try:
        num_atoms = mol_obj.GetNumAtoms()
        num_bonds = mol_obj.GetNumBonds()
        from rdkit.Chem import GetSSSR
        num_rings = len(GetSSSR(mol_obj))

        # Count rotatable bonds
        from rdkit.Chem import Descriptors
        num_rotatable = Descriptors.NumRotatableBonds(mol_obj)

        # Molecular weight
        mw = Descriptors.MolWt(mol_obj)

        # Polar surface area
        psa = Crippen.TPSA(mol_obj)

        return {
            "num_atoms": num_atoms,
            "num_bonds": num_bonds,
            "num_rings": num_rings,
            "num_rotatable_bonds": num_rotatable,
            "molecular_weight": mw,
            "polar_surface_area": psa
        }
    except Exception:
        return {}


def merge_datasets(
    symmetry_df: pd.DataFrame,
    assembly_df: pd.DataFrame,
    properties_df: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Merge symmetry, assembly index, and properties data.

    Args:
        symmetry_df: DataFrame with columns: smiles, point_group, order, max_rotation_order
        assembly_df: DataFrame with columns: smiles, assembly_index, source
        properties_df: (optional) DataFrame with columns: smiles, num_atoms, molecular_weight, etc.

    Returns:
        Merged DataFrame with all columns
    """
    symmetry = symmetry_df.copy().reset_index(drop=True)
    assembly = assembly_df.copy().reset_index(drop=True)

    # Preserve one-to-one row alignment when duplicate SMILES exist.
    if len(symmetry) == len(assembly):
        symmetry["_row_idx"] = symmetry.index
        assembly["_row_idx"] = assembly.index
        merged = symmetry.merge(
            assembly,
            on=["smiles", "_row_idx"],
            how="inner",
            validate="one_to_one",
        )
        merged = merged.drop(columns=["_row_idx"])
    else:
        symmetry["_smiles_occ"] = symmetry.groupby("smiles").cumcount()
        assembly["_smiles_occ"] = assembly.groupby("smiles").cumcount()
        merged = symmetry.merge(
            assembly,
            on=["smiles", "_smiles_occ"],
            how="inner",
            validate="one_to_one",
        )
        merged = merged.drop(columns=["_smiles_occ"])

    if properties_df is not None:
        merged = merged.merge(properties_df, on="smiles", how="left")

    return merged


def save_dataset(df: pd.DataFrame, output_path: str) -> None:
    """Save merged dataset to CSV."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved dataset to {output_path}")


def load_dataset(path: str) -> pd.DataFrame:
    """Load merged dataset from CSV."""
    return pd.read_csv(path)
