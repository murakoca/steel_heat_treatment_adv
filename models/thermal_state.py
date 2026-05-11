from dataclasses import dataclass
import numpy as np
@dataclass
class ThermalState:
    temperature: np.ndarray
    time: np.ndarray