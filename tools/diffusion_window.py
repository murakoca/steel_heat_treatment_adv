"""Karbon Difüzyonu Penceresi"""
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
