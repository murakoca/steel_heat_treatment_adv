"""Real physics simulation engine"""
import numpy as np
from scipy.integrate import solve_ivp
import json, os
from typing import Optional

from models.phase_state import PhaseState, PhaseResult, SimulationResult, HardnessResult
from models.steel_model import Material
from physics.heat_transfer import QuenchHeatTransfer
from kinetics.koistinen_marburger import martensite_fraction
from kinetics.additivity import get_tau_from_ttt

class PhysicsEngine:
    def __init__(self, material: Material, process_params: dict):
        self.material = material
        self.params = process_params
        self._load_ttt_data()

    def _load_ttt_data(self):
        path = os.path.join(os.path.dirname(__file__), "..", "database", "ttt_data", f"{self.material.name}_ttt.json")
        try:
            with open(path) as f:
                self.ttt_data = json.load(f)
        except FileNotFoundError:
            self.ttt_data = {
                "pearlite_start":{"T":[680,650,600,550],"t":[5,20,100,300]},
                "bainite_start":{"T":[550,500,450,400],"t":[100,60,80,200]},
                "Ms":self.material.Ms
            }

    def simulate_cooling(self, T_initial=850, t_end=120, n_points=500):
        media = self.params.get("media","Oil")
        agitation = self.params.get("agitation","moderate")
        ht = QuenchHeatTransfer(media, agitation)
        def ode(t, T): return [ht.cooling_rate(T[0])]
        sol = solve_ivp(ode, (0, t_end), [T_initial], t_eval=np.linspace(0, t_end, n_points), method='RK45', rtol=1e-6, atol=1e-8)
        return sol.t, sol.y[0]

    def simulate_phase_transform(self, time, temperature):
        Ms = self.material.Ms; Mf = self.material.Mf
        n = len(time)
        phases = [PhaseState(austenite=1.0) for _ in range(n)]
        pearlite_started = False
        bainite_started = False
        martensite_started = False

        for i in range(1, n):
            T = temperature[i]
            dt = time[i]-time[i-1]

            # Pearlite
            if T < self.material.Ae1 and not pearlite_started and T > 550:
                tau_p = get_tau_from_ttt(T, self.ttt_data["pearlite_start"])
                if tau_p < 1e4 and i > tau_p*0.1:
                    frac = 1.0 - np.exp(-(i/(2*tau_p))**3)
                    phases[i].pearlite = min(frac, 0.9)
                    phases[i].austenite = 1.0 - phases[i].pearlite
                    if frac > 0.01: pearlite_started = True

            # Bainite
            if T < 550 and T > Ms and not bainite_started:
                tau_b = get_tau_from_ttt(T, self.ttt_data.get("bainite_start",{"T":[550,500,450],"t":[100,60,80]}))
                if tau_b < 1e4 and i > tau_b*0.1:
                    remaining = phases[i].austenite
                    frac_b = (1.0 - np.exp(-(i/(1.5*tau_b))**2.5)) * remaining
                    phases[i].bainite = frac_b
                    phases[i].austenite = remaining - frac_b
                    if frac_b > 0.01: bainite_started = True

            # Martensite
            if T < Ms and not martensite_started:
                martensite_started = True
            if martensite_started and T < Ms:
                f_mart = martensite_fraction(T, Ms, Mf)
                remaining = phases[i].austenite
                phases[i].martensite = f_mart * remaining
                phases[i].austenite = remaining - phases[i].martensite

        final = phases[-1]
        final.normalize()

        # Build phase results
        phase_res = []
        if final.pearlite > 0.01:
            phase_res.append(PhaseResult("pearlite", final.pearlite, 250+100*self.material.carbon, self.material.carbon))
        if final.bainite > 0.01:
            phase_res.append(PhaseResult("bainite", final.bainite, 350, self.material.carbon))
        if final.martensite > 0.01:
            hv = 127 + 949 * self.material.carbon * 100
            phase_res.append(PhaseResult("martensite", final.martensite, hv, self.material.carbon))
        if final.austenite > 0.01:
            phase_res.append(PhaseResult("retained austenite", final.austenite, 200, self.material.carbon))

        # Hardness
        total_hv = sum(p.fraction * p.hardness_hv for p in phase_res)
        surface_hrc = (total_hv / 10) - 2
        core_hrc = surface_hrc * 0.85
        hardness = HardnessResult(surface_hrc=surface_hrc, core_hrc=core_hrc, surface_hv=total_hv, core_hv=total_hv*0.85)

        return SimulationResult(cooling_curve=(time, temperature), final_phases=final,
                                phases=phase_res, hardness=hardness, ttt_data=self.ttt_data,
                                log=f"Simulation completed.")

    def run(self, callback=None):
        if callback: callback(0.0)
        t, T = self.simulate_cooling(self.params.get("aust_temp", 850), self.params.get("time", 120))
        if callback: callback(0.3)
        result = self.simulate_phase_transform(t, T)
        if callback: callback(0.8)
        result.cooling_curve = (t, T)
        if callback: callback(1.0)
        return result

class SimulationEngine:
    def __init__(self, treatment):
        self.treatment = treatment
    def run(self, callback=None):
        params = {
            "aust_temp": getattr(self.treatment, 'aust_temp', 850),
            "media": getattr(self.treatment, 'media', 'Oil'),
            "agitation": getattr(self.treatment, 'agitation', 'moderate'),
            "time": getattr(self.treatment, 'time', 120)
        }
        engine = PhysicsEngine(self.treatment.material, params)
        return engine.run(callback)
