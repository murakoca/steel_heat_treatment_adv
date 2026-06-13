#!/usr/bin/env python3
"""
Tüm arayüzü tamamen iki dilli hale getirir.
"""
import os, json

BASE = os.path.dirname(os.path.abspath(__file__))
MAIN_PY = os.path.join(BASE, "app", "main.py")
TRANS_PATH = os.path.join(BASE, "database", "translations.json")

# 1. translations.json'u güncelle
with open(TRANS_PATH, 'r', encoding='utf-8') as f:
    trans = json.load(f)

new_keys = {
    "element_info": {"tr": "Element Bilgisi", "en": "Element Info"},
    "alloy_effects": {"tr": "Alaşım Etkileri", "en": "Alloy Effects"},
    "lever_composition": {"tr": "Kompozisyon Değerleri", "en": "Composition Values"},
    "lever_result": {"tr": "Sonuç", "en": "Result"},
    "lever_ca": {"tr": "Cα (α fazı %):", "en": "Cα (α phase %):"},
    "lever_cb": {"tr": "Cβ (β fazı %):", "en": "Cβ (β phase %):"},
    "lever_co": {"tr": "Co (Genel %):", "en": "Co (Overall %):"},
    "lever_calculate": {"tr": "Hesapla", "en": "Calculate"},
    "lever_examples": {"tr": "--- Örnekler ---", "en": "--- Examples ---"},
    "fec_ready_material": {"tr": "📋 Hazır Malzeme Seç", "en": "📋 Select Material"},
    "fec_element_composition": {"tr": "🧪 Element Bileşimi (%)", "en": "🧪 Element Composition (%)"},
    "fec_temperature": {"tr": "🌡️ Sıcaklık (°C)", "en": "🌡️ Temperature (°C)"},
    "fec_phase_analysis": {"tr": "📊 Faz Analizi", "en": "📊 Phase Analysis"},
    "fec_reset": {"tr": "🔄 Varsayılana Dön", "en": "🔄 Reset to Default"},
    "fec_custom": {"tr": "--- Özel Bileşim ---", "en": "--- Custom Composition ---"},
    "ttt_steel": {"tr": "Çelik:", "en": "Steel:"},
    "distortion_cooling_rate": {"tr": "Soğuma Hızı (°C/s):", "en": "Cooling Rate (°C/s):"},
    "distortion_martensite": {"tr": "Martensit Oranı (0-1):", "en": "Martensite Fraction (0-1):"},
    "distortion_carbon": {"tr": "Karbon (%)", "en": "Carbon (%)"},
    "distortion_yield": {"tr": "Akma Dayanımı (MPa):", "en": "Yield Strength (MPa):"},
    "distortion_calculate": {"tr": "Hesapla", "en": "Calculate"},
    "distortion_result_label": {"tr": "Sonuç:", "en": "Result:"},
    "diffusion_temperature": {"tr": "Sıcaklık (°C):", "en": "Temperature (°C):"},
    "diffusion_time": {"tr": "Süre (saat):", "en": "Time (hours):"},
    "diffusion_cs": {"tr": "Yüzey C pot. (%):", "en": "Surface C pot. (%):"},
    "diffusion_c0": {"tr": "Başlangıç C (%):", "en": "Initial C (%):"},
    "diffusion_depth": {"tr": "Maks. derinlik (mm):", "en": "Max. depth (mm):"},
    "diffusion_simulate": {"tr": "Simüle Et", "en": "Simulate"},
    "pdf_generate": {"tr": "📄 PDF Rapor Oluştur", "en": "📄 Generate PDF Report"},
    "why_alloy": {"tr": "❓ NEDEN ALAŞIM ÇELİĞİ?", "en": "❓ WHY ALLOY STEEL?"},
    "click_element": {"tr": "Bir elemente tıklayın...", "en": "Click an element..."},
}

for key, val in new_keys.items():
    if key not in trans:
        trans[key] = val
        print(f"  + {key}")

with open(TRANS_PATH, 'w', encoding='utf-8') as f:
    json.dump(trans, f, indent=2, ensure_ascii=False)
print("✅ translations.json güncellendi")

# 2. app/main.py'deki sabit metinleri dinamik yap
with open(MAIN_PY, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    ('"Element Bilgisi"', 'self.lang_manager.tr("element_info")'),
    ('"Alaşım Etkileri"', 'self.lang_manager.tr("alloy_effects")'),
    ('"Kompozisyon Değerleri"', 'self.lang_manager.tr("lever_composition")'),
    ('"Sonuç"', 'self.lang_manager.tr("lever_result")'),
    ('"Cα (α fazı %):"', 'self.lang_manager.tr("lever_ca")'),
    ('"Cβ (β fazı %):"', 'self.lang_manager.tr("lever_cb")'),
    ('"Co (Genel %):"', 'self.lang_manager.tr("lever_co")'),
    ('"Hesapla"', 'self.lang_manager.tr("lever_calculate")'),
    ('"--- Örnekler ---"', 'self.lang_manager.tr("lever_examples")'),
    ('"📋 Hazır Malzeme Seç"', 'self.lang_manager.tr("fec_ready_material")'),
    ('"🧪 Element Bileşimi (%)"', 'self.lang_manager.tr("fec_element_composition")'),
    ('"🌡️ Sıcaklık (°C)"', 'self.lang_manager.tr("fec_temperature")'),
    ('"📊 Faz Analizi"', 'self.lang_manager.tr("fec_phase_analysis")'),
    ('"🔄 Varsayılana Dön"', 'self.lang_manager.tr("fec_reset")'),
    ('"--- Özel Bileşim ---"', 'self.lang_manager.tr("fec_custom")'),
    ('"Soğuma Hızı (°C/s):"', 'self.lang_manager.tr("distortion_cooling_rate")'),
    ('"Martensit Oranı (0-1):"', 'self.lang_manager.tr("distortion_martensite")'),
    ('"Akma Dayanımı (MPa):"', 'self.lang_manager.tr("distortion_yield")'),
    ('"Sıcaklık (°C):"', 'self.lang_manager.tr("diffusion_temperature")'),
    ('"Süre (saat):"', 'self.lang_manager.tr("diffusion_time")'),
    ('"Yüzey C pot. (%):"', 'self.lang_manager.tr("diffusion_cs")'),
    ('"Başlangıç C (%):"', 'self.lang_manager.tr("diffusion_c0")'),
    ('"Maks. derinlik (mm):"', 'self.lang_manager.tr("diffusion_depth")'),
    ('"Simüle Et"', 'self.lang_manager.tr("diffusion_simulate")'),
    ('"📄 PDF Rapor Oluştur"', 'self.lang_manager.tr("pdf_generate")'),
    ('"❓ NEDEN ALAŞIM ÇELİĞİ?"', 'self.lang_manager.tr("why_alloy")'),
    ('"Bir elemente tıklayın..."', 'self.lang_manager.tr("click_element")'),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"  ✓ {old[:40]}... -> {new[:40]}...")

# _retranslate_ui'yi güncelle (ek widget'ları da kapsasın)
old_retrans = '''        # Periyodik tablo bilgi paneli
        self.elem_info_lbl.setText("Bir elemente tıklayın..." if lang == "tr" else "Click an element...")'''

new_retrans = '''        # Periyodik tablo bilgi paneli
        self.elem_info_lbl.setText(self.lang_manager.tr("click_element"))'''

content = content.replace(old_retrans, new_retrans)

with open(MAIN_PY, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ app/main.py güncellendi")
print("\nŞimdi uygulamayı başlatın: python main.py")