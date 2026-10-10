"""Read OpenTOPAS depth-dose CSV files."""
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class DepthDose:
    """A depth-dose curve.

    depth_mm: centre of each depth bin (mm), bin 0 = entrance face
    dose_Gy: summed dose in each bin over all histories (Gy)
    dose_unc_Gy: 1-sigma statistical uncertainty of dose_Gy (Gy)
    """

    depth_mm: np.ndarray
    dose_Gy: np.ndarray
    dose_unc_Gy: np.ndarray
    n_histories: int
    bin_width_mm: float


def read_topas_depth_dose(path: str | Path, n_histories: int, bin_width_mm: float = 0.5) -> DepthDose:
    """Read a TOPAS CSV with columns x bin, y bin, z bin, Sum, Standard_Deviation.

    TOPAS's Standard_Deviation is the spread of the per-history dose, so the
    uncertainty of the summed dose is std * sqrt(N) (see scoring/TsVBinnedScorer.cc in OpenTOPAS v4.3.0).
    """
    data = np.loadtxt(path, delimiter=",", comments="#")
    depth_mm = (data[:, 2] + 0.5) * bin_width_mm
    dose_Gy = data[:, 3]
    dose_unc_Gy = data[:, 4] * np.sqrt(n_histories)
    return DepthDose(depth_mm, dose_Gy, dose_unc_Gy, n_histories, bin_width_mm)
