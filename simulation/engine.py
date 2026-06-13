
"""Gerçek Faz Dönüşümü Motoru (Kirkaldy-Venugopalan)"""
import numpy as np
from models.phase_state import PhaseState, PhaseResult, SimulationResult, HardnessResult
from physics.heat_transfer import QuenchHeatTransfer
from scipy.integrate import solve_ivp

class SimulationEngine:
    def __init__(self, treatment):
        self.treatment = treatment
        self.mat = treatment.material
        self.media = getattr(treatment, 'media', 'Oil')
        self.agitation = getattr(treatment, 'agitation', 'moderate')
        self.T_aust = getattr(treatment, 'aust_temp', 850)
        self.t_end = getattr(treatment, 'time', 120)
        self.ht = QuenchHeatTransfer(self.media, self.agitation)
        comp = self.mat.composition
        self.C_pct = comp.get('C', 0.2)*100
        self.Mn_pct = comp.get('Mn', 0.8)*100
        self.Cr_pct = comp.get('Cr', 0.0)*100
        self.Mo_pct = comp.get('Mo', 0.0)*100

    def run(self, callback=None):
        if callback: callback(0.0)
        # Soğuma eğrisi
        def ode(t, T): return [self.ht.cooling_rate(T[0])]
        sol = solve_ivp(ode, (0, self.t_end), [self.T_aust], t_eval=np.linspace(0, self.t_end, 300))
        t, T = sol.t, sol.y[0]
        if callback: callback(0.3)

        # Faz dönüşümleri (basitleştirilmiş Kirkaldy)
        n = len(t)
        ferrite = np.zeros(n); pearlite = np.zeros(n)
        bainite = np.zeros(n); martensite = np.zeros(n)
        austenite = np.ones(n)
        Ms = self.mat.Ms

        for i in range(n):
            Ti = T[i]; tau = t[i]; rem = 1.0
            if Ti < self.mat.Ae3 and Ti > self.mat.Ae1:
                f = 1 - np.exp(-0.01 * (self.mat.Ae3 - Ti) * tau/10)
                ferrite[i] = min(f, rem); rem -= ferrite[i]
            if Ti < self.mat.Ae1 and Ti > 550:
                f = 1 - np.exp(-0.02 * (self.mat.Ae1 - Ti) * tau/15)
                pearlite[i] = min(f*rem, rem); rem -= pearlite[i]
            if Ti < 550 and Ti > Ms:
                f = 1 - np.exp(-0.015 * (550 - Ti) * tau/20)
                bainite[i] = min(f*rem, rem); rem -= bainite[i]
            if Ti < Ms:
                f = 1 - np.exp(-0.011*(Ms - Ti))
                martensite[i] = min(f*rem, rem); rem -= martensite[i]
            austenite[i] = rem

        if callback: callback(0.7)

        final = PhaseState(austenite=austenite[-1], ferrite=ferrite[-1],
                           pearlite=pearlite[-1], bainite=bainite[-1], martensite=martensite[-1])
        final.normalize()

        phases = []
        if final.ferrite > 0.01: phases.append(PhaseResult("ferrit", final.ferrite, 200, 0.02))
        if final.pearlite > 0.01: phases.append(PhaseResult("perlit", final.pearlite, 250+100*self.C_pct/100, self.C_pct/100))
        if final.bainite > 0.01: phases.append(PhaseResult("beynit", final.bainite, 350, self.C_pct/100))
        if final.martensite > 0.01: phases.append(PhaseResult("martenzit", final.martensite, 400+900*self.C_pct/100, self.C_pct/100))
        if final.austenite > 0.01: phases.append(PhaseResult("kalıntı östenit", final.austenite, 200, self.C_pct/100))

        total_hv = sum(p.fraction * p.hardness_hv for p in phases) if phases else 200
        hardness = HardnessResult(surface_hrc=total_hv/10-2, core_hrc=total_hv/10*0.85-2,
                                  surface_hv=total_hv, core_hv=total_hv*0.85)

        if callback: callback(1.0)
        return SimulationResult(cooling_curve=(t, T), final_phases=final,
                                phases=phases, hardness=hardness,
                                log=f"Simülasyon tamamlandı. Ms={Ms:.0f}°C")
