"""Make all figures from saved results: python -m analysis.figures"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from analysis.io import read_topas_depth_dose  # noqa: E402
from analysis.lateral import lateral_centroid_mm, read_dose_xz  # noqa: E402
from analysis.lorentz_ode import track  # noqa: E402
from analysis.summarize import (ENERGIES_MeV, FIELD_ENERGIES_MeV, FIELDS_T, N_HISTORIES, RESULTS,  # noqa: E402
                                RESULTS_FIELD, RESULTS_SPREAD, field_table, stage3_table)

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
    fig.text(0.01, 0.01, "Reference: NIST PSTAR CSDA range, liquid water (data/reference/pstar_water_liquid.txt)",
             color=MUTED, fontsize=7.5)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    out = FIGURES / "fig2_range_validation.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def fig3_energy_spread() -> Path:
    """Ideal beam (0 % energy spread) against a 1 % spread, near the Bragg peak, at the lowest and highest energy."""
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.8), dpi=150)
    for ax, energy_MeV in zip(axes, (70, 230)):
        ideal = read_topas_depth_dose(RESULTS / f"DepthDose_E{energy_MeV}_B0.csv", N_HISTORIES)
        spread = read_topas_depth_dose(RESULTS_SPREAD / f"DepthDose_E{energy_MeV}_B0_s1.csv", N_HISTORIES)
        norm = ideal.dose_Gy.max()
        ax.plot(ideal.depth_mm, ideal.dose_Gy / norm * 100, color=BLUES[1], lw=2, label="0 % spread (ideal)")
        ax.plot(spread.depth_mm, spread.dose_Gy / norm * 100, color=BLUES[4], lw=2, label="1 % spread")
        i = int(np.argmax(ideal.dose_Gy))
        ax.set_xlim(ideal.depth_mm[i] - 25, ideal.depth_mm[i] + 12)
        ax.set_ylim(0, 108)
        ax.set_title(f"{energy_MeV} MeV", loc="left", color=INK, fontsize=10)
        ax.set_xlabel("Depth in water (mm)", color=MUTED)
        _style(ax)
    axes[0].set_ylabel("Dose (% of ideal-beam peak)", color=MUTED)
    axes[0].legend(frameon=False, fontsize=8, loc="upper left")
    fig.suptitle("A 1 % energy spread lowers and widens the peak but leaves R80 almost unchanged", x=0.01, ha="left",
                 color=INK, fontsize=11)
    fig.text(0.01, 0.01, f"{N_HISTORIES:,} protons per run, same seed", color=MUTED, fontsize=7.5)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    out = FIGURES / "fig3_energy_spread.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def fig4_dose_map() -> Path:
    """Dose in the x-z plane for 230 MeV at 1.5 T, with the beam centroid and the Lorentz-force path."""
    dm = read_dose_xz(RESULTS_FIELD / "DoseXZ_E230_B1.5.csv")
    dm0 = read_dose_xz(RESULTS_FIELD / "DoseXZ_E230_B0.csv")
    z_mm, cx_mm = lateral_centroid_mm(dm)
    _, cx0_mm = lateral_centroid_mm(dm0)
    sign = np.sign(cx_mm[-1] - cx0_mm[0]) or 1.0  # plot the bend towards +x whatever the field direction
    ode = track(230.0, 1.5)
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
    ax.pcolormesh(dm.depth_mm, sign * (dm.x_mm - cx0_mm[0]), (dm.dose_Gy / dm.dose_Gy.max()).T, cmap="Blues",
                  vmin=0, vmax=1, shading="nearest", rasterized=True)
    ax.plot(z_mm, sign * (cx_mm - cx0_mm[0]), color=INK, lw=1.5, label="Simulated beam centre (dose-weighted)")
    ax.plot(ode.z_mm, ode.x_mm, color="#eb6834", lw=1.5, ls="--", label="Lorentz-force model")
    ax.axhline(0, color=MUTED, lw=0.8, ls=":")
    ax.set_xlim(0, 350)
    ax.set_ylim(-20, 60)
    ax.set_xlabel("Depth in water (mm)", color=MUTED)
    ax.set_ylabel("Sideways position (mm)", color=MUTED)
    ax.set_title("At 1.5 T a 230 MeV beam is bent about 4 cm sideways by the time it stops", loc="left", color=INK,
                 fontsize=11)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.tick_params(colors=MUTED)
    fig.text(0.01, 0.01, f"OpenTOPAS dose map, {N_HISTORIES:,} protons, field across the beam in the water only",
             color=MUTED, fontsize=7.5)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    out = FIGURES / "fig4_dose_map_230MeV_1.5T.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def fig5_trajectories() -> Path:
    """Beam centre against depth for each energy and field: simulation (solid) and Lorentz-force model (dashed)."""
    fig, axes = plt.subplots(1, 4, figsize=(11, 3.6), dpi=150, sharey=True)
    for ax, energy_MeV in zip(axes, FIELD_ENERGIES_MeV):
        _, cx0_mm = lateral_centroid_mm(read_dose_xz(RESULTS_FIELD / f"DoseXZ_E{energy_MeV}_B0.csv"))
        for field, colour in zip(FIELDS_T[1:], BLUES[1::2] + BLUES[-1:]):
            z_mm, cx_mm = lateral_centroid_mm(read_dose_xz(RESULTS_FIELD / f"DoseXZ_E{energy_MeV}_B{field}.csv"))
            shift_mm = cx_mm - cx0_mm[0]
            shift_mm *= np.sign(shift_mm[-1]) or 1.0
            ax.plot(z_mm, shift_mm, color=colour, lw=2, label=f"{field} T")
            ode = track(float(energy_MeV), float(field))
            ax.plot(ode.z_mm, ode.x_mm, color="#eb6834", lw=1, ls="--",
                    label="model" if field == FIELDS_T[-1] else None)
        ax.set_title(f"{energy_MeV} MeV", loc="left", color=INK, fontsize=10)
        ax.set_xlabel("Depth (mm)", color=MUTED)
        _style(ax)
    axes[0].set_ylabel("Sideways shift of beam centre (mm)", color=MUTED)
    axes[0].legend(frameon=False, fontsize=8, loc="upper left", title="solid: simulation",
                   title_fontsize=7.5)
    fig.suptitle("The bend grows with field and energy, and most of it happens near the end of the range",
                 x=0.01, ha="left", color=INK, fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out = FIGURES / "fig5_trajectories.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def fig6_shift_vs_field() -> Path:
    """Sideways shift of the Bragg peak against field strength: simulation (dots) and model (lines)."""
    t = field_table()
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
    for energy_MeV, colour in zip(FIELD_ENERGIES_MeV, BLUES[1:]):
        r = t[t.energy_MeV == energy_MeV]
        ax.plot(r.field_T, r.ode_lateral_at_peak_depth_mm, color=colour, lw=1.5, ls="--")
        ax.plot(r.field_T, r.lateral_shift_at_peak_mm, "o", color=colour, ms=7)
        last = r.iloc[-1]
        ax.annotate(f"{energy_MeV} MeV: {last.lateral_shift_at_peak_mm:.1f} mm", (last.field_T, last.lateral_shift_at_peak_mm),
                    xytext=(8, 0), textcoords="offset points", va="center", color=INK, fontsize=8.5)
    ax.set_xlim(-0.05, 1.95)
    ax.set_xticks([0, 0.5, 1.0, 1.5])
    ax.set_xlabel("Magnetic field across the beam (T)", color=MUTED)
    ax.set_ylabel("Sideways shift of the Bragg peak (mm)", color=MUTED)
    ax.set_title("The Bragg peak moves sideways in proportion to the field; the model tracks the simulation",
                 loc="left", color=INK, fontsize=11)
    _style(ax)
    fig.text(0.01, 0.01, "dots: OpenTOPAS (centroid at the peak depth)   dashed: Lorentz-force model at the same depth",
             color=MUTED, fontsize=7.5)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    out = FIGURES / "fig6_shift_vs_field.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def fig7_literature() -> Path:
    """Model and simulation against published numbers: Schellhammer 2018 (left) and Wang 2021 (right)."""
    from analysis.literature import ode_depth_shortening_mm, ode_lateral_in_pmma_mm, schellhammer_table, wang_table
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8), dpi=150)
    s = schellhammer_table()
    e_fine = np.arange(75, 186, 5.0)
    ax1.plot(e_fine, [ode_lateral_in_pmma_mm(e) for e in e_fine], color="#eb6834", lw=1.5, ls="--",
             label="my model (PMMA, uniform 0.95 T)")
    ax1.errorbar(s.energy_nominal_MeV, s.meas_lateral_y80_mm, yerr=s.meas_lateral_y80_unc_mm, fmt="o", color=BLUES[4],
                 ms=6, capsize=3, label="Schellhammer 2018, film")
    ax1.plot(s.energy_nominal_MeV, s.sim_lateral_y80_mm, "s", color=BLUES[1], ms=5, label="Schellhammer 2018, Geant4")
    ax1.set_title("Sideways shift in PMMA at 0.95 T", loc="left", color=INK, fontsize=10)
    ax1.set_xlabel("Proton energy (MeV)", color=MUTED)
    ax1.set_ylabel("Sideways shift (mm)", color=MUTED)
    ax1.legend(frameon=False, fontsize=8, loc="upper left")
    _style(ax1)
    w = wang_table()
    t = field_table()
    t = t[t.field_T == 1.5]
    e_fine = np.arange(70, 235, 5.0)
    ax2.plot(e_fine, [ode_depth_shortening_mm(e, 1.5) for e in e_fine], color="#eb6834", lw=1.5, ls="--",
             label="my model")
    ax2.plot(w.energy_MeV, w.depth_shortening_1p5T_mm, "s", color=BLUES[1], ms=5, label="Wang 2021, FLUKA (peak depth)")
    ax2.plot(t.energy_MeV, t.R80_shortening_mm, "o", color=BLUES[4], ms=6, label="this work, OpenTOPAS (R80)")
    ax2.set_title("Depth shortening in water at 1.5 T", loc="left", color=INK, fontsize=10)
    ax2.set_xlabel("Proton energy (MeV)", color=MUTED)
    ax2.set_ylabel("Depth shortening (mm)", color=MUTED)
    ax2.legend(frameon=False, fontsize=8, loc="upper left")
    _style(ax2)
    fig.text(0.01, 0.01, "Sources: Schellhammer et al. 2018 (arXiv:1709.00373, Table D.5); Wang et al. 2021 "
             "(Front. Public Health 9:641915, Table 2). PMMA stopping power 1.165 x water assumed (UNVERIFIED).",
             color=MUTED, fontsize=7)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    out = FIGURES / "fig7_literature.png"
    fig.savefig(out)
    plt.close(fig)
    return out


if __name__ == "__main__":
    FIGURES.mkdir(exist_ok=True)
    for make in (fig1_depth_dose, fig2_range_validation, fig3_energy_spread, fig4_dose_map, fig5_trajectories,
                 fig6_shift_vs_field, fig7_literature):
        print("wrote", make().relative_to(FIGURES.parent))
