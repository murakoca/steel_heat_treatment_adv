"""Kaldıraç Kuralı (Lever Rule) Hesaplamaları"""
from dataclasses import dataclass

@dataclass
class LeverResult:
    phase_alpha_name: str = "α"
    phase_beta_name: str = "β"
    fraction_alpha: float = 0.0
    fraction_beta: float = 0.0
    composition_alpha: float = 0.0
    composition_beta: float = 0.0
    overall_composition: float = 0.0
    
    @property
    def percent_alpha(self): return self.fraction_alpha * 100
    @property
    def percent_beta(self): return self.fraction_beta * 100

def calculate(Ca: float, Cb: float, Co: float) -> LeverResult:
    """Kaldıraç kuralı ile faz oranlarını hesapla"""
    if abs(Cb - Ca) < 1e-10:
        raise ValueError("Faz kompozisyonları aynı olamaz")
    
    f_alpha = (Cb - Co) / (Cb - Ca)
    f_beta = (Co - Ca) / (Cb - Ca)
    
    # 0-1 aralığında olduğundan emin ol
    f_alpha = max(0.0, min(1.0, f_alpha))
    f_beta = max(0.0, min(1.0, f_beta))
    
    return LeverResult(
        fraction_alpha=f_alpha,
        fraction_beta=f_beta,
        composition_alpha=Ca,
        composition_beta=Cb,
        overall_composition=Co
    )

# Fe-C faz diyagramı için örnek noktalar
FE_C_EXAMPLES = {
    "Ötektoid (0.8% C, 727°C)": {"Ca": 0.022, "Cb": 6.67, "Co": 0.8, "alpha": "Ferrit (α)", "beta": "Sementit (Fe₃C)"},
    "Ötektoid Altı (0.4% C)": {"Ca": 0.022, "Cb": 6.67, "Co": 0.4, "alpha": "Ferrit (α)", "beta": "Sementit (Fe₃C)"},
    "Ötektoid Üstü (1.2% C)": {"Ca": 0.022, "Cb": 6.67, "Co": 1.2, "alpha": "Ferrit (α)", "beta": "Sementit (Fe₃C)"},
    "Cu-Ni (30% Ni)": {"Ca": 25, "Cb": 40, "Co": 30, "alpha": "α (Ni-az)", "beta": "Sıvı (Ni-zengin)"},
}
