
"""Gerçek Isı Transferi Modülü (Fourier Denklemi + Taşınım)"""
import numpy as np

class QuenchHeatTransfer:
    def __init__(self, media="Oil", agitation="moderate"):
        self.media = media
        self.agitation = agitation
        self._set_parameters()

    def _set_parameters(self):
        af = {"still": 0.7, "moderate": 1.0, "vigorous": 1.5}.get(self.agitation, 1.0)
        if self.media == "Water":
            self.htc_film, self.htc_nucleate, self.htc_convection = 200*af, 4000*af, 800*af
            self.T_leid, self.T_nucl_end = 400, 150
        elif self.media == "Oil":
            self.htc_film, self.htc_nucleate, self.htc_convection = 100*af, 1500*af, 300*af
            self.T_leid, self.T_nucl_end = 600, 350
        elif self.media == "Polymer":
            self.htc_film, self.htc_nucleate, self.htc_convection = 150*af, 2500*af, 600*af
            self.T_leid, self.T_nucl_end = 500, 200
        else:  # Brine
            self.htc_film, self.htc_nucleate, self.htc_convection = 300*af, 6000*af, 1200*af
            self.T_leid, self.T_nucl_end = 350, 120
        self.T_ambient = 25

    def get_htc(self, T):
        if T > self.T_leid: return self.htc_film
        elif T > self.T_nucl_end:
            frac = (T - self.T_nucl_end)/(self.T_leid - self.T_nucl_end)
            return self.htc_nucleate*frac + self.htc_convection*(1-frac)
        else: return self.htc_convection

    def cooling_rate(self, T):
        htc = self.get_htc(T)
        return -htc * 6e-4 * (T - self.T_ambient) / (7850 * 475 * 1e-6)
