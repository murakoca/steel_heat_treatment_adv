
"""Steelmaking - İnteraktif EAF Simülatörü"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np

class SteelmakingWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Steelmaking - EAF Simülatörü")
        self.setMinimumSize(900, 700)
        self._ui()
        self._load_style()
    
    def _load_style(self):
        self.setStyleSheet("QMainWindow{background:#1e1e2e}QLabel{color:#cdd6f4}QGroupBox{color:#cdd6f4;border:1px solid #45475a;border-radius:6px;margin-top:10px;padding-top:14px;font-weight:bold}QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 6px;color:#89b4fa;background:#1e1e2e}QPushButton{background:#89b4fa;color:#1e1e2e;border-radius:4px;padding:8px 16px;font-weight:bold}QPushButton:hover{background:#74c7ec}QLineEdit{background:#313244;color:#cdd6f4;border:1px solid #45475a;border-radius:4px;padding:5px}QTextEdit{background:#313244;color:#cdd6f4;border:1px solid #45475a}QSlider::groove:horizontal{background:#45475a;height:8px;border-radius:4px}QSlider::handle:horizontal{background:#89b4fa;width:18px;height:18px;margin:-5px 0;border-radius:9px}")
    
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QHBoxLayout(c)
        
        left = QWidget()
        left_layout = QVBoxLayout(left)
        
        # Hurda seçimi
        scrap_group = QGroupBox("⚡ Hurda Şarjı (ton)")
        form = QFormLayout(scrap_group)
        self.scrap_heavy = QLineEdit("40"); form.addRow("Ağır Hurda:", self.scrap_heavy)
        self.scrap_light = QLineEdit("30"); form.addRow("Hafif Hurda:", self.scrap_light)
        self.scrap_pig = QLineEdit("20"); form.addRow("Pik Demir:", self.scrap_pig)
        self.scrap_other = QLineEdit("10"); form.addRow("Diğer:", self.scrap_other)
        left_layout.addWidget(scrap_group)
        
        # Proses parametreleri
        proc_group = QGroupBox("🔧 Proses Parametreleri")
        form2 = QFormLayout(proc_group)
        self.oxygen = QSlider(Qt.Horizontal); self.oxygen.setRange(0, 100); self.oxygen.setValue(60)
        form2.addRow("Oksijen Üfleme:", self.oxygen)
        self.oxygen_lbl = QLabel("%60"); form2.addRow("", self.oxygen_lbl)
        self.power = QSlider(Qt.Horizontal); self.power.setRange(0, 100); self.power.setValue(80)
        form2.addRow("Elektrik Gücü:", self.power)
        self.power_lbl = QLabel("%80"); form2.addRow("", self.power_lbl)
        self.lime = QSlider(Qt.Horizontal); self.lime.setRange(0, 100); self.lime.setValue(40)
        form2.addRow("Kireç İlavesi:", self.lime)
        self.lime_lbl = QLabel("%40"); form2.addRow("", self.lime_lbl)
        left_layout.addWidget(proc_group)
        
        self.btn_sim = QPushButton("🔥 Simülasyonu Çalıştır")
        self.btn_sim.clicked.connect(self._simulate)
        left_layout.addWidget(self.btn_sim)
        
        # Sonuç paneli
        right = QWidget(); right.setMaximumWidth(400)
        right_layout = QVBoxLayout(right)
        self.result = QTextEdit(); self.result.setReadOnly(True)
        right_layout.addWidget(QLabel("📊 Simülasyon Sonuçları:"))
        right_layout.addWidget(self.result)
        
        layout.addWidget(left, 3)
        layout.addWidget(right, 2)
    
    def _simulate(self):
        total_scrap = sum([float(getattr(self, f'scrap_{t}').text()) for t in ['heavy','light','pig','other']])
        O2 = self.oxygen.value()
        power = self.power.value()
        lime = self.lime.value()
        
        # Basit termodinamik model
        energy_used = total_scrap * 400 * power/100  # kWh
        oxygen_used = total_scrap * 50 * O2/100  # Nm³
        lime_used = total_scrap * 0.04 * lime/100  # ton
        slag = lime_used * 2.5  # ton cüruf
        
        # Karbon giderme
        initial_C = total_scrap * 0.002
        C_removed = initial_C * O2/100 * 0.8
        final_C_pct = (initial_C - C_removed) / (total_scrap * 0.92) * 100
        
        liquid_steel = total_scrap * 0.90  # %90 verim
        
        self.result.setHtml(f"""
        <h3>🏭 EAF Simülasyon Raporu</h3>
        <table>
        <tr><td><b>Toplam Şarj:</b></td><td>{total_scrap:.0f} ton</td></tr>
        <tr><td><b>Sıvı Çelik:</b></td><td>{liquid_steel:.1f} ton</td></tr>
        <tr><td><b>Verim:</b></td><td>%90</td></tr>
        <tr><td><b>Enerji Tüketimi:</b></td><td>{energy_used:.0f} kWh</td></tr>
        <tr><td><b>Oksijen Tüketimi:</b></td><td>{oxygen_used:.0f} Nm³</td></tr>
        <tr><td><b>Kireç İlavesi:</b></td><td>{lime_used:.2f} ton</td></tr>
        <tr><td><b>Cüruf Miktarı:</b></td><td>{slag:.2f} ton</td></tr>
        <tr><td><b>Nihai Karbon:</b></td><td>%{final_C_pct:.3f}</td></tr>
        <tr><td><b>Oksijen Üfleme:</b></td><td>%{O2}</td></tr>
        <tr><td><b>Elektrik Gücü:</b></td><td>%{power}</td></tr>
        </table>
        """)
