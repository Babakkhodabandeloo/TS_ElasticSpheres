"""Backscattering calculations for elastic spheres."""

import numpy as np
from scipy.special import spherical_jn, spherical_yn


def backscatter_amplitude(
    radius,
    frequency,
    rho_water,
    c_water,
    rho_sphere,
    c_compressional,
    c_shear,
    far_field_distance=100.0,
    expansion_order=None,
):
    """
    Calculate the far-field backscattering amplitude of an elastic sphere.

    Parameters
    ----------
    radius : float
        Sphere radius [m].
    frequency : float
        Acoustic frequency [Hz].
    rho_water : float
        Density of the surrounding water [kg/m^3].
    c_water : float
        Sound speed in the surrounding water [m/s].
    rho_sphere : float
        Density of the elastic sphere [kg/m^3].
    c_compressional : float
        Compressional-wave speed in the sphere [m/s].
    c_shear : float
        Shear-wave speed in the sphere [m/s].
    far_field_distance : float, optional
        Far-field evaluation distance [m].
    expansion_order : int, optional
        Number of spherical-wave expansion terms. If None,
        the expansion order is estimated automatically.

    Returns
    -------
    complex
        Far-field backscattering amplitude [m].
    """

    # ==========================================================
    # Angular frequency and wavenumbers
    # ==========================================================

    omega = 2.0 * np.pi * frequency

    k_water = omega / c_water
    k_compressional = omega / c_compressional
    k_shear = omega / c_shear

    mu = rho_sphere * c_shear**2


    # ==========================================================
    # Expansion order
    # ==========================================================

    if expansion_order is None:
        expansion_order = int(radius * 2.0 * np.pi * frequency / c_water) + 20

    m = np.arange(expansion_order)
    mm = m * (m + 1)


    # ==========================================================
    # Water-side spherical Bessel and Hankel functions
    # ==========================================================

    z_water = k_water * radius

    jm_water = spherical_jn(m, z_water)
    djm_water = spherical_jn(m, z_water, derivative=True)

    ym_water = spherical_yn(m, z_water)
    dym_water = spherical_yn(m, z_water, derivative=True)

    hm_water = jm_water + 1j * ym_water
    dhm_water = djm_water + 1j * dym_water


    # ==========================================================
    # Compressional-wave terms inside sphere
    # ==========================================================

    z_compressional = k_compressional * radius

    jm_compressional = spherical_jn(m, z_compressional)
    djm_compressional = spherical_jn(m, z_compressional, derivative=True)

    ddjm_compressional = (-2.0 * z_compressional * djm_compressional - (z_compressional**2 - m**2 - m) * jm_compressional) / z_compressional**2


    # ==========================================================
    # Shear-wave terms inside sphere
    # ==========================================================

    z_shear = k_shear * radius

    jm_shear = spherical_jn(m, z_shear)
    djm_shear = spherical_jn(m, z_shear, derivative=True)

    ddjm_shear = (-2.0 * z_shear * djm_shear - (z_shear**2 - m**2 - m) * jm_shear) / z_shear**2


    # ==========================================================
    # Boundary-condition matrices
    # ==========================================================

    M = np.zeros((expansion_order, 3, 3), dtype=complex)
    F = np.zeros((expansion_order, 3, 1), dtype=complex)


    # Row 1

    M[:, 0, 0] = k_water * radius * dhm_water
    M[:, 0, 1] = -k_compressional * radius * djm_compressional
    M[:, 0, 2] = mm * jm_shear

    F[:, 0, 0] = (1j**m) * (-2.0 * m - 1.0) * k_water * radius * djm_water


    # Row 2

    M[:, 1, 0] = omega**2 * radius**2 * rho_water * hm_water
    M[:, 1, 1] = mu * radius**2 * (2.0 * k_compressional**2 - k_shear**2) * jm_compressional + 2.0 * mu * k_compressional**2 * radius**2 * ddjm_compressional
    M[:, 1, 2] = -2.0 * mu * k_shear * radius * mm * djm_shear + 2.0 * mu * mm * jm_shear

    F[:, 1, 0] = (1j**m) * (-2.0 * m - 1.0) * omega**2 * radius**2 * rho_water * jm_water


    # Row 3

    M[:, 2, 0] = 0.0
    M[:, 2, 1] = 2.0 * k_compressional * radius * djm_compressional - 2.0 * jm_compressional
    M[:, 2, 2] = -k_shear**2 * radius**2 * ddjm_shear + 2.0 * jm_shear - mm * jm_shear


    # ==========================================================
    # Solve boundary-condition systems
    # ==========================================================

    result = np.linalg.solve(M, F)

    A_m = result[:, 0, 0]


    # ==========================================================
    # Far-field backscattering
    # ==========================================================

    z_far = k_water * far_field_distance

    jm_far = spherical_jn(m, z_far)
    ym_far = spherical_yn(m, z_far)

    hm_far = jm_far + 1j * ym_far

    phase_correction = np.exp(-1j * k_water * far_field_distance)

    terms = far_field_distance * A_m * ((-1.0)**m) * hm_far * phase_correction

    f_bs = np.sum(terms)

    return f_bs


def target_strength(
    radius,
    frequency,
    rho_water,
    c_water,
    rho_sphere,
    c_compressional,
    c_shear,
    far_field_distance=100.0,
    expansion_order=None,
):
    """Calculate target strength of an elastic sphere [dB]."""

    f_bs = backscatter_amplitude(
        radius,
        frequency,
        rho_water,
        c_water,
        rho_sphere,
        c_compressional,
        c_shear,
        far_field_distance,
        expansion_order,
    )

    return 20.0 * np.log10(np.abs(f_bs))