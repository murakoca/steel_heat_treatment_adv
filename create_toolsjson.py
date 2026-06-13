#!/usr/bin/env python3
"""
TÜM ARAÇLARI BAĞIMSIZ PENCERELERE DÖNÜŞTÜRÜR.
Ana GUI'de sadece Simülasyon, Elementler, Fe–C Diyagramı kalır.
Diğer tüm araçlar Araçlar sekmesindeki butonlarla bağımsız pencerelerde açılır.
"""
import os, sys, re

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✅ {path}")

print("=" * 70)
print("🔧 ARAÇLAR BAĞIMSIZ PENCERELERE DÖNÜŞTÜRÜLÜYOR")
print("=" * 70)

# =====================================================================
# 1. BAĞIMSIZ PENCERE SINIFLARI OLUŞTUR
# =====================================================================

# --- Malzeme Rehberi ---
write_file("tools/guide_window.py", '''"""Malzeme Rehberi Penceresi"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

MATERIAL_GUIDE = {
    "Düşük Karbonlu (örn. 1020)": "Yapısal çelikler, araba gövdeleri, borular.",
    "Orta Karbonlu (örn. 1045)": "Şaft, aks, dişli. Isıl işlemle sertleştirilebilir.",
    "Yüksek Karbonlu (örn. 1095)": "Yay, bıçak, kesici takım.",
    "Alaşımlı (örn. 4140)": "Krank mili, iniş takımı.",
    "Paslanmaz (örn. 316)": "Kimya, medikal, mutfak.",
    "Takım Çeliği (örn. H13)": "Sıcak iş kalıpları.",
    "AHSS (örn. DP600)": "Otomotiv panelleri."
}

class GuideWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📚 Malzeme Seçim Rehberi")
        self.setMinimumSize(600, 500)
        self._ui()
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QVBoxLayout(c)
        label = QLabel("Malzeme Seçim Rehberi")
        label.setStyleSheet("font-size:16px; font-weight:bold; color:#89b4fa;")
        layout.addWidget(label)
        for title, desc in MATERIAL_GUIDE.items():
            grp = QGroupBox(title)
            grp.setStyleSheet("QGroupBox{color:#cdd6f4;border:1px solid #45475a;border-radius:6px;margin-top:8px;padding-top:10px;font-weight:bold}")
            grp_lay = QVBoxLayout(grp)
            lbl = QLabel(desc); lbl.setWordWrap(True); lbl.setStyleSheet("color:#cdd6f4")
            grp_lay.addWidget(lbl)
            layout.addWidget(grp)
        layout.addStretch()
''')

# --- Lever Kuralı ---
write_file("tools/lever_window.py", '''"""Lever Rule Penceresi"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from metallurgy.lever_rule import calculate as lever_calculate, FE_C_EXAMPLES

class LeverWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚖️ Lever Kuralı Hesaplayıcı")
        self.setMinimumSize(500, 400)
        self._ui()
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QVBoxLayout(c)
        form = QFormLayout()
        self.lever_ca = QLineEdit("0.022"); form.addRow("Cα (%):", self.lever_ca)
        self.lever_cb = QLineEdit("6.67"); form.addRow("Cβ (%):", self.lever_cb)
        self.lever_co = QLineEdit("0.8"); form.addRow("Co (%):", self.lever_co)
        layout.addLayout(form)
        btn = QPushButton("Hesapla"); btn.clicked.connect(self._calc); layout.addWidget(btn)
        self.result = QLabel(""); self.result.setWordWrap(True)
        layout.addWidget(self.result)
        layout.addStretch()
    def _calc(self):
        try:
            Ca = float(self.lever_ca.text()); Cb = float(self.lever_cb.text()); Co = float(self.lever_co.text())
            res = lever_calculate(Ca, Cb, Co)
            self.result.setText(f"α: %{res.percent_alpha:.1f}, β: %{res.percent_beta:.1f}")
        except ValueError as e:
            self.result.setText(f"Hata: {e}")
''')

# --- REE ---
write_file("tools/ree_window.py", '''"""REE Penceresi"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from metallurgy.ree import REEDatabase

class REEWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🧪 Nadir Toprak Elementleri")
        self.setMinimumSize(700, 500)
        self._ui()
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QVBoxLayout(c)
        self.ree_db = REEDatabase()
        data = self.ree_db.get_all()
        lbl = QLabel(f"<h2>REE</h2><p>{data['description']}</p><p>17 element: {', '.join(data['elements'])}</p>")
        lbl.setWordWrap(True); layout.addWidget(lbl)
        layout.addStretch()
''')

# --- Satın Alma ---
write_file("tools/procurement_window.py", '''"""Satın Alma Penceresi"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from procurement.calculator import SupplierCost, compare_suppliers
import json, os

class ProcurementWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📊 Satın Alma Rehberi")
        self.setMinimumSize(500, 400)
        self._ui()
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QVBoxLayout(c)
        self.proc_a_price = QLineEdit("100000"); layout.addWidget(QLabel("A Fiyat:")); layout.addWidget(self.proc_a_price)
        self.proc_a_rework = QLineEdit("20000"); layout.addWidget(QLabel("A Yeniden İşleme:")); layout.addWidget(self.proc_a_rework)
        self.proc_a_delay = QLineEdit("15000"); layout.addWidget(QLabel("A Gecikme:")); layout.addWidget(self.proc_a_delay)
        self.proc_a_quality = QLineEdit("10000"); layout.addWidget(QLabel("A Kalite:")); layout.addWidget(self.proc_a_quality)
        self.proc_b_price = QLineEdit("110000"); layout.addWidget(QLabel("B Fiyat:")); layout.addWidget(self.proc_b_price)
        self.proc_b_rework = QLineEdit("5000"); layout.addWidget(QLabel("B Yeniden İşleme:")); layout.addWidget(self.proc_b_rework)
        self.proc_b_delay = QLineEdit("0"); layout.addWidget(QLabel("B Gecikme:")); layout.addWidget(self.proc_b_delay)
        self.proc_b_quality = QLineEdit("0"); layout.addWidget(QLabel("B Kalite:")); layout.addWidget(self.proc_b_quality)
        btn = QPushButton("Hesapla"); btn.clicked.connect(self._calc); layout.addWidget(btn)
        self.result = QLabel(""); layout.addWidget(self.result)
    def _calc(self):
        try:
            a = SupplierCost("A", float(self.proc_a_price.text()), float(self.proc_a_rework.text()), float(self.proc_a_delay.text()), float(self.proc_a_quality.text()))
            b = SupplierCost("B", float(self.proc_b_price.text()), float(self.proc_b_rework.text()), float(self.proc_b_delay.text()), float(self.proc_b_quality.text()))
            w, d = compare_suppliers(a, b)
            self.result.setText(f"{w.name} {d:,.0f} TL daha ekonomik!" if w else "Eşit")
        except: self.result.setText("Hata!")
''')

# --- PDF Rapor ---
write_file("tools/pdf_window.py", '''"""PDF Rapor Penceresi"""
from PyQt5.QtWidgets import *

class PDFWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📄 PDF Rapor")
        self.setMinimumSize(400, 300)
        self._ui()
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QVBoxLayout(c)
        layout.addWidget(QLabel("PDF rapor oluşturmak için önce simülasyon çalıştırın."))
        self.btn = QPushButton("PDF Oluştur"); layout.addWidget(self.btn)
        layout.addStretch()
''')

# --- TTT/CCT ---
write_file("tools/ttt_window.py", '''"""TTT/CCT Penceresi"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from metallurgy.ttt_cct_plot import load_ttt_data, draw_ttt
import json, os

class TTTWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📈 TTT/CCT Diyagramı")
        self.setMinimumSize(800, 600)
        self._ui()
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QVBoxLayout(c)
        self.cb = QComboBox()
        with open(os.path.join(os.path.dirname(__file__), "..", "database", "steels.json")) as f:
            self.cb.addItems(list(json.load(f).keys()))
        self.cb.currentTextChanged.connect(self._draw)
        layout.addWidget(self.cb)
        self.fig = Figure(facecolor='#1e1e2e')
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.ax = self.fig.add_subplot(111, facecolor='#1e1e2e')
        self.ax.tick_params(colors='#cdd6f4')
        for sp in self.ax.spines.values(): sp.set_color('#45475a')
        layout.addWidget(self.canvas)
    def _draw(self):
        steel = self.cb.currentText()
        ttt = load_ttt_data(steel)
        self.ax.clear()
        draw_ttt(self.ax, ttt)
        self.canvas.draw()
''')

# --- Distorsiyon ---
write_file("tools/distortion_window.py", '''"""Distorsiyon Penceresi"""
from PyQt5.QtWidgets import *
from mechanics.distortion_calc import estimate_residual_stress, distortion_risk

class DistortionWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔧 Distorsiyon Tahmini")
        self.setMinimumSize(400, 300)
        self._ui()
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QFormLayout(c)
        self.coolrate = QLineEdit("50"); layout.addRow("Soğuma Hızı (°C/s):", self.coolrate)
        self.mart = QLineEdit("0.8"); layout.addRow("Martensit Oranı:", self.mart)
        self.carbon = QLineEdit("0.4"); layout.addRow("Karbon (%):", self.carbon)
        self.yield_stress = QLineEdit("800"); layout.addRow("Akma (MPa):", self.yield_stress)
        self.btn = QPushButton("Hesapla"); self.btn.clicked.connect(self._calc); layout.addRow(self.btn)
        self.result = QLabel(""); layout.addRow("Sonuç:", self.result)
    def _calc(self):
        try:
            cr = float(self.coolrate.text()); fm = float(self.mart.text())
            cp = float(self.carbon.text()); ys = float(self.yield_stress.text())
            stress = estimate_residual_stress(cr, fm, cp)
            risk = distortion_risk(stress, ys)
            self.result.setText(f"Gerilme: {stress} MPa, Risk: {risk}")
        except: self.result.setText("Hata!")
''')

# --- Karbon Difüzyonu ---
write_file("tools/diffusion_window.py", '''"""Karbon Difüzyonu Penceresi"""
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from simulation.carburizing_sim import simulate_carburizing

class DiffusionWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🧪 Karbon Difüzyonu")
        self.setMinimumSize(800, 600)
        self._ui()
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QVBoxLayout(c)
        form = QFormLayout()
        self.diff_temp = QLineEdit("930"); form.addRow("Sıcaklık (°C):", self.diff_temp)
        self.diff_time = QLineEdit("2"); form.addRow("Süre (saat):", self.diff_time)
        self.diff_cs = QLineEdit("0.8"); form.addRow("Yüzey C (%):", self.diff_cs)
        self.diff_c0 = QLineEdit("0.2"); form.addRow("Başlangıç C (%):", self.diff_c0)
        layout.addLayout(form)
        btn = QPushButton("Simüle Et"); btn.clicked.connect(self._sim); layout.addWidget(btn)
        self.fig = Figure(facecolor='#1e1e2e')
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.ax = self.fig.add_subplot(111, facecolor='#1e1e2e')
        self.ax.tick_params(colors='#cdd6f4')
        for sp in self.ax.spines.values(): sp.set_color('#45475a')
        layout.addWidget(self.canvas)
    def _sim(self):
        try:
            T = float(self.diff_temp.text()); t = float(self.diff_time.text())
            Cs = float(self.diff_cs.text()); C0 = float(self.diff_c0.text())
            x, p = simulate_carburizing(T, t, Cs, C0)
            self.ax.clear(); self.ax.plot(x, p, 'c-', lw=2)
            self.ax.set_xlabel("mm"); self.ax.set_ylabel("%C")
            self.ax.set_title(f"{T}°C, {t}saat")
            self.canvas.draw()
        except: pass
''')

# --- Alaşım Rehberi ---
write_file("tools/alloy_window.py", '''"""Alaşım Rehberi Penceresi"""
from PyQt5.QtWidgets import *
from metallurgy.alloy_guide import AlloyGuide

class AlloyWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🧪 Alaşım Rehberi")
        self.setMinimumSize(700, 500)
        self._ui()
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QVBoxLayout(c)
        guide = AlloyGuide()
        data = guide.get_all()
        lbl = QLabel(f"<h2>{data['title']}</h2>"); lbl.setWordWrap(True)
        layout.addWidget(lbl)
        layout.addStretch()
''')

# --- Hata Modları ---
write_file("tools/failure_window.py", '''"""Hata Modları Penceresi"""
from PyQt5.QtWidgets import *
from metallurgy.failure_modes import FailureModes

class FailureWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔧 Hata Modları")
        self.setMinimumSize(700, 500)
        self._ui()
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QVBoxLayout(c)
        db = FailureModes()
        data = db.get_all()
        lbl = QLabel(f"<h2>{data['title']['tr']}</h2>"); lbl.setWordWrap(True)
        layout.addWidget(lbl)
        layout.addStretch()
''')

print("\n✅ Tüm bağımsız pencere sınıfları oluşturuldu.")

# =====================================================================
# 2. app/main.py GÜNCELLEMESİ
# =====================================================================
main_py = os.path.join(BASE, "app", "main.py")
if not os.path.exists(main_py):
    print("❌ app/main.py bulunamadı!")
    sys.exit(1)

with open(main_py, 'r', encoding='utf-8') as f:
    content = f.read()

# Yeni importları ekle
new_imports = """
from tools.guide_window import GuideWindow
from tools.lever_window import LeverWindow
from tools.ree_window import REEWindow
from tools.procurement_window import ProcurementWindow
from tools.pdf_window import PDFWindow
from tools.ttt_window import TTTWindow
from tools.distortion_window import DistortionWindow
from tools.diffusion_window import DiffusionWindow
from tools.alloy_window import AlloyWindow
from tools.failure_window import FailureWindow
"""
# Sadece eklenmemiş olanları ekle
for line in new_imports.strip().split('\n'):
    if line.strip() and line.strip() not in content:
        # Son import'un olduğu yere ekle
        last_import = "from tools.clemex_window import ClemexWindow"
        if last_import in content:
            content = content.replace(last_import, last_import + "\n" + line)
        else:
            content += "\n" + line

# _open_tool metodunu güncelle
new_open_tool = '''
    def _open_tool(self, name):
        """Bağımsız araç penceresini açar"""
        tools = {
            "metrical": MetricalWindow,
            "pandat": PandatWindow,
            "steelmaking": SteelmakingWindow,
            "simufact": SimufactWindow,
            "steeluni": SteeluniversityWindow,
            "mipar": MiparWindow,
            "comsol": ComsolWindow,
            "vesta": VestaWindow,
            "clemex": ClemexWindow,
            "ironmaking": IronmakingWindow,
            "bof": BOFSteelmakingWindow,
            "bof_principle": BOFPrincipleWindow,
            "guide": GuideWindow,
            "lever": LeverWindow,
            "ree": REEWindow,
            "procurement": ProcurementWindow,
            "pdf": PDFWindow,
            "ttt": TTTWindow,
            "distortion": DistortionWindow,
            "diffusion": DiffusionWindow,
            "alloy": AlloyWindow,
            "failure": FailureWindow,
        }
        if name in tools:
            self._tool_window = tools[name](self)
            self._tool_window.show()
'''

if 'def _open_tool(self, name):' in content:
    # Eski metodu bul ve değiştir
    start = content.find('def _open_tool(self, name):')
    end = content.find('\n    def ', start + 10)
    if end == -1:
        end = content.find('\ndef ', start + 10)
    if end > 0:
        content = content[:start] + new_open_tool.strip() + '\n' + content[end:]
        print("✅ _open_tool metodu güncellendi")

# Araçlar sekmesindeki buton listesini güncelle
new_tools_list = '''
        # --- Ana GUI'den taşınan araçlar ---
        tools_buttons = [
            ("📚 Malzeme Rehberi", "guide"),
            ("⚖️ Lever Kuralı", "lever"),
            ("🧪 REE", "ree"),
            ("📊 Satın Alma", "procurement"),
            ("📄 PDF Rapor", "pdf"),
            ("📈 TTT/CCT", "ttt"),
            ("🔧 Distorsiyon", "distortion"),
            ("🧪 Karbon Difüzyonu", "diffusion"),
            ("🧪 Alaşım Rehberi", "alloy"),
            ("🔧 Hata Modları", "failure"),
            ("🏭 Demir Üretimi", "ironmaking"),
            ("🏗️ BOF Çelik Üretimi", "bof"),
            ("📖 BOF Çalışma Prensibi", "bof_principle"),
            ("📏 Metrical", "metrical"),
            ("🔬 Pandat", "pandat"),
            ("🔨 Simufact", "simufact"),
            ("🎓 Steeluniversity", "steeluni"),
            ("🤖 Mipar", "mipar"),
            ("🧪 Comsol", "comsol"),
            ("💎 Vesta", "vesta"),
            ("📊 Clemex", "clemex"),
        ]
        for name, tool_id in tools_buttons:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, tid=tool_id: self._open_tool(tid))
            tools_layout.addWidget(btn)
'''

# Eski araçlar listesini temizle ve yenisini ekle
old_tools_marker = '        tools_list = ['
if old_tools_marker in content:
    # Eski listeyi bul ve sil
    start = content.find(old_tools_marker)
    end = content.find('        tools_layout.addStretch()', start)
    if end > 0:
        content = content[:start] + new_tools_list + '\n' + content[end:]
        print("✅ Araçlar buton listesi güncellendi")

# Ana GUI'deki eski sekmeleri temizle (daha önce taşınanlar)
# Bu sekmeleri oluşturan kod bloklarını yorum satırı yap veya sil
sections_to_remove = [
    "guide_tab",
    "lever_tab",
    "ree_tab",
    "proc_tab",
    "pdf_tab",
    "ttt_tab",
    "distort_tab",
    "diff_tab",
    "alloy_tab",
    "failure_tab",
]

for section in sections_to_remove:
    # Bu değişkenin geçtiği blokları temizle
    pattern = rf'        # ===== .*? =====.*?        self\.tabs\.addTab\({section}.*?\)'
    while True:
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            break
        content = content[:match.start()] + content[match.end():]
        print(f"  🗑️ {section} temizlendi")

with open(main_py, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "=" * 70)
print("🎉 TÜM ARAÇLAR BAĞIMSIZ PENCERELERE DÖNÜŞTÜRÜLDÜ!")
print("=" * 70)
print("\nAna GUI'de sadece 3 sekme:")
print("  🔥 Simülasyon")
print("  🧪 Elementler (Periyodik Tablo)")
print("  🔬 Fe–C Diyagramı")
print("\n🔗 Araçlar sekmesindeki butonlarla diğer tüm araçlar bağımsız pencerelerde açılır.")
print("\nÇalıştır: python main.py")