
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
        """Periyodik sınır koşullarını uygula - tüm değerleri [0, box_size] aralığında tutar"""
        pos = np.array(positions)
        pos = pos - self.box_size * np.floor(pos / self.box_size)
        pos = np.clip(pos, 0, self.box_size - 1e-10)
        return pos

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
            forces = self.velocity_verlet()
            # Pozisyonları sınırla
            self.positions = self.apply_pbc(self.positions)
            kinetic = 0.5 * np.sum(self.velocities**2)
            self.energy_history.append(kinetic)
            if callback:
                callback(step, self.positions, kinetic)

    def run_nvt(self, steps, target_temp, tau=0.1, callback=None):
        for step in range(steps):
            forces = self.velocity_verlet()
            # Pozisyonları sınırla
            self.positions = self.apply_pbc(self.positions)
            self.berendsen_thermostat(target_temp, tau)
            kinetic = 0.5 * np.sum(self.velocities**2)
            self.energy_history.append(kinetic)
            if callback:
                callback(step, self.positions, kinetic)
