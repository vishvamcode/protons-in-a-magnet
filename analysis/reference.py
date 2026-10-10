"""Reference data from data/reference/: the NIST PSTAR table for liquid water. See data/reference/SOURCE.md."""
from pathlib import Path

import numpy as np
import pandas as pd

REFERENCE_DIR = Path(__file__).resolve().parent.parent / "data" / "reference"
WATER_DENSITY_g_per_cm3 = 1.0
VALIDATION_ENERGIES_MeV = [70, 100, 150, 200, 230]


def pstar_table() -> pd.DataFrame:
    """PSTAR liquid water: energy (MeV), stopping powers (MeV cm2/g), CSDA and projected range (g/cm2)."""
    cols = ["energy_MeV", "S_electronic", "S_nuclear", "S_total", "csda_g_cm2", "projected_g_cm2", "detour"]
    return pd.read_csv(REFERENCE_DIR / "pstar_water_liquid.txt", sep="\t", comment="#", names=cols)


_T = pstar_table()


def pstar_stopping_power_MeV_per_mm(energy_MeV):
    """Total stopping power of liquid water (MeV/mm), log-log interpolation in the PSTAR table."""
    s = np.exp(np.interp(np.log(energy_MeV), np.log(_T.energy_MeV), np.log(_T.S_total)))
    return s * WATER_DENSITY_g_per_cm3 / 10.0


def pstar_csda_range_mm(energy_MeV: float) -> float:
    """CSDA range (mm) at any energy: the tabulated range at the grid point just below, plus the integral of
    1/S from there up to the requested energy (avoids interpolating the range itself between coarse grid points)."""
    i = int(np.searchsorted(_T.energy_MeV, energy_MeV, side="right")) - 1
    e0 = float(_T.energy_MeV[i])
    energies = np.linspace(e0, energy_MeV, 2001)
    extra_mm = np.trapezoid(1.0 / pstar_stopping_power_MeV_per_mm(energies), energies)
    return float(_T.csda_g_cm2[i]) / WATER_DENSITY_g_per_cm3 * 10.0 + extra_mm


def pstar_ranges() -> pd.DataFrame:
    """CSDA range in liquid water at the validation energies (columns energy_MeV, range_mm)."""
    return pd.DataFrame({"energy_MeV": VALIDATION_ENERGIES_MeV,
                         "range_mm": [round(pstar_csda_range_mm(e), 2) for e in VALIDATION_ENERGIES_MeV]})
