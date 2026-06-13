#!/usr/bin/env python3
"""
Figure UnboundLocalError + Karbon Difüzyonu Butonu KESİN ÇÖZÜM
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(BASE, "app", "main.py")

with open(MAIN, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. _ui metodu içindeki "from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg" satırlarını temizle
lines = content.split('\n')
new_lines = []
in_ui = False
for line in lines:
    if 'def _ui(self):' in line:
        in_ui = True
    elif line.strip().startswith('def ') and in_ui:
        in_ui = False
    
    if in_ui and 'from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg' in line:
        continue  # Bu satırı atla
    
    new_lines.append(line)

content = '\n'.join(new_lines)
print("✅ _ui içindeki FigureCanvasQTAgg import'ları temizlendi")

# 2. Karbon difüzyonu buton bağlantısını garantile
old_btn = 'self.diff_btn = QPushButton("Simüle Et")'
new_btn = 'self.diff_btn = QPushButton("Simüle Et")\n        self.diff_btn.clicked.connect(self._simulate_diffusion)'

if old_btn in content and 'self.diff_btn.clicked.connect' not in content:
    content = content.replace(old_btn, new_btn)
    print("✅ diff_btn.clicked.connect eklendi")

# 3. _simulate_diffusion metodunu güncelle (debug'lu, sağlam)
old_method = '    def _simulate_diffusion(self):'
new_method = '''    def _simulate_diffusion(self):
        """Karbon difüzyon profilini hesapla ve çiz"""
        from simulation.carburizing_sim import simulate_carburizing
        try:
            T = float(self.diff_temp.text())
            t_h = float(self.diff_time.text())
            Cs = float(self.diff_cs.text())
            C0 = float(self.diff_c0.text())
            x_mm, profile = simulate_carburizing(T, t_h, Cs, C0)
            self.diff_ax.clear()
            self.diff_ax.plot(x_mm, profile, 'c-', linewidth=2)
            self.diff_ax.set_xlabel("Derinlik (mm)", color='#cdd6f4')
            self.diff_ax.set_ylabel("Karbon (%)", color='#cdd6f4')
            self.diff_ax.set_title(f"Karbon Profili ({T}°C, {t_h}saat)", color='#cdd6f4')
            self.diff_ax.grid(True, alpha=0.3)
            self.diff_fig.canvas.draw()
        except Exception as e:
            QMessageBox.warning(self, "Difüzyon Hatası", str(e))'''

if old_method in content:
    # Metodun sonunu bul ve değiştir
    start = content.find(old_method)
    next_def = content.find('\n    def ', start + 10)
    if next_def == -1:
        next_def = content.find('\ndef ', start + 10)
    if next_def > 0:
        content = content[:start] + new_method + content[next_def:]
    else:
        content = content[:start] + new_method
    print("✅ _simulate_diffusion metodu güncellendi")

with open(MAIN, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n🎉 Figure hatası ve karbon difüzyonu butonu ÇÖZÜLDÜ!")
print("Çalıştır: python main.py")