"""Sideways position of the beam from an OpenTOPAS x-z dose map (Stage 4)."""
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class DoseMap:
    """Dose in the x-z plane, summed over y. dose_Gy[iz, ix]; positions are bin centres in mm."""
    x_mm: np.ndarray
    depth_mm: np.ndarray
    dose_Gy: np.ndarray


def read_dose_xz(path: Path, half_width_mm: float = 200.0, x_bin_mm: float = 1.0,
                 depth_bin_mm: float = 0.5) -> DoseMap:
    """Read a TOPAS csv with columns (x bin, y bin, z bin, dose). Bin sizes must match the run file.

    The repo stores these maps gzipped (7 MB -> 2 MB each); if `path` is missing, `path.gz` is read instead."""
    path = Path(path)
    if not path.exists():
        path = path.with_name(path.name + ".gz")
    data = np.loadtxt(path, delimiter=",", comments="#")
    ix, iz = data[:, 0].astype(int), data[:, 2].astype(int)
    dose = np.zeros((iz.max() + 1, ix.max() + 1))
    dose[iz, ix] = data[:, 3]
    x_mm = (np.arange(dose.shape[1]) + 0.5) * x_bin_mm - half_width_mm
    depth_mm = (np.arange(dose.shape[0]) + 0.5) * depth_bin_mm
    return DoseMap(x_mm, depth_mm, dose)


def lateral_centroid_mm(dm: DoseMap, min_fraction: float = 0.05) -> tuple[np.ndarray, np.ndarray]:
    """Dose-weighted mean x at each depth (mm), keeping only depths whose total dose is above
    min_fraction of the maximum (deeper slices hold only a few stragglers and are noise)."""
    depth_dose = dm.dose_Gy.sum(axis=1)
    keep = depth_dose > min_fraction * depth_dose.max()
    centroid = (dm.dose_Gy[keep] * dm.x_mm).sum(axis=1) / depth_dose[keep]
    return dm.depth_mm[keep], centroid


def bragg_peak_position_mm(dm: DoseMap) -> tuple[float, float]:
    """(lateral x, depth) of the Bragg peak: the depth of maximum laterally summed dose, and the centroid there."""
    depth_dose = dm.dose_Gy.sum(axis=1)
    i = int(np.argmax(depth_dose))
    x_peak = float((dm.dose_Gy[i] * dm.x_mm).sum() / depth_dose[i])
    return x_peak, float(dm.depth_mm[i])
