"""Make all figures from saved results: python -m analysis.figures"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from analysis.io import read_topas_depth_dose  # noqa: E402
from analysis.summarize import ENERGIES_MeV, N_HISTORIES, RESULTS, stage3_table  # noqa: E402

FIGURES = Path(__file__).resolve().parent.parent / "figures"
# Ordinal blue ramp, light -> dark with energy
BLUES = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e1e0d9"


def _style(ax):
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color("#c3c2b7")
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(colors=MUTED)


def fig1_depth_dose() -> Path:
    """Depth-dose curves for the five validation energies, each normalised to its own peak."""
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
    for energy_MeV, colour in zip(ENERGIES_MeV, BLUES):
        dd = read_topas_depth_dose(RESULTS / f"DepthDose_E{energy_MeV}_B0.csv", N_HISTORIES)
        rel = dd.dose_Gy / dd.dose_Gy.max() * 100
        ax.plot(dd.depth_mm, rel, color=colour, lw=2)
        i = int(np.argmax(rel))
        ax.annotate(f"{energy_MeV} MeV", (dd.depth_mm[i], 100), xytext=(0, 6), textcoords="offset points",
                    ha="center", color=INK, fontsize=9)
    ax.set_xlim(0, 360)
    ax.set_ylim(0, 112)
    ax.set_xlabel("Depth in water (mm)", color=MUTED)
    ax.set_ylabel("Dose (% of each curve's peak)", color=MUTED)
    ax.set_title("Higher energy, deeper Bragg peak: 70 to 230 MeV protons in water", loc="left", color=INK, fontsize=11)
    _style(ax)
    fig.text(0.01, 0.01, f"OpenTOPAS 4.3.0 / Geant4 11.4.2, {N_HISTORIES:,} protons per energy, 0.5 mm bins",
             color=MUTED, fontsize=7.5)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    out = FIGURES / "fig1_depth_dose_all_energies.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def fig2_range_validation() -> Path:
    """R80 minus the reference range at each energy, against the +-1% acceptance band."""
    t = stage3_table()
    fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
    e = np.array([50, 245])
    band_mm = 0.01 * np.interp(e, t.energy_MeV, t.reference_range_mm)
    ax.fill_between(e, -band_mm, band_mm, color="#cde2fb", alpha=0.6, lw=0)
    ax.axhline(0, color="#c3c2b7", lw=1)
    ax.plot(t.energy_MeV, t.R80_minus_ref_mm, "o", color="#2a78d6", ms=8)
    for _, r in t.iterrows():
        ax.annotate(f"+{r.R80_minus_ref_mm:.2f} mm ({r.R80_minus_ref_pct:.1f}%)", (r.energy_MeV, r.R80_minus_ref_mm),
                    xytext=(0, 9), textcoords="offset points", ha="center", color=INK, fontsize=8.5)
    ax.text(240, band_mm[1] - 0.25, "±1% of range\n(acceptance band)", ha="right", va="top", color=MUTED, fontsize=8)
    ax.set_xlim(50, 245)
    ax.set_ylim(-2.2, 3.4)
    ax.set_xlabel("Beam energy (MeV)", color=MUTED)
    ax.set_ylabel("Simulated R80 − reference range (mm)", color=MUTED)
    ax.set_title("Simulated range sits about 0.5% beyond the PSTAR reference at every energy", loc="left", color=INK,
                 fontsize=11)
    _style(ax)
    fig.text(0.01, 0.01, "Reference: NIST PSTAR via UCL table (provisional, see data/reference/SOURCE.md)",
             color=MUTED, fontsize=7.5)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    out = FIGURES / "fig2_range_validation.png"
    fig.savefig(out)
    plt.close(fig)
    return out


if __name__ == "__main__":
    FIGURES.mkdir(exist_ok=True)
    for make in (fig1_depth_dose, fig2_range_validation):
        print("wrote", make().relative_to(FIGURES.parent))
