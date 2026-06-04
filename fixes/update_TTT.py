#!/usr/bin/env python3
"""
FINAL UPGRADE v2.7
Adds: PDF report, TTT/CCT plotter, distortion calculator,
      carbon diffusion sim, web interface.
"""
import os, sys, json, shutil
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

def write_file(path, content):
    dirname = os.path.dirname(path)
    if dirname:                         # Boş değilse klasör oluştur
        os.makedirs(dirname, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✅ {path}")

def safe_backup(path):
    if os.path.exists(path):
        bak = path + f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(path, bak)
        print(f"  📦 Yedek: {bak}")
        return bak
    return None

print("="*60)
print("🚀 STEEL HEAT TREATMENT v2.7 UPGRADE")
print("="*60)

# =====================================================================
# 1. Güncel requirements.txt
# =====================================================================
req = """
PyQt5>=5.15
numpy>=1.20
scipy>=1.7
matplotlib>=3.5
pandas
pytest
fpdf
flask
"""
with open("requirements.txt", 'w') as f:
    f.write(req.strip())
print("✅ requirements.txt güncellendi (fpdf, flask eklendi)")

# =====================================================================
# 2. PDF Rapor Modülü
# =====================================================================
pdf_gen_code = '''"""PDF Rapor Üretici"""
from fpdf import FPDF
import os, datetime

def generate_pdf_report(sim_result, material, process_params, output_path="simulasyon_raporu.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Isil Islem Simulasyon Raporu", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Tarih: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.cell(0, 8, f"Malzeme: {material.name}", ln=True)
    pdf.cell(0, 8, f"Bilesim: {json.dumps(material.composition)}", ln=True)
    pdf.cell(0, 8, f"Proses: {process_params.get('process','')} / Sicaklik: {process_params.get('aust_temp','')}°C", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, "Faz Dagilimi:", ln=True)
    pdf.set_font("Arial", "", 11)
    for p in sim_result.phases:
        pdf.cell(0, 7, f"  {p.name}: %{p.fraction*100:.1f} - Sertlik: {p.hardness_hv:.0f} HV", ln=True)
    if sim_result.hardness:
        pdf.ln(3)
        pdf.cell(0, 7, f"Yuzey Sertligi: {sim_result.hardness.surface_hrc:.1f} HRC", ln=True)
        pdf.cell(0, 7, f"Merkez Sertligi: {sim_result.hardness.core_hrc:.1f} HRC", ln=True)
    pdf.output(output_path)
    return os.path.abspath(output_path)
'''
write_file("reports/pdf_generator.py", pdf_gen_code)

# =====================================================================
# 3. TTT/CCT Diyagram Çizici
# =====================================================================
ttt_cct_code = '''"""TTT / CCT Diyagram Çizimi"""
import numpy as np
import json, os

def load_ttt_data(steel_name):
    path = os.path.join(os.path.dirname(__file__), "..", "database", "ttt_data", f"{steel_name}_ttt.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def draw_ttt(ax, ttt_data):
    """TTT diyagramını çiz (basitleştirilmiş C-egrileri)"""
    if not ttt_data:
        ax.text(0.5, 0.5, "TTT verisi yok", transform=ax.transAxes, ha='center')
        return
    ps = ttt_data.get("pearlite_start")
    bs = ttt_data.get("bainite_start")
    Ms = ttt_data.get("Ms", 300)
    if ps:
        T = ps["T"]; t = ps["t"]
        ax.plot(t, T, 'b-o', lw=2, markersize=4, label='Perlit Başlangıcı')
    if bs:
        T = bs["T"]; t = bs["t"]
        ax.plot(t, T, 'r-s', lw=2, markersize=4, label='Beynit Başlangıcı')
    ax.axhline(Ms, color='orange', ls='--', lw=1.5, label=f'Ms = {Ms}°C')
    ax.set_xscale('log')
    ax.set_xlabel('Zaman (s)')
    ax.set_ylabel('Sıcaklık (°C)')
    ax.set_title('TTT Diyagramı')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(1, 1e4)
    ax.set_ylim(0, 900)
'''
write_file("metallurgy/ttt_cct_plot.py", ttt_cct_code)

# =====================================================================
# 4. Distorsiyon / Kalıntı Gerilme Hesaplayıcı
# =====================================================================
distortion_code = '''"""Basit Distorsiyon ve Kalıntı Gerilme Tahmini"""
def estimate_residual_stress(cooling_rate_C_per_s, martensite_fraction, carbon_pct=0.4):
    """Soğuma hızı ve martensit oranına bağlı yaklaşık kalıntı gerilme (MPa)"""
    base = 150  # MPa
    stress = base + 300 * martensite_fraction + 0.5 * cooling_rate_C_per_s * carbon_pct * 100
    return round(stress, 1)

def distortion_risk(residual_stress, yield_strength=800):
    """Kalıntı gerilme / akma dayanımı oranına göre risk seviyesi"""
    ratio = residual_stress / yield_strength
    if ratio < 0.3: return "Düşük"
    elif ratio < 0.6: return "Orta"
    else: return "Yüksek"
'''
write_file("mechanics/distortion_calc.py", distortion_code)

# =====================================================================
# 5. Web Arayüzü (Flask)
# =====================================================================
web_app_code = '''"""Web Tabanlı Isıl İşlem API ve Basit Arayüz"""
from flask import Flask, request, jsonify, render_template_string
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models.steel_model import Material
from heat_treatment.quenching import Quenching
from simulation.engine import SimulationEngine

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html><head><title>Isil Islem Simulasyonu</title>
<meta charset='utf-8'>
<style>
body { font-family:Arial; margin:40px; background:#1e1e2e; color:#cdd6f4; }
select, input, button { padding:8px; margin:5px; border-radius:5px; border:1px solid #45475a; background:#313244; color:#cdd6f4; }
.result { margin-top:20px; padding:15px; background:#313244; border-radius:8px; }
</style></head><body>
<h2>🔥 Isil Islem Simulasyonu</h2>
<form method='POST'>
    <label>Celik:</label>
    <select name='steel'>
        {% for s in steels %}
        <option value='{{s}}'>{{s}}</option>
        {% endfor %}
    </select><br>
    <label>Medya:</label>
    <select name='media'>
        <option>Oil</option><option>Water</option><option>Polymer</option><option>Brine</option>
    </select><br>
    <label>Sicaklik (°C):</label><input type='number' name='temp' value='850'><br>
    <button type='submit'>Simule Et</button>
</form>
{% if result %}
<div class='result'>
    <h3>Sonuc</h3>
    <p>{{ result }}</p>
</div>
{% endif %}
</body></html>
"""

def get_steels():
    import json
    with open(os.path.join(os.path.dirname(__file__), 'database', 'steels.json')) as f:
        return list(json.load(f).keys())

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        steel_name = request.form['steel']
        media = request.form['media']
        temp = float(request.form['temp'])
        mat = Material.from_database(steel_name)
        q = Quenching(mat, media, "moderate", temp)
        eng = SimulationEngine(q)
        res = eng.run()
        phases_str = ", ".join([f"{p['name']}: %{p['fraction']*100:.1f}" for p in res.phases])
        result = f"{mat.name} | Sertlik: {res.hardness.surface:.0f} HRC | Fazlar: {phases_str}"
    return render_template_string(HTML_TEMPLATE, steels=get_steels(), result=result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
'''
write_file("web_app.py", web_app_code)
print("✅ web_app.py (Flask) oluşturuldu")

# =====================================================================
# 6. Karbon Difüzyonu Simülatörü (GUI için sekme)
# =====================================================================
diffusion_sim_code = '''"""Karbon Difüzyonu Profil Simülasyonu"""
import numpy as np
from physics.diffusion import carbon_profile, carbon_diffusivity

def simulate_carburizing(T_celsius, time_hours, Cs, C0, depth_mm=5.0):
    """Karbon difüzyon profilini hesapla (yarı-sonsuz katı modeli)"""
    t_sec = time_hours * 3600
    D = carbon_diffusivity(T_celsius)
    x_mm = np.linspace(0, depth_mm, 200)
    x_m = x_mm / 1000.0
    profile = carbon_profile(x_m, t_sec, T_celsius, Cs/100, C0/100)
    return x_mm, profile * 100  # %C cinsinden döndür
'''
write_file("simulation/carburizing_sim.py", diffusion_sim_code)

# =====================================================================
# 7. app/main.py güncellemesi (yeni sekmeler ekle)
# =====================================================================
main_py = os.path.join(BASE, "app", "main.py")
if not os.path.exists(main_py):
    print("❌ app/main.py bulunamadı!")
    sys.exit(1)

safe_backup(main_py)
with open(main_py, 'r', encoding='utf-8') as f:
    content = f.read()

# 7a. Yeni importları ekle
new_imports = """
from reports.pdf_generator import generate_pdf_report
from metallurgy.ttt_cct_plot import load_ttt_data, draw_ttt
from mechanics.distortion_calc import estimate_residual_stress, distortion_risk
from simulation.carburizing_sim import simulate_carburizing
"""
if "from reports.pdf_generator import" not in content:
    # from procurement.calculator import ... satırından sonra ekle
    marker_import = "from procurement.calculator import SupplierCost, compare_suppliers"
    content = content.replace(marker_import, marker_import + new_imports)
    print("✅ Yeni importlar eklendi")

# 7b. Yeni sekmeleri _ui() metoduna ekle (en sona, "tabs.addTab(proc_tab..." sonrası)
new_tabs_code = '''
        # ===== PDF RAPOR SEKME =====
        pdf_tab = QWidget()
        pdf_layout = QVBoxLayout(pdf_tab)
        pdf_btn = QPushButton("📄 PDF Rapor Oluştur")
        pdf_btn.clicked.connect(self._generate_pdf_report)
        pdf_layout.addWidget(pdf_btn)
        self.pdf_status = QLabel("")
        pdf_layout.addWidget(self.pdf_status)
        pdf_layout.addStretch()
        tabs.addTab(pdf_tab, "📄 PDF Rapor")

        # ===== TTT/CCT DİYAGRAMI SEKME =====
        ttt_tab = QWidget()
        ttt_layout = QVBoxLayout(ttt_tab)
        ttt_mat_layout = QHBoxLayout()
        ttt_mat_layout.addWidget(QLabel("Çelik:"))
        self.ttt_steel_cb = QComboBox()
        self.ttt_steel_cb.addItems(self.steels)
        self.ttt_steel_cb.currentTextChanged.connect(self._draw_ttt_diagram)
        ttt_mat_layout.addWidget(self.ttt_steel_cb)
        ttt_mat_layout.addStretch()
        ttt_layout.addLayout(ttt_mat_layout)
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
        from matplotlib.figure import Figure
        ttt_fig = Figure(figsize=(8,6), facecolor='#1e1e2e')
        self.ttt_canvas = FigureCanvasQTAgg(ttt_fig)
        self.ttt_ax = ttt_fig.add_subplot(111, facecolor='#1e1e2e')
        self.ttt_ax.tick_params(colors='#cdd6f4')
        for sp in self.ttt_ax.spines.values(): sp.set_color('#45475a')
        ttt_layout.addWidget(self.ttt_canvas)
        tabs.addTab(ttt_tab, "📈 TTT/CCT")

        # ===== DİSTORSİYON SEKME =====
        distort_tab = QWidget()
        distort_layout = QFormLayout(distort_tab)
        self.distort_coolrate = QLineEdit("50")
        distort_layout.addRow("Soğuma Hızı (°C/s):", self.distort_coolrate)
        self.distort_mart = QLineEdit("0.8")
        distort_layout.addRow("Martensit Oranı (0-1):", self.distort_mart)
        self.distort_carbon = QLineEdit("0.4")
        distort_layout.addRow("Karbon (%)", self.distort_carbon)
        self.distort_yield = QLineEdit("800")
        distort_layout.addRow("Akma Dayanımı (MPa):", self.distort_yield)
        self.distort_btn = QPushButton("Hesapla")
        self.distort_btn.clicked.connect(self._calc_distortion)
        distort_layout.addRow(self.distort_btn)
        self.distort_result = QLabel("")
        distort_layout.addRow("Sonuç:", self.distort_result)
        tabs.addTab(distort_tab, "🔧 Distorsiyon")

        # ===== KARBON DİFÜZYONU SEKME =====
        diff_tab = QWidget()
        diff_layout = QVBoxLayout(diff_tab)
        diff_form = QFormLayout()
        self.diff_temp = QLineEdit("930")
        diff_form.addRow("Sıcaklık (°C):", self.diff_temp)
        self.diff_time = QLineEdit("2")
        diff_form.addRow("Süre (saat):", self.diff_time)
        self.diff_cs = QLineEdit("0.8")
        diff_form.addRow("Yüzey C pot. (%):", self.diff_cs)
        self.diff_c0 = QLineEdit("0.2")
        diff_form.addRow("Başlangıç C (%):", self.diff_c0)
        self.diff_depth = QLineEdit("5")
        diff_form.addRow("Maks. derinlik (mm):", self.diff_depth)
        diff_btn = QPushButton("Simüle Et")
        diff_btn.clicked.connect(self._simulate_diffusion)
        diff_form.addRow(diff_btn)
        diff_layout.addLayout(diff_form)
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
        from matplotlib.figure import Figure
        diff_fig = Figure(figsize=(8,4), facecolor='#1e1e2e')
        self.diff_canvas = FigureCanvasQTAgg(diff_fig)
        self.diff_ax = diff_fig.add_subplot(111, facecolor='#1e1e2e')
        self.diff_ax.tick_params(colors='#cdd6f4')
        for sp in self.diff_ax.spines.values(): sp.set_color('#45475a')
        diff_layout.addWidget(self.diff_canvas)
        tabs.addTab(diff_tab, "🧪 Karbon Difüzyonu")
'''

# "tabs.addTab(proc_tab, "📊 Satın Alma")" satırından sonra ekle
marker_tab = 'tabs.addTab(proc_tab, "📊 Satın Alma")'
if marker_tab in content:
    content = content.replace(marker_tab, marker_tab + "\n" + new_tabs_code)
    print("✅ Yeni sekmeler eklendi")
else:
    print("⚠️ Satın Alma sekmesi bulunamadı, sekmeler eklenemedi")

# 7c. Yeni metodları sınıfa ekle
new_methods_code = '''
    def _generate_pdf_report(self):
        if not hasattr(self, 'current_result') or not self.current_result:
            self.pdf_status.setText("Önce simülasyon çalıştırın.")
            return
        try:
            path = generate_pdf_report(self.current_result, Material.from_database(self.steel_cb.currentText()),
                                       {"process": self.proc_cb.currentText(), "aust_temp": getattr(self, 'aust_edit', None)})
            self.pdf_status.setText(f"Rapor oluşturuldu: {path}")
        except Exception as e:
            self.pdf_status.setText(f"Hata: {e}")

    def _draw_ttt_diagram(self):
        steel = self.ttt_steel_cb.currentText()
        ttt_data = load_ttt_data(steel)
        self.ttt_ax.clear()
        self.ttt_ax.tick_params(colors='#cdd6f4')
        for sp in self.ttt_ax.spines.values(): sp.set_color('#45475a')
        draw_ttt(self.ttt_ax, ttt_data)
        self.ttt_canvas.draw()

    def _calc_distortion(self):
        try:
            cr = float(self.distort_coolrate.text())
            fm = float(self.distort_mart.text())
            cp = float(self.distort_carbon.text())
            ys = float(self.distort_yield.text())
            stress = estimate_residual_stress(cr, fm, cp)
            risk = distortion_risk(stress, ys)
            self.distort_result.setText(f"Kalıntı Gerilme: {stress} MPa | Risk: {risk}")
        except ValueError:
            self.distort_result.setText("Geçersiz giriş.")

    def _simulate_diffusion(self):
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
            pass
'''

if '_generate_pdf_report' not in content:
    # _reset_fec metodundan sonra ekle
    marker_method = 'def _reset_fec(self):'
    if marker_method in content:
        content = content.replace(marker_method, new_methods_code + '\n    ' + marker_method)
        print("✅ Yeni metodlar eklendi")
    else:
        print("⚠️ _reset_fec bulunamadı, metodlar eklenemedi")

# Kaydet
with open(main_py, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n🎉 GÜNCELLEME TAMAMLANDI!")
print("="*60)
print("Eklenen özellikler:")
print("  📄 PDF Rapor sekmesi")
print("  📈 TTT/CCT Diyagramı sekmesi")
print("  🔧 Distorsiyon / Kalıntı Gerilme sekmesi")
print("  🧪 Karbon Difüzyonu sekmesi")
print("  🌐 Web arayüzü (web_app.py)")
print("\nÇalıştırmak için: python main.py")
print("Web arayüzü için: python web_app.py (port 5000)")
print("\nArdından Git'e push'layabilirsiniz.")