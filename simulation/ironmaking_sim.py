"""Demir Üretimi (Ironmaking) Hesaplama Motoru"""
import numpy as np


def calculate_hot_metal(ore_tons, fe_pct):
    """Sıcak metal (pik demir) miktarını ve bileşimini hesaplar."""
    fe_mass = ore_tons * fe_pct / 100  # ton Fe
    # Yüksek fırın verimi ~%92
    hm_total = fe_mass / 0.94  # ton sıcak metal
    return {
        'total': hm_total,
        'Fe': 94.0,
        'C': 4.5,
        'Si': 0.8,
        'Mn': 0.5,
        'P': 0.08,
        'S': 0.02
    }


def calculate_heat_zones(blast_temp):
    """Yüksek fırın sıcaklık bölgelerini hesaplar."""
    return {
        'throat': (200, 400),
        'stack': (400, 900),
        'cohesive': (1100, 1400),
        'bosh': (1400, 1800),
        'hearth': (1800, 2200)
    }


def calculate_reduction_steps(fe_pct):
    """İndirgenme basamaklarını hesaplar."""
    # Basitleştirilmiş model
    fe3o4_pct = fe_pct * 0.95  # %95'i Fe₃O₄'e dönüşür
    feo_pct = fe3o4_pct * 0.90  # %90'ı FeO'ya dönüşür
    fe_pct_final = feo_pct * 0.88  # %88'i metalik Fe'ye dönüşür
    return {
        'fe2o3_pct': 100,
        'fe3o4_pct': fe3o4_pct,
        'feo_pct': feo_pct,
        'fe_pct': fe_pct_final
    }


def calculate_slag(flux_rate, ore_tons, fe_pct):
    """Cüruf oluşumunu hesaplar."""
    gangue = ore_tons * (1 - fe_pct / 100) * 1000  # kg gang
    casio3 = flux_rate * ore_tons * 0.75  # CaSiO₃ oluşumu (kg)
    total_slag = gangue * 0.6 + casio3
    return {
        'amount': total_slag,
        'casio3': casio3,
        'gangue_removed': gangue * 0.6
    }


def calculate_fuel_rate(coke_rate, blast_temp):
    """Yakıt oranı ve verimlilik hesaplar."""
    # Sıcak hava sıcaklığı arttıkça kok tüketimi azalır
    corrected_coke = coke_rate * (1 - (blast_temp - 1000) * 0.0003)
    productivity = 2.5 * (1 + (blast_temp - 1000) * 0.001)
    top_gas_energy = corrected_coke * 3.5  # MJ/tHM (yaklaşık)
    return {
        'total_fuel_rate': corrected_coke + 150,  # kok + enjeksiyon
        'productivity': productivity,
        'top_gas_energy': top_gas_energy
    }


def hydrogen_reduction_feasibility(ore_tons, fe_pct):
    """Hidrojen ile doğrudan indirgeme fizibilitesi."""
    fe_mass = ore_tons * fe_pct / 100 * 1000  # kg Fe
    # Fe₂O₃ + 3H₂ → 2Fe + 3H₂O
    # 1 kg Fe için ~0.054 kg H₂ gerekir (teorik)
    h2_needed = fe_mass * 0.054
    h2_volume = h2_needed * 11.2  # Nm³ (STP'de 1 kg H₂ ≈ 11.2 Nm³)
    energy_needed = h2_needed * 120  # MJ (elektroliz için ~50-60 kWh/kg H₂ ≈ 180-216 MJ)
    co2_saved = fe_mass * 1.5  # kg CO₂ (geleneksel yönteme göre tasarruf)
    feasible = energy_needed < 50000  # Basit eşik
    return {
        'h2_needed_kg': h2_needed,
        'h2_volume_nm3': h2_volume,
        'energy_mj': energy_needed,
        'co2_saved_kg': co2_saved,
        'feasible': feasible
    }