"""My own deflection model: a proton slowing down in water while a uniform magnetic field bends it.

The proton moves in the x-z plane (beam along +z, field along y, so the force is along x). Along the path length s:

    dT/ds     = -S(T)          energy loss, S = stopping power of water (MeV/mm)
    dtheta/ds = 1 / R(T)       bending; R = p / (qB) is the radius of curvature at the current momentum
    dx/ds     = sin(theta)     sideways position
    dz/ds     = cos(theta)     depth

This ignores multiple Coulomb scattering and range straggling, so it describes the path of an "average" proton.
As the proton slows down, p falls and R shrinks, so most of the bending happens near the end of the range.
"""
from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp

from analysis.reference import pstar_stopping_power_MeV_per_mm

PROTON_MASS_MeV = 938.272088  # m_p c^2 (CODATA 2018)
ELECTRON_MASS_MeV = 0.51099895  # m_e c^2 (CODATA 2018)
C_LIGHT_GeV_PER_T_M = 0.299792458  # R[m] = p[GeV/c] / (0.2998 * B[T]) for charge e
K_BETHE_MeV_cm2_per_mol = 0.307075  # 4 pi N_A r_e^2 m_e c^2 (PDG)
WATER_Z_OVER_A = 0.55509  # mol/g, liquid water
WATER_DENSITY_g_per_cm3 = 1.0
WATER_I_eV = 75.0  # mean excitation energy used by PSTAR (ICRU 49); Geant4 opt4 uses 78 eV (ICRU 90)
T_STOP_MeV = 1.0  # stop the integration here: the residual range below 1 MeV is 0.025 mm (PSTAR)


def momentum_MeV(kinetic_MeV: float) -> float:
    """Proton momentum p c (MeV) from kinetic energy T (MeV)."""
    return np.sqrt(kinetic_MeV**2 + 2.0 * kinetic_MeV * PROTON_MASS_MeV)


def radius_mm(kinetic_MeV: float, field_T: float) -> float:
    """Radius of curvature R = p/(qB) in mm for a proton of kinetic energy T in a field B."""
    return momentum_MeV(kinetic_MeV) / 1000.0 / (C_LIGHT_GeV_PER_T_M * field_T) * 1000.0


def bethe_stopping_power_MeV_per_mm(kinetic_MeV: float, i_eV: float = WATER_I_eV) -> float:
    """Electronic stopping power of liquid water (MeV/mm) from the Bethe formula, no shell or density corrections.

    Good to about 1-2 % above ~10 MeV, which is where almost all of the path (and the bending) happens.
    """
    gamma = 1.0 + kinetic_MeV / PROTON_MASS_MeV
    beta2 = 1.0 - 1.0 / gamma**2
    me_ratio = ELECTRON_MASS_MeV / PROTON_MASS_MeV
    t_max = 2 * ELECTRON_MASS_MeV * beta2 * gamma**2 / (1 + 2 * gamma * me_ratio + me_ratio**2)  # MeV
    i_MeV = i_eV * 1e-6
    log_term = 0.5 * np.log(2 * ELECTRON_MASS_MeV * beta2 * gamma**2 * t_max / i_MeV**2)
    s_MeV_cm2_per_g = K_BETHE_MeV_cm2_per_mol * WATER_Z_OVER_A / beta2 * (log_term - beta2)
    return s_MeV_cm2_per_g * WATER_DENSITY_g_per_cm3 / 10.0  # MeV/cm -> MeV/mm


@dataclass
class Track:
    """Average proton path: arrays over path length, all in mm (energy in MeV, angle in rad)."""
    s_mm: np.ndarray
    x_mm: np.ndarray
    z_mm: np.ndarray
    energy_MeV: np.ndarray
    theta_rad: np.ndarray


def track(energy_MeV: float, field_T: float, stopping_power=pstar_stopping_power_MeV_per_mm,
          max_step_mm: float = 0.5) -> Track:
    """Integrate the path of a proton entering water along +z with kinetic energy T in a field B (along y).

    `stopping_power(T)` returns MeV/mm. Default: the NIST PSTAR table; `bethe_stopping_power_MeV_per_mm` is the
    textbook formula, kept as an independent check.
    """
    def rhs(s, y):
        x, z, theta, t = y
        curvature = 0.0 if field_T == 0 else 1.0 / radius_mm(t, field_T)
        return [np.sin(theta), np.cos(theta), curvature, -stopping_power(t)]

    def stopped(s, y):
        return y[3] - T_STOP_MeV
    stopped.terminal = True

    sol = solve_ivp(rhs, (0.0, 1000.0), [0.0, 0.0, 0.0, energy_MeV], events=stopped,
                    max_step=max_step_mm, rtol=1e-8, atol=1e-10)
    x, z, theta, t = sol.y
    return Track(sol.t, x, z, t, theta)
