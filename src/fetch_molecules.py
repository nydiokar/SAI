"""Fetch molecules from QM9 dataset for Bridge 6 analysis."""

import os
import gzip
import pandas as pd
import numpy as np
from pathlib import Path
import zipfile


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

    # Current public mirrors used by ML tooling for QM9.
    qm9_zip_url = "https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/molnet_publish/qm9.zip"
    qm9_tar_url = "https://springernature.figshare.com/ndownloader/files/3195389"
    zip_path = data_path / "qm9.zip"
    tar_path = data_path / "qm9.tar.bz2"
    extract_path = data_path / "qm9"

    if extract_path.exists() and not force:
        print(f"QM9 dataset already exists at {extract_path}")
        return str(extract_path)

    if force and extract_path.exists():
        for p in extract_path.iterdir():
            if p.is_file():
                p.unlink()

    if zip_path.exists() and not force:
        try:
            print(f"Found local archive at {zip_path}, extracting...")
            extract_path.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(path=extract_path)
            print("Done!")
            return str(extract_path)
        except Exception as e:
            print(f"Local archive extraction failed: {e}")

    print(f"Downloading QM9 dataset from {qm9_zip_url}...")
    try:
        urllib.request.urlretrieve(qm9_zip_url, zip_path)
        print(f"Extracting to {extract_path}...")
        extract_path.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(path=extract_path)
        print("Done!")
        return str(extract_path)
    except Exception as e:
        print(f"Primary QM9 download failed: {e}")

    print(f"Trying fallback QM9 mirror from {qm9_tar_url}...")
    try:
        urllib.request.urlretrieve(qm9_tar_url, tar_path)
        print(f"Extracting to {extract_path}...")
        extract_path.mkdir(parents=True, exist_ok=True)
        with tarfile.open(tar_path, "r:bz2") as tar:
            tar.extractall(path=extract_path)
        print("Done!")
        return str(extract_path)
    except Exception as e:
        print(f"Fallback download failed: {e}")
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

    # Preferred: parse CSV shipped by common QM9 mirrors.
    csv_candidates = list(qm9_path.glob("**/*.csv"))
    for csv_file in csv_candidates:
        try:
            df = pd.read_csv(csv_file)
            lower_cols = {c.lower(): c for c in df.columns}
            smiles_col = None
            for candidate in ["smiles", "smiles1", "smiles_relaxed"]:
                if candidate in lower_cols:
                    smiles_col = lower_cols[candidate]
                    break
            if smiles_col is None:
                continue

            out = pd.DataFrame({
                "id": df.index.astype(str),
                "smiles": df[smiles_col].astype(str)
            })
            out = out[out["smiles"].notna() & (out["smiles"].str.len() > 0)]
            if len(out) > 0:
                print(f"Loaded {len(out)} molecules from {csv_file.name}")
                return out.reset_index(drop=True)
        except Exception:
            continue

    # Fallback: parse XYZ metadata if available.
    smiles_list = []
    ids = []
    xyz_files = sorted(qm9_path.glob("**/*.xyz"))
    print(f"Found {len(xyz_files)} XYZ files in QM9")

    for xyz_file in xyz_files[:10000]:
        try:
            with open(xyz_file, "r") as f:
                lines = f.readlines()
                if len(lines) > 1:
                    metadata = lines[1].strip()
                    smiles_list.append(metadata)
                    ids.append(xyz_file.stem)
        except Exception:
            continue

    df = pd.DataFrame({"id": ids, "smiles": smiles_list})
    df = df[df["smiles"].notna()].reset_index(drop=True)
    if len(df) > 0:
        return df

    # Fallback: parse SDF and generate canonical SMILES.
    sdf_candidates = list(qm9_path.glob("**/*.sdf"))
    for sdf_file in sdf_candidates:
        try:
            from rdkit import Chem
            from rdkit import RDLogger
            RDLogger.DisableLog("rdApp.error")

            out_ids = []
            out_smiles = []
            supplier = Chem.SDMolSupplier(str(sdf_file), removeHs=False, sanitize=False)
            for idx, mol in enumerate(supplier):
                if mol is None:
                    continue
                try:
                    Chem.SanitizeMol(mol)
                except Exception:
                    continue
                smiles = Chem.MolToSmiles(mol, canonical=True)
                if not smiles:
                    continue
                name = mol.GetProp("_Name") if mol.HasProp("_Name") else f"mol_{idx}"
                out_ids.append(name)
                out_smiles.append(smiles)

            out = pd.DataFrame({"id": out_ids, "smiles": out_smiles})
            out = out[out["smiles"].notna() & (out["smiles"].str.len() > 0)]
            if len(out) > 0:
                print(f"Loaded {len(out)} molecules from {sdf_file.name}")
                return out.reset_index(drop=True)
        except Exception:
            continue

    return pd.DataFrame(columns=["id", "smiles"])


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


def fetch_pubchem_molecules(
    n: int = 100,
    max_heavy_atoms: int = 20,
    max_seconds: int = 90,
    max_consecutive_errors: int = 80,
) -> pd.DataFrame:
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
    start_time = time.time()
    consecutive_errors = 0

    while len(molecules) < n and cid < 10000000:
        if (time.time() - start_time) > max_seconds:
            print(f"PubChem fetch timed out after {max_seconds}s; falling back.")
            break
        if consecutive_errors >= max_consecutive_errors:
            print(f"PubChem fetch hit {max_consecutive_errors} consecutive failures; falling back.")
            break

        try:
            # Fetch compound info from PubChem
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/JSON"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                props = data['PC_Compounds'][0]
                consecutive_errors = 0

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
                    consecutive_errors += 1
            else:
                consecutive_errors += 1

            cid += 1
            time.sleep(0.01)  # Rate limiting

        except Exception:
            consecutive_errors += 1
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
        # 1) Prefer local/extracted QM9 if present.
        try:
            local_qm9_dir = Path(data_dir) / "qm9"
            if local_qm9_dir.exists():
                df = load_qm9_smiles(str(local_qm9_dir))
                if len(df) > 0:
                    print(f"Using {len(df)} molecules from local QM9 dataset")
                    return df.head(n)
        except Exception as e:
            print(f"Local QM9 read failed: {e}")

        # 2) Try to download/extract QM9 mirrors.
        try:
            qm9_dir = download_qm9_dataset(data_dir)
            if qm9_dir:
                df = load_qm9_smiles(qm9_dir)
                if len(df) > 0:
                    print(f"Using {len(df)} molecules from real QM9 dataset")
                    return df.head(n)
        except Exception as e:
            print(f"QM9 download failed: {e}")

        # 3) Last resort: PubChem.
        try:
            df = fetch_pubchem_molecules(n=n)
            if len(df) > 0:
                print(f"Using {len(df)} real molecules from PubChem")
                return df
        except Exception as e:
            print(f"PubChem fetch failed: {e}")

    # Fallback to synthetic
    print(f"Falling back to synthetic sample with {n} molecules")
    return generate_synthetic_qm9_sample(n)
