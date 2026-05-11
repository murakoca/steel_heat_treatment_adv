"""Tempering with Hollomon-Jaffe"""
import math
from models.phase_state import SimulationResult, PhaseResult, HardnessResult
from heat_treatment.quenching import Quenching

class Tempering:
    def __init__(self, material, temperature=300, time=3600):
        self.material = material
        self.temperature = temperature
        self.time = time
    def run(self):
        # First quench
        result = Quenching(self.material, "Oil", "moderate", 850).run()
        # Hollomon-Jaffe parameter P = T*(log t + C) / 1000
        T_K = self.temperature + 273.15
        P = T_K * (math.log10(self.time) + 20) * 1e-3
        initial_hv = result.hardness.surface_hv if result.hardness else 650
        hardness_drop = max(0, (P-14)*15)
        new_hv = initial_hv - hardness_drop
        new_phases = []
        retained_aus = 0.0
        for p in result.phases:
            if p.name == "martensite":
                new_phases.append(PhaseResult("tempered martensite", p.fraction*0.85, new_hv, p.carbon_content))
                new_phases.append(PhaseResult("carbides", p.fraction*0.10, 800, p.carbon_content))
                new_phases.append(PhaseResult("ferrite", p.fraction*0.05, 200, 0.02))
            elif p.name == "retained austenite":
                retained_aus = p.fraction * 0.5
            else:
                new_phases.append(p)
        if retained_aus > 0.01:
            new_phases.append(PhaseResult("retained austenite", retained_aus, 200, 0.4))
        total_hv = sum(p.fraction*p.hardness_hv for p in new_phases)
        surface_hrc = (total_hv/10)-2
        core_hrc = surface_hrc*0.9
        result.phases = new_phases
        result.hardness = HardnessResult(surface_hrc=surface_hrc, core_hrc=core_hrc, surface_hv=total_hv, core_hv=total_hv*0.9)
        result.log += f"\nTempered: P={P:.1f}, hardness drop={hardness_drop:.0f} HV"
        return result
