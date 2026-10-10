"""Tests of the range metrics on synthetic curves with known answers."""
import numpy as np
import pytest

from analysis.io import DepthDose
from analysis.metrics import (distal_depth_mm, distal_falloff_mm, energy_deposited_per_history_MeV, peak_depth_mm,
                              peak_to_entrance_ratio)


def make_curve(dose: np.ndarray, bin_width_mm: float = 0.5, n_histories: int = 1) -> DepthDose:
    depth_mm = (np.arange(dose.size) + 0.5) * bin_width_mm
    return DepthDose(depth_mm, dose, np.zeros_like(dose), n_histories, bin_width_mm)


def test_linear_falloff_gives_exact_r80_and_r20():
    # flat at 1 up to 100 mm, then a straight drop to 0 at 110 mm: R80 = 102 mm, R20 = 108 mm
    depth_mm = (np.arange(400) + 0.5) * 0.5
    dose = np.clip((110 - depth_mm) / 10, 0, 1)
    dose[0] = 0.5  # keep the peak well defined at the first full-dose bin
    dd = make_curve(dose)
    assert distal_depth_mm(dd, 0.8) == pytest.approx(102.0, abs=1e-9)
    assert distal_depth_mm(dd, 0.2) == pytest.approx(108.0, abs=1e-9)
    assert distal_falloff_mm(dd) == pytest.approx(6.0, abs=1e-9)


def test_peak_depth_and_entrance_ratio_of_gaussian_peak():
    depth_mm = (np.arange(400) + 0.5) * 0.5
    dose = 0.2 + np.exp(-0.5 * ((depth_mm - 150.25) / 3.0) ** 2)
    dd = make_curve(dose)
    assert peak_depth_mm(dd) == pytest.approx(150.25)
    assert peak_to_entrance_ratio(dd) == pytest.approx(1.2 / 0.2, rel=1e-3)


def test_curve_that_never_falls_raises():
    dd = make_curve(np.linspace(0.1, 1.0, 50))
    with pytest.raises(ValueError):
        distal_depth_mm(dd, 0.8)


def test_energy_deposited_round_trip():
    # 1 MeV per history deposited in a 1 kg slab gives dose 1.602e-13 Gy per history
    dd = make_curve(np.array([1.602176634e-13 * 10]), n_histories=10)
    assert energy_deposited_per_history_MeV(dd, slab_mass_kg=1.0) == pytest.approx(1.0)
