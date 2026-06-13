
"""Difüzyon Simülasyonu (Dictra benzeri)"""
import numpy as np

def solve_diffusion_1d(C0, Cs, D, length, time, nx=100):
    dx = length / (nx - 1)
    dt = 0.4 * dx**2 / D
    nt = int(time / dt)
    C = np.ones(nx) * C0
    C[0] = Cs
    for _ in range(nt):
        C_new = C.copy()
        for i in range(1, nx-1):
            C_new[i] = C[i] + D * dt / dx**2 * (C[i+1] - 2*C[i] + C[i-1])
        C = C_new
    return np.linspace(0, length, nx), C

def matano_plane(x, C):
    C_mid = (np.min(C) + np.max(C)) / 2
    return x[np.argmin(np.abs(C - C_mid))]
