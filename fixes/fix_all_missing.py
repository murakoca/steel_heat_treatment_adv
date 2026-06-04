#!/usr/bin/env python3
"""
TÜM EKSİK MODÜLLERİ VE VERİTABANLARINI OLUŞTURUR
- metallurgy/interactive_fec.py
- procurement/calculator.py
- database/procurement_guide.json
- app/main.py'yi çalışır hale getirir
"""
import os, json

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✅ {path}")

print("=" * 60)
print("🛠️ EKSİK MODÜL TAMİRCİSİ")
print("=" * 60)

# 1. metallurgy/interactive_fec.py
write_file("metallurgy/interactive_fec.py", '''"""
İnteraktif Fe-C Faz Diyagramı - Gelişmiş Modül
"""
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

@dataclass
class PhasePoint:
    temperature: float
    carbon_pct: float
    phases: List[str]
    fractions: Dict[str, float]
    description: str

class FeCDiagram:
    def __init__(self):
        self.T_eutectoid = 727.0
        self.C_eutectoid = 0.77
        self.T_eutectic = 1147.0
        self.C_eutectic = 4.3
        self.T_peritectic = 1493.0
        self.C_peritectic = 0.16
        self.element_effects = {
            "C": {"A1_shift": 0, "A3_shift": 0, "eutectoid_shift": 1.0},
            "Mn": {"A1_shift": -5, "A3_shift": -30, "eutectoid_shift": -0.05},
            "Si": {"A1_shift": 20, "A3_shift": 40, "eutectoid_shift": -0.1},
            "Cr": {"A1_shift": 15, "A3_shift": 20, "eutectoid_shift": -0.05},
            "Ni": {"A1_shift": -15, "A3_shift": -25, "eutectoid_shift": -0.08},
            "Mo": {"A1_shift": 20, "A3_shift": 30, "eutectoid_shift": -0.05},
        }
        self.A3_points = np.array([
            [0.0, 912.0], [0.1, 870.0], [0.2, 830.0],
            [0.3, 800.0], [0.4, 780.0], [0.5, 760.0],
            [0.6, 740.0], [0.77, 727.0]
        ])
        self.Acm_points = np.array([
            [0.77, 727.0], [1.0, 800.0], [1.5, 950.0],
            [2.0, 1050.0], [2.5, 1120.0], [3.0, 1160.0],
            [3.5, 1180.0], [4.3, 1147.0]
        ])
        self.solidus = np.array([
            [0.0, 1493.0], [0.16, 1493.0], [0.51, 1450.0],
            [1.0, 1350.0], [2.0, 1200.0], [3.0, 1150.0], [4.3, 1147.0]
        ])
        self.liquidus = np.array([
            [0.0, 1538.0], [0.16, 1493.0], [0.51, 1470.0],
            [1.0, 1420.0], [2.0, 1320.0], [3.0, 1250.0], [4.3, 1147.0]
        ])

    def adjust_boundaries(self, composition: Dict[str, float]):
        A1_shift = sum(self.element_effects.get(e, {}).get("A1_shift", 0) * pct 
                       for e, pct in composition.items())
        A3_shift = sum(self.element_effects.get(e, {}).get("A3_shift", 0) * pct 
                       for e, pct in composition.items())
        eut_shift = sum(self.element_effects.get(e, {}).get("eutectoid_shift", 0) * pct 
                        for e, pct in composition.items())
        return {"T_A1": self.T_eutectoid + A1_shift, 
                "C_eutectoid": self.C_eutectoid + eut_shift, 
                "T_A3_shift": A3_shift}

    def get_phases(self, T: float, C: float, composition: Dict = None) -> PhasePoint:
        if composition is None:
            composition = {"C": C}
        adj = self.adjust_boundaries(composition)
        T_A1 = adj["T_A1"]
        phases = []; fractions = {}; desc = ""
        if T > 1493:
            phases = ["Sıvı (L)"]; fractions = {"Sıvı": 1.0}; desc = "Tamamen ergimiş"
        elif T > T_A1:
            if C < adj["C_eutectoid"]:
                phases = ["α (ferrit)", "γ (östenit)"]
                f = (adj["C_eutectoid"] - C) / (adj["C_eutectoid"] - 0.022)
                f = max(0, min(1, f))
                fractions = {"α": f, "γ": 1-f}
                desc = f"Hipoötektoid (%{C:.2f} C)"
            else:
                phases = ["γ (östenit)", "Fe₃C (sementit)"]
                f = (6.67 - C) / (6.67 - adj["C_eutectoid"])
                f = max(0, min(1, f))
                fractions = {"γ": f, "Fe₃C": 1-f}
                desc = f"Hiperötektoid (%{C:.2f} C)"
        else:
            if C < 0.77:
                phases = ["α (ferrit)", "Fe₃C (sementit)"]
                f = (6.67 - C) / (6.67 - 0.022)
                f = max(0, min(1, f))
                fractions = {"α": f, "Fe₃C": 1-f}
                desc = "Ferrit + Perlit"
            else:
                phases = ["Perlit", "Fe₃C (sementit)"]
                f = (6.67 - C) / (6.67 - 0.77)
                f = max(0, min(1, f))
                fractions = {"Perlit": f, "Fe₃C": 1-f}
                desc = "Perlit + Sementit"
        return PhasePoint(temperature=T, carbon_pct=C, phases=phases, fractions=fractions, description=desc)

    def draw(self, ax, composition=None, highlight_point=None):
        if composition is None:
            composition = {"C": 0.77}
        adj = self.adjust_boundaries(composition)
        A3_adj = self.A3_points.copy()
        A3_adj[:, 1] += adj["T_A3_shift"]
        ax.plot(A3_adj[:, 0], A3_adj[:, 1], 'b-', lw=2.5, label='A3')
        ax.plot(self.Acm_points[:, 0], self.Acm_points[:, 1], 'r-', lw=2.5, label='Acm')
        ax.plot(self.solidus[:, 0], self.solidus[:, 1], 'k-', lw=2, label='Solidus')
        ax.plot(self.liquidus[:, 0], self.liquidus[:, 1], 'k--', lw=2, label='Liquidus')
        ax.axhline(adj["T_A1"], color='green', ls='--', lw=1.5, alpha=0.7, label=f'A1={adj["T_A1"]:.0f}°C')
        ax.axhline(self.T_eutectic, color='purple', ls='--', lw=1.5, alpha=0.7, label=f'Ötektik={self.T_eutectic}°C')
        ax.text(0.15, 800, 'α+γ', fontsize=10, color='blue', alpha=0.8)
        ax.text(1.2, 900, 'γ+Fe₃C', fontsize=10, color='red', alpha=0.8)
        ax.text(0.3, 400, 'α+Fe₃C', fontsize=10, color='green', alpha=0.8)
        if highlight_point:
            C_pt, T_pt = highlight_point
            ax.plot(C_pt, T_pt, 'yo', markersize=12, markeredgecolor='black', markeredgewidth=2)
            ax.annotate(f'%{C_pt:.2f} C\n{T_pt:.0f}°C', xy=(C_pt, T_pt), 
                       xytext=(C_pt+0.5, T_pt+50),
                       arrowprops=dict(arrowstyle='->', color='yellow'),
                       fontsize=10, color='yellow', fontweight='bold')
        ax.set_xlabel('Karbon (% ağırlık)', fontsize=12)
        ax.set_ylabel('Sıcaklık (°C)', fontsize=12)
        ax.set_title('Fe–C Faz Diyagramı', fontsize=14, fontweight='bold')
        ax.set_xlim(0, 6.67); ax.set_ylim(0, 1600)
        ax.legend(loc='upper right', framealpha=0.8)
        ax.grid(True, alpha=0.2)
''')

# 2. procurement/calculator.py
write_file("procurement/__init__.py", "")
write_file("procurement/calculator.py", '''"""Satın Alma Toplam Maliyet Hesaplayıcı"""
from dataclasses import dataclass

@dataclass
class SupplierCost:
    name: str
    purchase_price: float = 0.0
    rework_cost: float = 0.0
    delay_cost: float = 0.0
    quality_cost: float = 0.0
    
    @property
    def total(self) -> float:
        return self.purchase_price + self.rework_cost + self.delay_cost + self.quality_cost

def compare_suppliers(a: SupplierCost, b: SupplierCost) -> tuple:
    if a.total < b.total:
        return a, b.total - a.total
    elif b.total < a.total:
        return b, a.total - b.total
    return None, 0.0
''')

# 3. database/procurement_guide.json
procurement_db = {
    "tr": {
        "title": "📊 Satın Alma Rehberi – Toplam Değer Yaklaşımı",
        "subtitle": "\"Çelik maliyet baskısı altında ayakta kalan satın alma kararları\"",
        "sections": {
            "lower_total_cost": {
                "title": "1. Daha Düşük Toplam Maliyet",
                "content": [
                    "Toplam Maliyet = Satın Alma Fiyatı + İşletme Maliyeti + Kalite Maliyeti + Gecikme Maliyeti",
                    "• Tedarikçi A: 100.000 TL + 20.000 TL yeniden işleme + 15.000 TL gecikme = 145.000 TL",
                    "• Tedarikçi B: 110.000 TL = daha ekonomik!"
                ]
            },
            "lower_project_risk": {
                "title": "2. Daha Düşük Proje Riski",
                "content": [
                    "Kalitesiz malzeme, tedarikçi iflası, teslimat gecikmesi riskleri.",
                    "Profesyonel ekipler tedarikçi geçmişini, sertifikaları, referansları inceler."
                ]
            },
            "on_time_delivery": {
                "title": "3. Zamanında Teslimat",
                "content": [
                    "Üretim hattı durduğunda maliyetler çok yüksektir.",
                    "%5 daha pahalı ama zamanında teslim eden tedarikçi tercih edilir."
                ]
            },
            "best_total_value": {
                "title": "4. En İyi Toplam Değer",
                "content": [
                    "En düşük fiyat ≠ En iyi satın alma kararı",
                    "Toplam değer: Fiyat + Kalite + Güvenilirlik + Teslimat + Destek + Risk"
                ]
            }
        },
        "calculator": {
            "title": "Toplam Maliyet Hesaplayıcı",
            "supplier_a": "Tedarikçi A",
            "supplier_b": "Tedarikçi B",
            "purchase_price": "Satın Alma Fiyatı",
            "rework_cost": "Yeniden İşleme",
            "delay_cost": "Gecikme",
            "quality_cost": "Kalite Kaybı",
            "total": "Gerçek Toplam"
        }
    },
    "en": {
        "title": "📊 Procurement Guide – Total Value Approach",
        "subtitle": "\"Procurement decisions that hold up under steel-cost pressure\"",
        "sections": {
            "lower_total_cost": {
                "title": "1. Lower Total Cost",
                "content": [
                    "Total Cost = Purchase Price + Operating Cost + Quality Cost + Delay Cost",
                    "• Supplier A: 100k + 20k rework + 15k delay = 145k",
                    "• Supplier B: 110k = more economical!"
                ]
            },
            "lower_project_risk": {
                "title": "2. Lower Project Risk",
                "content": [
                    "Risks: poor materials, supplier bankruptcy, delivery delays.",
                    "Professional teams examine history, certifications, references."
                ]
            },
            "on_time_delivery": {
                "title": "3. On-Time Delivery",
                "content": [
                    "When production stops, costs skyrocket.",
                    "Managers prefer 5% more expensive but on-time supplier."
                ]
            },
            "best_total_value": {
                "title": "4. Best Total Value",
                "content": [
                    "Lowest price ≠ Best decision",
                    "Value = Price + Quality + Reliability + Delivery + Support + Risk"
                ]
            }
        },
        "calculator": {
            "title": "Total Cost Calculator",
            "supplier_a": "Supplier A",
            "supplier_b": "Supplier B",
            "purchase_price": "Purchase Price",
            "rework_cost": "Rework",
            "delay_cost": "Delay",
            "quality_cost": "Quality Loss",
            "total": "True Total"
        }
    }
}
write_file("database/procurement_guide.json", json.dumps(procurement_db, indent=2, ensure_ascii=False))

print("\n" + "=" * 60)
print("🎉 TÜM EKSİKLER GİDERİLDİ!")
print("=" * 60)
print("\nŞimdi çalıştırın: python main.py")