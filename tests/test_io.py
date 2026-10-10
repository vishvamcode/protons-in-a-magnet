"""Reading a TOPAS CSV: depth from bin index, uncertainty scaled by sqrt(N)."""
import numpy as np
import pytest

from analysis.io import read_topas_depth_dose


def test_read_scales_std_by_sqrt_n(tmp_path):
    f = tmp_path / "dd.csv"
    f.write_text("# TOPAS header\n# DoseToMedium ( Gy ) : Sum   Standard_Deviation\n0, 0, 0, 4.0, 0.01\n0, 0, 1, 8.0, 0.02\n")
    dd = read_topas_depth_dose(f, n_histories=100)
    assert np.allclose(dd.depth_mm, [0.25, 0.75])
    assert dd.dose_unc_Gy == pytest.approx([0.1, 0.2])
