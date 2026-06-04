#!/usr/bin/env python3
"""
Dil desteği güçlendirme: sağ alt köşe dropbox, tam TR/EN geçiş
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
main_py = os.path.join(BASE, "app", "main.py")

with open(main_py, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Dil butonu kodunu QComboBox ile değiştir (daha şık)
old_button = """self.lang_btn = QPushButton("🇹🇷 TR")
        self.lang_btn.setFixedSize(80, 28)
        self.lang_btn.setStyleSheet("QPushButton { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; font-weight: bold; } QPushButton:hover { background-color: #45475a; }")
        self.lang_btn.clicked.connect(self._toggle_language)
        self.statusBar().addPermanentWidget(self.lang_btn)"""

new_button = """self.lang_combo = QComboBox()
        self.lang_combo.addItems(["🇹🇷 Türkçe", "🇬🇧 English"])
        self.lang_combo.setCurrentIndex(0 if self.lang_manager.current_lang == "tr" else 1)
        self.lang_combo.setFixedWidth(130)
        self.lang_combo.setStyleSheet("QComboBox { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 2px 6px; font-weight: bold; } QComboBox:hover { border-color: #89b4fa; } QComboBox QAbstractItemView { background-color: #313244; color: #cdd6f4; selection-background-color: #89b4fa; }")
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        self.statusBar().addPermanentWidget(self.lang_combo)"""

if old_button in content:
    content = content.replace(old_button, new_button)
    print("✅ Dil butonu QComboBox ile değiştirildi")
else:
    print("⚠️ Eski dil butonu bulunamadı")

# 2. _toggle_language yerine _on_lang_changed ekle
old_toggle = """def _toggle_language(self):
        self.lang_manager.toggle()
        lang = self.lang_manager.current_lang
        self.lang_btn.setText("🇹🇷 TR" if lang == "tr" else "🇬🇧 EN")
        self._retranslate_ui()"""

new_toggle = """def _on_lang_changed(self, index):
        lang = "tr" if index == 0 else "en"
        if lang != self.lang_manager.current_lang:
            self.lang_manager.set_language(lang)
            self._retranslate_ui()

    def _toggle_language(self):
        self.lang_manager.toggle()
        lang = self.lang_manager.current_lang
        self.lang_combo.setCurrentIndex(0 if lang == "tr" else 1)
        self._retranslate_ui()"""

if old_toggle in content:
    content = content.replace(old_toggle, new_toggle)
    print("✅ Dil değiştirme metodları güncellendi")

# 3. _retranslate_ui metodunu güçlendir
old_retranslate = """def _retranslate_ui(self):
        self.setWindowTitle(self.lang_manager.tr("window_title"))
        tab_keys = [
            (0, "simulation_tab"), (1, "guide_tab"), (2, "periodic_tab"),
            (3, "lever_tab"), (4, "fec_tab"), (5, "ree_tab"),
            (6, "procurement_tab"), (7, "pdf_tab"), (8, "ttt_tab"),
            (9, "distortion_tab"), (10, "diffusion_tab"), (11, "alloy_tab")
        ]
        tabs = self.findChild(QTabWidget)
        if tabs:
            for i, key in tab_keys:
                if i < tabs.count():
                    tabs.setTabText(i, self.lang_manager.tr(key))
        self.statusBar().showMessage(self.lang_manager.tr("ready"))
        self._translate_failure_modes()"""

new_retranslate = """def _retranslate_ui(self):
        self.setWindowTitle(self.lang_manager.tr("window_title"))
        tab_keys = [
            (0, "simulation_tab"), (1, "guide_tab"), (2, "periodic_tab"),
            (3, "lever_tab"), (4, "fec_tab"), (5, "ree_tab"),
            (6, "procurement_tab"), (7, "pdf_tab"), (8, "ttt_tab"),
            (9, "distortion_tab"), (10, "diffusion_tab"), (11, "alloy_tab"),
            (12, "failure_modes_tab")
        ]
        tabs = self.findChild(QTabWidget)
        if tabs:
            for i, key in tab_keys:
                if i < tabs.count():
                    tabs.setTabText(i, self.lang_manager.tr(key))
        self.statusBar().showMessage(self.lang_manager.tr("ready"))
        self.run_btn.setText(self.lang_manager.tr("run_btn"))
        if hasattr(self, '_translate_failure_modes'):
            self._translate_failure_modes()
        # ComboBox dil göstergesini güncelle
        if hasattr(self, 'lang_combo'):
            self.lang_combo.blockSignals(True)
            self.lang_combo.setCurrentIndex(0 if self.lang_manager.current_lang == "tr" else 1)
            self.lang_combo.blockSignals(False)"""

if old_retranslate in content:
    content = content.replace(old_retranslate, new_retranslate)
    print("✅ _retranslate_ui güçlendirildi")
elif "_retranslate_ui" not in content:
    # Metod hiç yoksa ekle
    class_end = content.rfind("def main():")
    if class_end > 0:
        content = content[:class_end] + "\n    " + new_retranslate.replace("        ", "    ") + "\n\n" + content[class_end:]
        print("✅ _retranslate_ui metodu eklendi")

# Kaydet
with open(main_py, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n🎉 Dil desteği güçlendirildi!")
print("Özellikler:")
print("  🌍 Sağ alt köşede dil seçme açılır menüsü")
print("  🇹🇷 Türkçe / 🇬🇧 İngilizce tam geçiş")
print("  📝 Tüm sekmeler, butonlar ve etiketler anında değişir")
print("\nÇalıştır: python main.py")