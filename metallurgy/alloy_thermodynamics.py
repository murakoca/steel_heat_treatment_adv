
"""Alaşım Termodinamiği (FactSage benzeri)"""
import numpy as np

R = 8.314

def redlich_kister_excess_gibbs(x, T, params):
    x_A, x_B = x, 1 - x
    G_excess = sum(L * (x_A - x_B)**i for i, L in enumerate(params))
    return x_A * x_B * G_excess

def activity_coefficient(x, T, params):
    G_excess = redlich_kister_excess_gibbs(x, T, params)
    return np.exp(G_excess / (R * T))

def calculate_eutectic(T_melt_A, T_melt_B, delta_H_A, delta_H_B):
    T_eut = 1 / (1/T_melt_A + 1/T_melt_B) * 0.8
    return {'T_eutectic': T_eut, 'composition': 0.5}
