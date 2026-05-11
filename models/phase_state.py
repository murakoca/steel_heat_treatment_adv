"""Phase state and result models"""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import numpy as np

@dataclass
class PhaseState:
    austenite: float = 1.0
    ferrite: float = 0.0
    pearlite: float = 0.0
    bainite: float = 0.0
    martensite: float = 0.0
    def total(self): return self.austenite+self.ferrite+self.pearlite+self.bainite+self.martensite
    def normalize(self):
        t = self.total()
        if t>0:
            self.austenite/=t; self.ferrite/=t; self.pearlite/=t; self.bainite/=t; self.martensite/=t

@dataclass
class PhaseResult:
    name: str
    fraction: float
    hardness_hv: float = 0.0
    carbon_content: float = 0.0

@dataclass
class HardnessResult:
    surface_hrc: float = 0.0
    core_hrc: float = 0.0
    surface_hv: float = 0.0
    core_hv: float = 0.0

@dataclass
class SimulationResult:
    cooling_curve: Optional[Tuple[np.ndarray, np.ndarray]] = None
    final_phases: Optional[PhaseState] = None
    phases: List[PhaseResult] = field(default_factory=list)
    hardness: Optional[HardnessResult] = None
    ttt_data: dict = field(default_factory=dict)
    log: str = ""
    def microstructure_summary(self) -> str:
        if not self.phases: return "No data"
        return "; ".join(f"{p.name}: {p.fraction*100:.1f}%" for p in self.phases)
