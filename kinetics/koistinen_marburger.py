"""Koistinen-Marburger"""
import numpy as np
def martensite_fraction(T, Ms, Mf=None, alpha=0.011):
    if T >= Ms: return 0.0
    if Mf is not None and T <= Mf: return 0.95
    return 1.0 - np.exp(-alpha * (Ms - T))
