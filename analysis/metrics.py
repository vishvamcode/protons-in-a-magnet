"""Range metrics of a Bragg curve. All depths in mm."""
import numpy as np

from analysis.io import DepthDose

MEV_TO_J = 1.602176634e-13


def peak_depth_mm(dd: DepthDose) -> float:
    """Depth of the bin with the highest dose (bin centre, so +-half a bin)."""
    return float(dd.depth_mm[np.argmax(dd.dose_Gy)])


def distal_depth_mm(dd: DepthDose, fraction: float) -> float:
    """Depth beyond the peak where dose first falls to `fraction` of the maximum (e.g. 0.8 -> R80).

    Linear interpolation between the two bins that bracket the level.
    """
    i_peak = int(np.argmax(dd.dose_Gy))
    level = fraction * dd.dose_Gy[i_peak]
    beyond = dd.dose_Gy[i_peak:]
    j = i_peak + int(np.argmax(beyond < level))
    if j == i_peak:
        raise ValueError(f"dose never falls below {fraction:.0%} of the peak")
    z0, z1 = dd.depth_mm[j - 1], dd.depth_mm[j]
    d0, d1 = dd.dose_Gy[j - 1], dd.dose_Gy[j]
    return float(z0 + (d0 - level) * (z1 - z0) / (d0 - d1))


def distal_falloff_mm(dd: DepthDose) -> float:
    """R20 - R80: width of the distal dose edge."""
    return distal_depth_mm(dd, 0.2) - distal_depth_mm(dd, 0.8)


def peak_to_entrance_ratio(dd: DepthDose) -> float:
    """Peak dose divided by the dose in the first bin."""
    return float(dd.dose_Gy.max() / dd.dose_Gy[0])


def relative_uncertainty_at_peak(dd: DepthDose) -> float:
    """1-sigma relative statistical uncertainty of the peak bin (fraction, not %)."""
    i = int(np.argmax(dd.dose_Gy))
    return float(dd.dose_unc_Gy[i] / dd.dose_Gy[i])


def energy_deposited_per_history_MeV(dd: DepthDose, slab_mass_kg: float) -> float:
    """Total energy deposited in the scored volume per history (MeV).

    slab_mass_kg: mass of one depth bin (for 40 x 40 x 0.05 cm of water: 0.08 kg).
    """
    return float(dd.dose_Gy.sum() * slab_mass_kg / MEV_TO_J / dd.n_histories)
