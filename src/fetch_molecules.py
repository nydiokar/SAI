"""Fetch molecules from QM9 dataset for Bridge 6 analysis."""

import os
import gzip
import pandas as pd
import numpy as np
from pathlib import Path


def download_qm9_dataset(data_dir: str = "data/raw", force: bool = False) -> str:
    """
    Download QM9 dataset from quantum-machine.org.

    Args:
        data_dir: directory to store downloaded files
        force: re-download even if files exist

    Returns:
        path to downloaded QM9 data directory
    """
    import urllib.request
    import tarfile

    data_path = Path(data_dir)
    data_path.mkdir(parents=True, exist_ok=True)

    qm9_url = "http://quantum-machine.org/datasets/qm9.tar.gz"
    tar_path = data_path / "qm9.tar.gz"
    extract_path = data_path / "qm9"

    if extract_path.exists() and not force:
        print(f"QM9 dataset already exists at {extract_path}")
        return str(extract_path)

    print(f"Downloading QM9 dataset from {qm9_url}...")
    try:
        urllib.request.urlretrieve(qm9_url, tar_path)
        print(f"Extracting to {extract_path}...")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=data_path)
        print("Done!")
        return str(extract_path)
    except Exception as e:
        print(f"Download failed: {e}")
        print("Falling back to synthetic dataset generation.")
        return None


def load_qm9_smiles(qm9_dir: str) -> pd.DataFrame:
    """
    Load QM9 dataset and extract SMILES strings.

    Args:
        qm9_dir: path to QM9 dataset directory

    Returns:
        DataFrame with columns: smiles, id, and other properties
    """
    qm9_path = Path(qm9_dir)

    # QM9 stores data as individual .xyz files
    # This is a parser for the standard format
    smiles_list = []
    ids = []

    xyz_files = sorted(qm9_path.glob("**/*.xyz"))
    print(f"Found {len(xyz_files)} molecules in QM9")

    for xyz_file in xyz_files[:10000]:  # Limit to first 10k for testing
        try:
            # Read first line of .xyz file (contains SMILES in some versions)
            with open(xyz_file, 'r') as f:
                lines = f.readlines()
                # QM9 format: first line is atom count, second line often has metadata
                if len(lines) > 1:
                    # Try to extract SMILES from metadata line
                    metadata = lines[1].strip()
                    # This is dataset-specific—adjust parsing as needed
                    smiles_list.append(metadata)
                    ids.append(xyz_file.stem)
        except Exception:
            continue

    df = pd.DataFrame({
        'id': ids,
        'smiles': smiles_list
    })

    return df[df['smiles'].notna()].reset_index(drop=True)


def generate_synthetic_qm9_sample(n_molecules: int = 100, seed: int = 42) -> pd.DataFrame:
    """
    Generate a synthetic QM9-like dataset for testing.

    Uses common SMILES strings for small organic molecules.

    Args:
        n_molecules: how many molecules to generate
        seed: random seed

    Returns:
        DataFrame with columns: smiles, id
    """
    np.random.seed(seed)

    # Curated list of chemically valid SMILES for small molecules
    common_smiles = [
        # Alkanes
        "C", "CC", "CCC", "CCCC", "C(C)C", "CC(C)C",
        # Alcohols
        "CO", "CCO", "CCCO", "CC(C)O", "CCCO",
        # Aldehydes/Ketones
        "C=O", "CC=O", "CCC=O", "CC(=O)C",
        # Amines
        "CN", "CCN", "CC(C)N",
        # Alkenes
        "C=C", "C=CC", "CC=C", "C=C(C)C",
        # Alkynes
        "C#C", "CC#C",
        # Aromatics
        "c1ccccc1", "c1ccccc1C", "c1ccccc1O", "c1ccccc1N",
        # Cycloalkanes
        "C1CC1", "C1CCC1", "C1CCCC1", "C1CCCCC1",
        # Ethers
        "COC", "CCOC", "CCO CC",
        # Esters
        "CC(=O)O", "CC(=O)OC",
        # Carboxylic acids
        "C(=O)O", "CC(=O)O",
        # Thiols
        "CS", "CCS",
        # Sulfides
        "CSC", "CCSC",
        # Common drugs / natural products (small molecules)
        "O=C(O)c1ccccc1", "CC(=O)Oc1ccccc1C(=O)O",
    ]

    # Sample with replacement to reach n_molecules
    sampled = np.random.choice(common_smiles, size=n_molecules, replace=True)

    df = pd.DataFrame({
        'id': [f'mol_{i:06d}' for i in range(n_molecules)],
        'smiles': sampled
    })

    return df


def fetch_pubchem_molecules(n: int = 100, max_heavy_atoms: int = 20) -> pd.DataFrame:
    """
    Fetch molecules from PubChem with specified constraints.

    Uses PubChem's REST API to get real, diverse organic molecules.

    Args:
        n: approximate number of molecules to fetch
        max_heavy_atoms: max number of heavy atoms per molecule

    Returns:
        DataFrame with columns: smiles, id, molecular_weight, num_atoms
    """
    import requests
    import time

    print(f"Fetching {n} molecules from PubChem...")

    molecules = []
    cid = 1  # Start from compound ID 1

    while len(molecules) < n and cid < 10000000:
        try:
            # Fetch compound info from PubChem
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/JSON"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                props = data['PC_Compounds'][0]

                # Extract SMILES if available
                try:
                    atoms = props['atoms']
                    n_atoms = len(atoms)

                    if n_atoms <= max_heavy_atoms:
                        # Try to get isomeric SMILES
                        smiles = None
                        for prop in props.get('props', []):
                            if prop['urn']['label'] == 'SMILES' and prop['urn'].get('name') == 'Isomeric':
                                smiles = prop['value']['sval']
                                break

                        if smiles:
                            molecules.append({
                                'id': f'PubChem_{cid}',
                                'smiles': smiles,
                                'num_atoms': n_atoms
                            })

                            if len(molecules) % 50 == 0:
                                print(f"  {len(molecules)}/{n} molecules fetched...")

                except Exception:
                    pass

            cid += 1
            time.sleep(0.01)  # Rate limiting

        except Exception as e:
            cid += 1
            continue

    df = pd.DataFrame(molecules)
    print(f"Successfully fetched {len(df)} molecules")
    return df.head(n)


def get_qm9_sample(n: int = 500, use_real_data: bool = True, data_dir: str = "data/raw") -> pd.DataFrame:
    """
    Get a sample of molecules for testing.

    Args:
        n: number of molecules
        use_real_data: if True, fetch from PubChem; if False, use synthetic
        data_dir: directory for downloaded data

    Returns:
        DataFrame with SMILES
    """
    if use_real_data:
        try:
            # Try PubChem first (faster, more reliable)
            df = fetch_pubchem_molecules(n=n)
            if len(df) > 0:
                print(f"Using {len(df)} real molecules from PubChem")
                return df
        except Exception as e:
            print(f"PubChem fetch failed: {e}")

        # Fallback to QM9 download
        try:
            qm9_dir = download_qm9_dataset(data_dir)
            if qm9_dir:
                df = load_qm9_smiles(qm9_dir)
                if len(df) > 0:
                    print(f"Using {len(df)} molecules from real QM9 dataset")
                    return df.head(n)
        except Exception as e:
            print(f"QM9 download failed: {e}")

    # Fallback to synthetic
    print(f"Falling back to synthetic sample with {n} molecules")
    return generate_synthetic_qm9_sample(n)
