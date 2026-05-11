"""Carburizing process"""
import numpy as np
from simulation.engine import SimulationEngine
from physics.diffusion import carbon_diffusivity, carbon_profile, effective_case_depth
from models.phase_state import SimulationResult, PhaseResult, HardnessResult

class Carburizing:
    def __init__(self, material, temperature=930, time=7200, carbon_pot=0.8, base_carbon=0.2):
        self.material = material
        self.temperature = temperature
        self.time = time
        self.carbon_pot = carbon_pot/100
        self.base_carbon = base_carbon/100
    def run(self):
        x = np.linspace(0, 0.01, 100)  # 0-10 mm
        D = carbon_diffusivity(self.temperature)
        profile = carbon_profile(x, self.time, self.temperature, self.carbon_pot, self.base_carbon)
        case_depth = effective_case_depth(profile, x, 0.004)*1000
        eff_depth = effective_case_depth(profile, x, 0.005)*1000
        surface_C = profile[0]
        surface_hv = 127 + 949*(surface_C*100)
        core_hv = 127 + 949*(self.base_carbon*100)
        phases = [
            PhaseResult("high-C martensite (case)", 0.6, surface_hv, surface_C),
            PhaseResult("low-C martensite (core)", 0.3, core_hv, self.base_carbon),
            PhaseResult("retained austenite", 0.1, 200, surface_C)
        ]
        surface_hrc = (surface_hv/10)-2
        core_hrc = (core_hv/10)-2
        return SimulationResult(
            phases=phases,
            hardness=HardnessResult(surface_hrc=surface_hrc, core_hrc=core_hrc, surface_hv=surface_hv, core_hv=core_hv),
            log=f"Carburizing: {self.temperature}°C, {self.time/3600:.1f}h, case depth: {case_depth:.2f} mm, surface C: {surface_C*100:.2f}%"
        )
