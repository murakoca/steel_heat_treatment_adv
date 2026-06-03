"""Karbon Difüzyonu Profil Simülasyonu"""
import numpy as np
from physics.diffusion import carbon_profile, carbon_diffusivity

def simulate_carburizing(T_celsius, time_hours, Cs, C0, depth_mm=5.0):
    """Karbon difüzyon profilini hesapla (yarı-sonsuz katı modeli)"""
    t_sec = time_hours * 3600
    D = carbon_diffusivity(T_celsius)
    x_mm = np.linspace(0, depth_mm, 200)
    x_m = x_mm / 1000.0
    profile = carbon_profile(x_m, t_sec, T_celsius, Cs/100, C0/100)
    return x_mm, profile * 100  # %C cinsinden döndür
