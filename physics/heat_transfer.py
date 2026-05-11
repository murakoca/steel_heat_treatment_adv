"""Real quench heat transfer"""
import numpy as np

class QuenchHeatTransfer:
    def __init__(self, media="Oil", agitation="moderate"):
        self.media = media
        self.agitation = agitation
        af = {"still":0.7, "moderate":1.0, "vigorous":1.5}.get(agitation,1.0)
        if media=="Water":
            self.htc_film=200*af; self.htc_nucleate=4000*af; self.htc_convection=800*af
            self.T_leid=400; self.T_nucl_end=150
        elif media=="Oil":
            self.htc_film=100*af; self.htc_nucleate=1500*af; self.htc_convection=300*af
            self.T_leid=600; self.T_nucl_end=350
        elif media=="Polymer":
            self.htc_film=150*af; self.htc_nucleate=2500*af; self.htc_convection=600*af
            self.T_leid=500; self.T_nucl_end=200
        else: # Brine
            self.htc_film=300*af; self.htc_nucleate=6000*af; self.htc_convection=1200*af
            self.T_leid=350; self.T_nucl_end=120
        self.T_ambient=25

    def get_htc(self, T):
        if T > self.T_leid: return self.htc_film
        elif T > self.T_nucl_end:
            frac = (T - self.T_nucl_end)/(self.T_leid - self.T_nucl_end)
            return self.htc_nucleate*frac + self.htc_convection*(1-frac)
        else: return self.htc_convection

    def cooling_rate(self, T):
        htc = self.get_htc(T)
        rho, cp = 7850, 475
        heat_loss = htc * 6e-4 * (T - self.T_ambient)
        return -heat_loss / (rho * cp * 1e-6)
