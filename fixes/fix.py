#!/usr/bin/env python3
"""
DEBUG & FIX – Eksik modülleri oluşturur, hata varsa gösterir.
"""
import os, sys, traceback

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

print("=" * 60)
print("📍 Proje konumu:", BASE)
print("=" * 60)

# 1. Eksik klasörleri oluştur
def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# part/
if not os.path.exists("part/geometry.py"):
    write_file("part/__init__.py", "")
    write_file("part/geometry.py", "from dataclasses import dataclass\nimport math\n@dataclass\nclass Cylinder:\n    diameter_mm: float = 25.0\n    length_mm: float = 100.0\n@dataclass\nclass Plate:\n    thickness_mm: float = 10.0\n    width_mm: float = 50.0\n    length_mm: float = 100.0\n")
    print("✅ part/geometry.py oluşturuldu")

# furnace/
if not os.path.exists("furnace/profile.py"):
    write_file("furnace/__init__.py", "")
    write_file("furnace/profile.py", "class FurnaceProfile:\n    def __init__(self):\n        self.segments = []\n    def add_segment(self, t_min, T_C):\n        self.segments.append((t_min*60, T_C))\n    def get_temperature(self, t_s):\n        if not self.segments: return 850.0\n        for t_end, T in self.segments:\n            if t_s <= t_end: return T\n        return self.segments[-1][1]\n")
    print("✅ furnace/profile.py oluşturuldu")

# reports/
if not os.path.exists("reports/report_generator.py"):
    write_file("reports/__init__.py", "")
    write_file("reports/report_generator.py", "def generate_html_report(result, material, process, output_path='report.html'):\n    return output_path\n")
    print("✅ reports/report_generator.py oluşturuldu")

# periodic/
if not os.path.exists("periodic/table.py"):
    write_file("periodic/__init__.py", "")
    write_file("periodic/table.py", '''"""Periyodik Tablo Modülü"""
import json, os

class PeriodicTable:
    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        db = os.path.join(base, "..", "database")
        with open(os.path.join(db, "periodic_table.json"), encoding='utf-8') as f:
            self.elements = json.load(f)
        with open(os.path.join(db, "steel_element_effects.json"), encoding='utf-8') as f:
            self.steel_effects = json.load(f)
        with open(os.path.join(db, "element_interactions.json"), encoding='utf-8') as f:
            self.interactions = json.load(f)
        with open(os.path.join(db, "element_categories.json"), encoding='utf-8') as f:
            cat = json.load(f)
            self.categories = cat["categories"]
            self.element_cat = cat["element_cat"]

    def get(self, num):
        return self.elements.get(str(num))

    def get_effect(self, sym):
        return self.steel_effects.get(sym)

    def get_interactions(self, sym):
        return [i for i in self.interactions if sym in i["pair"]]

    def get_color(self, num):
        cat = self.element_cat.get(str(num), "bilinmeyen")
        return self.categories.get(cat, "#666666")
''')
    print("✅ periodic/table.py oluşturuldu")

# metallurgy/lever_rule.py
if not os.path.exists("metallurgy/lever_rule.py"):
    write_file("metallurgy/lever_rule.py", '''"""Kaldıraç Kuralı"""
from dataclasses import dataclass

@dataclass
class LeverResult:
    fraction_alpha: float = 0.0
    fraction_beta: float = 0.0
    @property
    def percent_alpha(self): return self.fraction_alpha * 100
    @property
    def percent_beta(self): return self.fraction_beta * 100

def calculate(Ca, Cb, Co):
    if abs(Cb - Ca) < 1e-10:
        raise ValueError("Faz kompozisyonları aynı olamaz")
    f_alpha = max(0.0, min(1.0, (Cb - Co) / (Cb - Ca)))
    f_beta = 1.0 - f_alpha
    return LeverResult(fraction_alpha=f_alpha, fraction_beta=f_beta)

FE_C_EXAMPLES = {
    "Ötektoid (0.8% C)": {"Ca": 0.022, "Cb": 6.67, "Co": 0.8},
    "Ötektoid Altı (0.4% C)": {"Ca": 0.022, "Cb": 6.67, "Co": 0.4},
    "Cu-Ni (30% Ni)": {"Ca": 25, "Cb": 40, "Co": 30},
}
''')
    print("✅ metallurgy/lever_rule.py oluşturuldu")

# 2. Şimdi main'i çağır ve hatayı yakala
print("\n" + "=" * 60)
print("🚀 Uygulama başlatılıyor...")
print("=" * 60)

try:
    from app.main import main
    main()
except Exception as e:
    print("\n" + "!" * 60)
    print("HATA OLUŞTU:")
    traceback.print_exc()
    print("!" * 60)
    input("Devam etmek için Enter'a basın...")