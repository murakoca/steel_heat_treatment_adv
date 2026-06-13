
"""Katılaşma Simülasyonu (Click2Cast benzeri)"""
import numpy as np

def chvorinov_rule(volume, surface_area, mold_constant=1.0):
    return mold_constant * (volume / surface_area) ** 2

def solidification_microstructure(cooling_rate, composition):
    if cooling_rate > 100:
        return "İnce dendritik / Martensitik"
    elif cooling_rate > 10:
        return "Dendritik"
    else:
        return "Kaba dendritik / Eş eksenli"

def cooling_curve(t, T_initial, T_ambient, htc, rho, cp, volume, area):
    tau = rho * cp * volume / (htc * area)
    return T_ambient + (T_initial - T_ambient) * np.exp(-t / tau)
