#!/usr/bin/env python3
"""
REE (Rare Earth Elements) modülü ve GUI sekmesi ekler
"""
import os, json

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("=" * 60)
print("🧪 REE MODÜLÜ EKLENİYOR")
print("=" * 60)

# =====================================================================
# 1. REE VERİTABANI
# =====================================================================
ree_data = {
    "description": "Nadir Toprak Elementleri (REE), 15 lantanit + skandiyum (Sc) ve itriyum (Y) olmak üzere 17 elementten oluşur. İsmine rağmen nispeten bol bulunurlar, ancak konsantre formda nadirdirler. Benzersiz manyetik, optik ve elektronik özellikleri nedeniyle ileri teknolojiler için kritiktir.",
    "elements": ["Sc","Y","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu"],
    "light_ree": ["La","Ce","Pr","Nd","Pm","Sm","Eu"],
    "heavy_ree": ["Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu","Sc","Y"],
    "minerals": [
        {"name": "Monazit", "formula": "(Ce,La,Nd,Th)PO₄", "type": "Fosfat"},
        {"name": "Bastnäsit", "formula": "(Ce,La,Y)CO₃F", "type": "Karbonat-florür"},
        {"name": "Ksenotim", "formula": "YPO₄", "type": "Fosfat (ağır REE)"},
        {"name": "Loparit", "formula": "(Ce,Na,Ca)(Ti,Nb)O₃", "type": "Oksit"}
    ],
    "extraction_steps": [
        "Kırma ve öğütme",
        "Köpük flotasyonu / gravite ayırma",
        "Asit/alkali liçi",
        "Çözücü ekstraksiyonu (SX) ile ayırma",
        "İyon değiştirme",
        "İndirgeme ve saflaştırma"
    ],
    "applications": {
        "Elektrikli Araç Motorları": {"elements": ["Nd","Dy","Pr"], "desc": "Yüksek mukavemetli kalıcı mıknatıslar"},
        "Rüzgar Türbinleri": {"elements": ["Nd","Dy"], "desc": "Verimli jeneratör mıknatısları"},
        "Akıllı Telefonlar": {"elements": ["Nd","Y","Eu","Tb"], "desc": "Hoparlör, titreşim, ekran fosforu"},
        "Savunma Sistemleri": {"elements": ["Sm","Gd","Dy"], "desc": "Radar, güdüm, lazer sistemleri"},
        "Katalitik Konvertörler": {"elements": ["Ce","La"], "desc": "Otomotiv emisyon kontrolü (%62 kullanım)"},
        "Cam Parlatma & Seramik": {"elements": ["Ce","La"], "desc": "Optik cam, lens parlatma (%9)"},
        "Petrol Rafinajı": {"elements": ["La","Ce"], "desc": "FCC katalizörleri (%13)"},
        "Fosforlar & Aydınlatma": {"elements": ["Eu","Tb","Y"], "desc": "LED, floresan lamba fosforu (%3)"},
    },
    "usage_distribution": {
        "Katalizör": 62,
        "Metalurji": 13,
        "Cam & Seramik": 9,
        "Mıknatıslar": 7,
        "Fosforlar": 3,
        "Diğer": 6
    },
    "separation_challenge": "REE'lerin kimyasal özellikleri birbirine çok benzediğinden, solvent ekstraksiyonu ile ayırma zor ve maliyetlidir. 99.99% saflık için yüzlerce aşama gerekebilir.",
    "top_producers": {
        "Çin": "~%70 (dünya üretimi)",
        "ABD": "~%15 (Mountain Pass)",
        "Avustralya": "~%8 (Lynas)",
        "Myanmar": "~%5"
    }
}

write_file("database/ree_data.json", json.dumps(ree_data, indent=2, ensure_ascii=False))
print("✅ database/ree_data.json")

# =====================================================================
# 2. REE MODÜLÜ
# =====================================================================
write_file("metallurgy/__init__.py", "")
write_file("metallurgy/ree.py", '''"""Nadir Toprak Elementleri Modülü"""
import json, os

class REEDatabase:
    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, "..", "database", "ree_data.json")
        with open(path, encoding='utf-8') as f:
            self.data = json.load(f)
    
    def get_all(self): return self.data
    def get_applications(self): return self.data["applications"]
    def get_usage_distribution(self): return self.data["usage_distribution"]
    def get_extraction_steps(self): return self.data["extraction_steps"]
    def get_minerals(self): return self.data["minerals"]
''')
print("✅ metallurgy/ree.py")

# =====================================================================
# 3. GUI'YE REE SEKMESİ EKLEME
# =====================================================================
main_py = os.path.join(BASE, "app", "main.py")
if not os.path.exists(main_py):
    print("❌ app/main.py bulunamadı!")
    exit(1)

with open(main_py, 'r', encoding='utf-8') as f:
    content = f.read()

# 3a. Import ekle
if "from metallurgy.ree import REEDatabase" not in content:
    old = "from metallurgy.lever_rule import"
    new = "from metallurgy.ree import REEDatabase\nfrom metallurgy.lever_rule import"
    if old in content:
        content = content.replace(old, new)
        print("✅ REE import eklendi")

# 3b. REE sekmesini Lever Rule sekmesinden sonra ekle
ree_tab_code = '''
        # ===== REE SEKMESI =====
        self.ree_db = REEDatabase()
        ree_data = self.ree_db.get_all()
        
        ree_tab = QWidget()
        ree_layout = QVBoxLayout(ree_tab)
        
        # Başlık
        title = QLabel("<h2>🧪 Nadir Toprak Elementleri (REE)</h2>")
        title.setWordWrap(True)
        ree_layout.addWidget(title)
        
        # Açıklama
        desc = QTextEdit()
        desc.setReadOnly(True)
        desc.setMaximumHeight(100)
        desc.setHtml(f"<p>{ree_data['description']}</p>"
                     f"<p><b>17 element:</b> {', '.join(ree_data['elements'])}</p>"
                     f"<p><b>Hafif REE:</b> {', '.join(ree_data['light_ree'])}</p>"
                     f"<p><b>Ağır REE:</b> {', '.join(ree_data['heavy_ree'])}</p>")
        ree_layout.addWidget(desc)
        
        # Sekme içinde alt sekmeler
        ree_tabs = QTabWidget()
        
        # --- Uygulamalar ---
        app_tab = QWidget()
        app_layout = QVBoxLayout(app_tab)
        apps = ree_data["applications"]
        for app_name, app_info in apps.items():
            grp = QGroupBox(f"📌 {app_name}")
            grp_lay = QVBoxLayout(grp)
            lbl = QLabel(f"<b>Elementler:</b> {', '.join(app_info['elements'])}<br>"
                        f"<b>Açıklama:</b> {app_info['desc']}")
            lbl.setWordWrap(True)
            grp_lay.addWidget(lbl)
            app_layout.addWidget(grp)
        app_layout.addStretch()
        ree_tabs.addTab(app_tab, "Uygulamalar")
        
        # --- Kullanım Dağılımı ---
        usage_tab = QWidget()
        usage_layout = QVBoxLayout(usage_tab)
        usage_lbl = QLabel("<h3>ABD Nadir Toprak Kullanımı</h3>")
        usage_layout.addWidget(usage_lbl)
        for sector, pct in ree_data["usage_distribution"].items():
            bar = QProgressBar()
            bar.setValue(pct)
            bar.setFormat(f"{sector}: %{pct}")
            usage_layout.addWidget(QLabel(sector))
            usage_layout.addWidget(bar)
        usage_layout.addStretch()
        ree_tabs.addTab(usage_tab, "Kullanım Dağılımı")
        
        # --- Mineraller ve Ekstraksiyon ---
        mineral_tab = QWidget()
        mineral_layout = QVBoxLayout(mineral_tab)
        mineral_layout.addWidget(QLabel("<h3>REE Mineralleri</h3>"))
        for m in ree_data["minerals"]:
            mineral_layout.addWidget(QLabel(f"• <b>{m['name']}</b>: {m['formula']} ({m['type']})"))
        mineral_layout.addWidget(QLabel("<br><h3>Ekstraksiyon Aşamaları</h3>"))
        for i, step in enumerate(ree_data["extraction_steps"], 1):
            mineral_layout.addWidget(QLabel(f"  {i}. {step}"))
        mineral_layout.addWidget(QLabel(f"<br><b>⚠️ Zorluk:</b> {ree_data['separation_challenge']}"))
        mineral_layout.addStretch()
        ree_tabs.addTab(mineral_tab, "Mineraller & İşleme")
        
        ree_layout.addWidget(ree_tabs)
        tabs.addTab(ree_tab, "🧪 REE")
'''

# Lever Rule sekmesinden sonra ekle
marker = 'tabs.addTab(lever_tab, "⚖️ Lever Kuralı")'
if marker in content:
    content = content.replace(marker, marker + "\n" + ree_tab_code)
    print("✅ REE sekmesi eklendi")
else:
    print("⚠️ Lever Rule sekmesi bulunamadı, REE sekmesi eklenemedi")

# Kaydet
with open(main_py, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "=" * 60)
print("🎉 REE modülü başarıyla eklendi!")
print("=" * 60)
print("Yeni sekme: 🧪 REE")
print("İçerik:")
print("  - REE tanımı ve 17 element listesi")
print("  - Uygulamalar (EV, rüzgar, telefon, savunma, katalizör)")
print("  - Kullanım dağılımı (progress bar)")
print("  - Mineraller ve ekstraksiyon aşamaları")
print("\nÇalıştır: python main.py")