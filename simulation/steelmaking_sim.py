
"""BOF Çelik Üretimi ve İkincil Metalurji Hesaplama Motoru"""
import numpy as np

def calculate_decarburization(initial_C, target_C, oxygen_volume):
    """Dekarbürizasyon: giderilen karbon miktarını ve CO/CO₂ oluşumunu hesaplar"""
    C_removed = initial_C - target_C
    if C_removed <= 0:
        return {"C_removed": 0, "CO": 0, "CO2": 0, "O2_used": 0}
    # Karbonun %90'ı CO, %10'u CO₂ oluşturur (basitleştirilmiş)
    CO_formed = C_removed * 0.9 * (28/12)
    CO2_formed = C_removed * 0.1 * (44/12)
    O2_for_CO = C_removed * 0.9 * (16/12)
    O2_for_CO2 = C_removed * 0.1 * (32/12)
    O2_used = O2_for_CO + O2_for_CO2
    return {"C_removed": C_removed, "CO": CO_formed, "CO2": CO2_formed, "O2_used": O2_used}

def calculate_dephosphorization(P_initial, CaO, FeO, temperature):
    """Fosfor giderme hesabı"""
    # Yüksek FeO, yüksek baziklik, düşük sıcaklık → daha iyi P giderme
    basicity = CaO / 15  # SiO₂ yaklaşık %15 varsayımı
    if basicity <= 0:
        basicity = 2.5
    temp_factor = max(0, 1 - (temperature - 1600) / 200)
    P_removal_efficiency = min(0.9, 0.3 * (FeO/20) * (basicity/3) * temp_factor)
    P_removed = P_initial * P_removal_efficiency
    return {"P_removed": P_removed, "final_P": P_initial - P_removed, "efficiency": P_removal_efficiency}

def calculate_desulfurization(S_initial, CaO, FeO, temperature):
    """Kükürt giderme hesabı (BOF'ta sınırlı)"""
    basicity = CaO / 15
    if basicity <= 0:
        basicity = 2.5
    # Düşük FeO, yüksek baziklik → daha iyi S giderme
    FeO_factor = max(0, 1 - FeO/30)
    S_removal_efficiency = min(0.4, 0.15 * (basicity/3) * FeO_factor)
    S_removed = S_initial * S_removal_efficiency
    return {"S_removed": S_removed, "final_S": S_initial - S_removed, "efficiency": S_removal_efficiency}

def calculate_inclusion_modification(Al2O3_amount, Ca_injection):
    """Kalıntı modifikasyonu: Al₂O₃ → sıvı kalsiyum alüminat"""
    modified = min(Al2O3_amount, Ca_injection * 0.8)
    remaining_Al2O3 = Al2O3_amount - modified
    return {"modified": modified, "remaining_Al2O3": remaining_Al2O3, "castability": "İyi" if modified > Al2O3_amount*0.7 else "Orta"}

def calculate_ladle_refining(initial_S, CaO_ladle, Al_killing):
    """İkincil metalurji: kükürt giderme ve kalıntı kontrolü"""
    S_removed_ladle = min(initial_S * 0.8, CaO_ladle * 0.02)
    final_S = initial_S - S_removed_ladle
    inclusion_rating = "Temiz" if Al_killing > 0.5 else "Orta"
    return {"S_removed": S_removed_ladle, "final_S": final_S, "inclusion_rating": inclusion_rating}
