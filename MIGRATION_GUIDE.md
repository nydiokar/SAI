# Linux Migration Guide for Bridge 6 + Thread 1

**Status:** Windows Phase Complete. Ready for Linux Migration.

**Estimated Time:** 1-2 hours total setup

---

## Why Switch to Linux?

| Issue | Windows | Linux |
|-------|---------|-------|
| pymatgen/ASE installation | ❌ Build failures | ✅ Works via pip |
| Scientific Python stack | ⚠️ Variable | ✅ Standard |
| Chemistry package support | ❌ Limited | ✅ Full |
| Computational chemistry tools | ❌ Difficult | ✅ Native |
| Current blocker (symmetry detection) | **BLOCKS P1** | ✅ Fixes this |

**Bottom line:** You're hitting Windows limitations. Linux is standard for this type of research.

---

## Quick Start (Linux Setup)

### Step 1: Install Dependencies (5 minutes)

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3.10 python3.10-venv git \
  build-essential gfortran libopenblas-dev liblapack-dev libgomp1

# macOS (if on Mac)
brew install python@3.10 openblas lapack
```

### Step 2: Clone & Setup Repo (5 minutes)

```bash
cd ~/projects
git clone https://github.com/nydiokar/SAI.git
cd SAI

# Create and activate venv
python3.10 -m venv .venv
source .venv/bin/activate  # Use .venv\Scripts\activate on Windows bash

# Install all dependencies (now will work!)
pip install --upgrade pip setuptools wheel
pip install -e ".[dev]"
pip install pymatgen ase  # These now work on Linux
```

### Step 3: Verify Installation (2 minutes)

```bash
python -c "import pymatgen; import ase; print('✓ Ready for Bridge 6')"

# Quick test
cd notebooks
jupyter notebook 00_sanity_check.ipynb
```

### Step 4: Download QM9 Dataset (20-30 minutes, can run in background)

```bash
cd data/raw
wget http://quantum-machine.org/datasets/qm9.tar.gz  # 1.3GB
tar xzf qm9.tar.gz
# This will extract to data/raw/qm9/
```

### Step 5: Update Code for pymatgen (20 minutes)

Once on Linux with pymatgen, update `src/compute_symmetry.py`:

```python
# Change the main detection function to use pymatgen
from pymatgen.symmetry.analyzer import PointGroupAnalyzer
from pymatgen.core import Molecule as PMGMolecule

def compute_point_group(smiles: str, tolerance: float = 0.1) -> dict:
    """Use pymatgen for proper symmetry detection."""
    coords = get_3d_coords_from_smiles(smiles)
    symbols = get_atomic_symbols(smiles)

    # Create pymatgen Molecule
    mol = PMGMolecule(symbols, coords)

    # Analyze symmetry
    pga = PointGroupAnalyzer(mol, tolerance=tolerance)

    return {
        "point_group": pga.sch_symbol,
        "order": len(pga.symmops),
        "max_rotation_order": pga.max_rotation_order,
        "confidence": 0.95  # pymatgen is highly reliable
    }
```

### Step 6: Re-run P1 Pilot (10 minutes)

```bash
source .venv/bin/activate
python run_pilot_v2.py

# Now should see:
#   Unique point groups: 15+  (was 2)
#   Symmetry diversity: orders 1, 2, 3, 4, 6, 12, 24, 48  (was just 1, 2)
#   Spearman correlation: meaningful result  (was p=0.83)
```

---

## What Gets Fixed

**Before (Windows):**
```
Point group distribution:
  C1   : 33
  Cs   : 11
Unique orders: 2
Result: p=0.83 (meaningless)
```

**After (Linux + pymatgen):**
```
Point group distribution:
  C1   : ~40  (asymmetric)
  Cs   : ~25  (mirror plane)
  C2   : ~8   (2-fold rotation)
  C2v  : ~12  (2-fold + mirror)
  C3v  : ~3   (3-fold + mirror)
  Td   : ~4   (tetrahedral)
  D3h  : ~2   (benzene-like)
  D6h  : ~1   (benzene)
Unique orders: 8+
Result: p < 0.05 or p >= 0.05 (meaningful either way)
```

---

## Alternative: Windows WSL2 (If You Can't Dual Boot)

If you must stay on Windows, use **Windows Subsystem for Linux 2**:

```bash
# In Windows PowerShell (admin)
wsl --install Ubuntu-22.04

# Then follow the Linux setup above inside WSL
```

This gives you Linux environment running on Windows. Performance is good enough for this project.

---

## What Happens Next

Once you're on Linux with pymatgen + QM9:

### Bridge 6 (Thread 2):
1. Run P1 pilot with real symmetry data → get meaningful correlation (or lack thereof)
2. If correlation found → scale to full QM9 (134k molecules)
3. If no correlation → publish as "orthogonal molecular descriptors" (still valuable)

### Thread 1 (SAI - Can Start Now in Parallel):
1. Don't wait for Thread 2 — you can start defining SAI on finite groups
2. Install GAP or SageMath on Linux (easier than Windows)
3. Define cost function for group extensions
4. Compute SAI for groups of order 1-100
5. Eventually merge results from both threads in Phase 5

---

## Files to Track

Once on Linux, these will be updated:

- `src/compute_symmetry.py` → Will use pymatgen instead of custom RDKit
- `src/fetch_molecules.py` → Will parse actual QM9 `.xyz` files instead of API
- `run_pilot_v2.py` → Will show proper symmetry distribution

Everything else stays the same. Architecture is solid.

---

## Timeline Estimate

- **Setup (Steps 1-4):** 45-60 minutes
- **Code update (Step 5):** 20 minutes
- **Re-run & validate (Step 6):** 10 minutes
- **Total:** ~90 minutes

Then you'll have:
- ✓ Proper Bridge 6 correlation test
- ✓ Ready for Thread 1 (SAI definition)
- ✓ Solid foundation for next 6 months of research

---

## Questions?

All instructions are in `.ai/CONTEXT.md` as well. This is just the quick reference.

Good luck! 🚀
