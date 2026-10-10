"""Compute the metrics tables for Stages 3, 3b, 4 and the range-offset test: python -m analysis.summarize"""
from pathlib import Path

import numpy as np
import pandas as pd

from analysis.io import read_topas_depth_dose
from analysis.metrics import (distal_depth_mm, distal_falloff_mm, energy_deposited_per_history_MeV,
                              peak_depth_mm, peak_to_entrance_ratio, relative_uncertainty_at_peak)
from analysis.lateral import bragg_peak_position_mm, read_dose_xz
from analysis.lorentz_ode import track
from analysis.reference import pstar_ranges

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results" / "stage3"
RESULTS_SPREAD = ROOT / "results" / "stage3_spread1"
RESULTS_FIELD = ROOT / "results" / "stage4"
RESULTS_OFFSET = ROOT / "results"  # icru90_off/ and water75/: tests of the +0.5 % range offset
OFFSET_ENERGIES_MeV = [70, 150, 230]
FIELD_ENERGIES_MeV = [100, 150, 200, 230]
FIELDS_T = ["0", "0.5", "1.0", "1.5"]
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


def spread_table() -> pd.DataFrame:
    """Stage 3b: 1 % energy spread against the ideal (0 %) beam at the same energy."""
    rows = []
    for energy_MeV in ENERGIES_MeV:
        ideal = read_topas_depth_dose(RESULTS / f"DepthDose_E{energy_MeV}_B0.csv", N_HISTORIES)
        spread = read_topas_depth_dose(RESULTS_SPREAD / f"DepthDose_E{energy_MeV}_B0_s1.csv", N_HISTORIES)
        rows.append({
            "energy_MeV": energy_MeV,
            "R80_ideal_mm": round(distal_depth_mm(ideal, 0.8), 2),
            "R80_spread_mm": round(distal_depth_mm(spread, 0.8), 2),
            "R80_change_mm": round(distal_depth_mm(spread, 0.8) - distal_depth_mm(ideal, 0.8), 2),
            "falloff_ideal_mm": round(distal_falloff_mm(ideal), 2),
            "falloff_spread_mm": round(distal_falloff_mm(spread), 2),
            "peak_to_entrance_ideal": round(peak_to_entrance_ratio(ideal), 2),
            "peak_to_entrance_spread": round(peak_to_entrance_ratio(spread), 2),
            "rel_unc_peak_pct_spread": round(100 * relative_uncertainty_at_peak(spread), 3),
        })
    return pd.DataFrame(rows)


def field_table() -> pd.DataFrame:
    """Stage 4: Bragg-peak position in each field, against B = 0 and against the Lorentz-force model."""
    rows = []
    for energy_MeV in FIELD_ENERGIES_MeV:
        x0_mm = r80_0_mm = ode_z0_mm = None
        for field in FIELDS_T:
            name = f"E{energy_MeV}_B{field}"
            dd = read_topas_depth_dose(RESULTS_FIELD / f"DepthDose_{name}.csv", N_HISTORIES)
            x_peak_mm, z_peak_mm = bragg_peak_position_mm(read_dose_xz(RESULTS_FIELD / f"DoseXZ_{name}.csv"))
            r80_mm = distal_depth_mm(dd, 0.8)
            ode = track(energy_MeV, float(field))
            if field == "0":
                x0_mm, r80_0_mm, ode_z0_mm = x_peak_mm, r80_mm, ode.z_mm[-1]
            rows.append({
                "energy_MeV": energy_MeV,
                "field_T": float(field),
                "peak_depth_mm": z_peak_mm,
                "lateral_shift_at_peak_mm": round(abs(x_peak_mm - x0_mm), 2),
                "ode_lateral_at_peak_depth_mm": round(float(np.interp(z_peak_mm, ode.z_mm, ode.x_mm)), 2),
                "ode_lateral_end_of_range_mm": round(float(ode.x_mm[-1]), 2),
                "R80_mm": round(r80_mm, 2),
                "R80_shortening_mm": round(r80_0_mm - r80_mm, 2),
                "ode_depth_shortening_mm": round(float(ode_z0_mm - ode.z_mm[-1]), 2),
                "rel_unc_peak_pct": round(100 * relative_uncertainty_at_peak(dd), 3),
            })
    return pd.DataFrame(rows)


def offset_test_table() -> pd.DataFrame:
    """R80 minus PSTAR (mm) for the default set-up, with ICRU 90 switched off, and with water of I = 75 eV."""
    ref = pstar_ranges().set_index("energy_MeV").range_mm
    runs = {"default": RESULTS / "DepthDose_E{e}_B0.csv",
            "icru90_off": RESULTS_OFFSET / "icru90_off" / "DepthDose_E{e}_B0_noICRU90.csv",
            "water_75eV": RESULTS_OFFSET / "water75" / "DepthDose_E{e}_B0_water75.csv"}
    rows = []
    for energy_MeV in OFFSET_ENERGIES_MeV:
        row = {"energy_MeV": energy_MeV, "pstar_range_mm": ref[energy_MeV]}
        for label, path in runs.items():
            r80_mm = distal_depth_mm(read_topas_depth_dose(str(path).format(e=energy_MeV), N_HISTORIES), 0.8)
            row[f"R80_minus_ref_{label}_mm"] = round(r80_mm - ref[energy_MeV], 2)
        rows.append(row)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    for table, out in ((stage3_table(), RESULTS), (spread_table(), RESULTS_SPREAD), (field_table(), RESULTS_FIELD),
                       (offset_test_table(), RESULTS_OFFSET / "water75")):
        table.to_csv(out / "summary.csv", index=False)
        print(table.to_string(index=False), "\n")
