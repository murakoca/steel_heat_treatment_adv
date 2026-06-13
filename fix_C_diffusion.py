#!/usr/bin/env python3
"""
GUI DÜZENLEME: Ana GUI'de sadece Simülasyon, Elementler, Fe-C Diyagramı kalsın.
Diğer tüm sekmeler Araçlar sekmesine buton olarak taşınsın.
"""
import os, re

BASE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(BASE, "app", "main.py")

with open(MAIN, 'r', encoding='utf-8') as f:
    content = f.read()

# Ana GUI'de tutulacak sekmeler (bunlara dokunma)
KEEP_TABS = [
    "simulation_tab",
    "periodic_tab", 
    "fec_tab"
]

# Araçlar sekmesine taşınacak sekmelerin isimleri ve buton callback'leri
TOOLS_TO_ADD = {
    "guide_tab": ("📚 Malzeme Rehberi", "self._show_guide"),
    "lever_tab": ("⚖️ Lever Kuralı", "self._show_lever"),
    "ree_tab": ("🧪 REE", "self._show_ree"),
    "procurement_tab": ("📊 Satın Alma", "self._show_procurement"),
    "pdf_tab": ("📄 PDF Rapor", "self._show_pdf"),
    "ttt_tab": ("📈 TTT/CCT", "self._show_ttt"),
    "distortion_tab": ("🔧 Distorsiyon", "self._show_distortion"),
    "diffusion_tab": ("🧪 Karbon Difüzyonu", "self._show_diffusion"),
    "alloy_tab": ("🧪 Alaşım Rehberi", "self._show_alloy"),
    "failure_modes_tab": ("🔧 Hata Modları", "self._show_failure"),
}

# 1. Ana GUI'deki sekmeleri sakla (sadece istenenler kalsın)
# _ui metodunun başlangıcını ve self.tabs = QTabWidget() satırını koru
# Her tabs.addTab satırını kontrol et, istenmeyenleri yoruma al

lines = content.split('\n')
new_lines = []
skip_until_tabs_end = False
in_tools_section = False

for line in lines:
    # Araçlar sekmesinin başladığını tespit et
    if 'tools_tab = QWidget()' in line or '# ===== ARAÇLAR' in line:
        in_tools_section = True
    
    # self.tabs.addTab satırlarını kontrol et
    if 'self.tabs.addTab(' in line or 'tabs.addTab(' in line:
        # Hangi sekme olduğunu bul
        tab_found = None
        for tab_key in TOOLS_TO_ADD.keys():
            if tab_key in line:
                tab_found = tab_key
                break
        
        if tab_found:
            # Bu sekmeyi ana GUI'den kaldır (yorum satırı yap)
            new_lines.append(f"        # {line.strip()}  # ARAÇLAR'a taşındı")
            continue
    
    new_lines.append(line)

content = '\n'.join(new_lines)

# 2. Araçlar sekmesine yeni butonlar ekle
tools_buttons = []
for tab_key, (name, callback) in TOOLS_TO_ADD.items():
    tools_buttons.append(f'            ("{name}", {callback}),')

tools_block = '''
        # --- Ana GUI\'den taşınan araçlar ---
        for name, callback in [\n''' + '\n'.join(tools_buttons) + '''\n        ]:
            btn = QPushButton(name)
            btn.clicked.connect(callback)
            tools_layout.addWidget(btn)
'''

# tools_layout.addStretch() satırından önce ekle
if 'tools_layout.addStretch()' in content:
    content = content.replace('tools_layout.addStretch()', tools_block + '\n        tools_layout.addStretch()')
    print("✅ Araçlar butonları eklendi")
else:
    print("⚠️ tools_layout.addStretch() bulunamadı")

# 3. Eksik callback metodlarını ekle
callbacks = '''
    def _show_guide(self):
        """Malzeme Rehberi'ni göster"""
        for i in range(self.tabs.count()):
            if 'Rehber' in self.tabs.tabText(i) or 'Guide' in self.tabs.tabText(i):
                self.tabs.setCurrentIndex(i)
                return

    def _show_lever(self):
        for i in range(self.tabs.count()):
            if 'Lever' in self.tabs.tabText(i):
                self.tabs.setCurrentIndex(i)
                return

    def _show_ree(self):
        for i in range(self.tabs.count()):
            if 'REE' in self.tabs.tabText(i):
                self.tabs.setCurrentIndex(i)
                return

    def _show_procurement(self):
        for i in range(self.tabs.count()):
            if 'Satın Alma' in self.tabs.tabText(i) or 'Procurement' in self.tabs.tabText(i):
                self.tabs.setCurrentIndex(i)
                return

    def _show_pdf(self):
        for i in range(self.tabs.count()):
            if 'PDF' in self.tabs.tabText(i):
                self.tabs.setCurrentIndex(i)
                return

    def _show_ttt(self):
        for i in range(self.tabs.count()):
            if 'TTT' in self.tabs.tabText(i):
                self.tabs.setCurrentIndex(i)
                return

    def _show_distortion(self):
        for i in range(self.tabs.count()):
            if 'Distorsiyon' in self.tabs.tabText(i) or 'Distortion' in self.tabs.tabText(i):
                self.tabs.setCurrentIndex(i)
                return

    def _show_diffusion(self):
        for i in range(self.tabs.count()):
            if 'Difüzyon' in self.tabs.tabText(i) or 'Diffusion' in self.tabs.tabText(i):
                self.tabs.setCurrentIndex(i)
                return

    def _show_alloy(self):
        for i in range(self.tabs.count()):
            if 'Alaşım' in self.tabs.tabText(i) or 'Alloy' in self.tabs.tabText(i):
                self.tabs.setCurrentIndex(i)
                return

    def _show_failure(self):
        for i in range(self.tabs.count()):
            if 'Hata' in self.tabs.tabText(i) or 'Failure' in self.tabs.tabText(i):
                self.tabs.setCurrentIndex(i)
                return
'''

if '_show_guide' not in content:
    main_pos = content.find('\ndef main():')
    if main_pos > 0:
        content = content[:main_pos] + callbacks + '\n' + content[main_pos:]
        print("✅ Callback metodları eklendi")
    else:
        print("⚠️ def main() bulunamadı")

with open(MAIN, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n🎉 GUI DÜZENLEMESİ TAMAMLANDI!")
print("Ana GUI'de sadece 3 sekme kaldı:")
print("  🔥 Simülasyon")
print("  🧪 Elementler (Periyodik Tablo)")
print("  🔬 Fe–C Diyagramı")
print("\nDiğer tüm araçlar '🔗 Araçlar' sekmesinde buton olarak yer alır.")
print("\nÇalıştır: python main.py")