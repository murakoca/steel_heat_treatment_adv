"""Demir Üretimi (Ironmaking) Simülasyon Penceresi"""
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from simulation.ironmaking_sim import (
    calculate_reduction_steps,
    calculate_heat_zones,
    calculate_hot_metal,
    calculate_slag,
    calculate_fuel_rate,
    hydrogen_reduction_feasibility,
)


class IronmakingWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🏭 Demir Üretimi Simülasyonu (Ironmaking)")
        self.setMinimumSize(1100, 800)
        self._ui()
        self._load_style()

    def _load_style(self):
        self.setStyleSheet("""
            QMainWindow { background: #1e1e2e; }
            QLabel { color: #cdd6f4; }
            QGroupBox { color: #cdd6f4; border: 1px solid #45475a; border-radius: 6px; margin-top: 12px; padding-top: 14px; font-weight: bold; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 6px; color: #89b4fa; background: #1e1e2e; }
            QPushButton { background: #89b4fa; color: #1e1e2e; border-radius: 4px; padding: 8px 16px; font-weight: bold; }
            QPushButton:hover { background: #74c7ec; }
            QLineEdit, QComboBox, QDoubleSpinBox { background: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 5px; }
            QTextEdit { background: #313244; color: #cdd6f4; border: 1px solid #45475a; }
            QTabWidget::pane { border: 1px solid #45475a; background: #1e1e2e; }
            QTabBar::tab { background: #313244; color: #a6adc8; padding: 8px 16px; margin-right: 2px; border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background: #45475a; color: #89b4fa; }
        """)

    def _ui(self):
        c = QWidget()
        self.setCentralWidget(c)
        main_layout = QVBoxLayout(c)

        # Üst Panel – Parametreler
        top = QGroupBox("Yüksek Fırın Parametreleri")
        top_layout = QHBoxLayout(top)

        # Cevher girişi
        ore_group = QGroupBox("Cevher Şarjı")
        ore_layout = QFormLayout(ore_group)
        self.ore_input = QDoubleSpinBox()
        self.ore_input.setRange(100, 10000)
        self.ore_input.setValue(1000)
        self.ore_input.setSuffix(" ton")
        ore_layout.addRow("Cevher Miktarı:", self.ore_input)
        self.fe_pct = QDoubleSpinBox()
        self.fe_pct.setRange(30, 70)
        self.fe_pct.setValue(62)
        self.fe_pct.setSuffix(" % Fe")
        ore_layout.addRow("Cevher Tenörü:", self.fe_pct)
        top_layout.addWidget(ore_group)

        # İşletme parametreleri
        proc_group = QGroupBox("İşletme Parametreleri")
        proc_layout = QFormLayout(proc_group)
        self.coke_rate = QDoubleSpinBox()
        self.coke_rate.setRange(200, 800)
        self.coke_rate.setValue(450)
        self.coke_rate.setSuffix(" kg/tHM")
        proc_layout.addRow("Kok Oranı:", self.coke_rate)
        self.blast_temp = QDoubleSpinBox()
        self.blast_temp.setRange(800, 1400)
        self.blast_temp.setValue(1200)
        self.blast_temp.setSuffix(" °C")
        proc_layout.addRow("Sıcak Hava Sıcaklığı:", self.blast_temp)
        self.flux_rate = QDoubleSpinBox()
        self.flux_rate.setRange(50, 400)
        self.flux_rate.setValue(200)
        self.flux_rate.setSuffix(" kg/tHM")
        proc_layout.addRow("Flaks (CaO) Oranı:", self.flux_rate)
        top_layout.addWidget(proc_group)

        # Butonlar
        btn_group = QGroupBox("Simülasyon")
        btn_layout = QVBoxLayout(btn_group)
        self.btn_calc = QPushButton("🏭 Simülasyonu Çalıştır")
        self.btn_calc.clicked.connect(self._run_simulation)
        btn_layout.addWidget(self.btn_calc)
        self.btn_h2 = QPushButton("🟢 H₂ İndirgeme Fizibilitesi")
        self.btn_h2.clicked.connect(self._run_h2_feasibility)
        btn_layout.addWidget(self.btn_h2)
        top_layout.addWidget(btn_group)
        main_layout.addWidget(top)

        # Alt sekmeler
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Sekme 1: Sıcaklık Bölgeleri
        self.fig_zone = Figure(figsize=(10, 5), facecolor='#1e1e2e')
        self.canvas_zone = FigureCanvasQTAgg(self.fig_zone)
        self.ax_zone = self.fig_zone.add_subplot(111, facecolor='#1e1e2e')
        self.ax_zone.tick_params(colors='#cdd6f4')
        for sp in self.ax_zone.spines.values():
            sp.set_color('#45475a')
        self.tabs.addTab(self.canvas_zone, "🌡️ Sıcaklık Bölgeleri")

        # Sekme 2: İndirgenme Basamakları
        self.fig_red = Figure(figsize=(10, 5), facecolor='#1e1e2e')
        self.canvas_red = FigureCanvasQTAgg(self.fig_red)
        self.ax_red = self.fig_red.add_subplot(111, facecolor='#1e1e2e')
        self.ax_red.tick_params(colors='#cdd6f4')
        for sp in self.ax_red.spines.values():
            sp.set_color('#45475a')
        self.tabs.addTab(self.canvas_red, "⚗️ İndirgenme Basamakları")

        # Sekme 3: Sonuç Raporu
        self.report = QTextEdit()
        self.report.setReadOnly(True)
        self.tabs.addTab(self.report, "📊 Sonuç Raporu")

        self.statusBar().showMessage("Hazır – Parametreleri girin ve simülasyonu çalıştırın.")

    # -----------------------------------------------------------------
    # SİMÜLASYON METODLARI
    # -----------------------------------------------------------------
    def _run_simulation(self):
        """Ana demir üretimi simülasyonu"""
        ore_tons = self.ore_input.value()
        fe_pct = self.fe_pct.value()
        coke_rate = self.coke_rate.value()
        blast_temp = self.blast_temp.value()
        flux_rate = self.flux_rate.value()

        # Hesaplamalar
        hot_metal = calculate_hot_metal(ore_tons, fe_pct)
        zones = calculate_heat_zones(blast_temp)
        reduction = calculate_reduction_steps(fe_pct)
        slag = calculate_slag(flux_rate, ore_tons, fe_pct)
        fuel = calculate_fuel_rate(coke_rate, blast_temp)

        # --- Sıcaklık Bölgeleri Grafiği ---
        self.ax_zone.clear()
        zone_names = ["Boğaz\n(Throat)", "Stack", "Koheziv\nBölge", "Bosh", "Ocak\n(Hearth)"]
        y_bottom = [200, 400, 1100, 1400, 1800]
        y_top = [400, 900, 1400, 1800, 2200]
        colors = ['#a6e3a1', '#74c7ec', '#f9e2af', '#fab387', '#f38ba8']
        for i, (name, yb, yt, col) in enumerate(zip(zone_names, y_bottom, y_top, colors)):
            self.ax_zone.bar(i, yt - yb, bottom=yb, color=col, edgecolor='white', linewidth=1)
            self.ax_zone.text(i, (yb + yt) / 2, name, ha='center', va='center', fontsize=9,
                              color='#1e1e2e', fontweight='bold')
        self.ax_zone.set_xticks([])
        self.ax_zone.set_ylabel("Sıcaklık (°C)", color='#cdd6f4')
        self.ax_zone.set_title("Yüksek Fırın Sıcaklık Bölgeleri", color='#cdd6f4')
        self.ax_zone.set_ylim(0, 2300)
        self.ax_zone.grid(True, alpha=0.2, axis='y')
        self.canvas_zone.draw()

        # --- İndirgenme Basamakları Grafiği ---
        self.ax_red.clear()
        steps = ["Fe₂O₃", "Fe₃O₄", "FeO", "Fe"]
        values = [100, reduction['fe3o4_pct'], reduction['feo_pct'], reduction['fe_pct']]
        bar_colors = ['#f38ba8', '#fab387', '#f9e2af', '#a6e3a1']
        self.ax_red.bar(steps, values, color=bar_colors, edgecolor='white', linewidth=1)
        for i, v in enumerate(values):
            self.ax_red.text(i, v + 1, f"%{v:.1f}", ha='center', color='#cdd6f4', fontsize=10)
        self.ax_red.set_ylabel("Oran (%)", color='#cdd6f4')
        self.ax_red.set_title("Cevherin İndirgenme Basamakları", color='#cdd6f4')
        self.ax_red.grid(True, alpha=0.2, axis='y')
        self.canvas_red.draw()

        # --- Sonuç Raporu ---
        self.report.setHtml(f"""
        <h2>🏭 Demir Üretimi Simülasyon Raporu</h2>
        <table border='1' cellpadding='6' style='border-collapse:collapse; width:100%; color:#cdd6f4;'>
        <tr style='background:#45475a;'><td><b>Parametre</b></td><td><b>Değer</b></td></tr>
        <tr><td>Cevher Miktarı</td><td>{ore_tons:.0f} ton</td></tr>
        <tr><td>Cevher Tenörü</td><td>%{fe_pct:.1f} Fe</td></tr>
        <tr><td>Kok Oranı</td><td>{coke_rate:.0f} kg/tHM</td></tr>
        <tr><td>Sıcak Hava Sıcaklığı</td><td>{blast_temp:.0f} °C</td></tr>
        <tr><td>Flaks (CaO) Oranı</td><td>{flux_rate:.0f} kg/tHM</td></tr>
        <tr style='background:#313244;'><td colspan='2'><b>Üretim Sonuçları</b></td></tr>
        <tr><td>Sıcak Metal (Pik Demir)</td><td>{hot_metal['total']:.0f} ton</td></tr>
        <tr><td>Sıcak Metal Bileşimi</td><td>Fe: %{hot_metal['Fe']:.1f}, C: %{hot_metal['C']:.1f}, Si: %{hot_metal['Si']:.1f}, Mn: %{hot_metal['Mn']:.1f}</td></tr>
        <tr><td>Cüruf Miktarı</td><td>{slag['amount']:.0f} kg</td></tr>
        <tr><td>Cüruf Bileşimi (CaSiO₃)</td><td>{slag['casio3']:.0f} kg</td></tr>
        <tr><td>Verimlilik</td><td>{fuel['productivity']:.2f} tHM/m³/gün</td></tr>
        <tr><td>Tepe Gazı Enerjisi</td><td>{fuel['top_gas_energy']:.0f} MJ/tHM</td></tr>
        <tr><td>Toplam Yakıt Oranı</td><td>{fuel['total_fuel_rate']:.0f} kg/tHM</td></tr>
        </table>
        <p><i>Not: Sıcak metal BOF veya EAF yoluyla çelik üretimine gönderilir.</i></p>
        """)
        self.tabs.setCurrentIndex(2)
        self.statusBar().showMessage("✅ Simülasyon tamamlandı.")

    def _run_h2_feasibility(self):
        """Hidrojen indirgeme fizibilitesi"""
        ore_tons = self.ore_input.value()
        fe_pct = self.fe_pct.value()
        result = hydrogen_reduction_feasibility(ore_tons, fe_pct)

        QMessageBox.information(
            self,
            "🟢 H₂ İndirgeme Fizibilitesi",
            f"Hidrojen ihtiyacı: {result['h2_needed_kg']:.0f} kg\n"
            f"H₂ hacmi (STP): {result['h2_volume_nm3']:.0f} Nm³\n"
            f"Gerekli enerji: {result['energy_mj']:.0f} MJ\n"
            f"CO₂ tasarrufu: {result['co2_saved_kg']:.0f} kg\n"
            f"{'✅ Ekonomik olarak uygulanabilir.' if result['feasible'] else '⚠️ Şu anki enerji maliyetleriyle ekonomik değil.'}"
        )