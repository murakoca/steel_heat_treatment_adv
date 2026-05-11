"""Carbon diffusion"""
import numpy as np
from scipy.special import erfc
def carbon_diffusivity(T_celsius: float) -> float:
    T_k = T_celsius + 273.15
    return 2.0e-5 * np.exp(-140000/(8.314*T_k))
def carbon_profile(x, t, T, Cs, C0):
    D = carbon_diffusivity(T)
    if D*t <= 0: return np.full_like(x, C0)
    return C0 + (Cs-C0)*erfc(x/(2*np.sqrt(D*t)))
def effective_case_depth(profile, x, limit=0.004):
    idx = np.argmin(np.abs(profile - limit))
    return x[idx]
