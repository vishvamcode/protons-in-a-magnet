"""Checks of the Lorentz-force model with answers known in advance."""
import numpy as np

from analysis.lorentz_ode import bethe_stopping_power_MeV_per_mm, radius_mm, track
from analysis.reference import pstar_csda_range_mm


def test_no_field_gives_straight_line():
    t = track(150.0, 0.0)
    assert np.max(np.abs(t.x_mm)) < 1e-9


def test_radius_matches_p_over_qB():
    # 150 MeV proton: p c = sqrt(T^2 + 2 T m c^2) = 551.35 MeV, so R = 0.55135 / (0.29979 * 1.5) m = 1.2261 m
    assert abs(radius_mm(150.0, 1.5) - 1226.1) < 0.5


def test_constant_energy_path_is_a_circle():
    # Switch off energy loss: the proton must move on a circle of radius R = p/(qB)
    r_mm = radius_mm(150.0, 1.5)
    t = track(150.0, 1.5, stopping_power=lambda e: 1e-9, max_step_mm=5.0)
    s = t.s_mm[t.s_mm < 300]
    x = t.x_mm[: len(s)]
    assert np.allclose(x, r_mm * (1 - np.cos(s / r_mm)), atol=1e-3)


def test_range_without_field_matches_integral_of_inverse_stopping_power():
    energies_MeV = np.linspace(1.0, 150.0, 20001)
    csda_mm = np.trapezoid(1.0 / bethe_stopping_power_MeV_per_mm(energies_MeV), energies_MeV)
    assert abs(track(150.0, 0.0, stopping_power=bethe_stopping_power_MeV_per_mm).z_mm[-1] - csda_mm) < 0.05


def test_no_field_range_matches_pstar_csda():
    # The path stops at 1 MeV, where PSTAR's residual CSDA range is 0.025 mm. Tolerance 0.1 mm: the table gives
    # ranges to 4 significant figures (e.g. 31.74 g/cm2 at 225 MeV, so +-0.05 mm)
    for energy_MeV in (70.0, 150.0, 230.0):
        assert abs(track(energy_MeV, 0.0).z_mm[-1] + 0.025 - pstar_csda_range_mm(energy_MeV)) < 0.1


def test_bethe_agrees_with_pstar_above_10_MeV():
    from analysis.reference import pstar_stopping_power_MeV_per_mm
    e = np.array([10.0, 50.0, 100.0, 230.0])
    ratio = bethe_stopping_power_MeV_per_mm(e) / pstar_stopping_power_MeV_per_mm(e)
    assert np.all(np.abs(ratio - 1) < 0.02)


def test_stronger_field_bends_more_and_shortens_depth():
    x_end = [track(150.0, b).x_mm[-1] for b in (0.5, 1.0, 1.5)]
    z_end = [track(150.0, b).z_mm[-1] for b in (0.0, 0.5, 1.0, 1.5)]
    assert x_end[0] < x_end[1] < x_end[2]
    assert all(np.diff(z_end) < 0)
