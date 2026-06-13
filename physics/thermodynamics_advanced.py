
"""Termodinamik ve Faz Diyagramı (Thermo-Calc benzeri)"""
import numpy as np
from scipy.optimize import minimize

R = 8.314

def regular_solution_gibbs(x, T, omega):
    if x <= 0 or x >= 1:
        return 1e10
    return omega * x * (1 - x) + R * T * (x * np.log(x) + (1 - x) * np.log(1 - x))

def equilibrium_composition(T, omega, x0=0.5):
    G = lambda x: regular_solution_gibbs(x, T, omega)
    res = minimize(G, x0, bounds=[(0.001, 0.999)])
    return res.x[0] if res.success else None
