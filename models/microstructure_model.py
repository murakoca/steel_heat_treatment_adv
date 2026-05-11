"""Microstructure model"""
from dataclasses import dataclass
@dataclass
class Microstructure:
    grain_size_um: float = 10.0
    dislocation_density: float = 1e14
    carbide_fraction: float = 0.0
    carbide_size_nm: float = 0.0
    retained_austenite: float = 0.0
    residual_stress_mpa: float = 0.0
