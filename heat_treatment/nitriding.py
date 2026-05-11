class Nitriding:
    def __init__(self, material, **kwargs): self.material=material
    def run(self):
        from simulation.engine import SimulationEngine
        return SimulationEngine(self).run()
