"""TTT/CCT Penceresi"""
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
