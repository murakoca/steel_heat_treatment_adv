
"""Simufact Forming - 3D Şekillendirme Simülasyonu"""
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class SimufactWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Simufact Forming - Metal Şekillendirme")
        self.setMinimumSize(900, 700)
        self._ui()
        self._load_style()
    
    def _load_style(self):
        self.setStyleSheet("QMainWindow{background:#1e1e2e}QLabel{color:#cdd6f4}QGroupBox{color:#cdd6f4;border:1px solid #45475a;border-radius:6px;margin-top:10px;padding-top:14px;font-weight:bold}QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 6px;color:#89b4fa;background:#1e1e2e}QPushButton{background:#89b4fa;color:#1e1e2e;border-radius:4px;padding:8px 16px;font-weight:bold}QLineEdit{background:#313244;color:#cdd6f4;border:1px solid #45475a;border-radius:4px;padding:5px}QTextEdit{background:#313244;color:#cdd6f4;border:1px solid #45475a}")
    
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QHBoxLayout(c)
        
        left = QWidget()
        left_layout = QVBoxLayout(left)
        self.fig = Figure(figsize=(8,6), facecolor='#1e1e2e')
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.ax = self.fig.add_subplot(111, facecolor='#1e1e2e')
        self.ax.tick_params(colors='#cdd6f4')
        for s in self.ax.spines.values(): s.set_color('#45475a')
        left_layout.addWidget(self.canvas)
        
        right = QWidget(); right.setMaximumWidth(300)
        right_layout = QVBoxLayout(right)
        ctrl = QGroupBox("Proses Parametreleri")
        form = QFormLayout(ctrl)
        self.process = QComboBox()
        self.process.addItems(["Dövme", "Ekstrüzyon", "Haddeleme", "Sac Şekillendirme"])
        form.addRow("Proses:", self.process)
        self.temp = QLineEdit("1100"); form.addRow("Sıcaklık (°C):", self.temp)
        self.force = QLineEdit("500"); form.addRow("Kuvvet (kN):", self.force)
        self.friction = QLineEdit("0.3"); form.addRow("Sürtünme:", self.friction)
        self.btn = QPushButton("🔨 Simüle Et"); self.btn.clicked.connect(self._simulate)
        form.addRow(self.btn)
        right_layout.addWidget(ctrl)
        self.result = QTextEdit(); self.result.setReadOnly(True)
        right_layout.addWidget(self.result)
        
        layout.addWidget(left, 3)
        layout.addWidget(right, 1)
        self._simulate()
    
    def _simulate(self):
        try:
            T = float(self.temp.text())
            F = float(self.force.text())
            mu = float(self.friction.text())
            
            strains = np.linspace(0, 1.5, 100)
            # Johnson-Cook benzeri model
            A, B, n, m = 200, 300, 0.3, 1.0
            T_room, T_melt = 25, 1500
            T_hom = (T - T_room) / (T_melt - T_room)
            stresses = (A + B * strains**n) * (1 - T_hom**m)
            
            self.ax.clear()
            self.ax.plot(strains, stresses, 'c-', lw=2.5)
            self.ax.fill_between(strains, 0, stresses, alpha=0.2, color='cyan')
            self.ax.set_xlabel("Gerçek Şekil Değiştirme", color='#cdd6f4')
            self.ax.set_ylabel("Akma Gerilmesi (MPa)", color='#cdd6f4')
            self.ax.set_title(f"Akma Eğrisi ({T:.0f}°C)", color='#cdd6f4')
            self.canvas.draw()
            
            self.result.setHtml(f"""
            <b>Proses:</b> {self.process.currentText()}<br>
            <b>Sıcaklık:</b> {T:.0f}°C<br>
            <b>Maks. Gerilme:</b> {stresses[-1]:.0f} MPa<br>
            <b>Sürtünme:</b> {mu:.2f}<br>
            """)
        except: pass
