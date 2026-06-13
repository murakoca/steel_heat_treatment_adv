
"""Comsol - Korozyon ve SCC Modelleme"""
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class ComsolWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Comsol - Korozyon & SCC Simülasyonu")
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
        ctrl = QGroupBox("Korozyon Parametreleri")
        form = QFormLayout(ctrl)
        self.corr_rate = QLineEdit("0.15"); form.addRow("Korozyon Hızı (mm/yıl):", self.corr_rate)
        self.stress = QLineEdit("250"); form.addRow("Gerilme (MPa):", self.stress)
        self.time = QLineEdit("20"); form.addRow("Süre (yıl):", self.time)
        self.btn = QPushButton("🧪 Simüle Et"); self.btn.clicked.connect(self._simulate)
        form.addRow(self.btn)
        right_layout.addWidget(ctrl)
        self.result = QTextEdit(); self.result.setReadOnly(True)
        right_layout.addWidget(self.result)
        
        layout.addWidget(left, 3)
        layout.addWidget(right, 1)
        self._simulate()
    
    def _simulate(self):
        try:
            rate = float(self.corr_rate.text())
            stress = float(self.stress.text())
            years = float(self.time.text())
            
            t = np.linspace(0, years, 100)
            depth = rate * t
            # SCC risk modeli
            K_threshold = 50  # MPa√m
            K_applied = stress * np.sqrt(np.pi * depth/1000)
            scc_risk = np.clip(K_applied / K_threshold, 0, 1)
            
            self.ax.clear()
            self.ax.plot(t, depth, 'r-', lw=2.5, label='Korozyon Derinliği')
            self.ax.set_xlabel("Zaman (yıl)", color='#cdd6f4')
            self.ax.set_ylabel("Derinlik (mm)", color='#cdd6f4')
            self.ax.set_title("Korozyon İlerlemesi", color='#cdd6f4')
            self.ax.legend(framealpha=0.3, facecolor='#313244', edgecolor='#45475a', labelcolor='#cdd6f4')
            self.canvas.draw()
            
            self.result.setHtml(f"""
            <b>Nihai Derinlik:</b> {depth[-1]:.2f} mm<br>
            <b>SCC Risk Faktörü:</b> {scc_risk[-1]:.3f}<br>
            <b>Kritik Gerilme:</b> {K_threshold:.0f} MPa√m<br>
            <b>Uygulanan K:</b> {K_applied[-1]:.1f} MPa√m<br>
            """)
        except: pass
