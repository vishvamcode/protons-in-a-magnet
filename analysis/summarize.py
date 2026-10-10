"""Compute the Stage 3 metrics table: python -m analysis.summarize"""
from pathlib import Path

import pandas as pd

from analysis.io import read_topas_depth_dose
from analysis.metrics import (distal_depth_mm, distal_falloff_mm, energy_deposited_per_history_MeV,
                              peak_depth_mm, peak_to_entrance_ratio, relative_uncertainty_at_peak)
from analysis.reference import pstar_ranges

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results" / "stage3"
ENERGIES_MeV = [70, 100, 150, 200, 230]
N_HISTORIES = 100_000
SLAB_MASS_KG = 0.40 * 0.40 * 0.0005 * 1000.0  # 40 x 40 cm x 0.5 mm of water at 1000 kg/m^3


def stage3_table() -> pd.DataFrame:
    ref = pstar_ranges().set_index("energy_MeV")
    rows = []
    for energy_MeV in ENERGIES_MeV:
        dd = read_topas_depth_dose(RESULTS / f"DepthDose_E{energy_MeV}_B0.csv", N_HISTORIES)
        r80_mm = distal_depth_mm(dd, 0.8)
        ref_mm = float(ref.loc[energy_MeV, "range_mm"])
        e_dep_MeV = energy_deposited_per_history_MeV(dd, SLAB_MASS_KG)
        rows.append({
            "energy_MeV": energy_MeV,
            "peak_depth_mm": peak_depth_mm(dd),
            "R90_mm": round(distal_depth_mm(dd, 0.9), 2),
            "R80_mm": round(r80_mm, 2),
            "R20_mm": round(distal_depth_mm(dd, 0.2), 2),
            "falloff_R20_R80_mm": round(distal_falloff_mm(dd), 2),
            "reference_range_mm": ref_mm,
            "R80_minus_ref_mm": round(r80_mm - ref_mm, 2),
            "R80_minus_ref_pct": round(100 * (r80_mm - ref_mm) / ref_mm, 2),
            "peak_to_entrance": round(peak_to_entrance_ratio(dd), 2),
            "rel_unc_peak_pct": round(100 * relative_uncertainty_at_peak(dd), 3),
            "energy_deposited_MeV": round(e_dep_MeV, 1),
            "energy_deposited_pct": round(100 * e_dep_MeV / energy_MeV, 1),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    table = stage3_table()
    table.to_csv(RESULTS / "summary.csv", index=False)
    print(table.to_string(index=False))
