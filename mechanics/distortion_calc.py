"""Basit Distorsiyon ve Kalıntı Gerilme Tahmini"""
def estimate_residual_stress(cooling_rate_C_per_s, martensite_fraction, carbon_pct=0.4):
    """Soğuma hızı ve martensit oranına bağlı yaklaşık kalıntı gerilme (MPa)"""
    base = 150  # MPa
    stress = base + 300 * martensite_fraction + 0.5 * cooling_rate_C_per_s * carbon_pct * 100
    return round(stress, 1)

def distortion_risk(residual_stress, yield_strength=800):
    """Kalıntı gerilme / akma dayanımı oranına göre risk seviyesi"""
    ratio = residual_stress / yield_strength
    if ratio < 0.3: return "Düşük"
    elif ratio < 0.6: return "Orta"
    else: return "Yüksek"
