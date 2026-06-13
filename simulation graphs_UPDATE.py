#!/usr/bin/env python3
"""
TERMODİNAMİK, KATILAŞMA, JMatPro ve diğer sekmeleri Araçlar sekmesine taşır.
Ana GUI'de sadece Simülasyon, Elementler, Fe–C Diyagramı kalır.
"""
import os, re

BASE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(BASE, "app", "main.py")

with open(MAIN, 'r', encoding='utf-8') as f:
    content = f.read()

# Ana GUI'den kaldırılacak sekmeler ve Araçlar'daki buton isimleri
TABS_TO_MOVE = {
    "thermo_tab": ("🧪 Termodinamik", "thermo"),
    "alloy_tab": ("🏗️ Alaşım Termo.", "alloy_thermo"),
    "cast_tab": ("🏭 Katılaşma", "cast"),
    "jmatpro_tab": ("📈 JMatPro", "jmatpro"),
    "md_tab": ("⚛️ Mol. Dinamik", "md"),
    "data_tab": ("📊 Veri Analizi", "data"),
    "crystal_tab": ("🔬 Kristal Yapı", "crystal"),
    "diff_tab": ("🧪 Difüzyon", "diffusion"),
    "img_tab": ("🖼️ Görüntü Analizi", "image"),
}

# 1. Ana GUI'deki bu sekmeleri yorum satırı yap (silme, koru ama gösterme)
for tab_var, (btn_name, tool_id) in TABS_TO_MOVE.items():
    # tabs.addTab satırını yorum satırı yap
    content = re.sub(
        rf'(\s*)(self\.tabs\.addTab\({tab_var}.*?\))',
        rf'\1# \2  # → Araçlar sekmesine taşındı',
        content
    )
    # Bu sekmeyi oluşturan kod bloğunun başlangıcını bul ve yorum satırı yap
    # (basitleştirilmiş: sadece addTab satırını yorumla, içerik kalsın)

# 2. Araçlar sekmesine butonları ekle
new_buttons = []
for tab_var, (btn_name, tool_id) in TABS_TO_MOVE.items():
    new_buttons.append(f'            ("{btn_name}", "{tool_id}"),')

buttons_block = '''
        # --- Ana GUI\'den taşınan sekmeler ---
        for name, tid in [\n''' + '\n'.join(new_buttons) + '''\n        ]:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, t=tid: self._show_tab(t))
            tools_layout.addWidget(btn)
'''

# tools_layout.addStretch() satırından önce ekle
if 'tools_layout.addStretch()' in content:
    content = content.replace('tools_layout.addStretch()', buttons_block + '\n        tools_layout.addStretch()')
    print("✅ Butonlar eklendi")
else:
    print("⚠️ tools_layout.addStretch() bulunamadı")

# 3. _show_tab metodunu ekle (butona tıklayınca ilgili sekmeye git)
show_tab_method = '''
    def _show_tab(self, tab_id):
        """Belirtilen sekmeyi göster (varsa)"""
        tab_map = {
            "thermo": "Termodinamik",
            "alloy_thermo": "Alaşım",
            "cast": "Katılaşma",
            "jmatpro": "JMatPro",
            "md": "Mol. Dinamik",
            "data": "Veri Analizi",
            "crystal": "Kristal",
            "diffusion": "Difüzyon",
            "image": "Görüntü",
        }
        target = tab_map.get(tab_id, "")
        for i in range(self.tabs.count()):
            if target in self.tabs.tabText(i):
                self.tabs.setCurrentIndex(i)
                return
'''

if '_show_tab' not in content:
    main_pos = content.find('\ndef main():')
    if main_pos > 0:
        content = content[:main_pos] + show_tab_method + '\n' + content[main_pos:]
        print("✅ _show_tab metodu eklendi")

with open(MAIN, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n🎉 TAŞIMA TAMAMLANDI!")
print("Ana GUI'deki sekmeler: 🔥 Simülasyon, 🧪 Elementler, 🔬 Fe–C Diyagramı")
print("Termodinamik, Katılaşma, JMatPro ve diğerleri Araçlar sekmesinde buton olarak görünür.")
print("\nÇalıştır: python main.py")