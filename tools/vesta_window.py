
"""Vesta - 3D Kristal Yapı ve XRD Simülasyonu"""
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class VestaWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vesta - 3D Kristal Yapı & XRD")
        self.setMinimumSize(1000, 750)
        self._ui()
        self._load_style()
    
    def _load_style(self):
        self.setStyleSheet("QMainWindow{background:#1e1e2e}QLabel{color:#cdd6f4}QGroupBox{color:#cdd6f4;border:1px solid #45475a;border-radius:6px;margin-top:10px;padding-top:14px;font-weight:bold}QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 6px;color:#89b4fa;background:#1e1e2e}QPushButton{background:#89b4fa;color:#1e1e2e;border-radius:4px;padding:8px 16px;font-weight:bold}QComboBox{background:#313244;color:#cdd6f4;border:1px solid #45475a;padding:5px}QTextEdit{background:#313244;color:#cdd6f4;border:1px solid #45475a}")
    
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QVBoxLayout(c)
        
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Kristal Yapı:"))
        self.structure = QComboBox()
        self.structure.addItems(["BCC (Fe-α)", "FCC (Fe-γ)", "HCP (Ti)", "NaCl", "CsCl", "Elmas", "Perovskit"])
        ctrl.addWidget(self.structure)
        self.size = QSpinBox(); self.size.setRange(1,5); self.size.setValue(2)
        ctrl.addWidget(QLabel("Birim:")); ctrl.addWidget(self.size)
        self.btn_draw = QPushButton("🎨 Çiz"); self.btn_draw.clicked.connect(self._draw)
        ctrl.addWidget(self.btn_draw)
        self.btn_xrd = QPushButton("📊 XRD Simüle Et"); self.btn_xrd.clicked.connect(self._xrd)
        ctrl.addWidget(self.btn_xrd)
        ctrl.addStretch()
        layout.addLayout(ctrl)
        
        self.fig = Figure(figsize=(10,5), facecolor='#1e1e2e')
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.ax3d = self.fig.add_subplot(121, projection='3d', facecolor='#1e1e2e')
        self.ax_xrd = self.fig.add_subplot(122, facecolor='#1e1e2e')
        for ax in [self.ax3d, self.ax_xrd]:
            ax.tick_params(colors='#cdd6f4')
            for s in ax.spines.values(): s.set_color('#45475a')
        layout.addWidget(self.canvas)
        self._draw()
    
    def _draw(self):
        struct = self.structure.currentText()
        n = self.size.value()
        pos = []
        for i,j,k in [(i,j,k) for i in range(n) for j in range(n) for k in range(n)]:
            pos.append([i,j,k])
            if "BCC" in struct: pos.append([i+0.5,j+0.5,k+0.5])
            elif "FCC" in struct:
                pos.extend([[i+0.5,j+0.5,k],[i+0.5,j,k+0.5],[i,j+0.5,k+0.5]])
            elif "NaCl" in struct:
                pos.append([i+0.5,j+0.5,k+0.5])
                pos.append([i+1,j,k])
        
        pos = np.array(pos)
        self.ax3d.clear()
        self.ax3d.scatter(pos[:,0], pos[:,1], pos[:,2], c='steelblue', s=80, alpha=0.8, edgecolors='white')
        self.ax3d.set_title(f"3D Yapı: {struct}", color='#cdd6f4')
        self.canvas.draw()
    
    def _xrd(self):
        hkl_list = [(1,0,0),(1,1,0),(1,1,1),(2,0,0),(2,1,0),(2,1,1),(2,2,0),(3,1,0)]
        theta = np.linspace(10, 90, 1000)
        pattern = np.zeros_like(theta)
        a = 2.86  # Fe BCC lattice parameter
        wavelength = 0.15406  # Cu Kα
        
        for h,k,l in hkl_list:
            d = a / np.sqrt(h**2 + k**2 + l**2)
            sin_th = wavelength / (2*d)
            if sin_th <= 1:
                th_peak = np.degrees(np.arcsin(sin_th))
                pattern += np.exp(-((theta - th_peak) / 0.3)**2)
        
        self.ax_xrd.clear()
        self.ax_xrd.plot(theta, pattern, 'c-', lw=2)
        self.ax_xrd.set_xlabel("2θ (°)", color='#cdd6f4')
        self.ax_xrd.set_ylabel("Şiddet", color='#cdd6f4')
        self.ax_xrd.set_title("XRD Deseni (Cu Kα)", color='#cdd6f4')
        self.canvas.draw()
