#!/usr/bin/env python3
"""
Paslanmaz Çelik Ailesi Eksik Kaliteleri Ekleme
- 303, 303Se, 201, 202, 317, 317L, 310, 314, 330, 403
- Süper östenitik, süper ferritik
"""
import json, os, shutil
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "database", "steels.json")
TTT_DIR = os.path.join(BASE, "database", "ttt_data")

# Yedek al
shutil.copy(DB_PATH, DB_PATH + f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
print("✅ steels.json yedeklendi")

# Mevcut veriyi yükle
with open(DB_PATH, 'r', encoding='utf-8') as f:
    db = json.load(f)

# Eklenecek yeni paslanmaz çelikler
new_steels = {
    "AISI_303": {
        "composition": {"C": 0.15, "Cr": 18.0, "Ni": 9.0, "S": 0.15, "Mn": 2.0, "Si": 1.0},
        "Ms": -100, "Mf": -200, "Ae1": 800, "Ae3": 1000,
        "category": "östenitik paslanmaz (işlenebilir)"
    },
    "AISI_303Se": {
        "composition": {"C": 0.15, "Cr": 18.0, "Ni": 9.0, "Se": 0.15, "Mn": 2.0, "Si": 1.0},
        "Ms": -100, "Mf": -200, "Ae1": 800, "Ae3": 1000,
        "category": "östenitik paslanmaz (işlenebilir, Se'li)"
    },
    "AISI_201": {
        "composition": {"C": 0.15, "Mn": 7.5, "Ni": 5.0, "Cr": 17.0, "N": 0.25, "Si": 1.0},
        "Ms": -50, "Mf": -150, "Ae1": 750, "Ae3": 950,
        "category": "östenitik paslanmaz (yüksek Mn, düşük Ni)"
    },
    "AISI_202": {
        "composition": {"C": 0.15, "Mn": 10.0, "Ni": 5.0, "Cr": 18.0, "N": 0.25, "Si": 1.0},
        "Ms": -60, "Mf": -160, "Ae1": 750, "Ae3": 950,
        "category": "östenitik paslanmaz (yüksek Mn, düşük Ni)"
    },
    "AISI_317": {
        "composition": {"C": 0.08, "Cr": 19.0, "Ni": 13.0, "Mo": 3.5, "Mn": 2.0, "Si": 1.0},
        "Ms": -120, "Mf": -220, "Ae1": 810, "Ae3": 1010,
        "category": "östenitik paslanmaz (yüksek Mo)"
    },
    "AISI_317L": {
        "composition": {"C": 0.03, "Cr": 19.0, "Ni": 13.0, "Mo": 3.5, "Mn": 2.0, "Si": 1.0},
        "Ms": -120, "Mf": -220, "Ae1": 810, "Ae3": 1010,
        "category": "östenitik paslanmaz (yüksek Mo, düşük C)"
    },
    "AISI_310": {
        "composition": {"C": 0.25, "Cr": 25.0, "Ni": 20.0, "Mn": 2.0, "Si": 1.5},
        "Ms": -80, "Mf": -180, "Ae1": 850, "Ae3": 1050,
        "category": "östenitik paslanmaz (yüksek sıcaklık)"
    },
    "AISI_314": {
        "composition": {"C": 0.25, "Cr": 25.0, "Ni": 20.0, "Si": 2.5, "Mn": 2.0},
        "Ms": -80, "Mf": -180, "Ae1": 850, "Ae3": 1050,
        "category": "östenitik paslanmaz (yüksek Si, yüksek sıcaklık)"
    },
    "AISI_330": {
        "composition": {"C": 0.08, "Cr": 19.0, "Ni": 35.0, "Mn": 2.0, "Si": 1.0},
        "Ms": -100, "Mf": -200, "Ae1": 850, "Ae3": 1050,
        "category": "östenitik paslanmaz (çok yüksek Ni)"
    },
    "AISI_403": {
        "composition": {"C": 0.15, "Cr": 12.5, "Mn": 1.0, "Si": 0.5},
        "Ms": 350, "Mf": 200, "Ae1": 820, "Ae3": 950,
        "category": "martensitik paslanmaz"
    },
    "Super_Austenitic_254SMO": {
        "composition": {"C": 0.02, "Cr": 20.0, "Ni": 18.0, "Mo": 6.0, "N": 0.20, "Cu": 0.7, "Mn": 1.0},
        "Ms": -150, "Mf": -250, "Ae1": 850, "Ae3": 1050,
        "category": "süper östenitik paslanmaz"
    },
    "Super_Ferritic_446": {
        "composition": {"C": 0.20, "Cr": 27.0, "Mo": 1.5, "Mn": 1.5, "Si": 1.0, "N": 0.04},
        "Ms": 200, "Mf": 50, "Ae1": 850, "Ae3": 1000,
        "category": "süper ferritik paslanmaz"
    }
}

added = 0
for name, props in new_steels.items():
    if name not in db:
        db[name] = {
            "composition": props["composition"],
            "Ms": props["Ms"],
            "Mf": props["Mf"],
            "Ae1": props["Ae1"],
            "Ae3": props["Ae3"],
            "category": props.get("category", "")
        }
        added += 1
        print(f"  ✅ {name} eklendi ({props['category']})")
    else:
        print(f"  ⏭️ {name} zaten var")

with open(DB_PATH, 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print(f"\n➕ {added} yeni paslanmaz çelik eklendi. Toplam: {len(db)}")

# TTT verilerini oluştur (basit tahmini)
os.makedirs(TTT_DIR, exist_ok=True)
for name in new_steels:
    ttt_file = os.path.join(TTT_DIR, f"{name}_ttt.json")
    if not os.path.exists(ttt_file):
        ttt_data = {
            "pearlite_start": {"T": [800, 750, 700], "t": [100, 300, 1000]},
            "bainite_start": {"T": [500, 450, 400], "t": [500, 400, 800]},
            "Ms": new_steels[name]["Ms"]
        }
        with open(ttt_file, 'w') as f:
            json.dump(ttt_data, f, indent=2)
        print(f"  📊 TTT oluşturuldu: {name}")