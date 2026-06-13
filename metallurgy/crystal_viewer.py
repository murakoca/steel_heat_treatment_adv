
"""Kristal Yapı Görselleştirme (Crystal Maker benzeri)"""
import numpy as np
from itertools import product

CRYSTAL_SYSTEMS = {
    'cubic': {'a': 1.0, 'b': 1.0, 'c': 1.0, 'alpha': 90, 'beta': 90, 'gamma': 90},
    'tetragonal': {'a': 1.0, 'b': 1.0, 'c': 1.5, 'alpha': 90, 'beta': 90, 'gamma': 90},
    'orthorhombic': {'a': 1.0, 'b': 1.2, 'c': 1.5, 'alpha': 90, 'beta': 90, 'gamma': 90},
    'hexagonal': {'a': 1.0, 'b': 1.0, 'c': 1.633, 'alpha': 90, 'beta': 90, 'gamma': 120},
    'monoclinic': {'a': 1.0, 'b': 1.2, 'c': 1.5, 'alpha': 90, 'beta': 100, 'gamma': 90},
    'triclinic': {'a': 1.0, 'b': 1.2, 'c': 1.5, 'alpha': 80, 'beta': 90, 'gamma': 100},
    'rhombohedral': {'a': 1.0, 'b': 1.0, 'c': 1.0, 'alpha': 60, 'beta': 60, 'gamma': 60},
}

def generate_lattice(system, nx=2, ny=2, nz=2):
    params = CRYSTAL_SYSTEMS[system]
    positions = []
    for i, j, k in product(range(nx), range(ny), range(nz)):
        x, y, z = i * params['a'], j * params['b'], k * params['c']
        positions.append([x, y, z])
        if system in ['cubic', 'tetragonal', 'orthorhombic']:
            positions.append([x + params['a']/2, y + params['b']/2, z + params['c']/2])
            positions.append([x + params['a']/2, y + params['b']/2, z])
            positions.append([x + params['a']/2, y, z + params['c']/2])
            positions.append([x, y + params['b']/2, z + params['c']/2])
    return np.array(positions)

def simulate_xrd(wavelength, two_theta_range, hkl_list, lattice_param=1.0):
    theta = np.linspace(two_theta_range[0]/2, two_theta_range[1]/2, 1000)
    pattern = np.zeros_like(theta)
    for h, k, l in hkl_list:
        d = lattice_param / np.sqrt(h**2 + k**2 + l**2)
        sin_theta = wavelength / (2 * d)
        if sin_theta <= 1:
            theta_peak = np.arcsin(sin_theta)
            pattern += np.exp(-((theta - theta_peak) / 0.02)**2)
    return theta * 2, pattern
