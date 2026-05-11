"""JMAK model"""
import numpy as np
def jmak_fraction(t, tau, n=2.0):
    if tau<=0: return 0.0
    return 1.0 - np.exp(-(t/tau)**n)
