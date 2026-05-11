"""Quenching process"""
from simulation.engine import SimulationEngine
class Quenching:
    def __init__(self, material, media="Oil", agitation="moderate", aust_temp=850, time=120):
        self.material = material
        self.media = media
        self.agitation = agitation
        self.aust_temp = aust_temp
        self.time = time
    def run(self):
        return SimulationEngine(self).run()
