"""Load reference ranges from data/reference/."""
from pathlib import Path

import pandas as pd

REFERENCE_DIR = Path(__file__).resolve().parent.parent / "data" / "reference"


def pstar_ranges() -> pd.DataFrame:
    """Proton range in liquid water vs energy (columns energy_MeV, range_mm). See data/reference/SOURCE.md."""
    return pd.read_csv(REFERENCE_DIR / "pstar_range_water_ucl.csv", comment="#")
