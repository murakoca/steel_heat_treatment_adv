#!/usr/bin/env python3
"""Karbon difüzyonu butonunu ve metodunu düzeltir."""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(BASE, "app", "main.py")

with open(MAIN, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Buton bağlantısını ekle veya düzelt
old_btn_line = 'diff_btn = QPushButton(self.lang_manager.tr("diffusion_simulate"))'
new_btn_line = 'diff_btn = QPushButton(self.lang_manager.tr("diffusion_simulate"))\n        diff_btn.clicked.connect(self._simulate_diffusion)'

if old_btn_line in content and 'diff_btn.clicked.connect' not in content:
    content = content.replace(old_btn_line, new_btn_line)
    print("✅ Buton bağlantısı eklendi.")
else:
    print("ℹ️ Buton bağlantısı zaten var veya buton satırı bulunamadı.")

# 2. _simulate_diffusion metodunu güvenli hale getir
old_method = '''    def _simulate_diffusion(self):
        try:
            T = float(self.diff_temp.text())
            t_h = float(self.diff_time.text())
            Cs = float(self.diff_cs.text())
            C0 = float(self.diff_c0.text())
            depth = float(self.diff_depth.text())
            x_mm, profile = simulate_carburizing(T, t_h, Cs, C0, depth)
            self.diff_ax.clear()
            self.diff_ax.plot(x_mm, profile, 'c-', lw=2)
            self.diff_ax.set_xlabel("Derinlik (mm)"); self.diff_ax.set_ylabel("Karbon (%)")
            self.diff_ax.set_title("Karbon Profili")
            self.diff_ax.grid(True, alpha=0.3)
            self.diff_canvas.draw()
        except Exception as e:
            pass'''

new_method = '''    def _simulate_diffusion(self):
        """Karbon difüzyon profilini hesapla ve çiz"""
        try:
            T = float(self.diff_temp.text())
            t_h = float(self.diff_time.text())
            Cs = float(self.diff_cs.text())
            C0 = float(self.diff_c0.text())
            depth = float(self.diff_depth.text())
            x_mm, profile = simulate_carburizing(T, t_h, Cs, C0, depth)
            self.diff_ax.clear()
            self.diff_ax.plot(x_mm, profile, 'c-', lw=2)
            self.diff_ax.set_xlabel("Derinlik (mm)")
            self.diff_ax.set_ylabel("Karbon (%)")
            self.diff_ax.set_title("Karbon Profili")
            self.diff_ax.grid(True, alpha=0.3)
            self.diff_canvas.draw()
        except Exception as e:
            print(f"Difüzyon hatası: {e}")'''

if old_method in content:
    content = content.replace(old_method, new_method)
    print("✅ _simulate_diffusion metodu güncellendi.")
elif '_simulate_diffusion' not in content:
    # Metod hiç yok, sınıfın sonuna ekle
    class_end = content.rfind('\ndef main():')
    if class_end == -1:
        class_end = content.rfind('\nif __name__')
    if class_end > 0:
        content = content[:class_end] + '\n' + new_method + '\n' + content[class_end:]
        print("✅ _simulate_diffusion metodu sınıfa eklendi.")
else:
    print("ℹ️ _simulate_diffusion metodu zaten var ancak farklı biçimde.")

with open(MAIN, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n🎉 Düzeltme tamamlandı. Lütfen python main.py ile test edin.")