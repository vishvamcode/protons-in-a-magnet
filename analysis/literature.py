"""Literature checks of the Lorentz-force model (data and sources in data/reference/SOURCE.md)."""
import numpy as np
import pandas as pd

from analysis.lorentz_ode import track
from analysis.reference import REFERENCE_DIR, pstar_stopping_power_MeV_per_mm

PMMA_RELATIVE_STOPPING_POWER = 1.165  # typical literature value, UNVERIFIED (see SOURCE.md)
SCHELLHAMMER_FIELD_T = 0.95  # their permanent magnet, treated here as uniform inside the phantom only


def schellhammer_table() -> pd.DataFrame:
    """Schellhammer et al. 2018, Table D.5: lateral deflection and R80 retraction in PMMA at 0.95 T (mm)."""
    return pd.read_csv(REFERENCE_DIR / "schellhammer2018_table_d5.csv")


def wang_table() -> pd.DataFrame:
    """Wang et al. 2021, Table 2: Bragg-peak depth shortening in water at 1.5 T (mm, given to 0.2 mm)."""
    return pd.read_csv(REFERENCE_DIR / "wang2021_table2_depth_shortening_1p5T.csv")


def ode_lateral_in_pmma_mm(energy_MeV: float) -> float:
    """End-of-range sideways shift (mm) in PMMA at 0.95 T: water stopping power scaled by the PMMA RSP."""
    def s_pmma(e):
        return PMMA_RELATIVE_STOPPING_POWER * pstar_stopping_power_MeV_per_mm(e)
    return float(track(energy_MeV, SCHELLHAMMER_FIELD_T, stopping_power=s_pmma).x_mm[-1])


def ode_depth_shortening_mm(energy_MeV: float, field_T: float) -> float:
    """How much less deep (mm) the proton stops in a field than without one, in water."""
    return float(track(energy_MeV, 0.0).z_mm[-1] - track(energy_MeV, field_T).z_mm[-1])


if __name__ == "__main__":
    s = schellhammer_table()
    s["ode_lateral_mm"] = [round(ode_lateral_in_pmma_mm(e), 2) for e in s.energy_nominal_MeV]
    print(s[["energy_nominal_MeV", "meas_lateral_y80_mm", "sim_lateral_y80_mm", "ode_lateral_mm"]].to_string(index=False))
    w = wang_table()
    w["ode_mm"] = [round(ode_depth_shortening_mm(e, 1.5), 2) for e in w.energy_MeV]
    print(w.to_string(index=False))
