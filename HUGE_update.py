#!/usr/bin/env python3
"""
TÜM DETAYLI MODÜLLERİ VE GUI SEK MELERİNİ KURAR
"""
import os, sys, json, shutil
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✅ {path}")

def backup_file(path):
    if os.path.exists(path):
        bak = path + f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(path, bak)
        return bak
    return None

print("=" * 70)
print("🚀 DETAYLANDIRILMIŞ MODÜLLER KURULUYOR")
print("=" * 70)

# ─────────────────────────────────────────────────
# 1. LAMMPS – Moleküler Dinamik
# ─────────────────────────────────────────────────
write_file("simulation/molecular_dynamics.py", r'''
"""Kapsamlı Moleküler Dinamik Simülatörü (LAMMPS benzeri)"""
import numpy as np
from scipy.spatial import cKDTree

class MolecularDynamics:
    def __init__(self, positions, box_size, potential='LJ', temperature=300, dt=0.001):
        self.positions = np.array(positions)
        self.velocities = np.random.randn(*self.positions.shape) * np.sqrt(temperature)
        self.box_size = box_size
        self.dt = dt
        self.potential = potential
        self.n_atoms = len(positions)
        self.dim = positions.shape[1]
        self.temperature = temperature
        self.energy_history = []

    def apply_pbc(self, positions):
        return positions - self.box_size * np.round(positions / self.box_size)

    def lj_force(self, r, epsilon=1.0, sigma=1.0):
        r_mag = np.linalg.norm(r)
        if r_mag < 1e-10 or r_mag > 2.5 * sigma:
            return np.zeros_like(r)
        sr = sigma / r_mag
        sr6 = sr ** 6
        sr12 = sr6 ** 2
        return 24 * epsilon * (2 * sr12 - sr6) / r_mag * r / r_mag

    def eam_force(self, r, rho_0=1.0, a=2.0, c=1.0):
        r_mag = np.linalg.norm(r)
        if r_mag < 1e-10 or r_mag > 5.0:
            return np.zeros_like(r)
        rho = rho_0 * np.exp(-a * (r_mag - 1.0))
        F_rho = -c * np.sqrt(rho)
        return F_rho * r / r_mag

    def compute_forces(self):
        forces = np.zeros_like(self.positions)
        tree = cKDTree(self.positions, boxsize=self.box_size)
        pairs = tree.query_pairs(r=2.5, output_type='ndarray')
        for i, j in pairs:
            rij = self.positions[i] - self.positions[j]
            rij = self.apply_pbc(rij)
            f = self.lj_force(rij) if self.potential == 'LJ' else self.eam_force(rij)
            forces[i] += f
            forces[j] -= f
        return forces

    def velocity_verlet(self):
        forces = self.compute_forces()
        self.positions += self.velocities * self.dt + 0.5 * forces * self.dt**2
        self.positions = self.apply_pbc(self.positions)
        new_forces = self.compute_forces()
        self.velocities += 0.5 * (forces + new_forces) * self.dt
        return new_forces

    def berendsen_thermostat(self, target_temp, tau=0.1):
        kinetic = 0.5 * np.sum(self.velocities**2)
        current_temp = 2 * kinetic / (3 * self.n_atoms)
        scale = np.sqrt(1 + self.dt / tau * (target_temp / current_temp - 1))
        self.velocities *= scale

    def run_nve(self, steps, callback=None):
        for step in range(steps):
            self.velocity_verlet()
            kinetic = 0.5 * np.sum(self.velocities**2)
            self.energy_history.append(kinetic)
            if callback:
                callback(step, self.positions, kinetic)

    def run_nvt(self, steps, target_temp, tau=0.1, callback=None):
        for step in range(steps):
            self.velocity_verlet()
            self.berendsen_thermostat(target_temp, tau)
            kinetic = 0.5 * np.sum(self.velocities**2)
            self.energy_history.append(kinetic)
            if callback:
                callback(step, self.positions, kinetic)
''')

# ─────────────────────────────────────────────────
# 2. Origin – Veri Analizi
# ─────────────────────────────────────────────────
write_file("metallurgy/data_analyzer.py", r'''
"""Kapsamlı Veri Analizi (Origin benzeri)"""
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit

def linear_fit(x, y):
    slope, intercept, r, p, std = stats.linregress(x, y)
    return {'slope': slope, 'intercept': intercept, 'r_squared': r**2}

def poly_fit(x, y, degree=2):
    coeffs = np.polyfit(x, y, degree)
    y_pred = np.polyval(coeffs, x)
    r2 = 1 - np.sum((y - y_pred)**2) / np.sum((y - np.mean(y))**2)
    return {'coeffs': coeffs.tolist(), 'r_squared': r2, 'y_pred': y_pred}

def exp_fit(x, y):
    try:
        popt, _ = curve_fit(lambda x, a, b: a * np.exp(b * x), x, y, p0=[1, 0.1])
        y_pred = popt[0] * np.exp(popt[1] * x)
        r2 = 1 - np.sum((y - y_pred)**2) / np.sum((y - np.mean(y))**2)
        return {'a': popt[0], 'b': popt[1], 'r_squared': r2}
    except:
        return None

def gaussian_fit(x, y):
    def gauss(x, a, mu, sigma):
        return a * np.exp(-(x - mu)**2 / (2 * sigma**2))
    try:
        popt, _ = curve_fit(gauss, x, y, p0=[max(y), np.mean(x), np.std(x)])
        y_pred = gauss(x, *popt)
        r2 = 1 - np.sum((y - y_pred)**2) / np.sum((y - np.mean(y))**2)
        return {'amplitude': popt[0], 'mean': popt[1], 'sigma': popt[2], 'r_squared': r2}
    except:
        return None

def descriptive_stats(data):
    d = np.array(data)
    return {'mean': np.mean(d), 'std': np.std(d, ddof=1), 'skew': stats.skew(d), 'kurtosis': stats.kurtosis(d)}

def anova(*groups):
    return stats.f_oneway(*groups)
''')

# ─────────────────────────────────────────────────
# 3. Thermo-Calc – Termodinamik
# ─────────────────────────────────────────────────
write_file("physics/thermodynamics_advanced.py", r'''
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
''')

# ─────────────────────────────────────────────────
# 4. FactSage – Alaşım Termodinamiği
# ─────────────────────────────────────────────────
write_file("metallurgy/alloy_thermodynamics.py", r'''
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
''')

# ─────────────────────────────────────────────────
# 5. Click2Cast – Katılaşma / Döküm
# ─────────────────────────────────────────────────
write_file("simulation/casting_sim.py", r'''
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
''')

# ─────────────────────────────────────────────────
# 6. Crystal Maker – Kristal Yapı
# ─────────────────────────────────────────────────
write_file("metallurgy/crystal_viewer.py", r'''
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
''')

# ─────────────────────────────────────────────────
# 7. Dictra – Difüzyon
# ─────────────────────────────────────────────────
write_file("simulation/diffusion_sim.py", r'''
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
''')

# ─────────────────────────────────────────────────
# 8. ImageJ – Görüntü Analizi
# ─────────────────────────────────────────────────
write_file("metallurgy/image_analyzer.py", r'''
"""Bilimsel Görüntü Analizi (ImageJ benzeri)"""
import numpy as np
from scipy import ndimage

def threshold(image, value=128):
    return (image > value).astype(np.uint8) * 255

def auto_threshold_otsu(image):
    if image.max() <= 1:
        image = (image * 255).astype(np.uint8)
    hist, _ = np.histogram(image.flatten(), 256, [0, 256])
    total = image.size
    sum_all = np.sum(np.arange(256) * hist)
    sum_b, w_b = 0, 0
    max_var, best = 0, 128
    for t in range(256):
        w_b += hist[t]
        if w_b == 0: continue
        w_f = total - w_b
        if w_f == 0: break
        sum_b += t * hist[t]
        mean_b = sum_b / w_b
        mean_f = (sum_all - sum_b) / w_f
        var = w_b * w_f * (mean_b - mean_f)**2
        if var > max_var:
            max_var = var
            best = t
    return threshold(image, best)

def particle_analysis(binary):
    labeled, n = ndimage.label(binary > 0)
    particles = []
    for i in range(1, n+1):
        area = np.sum(labeled == i)
        if area > 10:
            y, x = np.where(labeled == i)
            particles.append({'id': i, 'area': area, 'diameter': np.sqrt(4*area/np.pi)})
    return particles, labeled

def grain_size_distribution(labels, pixel_size=1.0):
    areas = []
    for label in range(1, labels.max()+1):
        area = np.sum(labels == label) * pixel_size**2
        if area > 0: areas.append(area)
    return np.array(areas)

def phase_fraction(binary):
    return np.sum(binary > 0) / binary.size
''')

# ─────────────────────────────────────────────────
# 9. JMatPro – TTT/CCT ve Sertlik
# ─────────────────────────────────────────────────
write_file("metallurgy/ttt_cct_plot.py", r'''
"""Malzeme Özellik Tahmini (JMatPro benzeri)"""
import numpy as np

def calculate_ttt(composition, grain_size=10):
    C = composition.get('C', 0) * 100
    Mn = composition.get('Mn', 0) * 100
    Cr = composition.get('Cr', 0) * 100
    Ni = composition.get('Ni', 0) * 100
    Mo = composition.get('Mo', 0) * 100
    T_pearlite = np.linspace(550, 700, 10)
    tau_pearlite = np.exp(2 + 0.5*C + 0.3*Mn + 0.4*Cr) / (grain_size**0.5)
    T_bainite = np.linspace(300, 550, 10)
    tau_bainite = np.exp(3 + 0.8*C + 0.5*Mn + 0.6*Cr + 1.0*Mo) / (grain_size**0.5)
    Ms = 539 - 423*C - 30.4*Mn - 17.7*Ni - 12.1*Cr - 7.5*Mo
    return {'pearlite': {'T': T_pearlite.tolist(), 't': tau_pearlite.tolist()},
            'bainite': {'T': T_bainite.tolist(), 't': tau_bainite.tolist()}, 'Ms': Ms}

def cct_from_ttt(ttt_data, cooling_rates):
    cct = {'pearlite_start': [], 'bainite_start': [], 'martensite_start': []}
    Ms = ttt_data['Ms']
    for rate in cooling_rates:
        T_pearl = np.interp(rate, [0.1, 100], [700, 500])
        T_bain = np.interp(rate, [0.1, 100], [550, 300])
        cct['pearlite_start'].append({'rate': rate, 'T': T_pearl})
        cct['bainite_start'].append({'rate': rate, 'T': T_bain})
        cct['martensite_start'].append({'rate': rate, 'T': Ms})
    return cct

def hardness_from_cct(cooling_rate, composition):
    C = composition.get('C', 0) * 100
    hardness = 200 + 300 * C + 5 * np.log10(cooling_rate + 1)
    return min(hardness, 700)
''')

print("\n✅ Tüm detaylı modüller başarıyla oluşturuldu.")