
"""Pandat - Çok Bileşenli CALPHAD Termodinamik"""
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class PandatWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pandat - Çok Bileşenli Faz Diyagramı")
        self.setMinimumSize(1000, 750)
        self._ui()
        self._load_style()
    
    def _load_style(self):
        self.setStyleSheet("QMainWindow{background:#1e1e2e}QLabel{color:#cdd6f4}QGroupBox{color:#cdd6f4;border:1px solid #45475a;border-radius:6px;margin-top:10px;padding-top:14px;font-weight:bold}QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 6px;color:#89b4fa;background:#1e1e2e}QPushButton{background:#89b4fa;color:#1e1e2e;border-radius:4px;padding:8px 16px;font-weight:bold}QPushButton:hover{background:#74c7ec}QLineEdit{background:#313244;color:#cdd6f4;border:1px solid #45475a;border-radius:4px;padding:5px}QTextEdit{background:#313244;color:#cdd6f4;border:1px solid #45475a}")
    
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
        
        right = QWidget(); right.setMaximumWidth(350)
        right_layout = QVBoxLayout(right)
        
        ctrl = QGroupBox("Alaşım Bileşimi (% ağırlık)")
        form = QFormLayout(ctrl)
        self.elements = {}
        for el, default in [("Fe", 70), ("Cr", 20), ("Ni", 10), ("Mn", 0), ("Si", 0)]:
            le = QLineEdit(str(default))
            form.addRow(f"{el} (%):", le)
            self.elements[el] = le
        self.T_min = QLineEdit("500"); form.addRow("T_min (K):", self.T_min)
        self.T_max = QLineEdit("1800"); form.addRow("T_max (K):", self.T_max)
        self.btn = QPushButton("🧪 Faz Diyagramı Hesapla")
        self.btn.clicked.connect(self._calculate)
        form.addRow(self.btn)
        right_layout.addWidget(ctrl)
        
        self.result = QTextEdit(); self.result.setReadOnly(True)
        right_layout.addWidget(QLabel("📋 Sonuç:"))
        right_layout.addWidget(self.result)
        
        layout.addWidget(left, 3)
        layout.addWidget(right, 1)
    
    def _calculate(self):
        try:
            comp = {el: float(le.text())/100 for el, le in self.elements.items()}
            total = sum(comp.values())
            comp = {k: v/total for k, v in comp.items()}
            
            T_min = float(self.T_min.text())
            T_max = float(self.T_max.text())
            
            # Cr-Ni eşdeğeri hesapla (Schaeffler diyagramı için)
            Cr_eq = comp.get('Cr', 0)*100 + comp.get('Mo', 0)*100 + 1.5*comp.get('Si', 0)*100
            Ni_eq = comp.get('Ni', 0)*100 + 30*comp.get('C', 0)*100 + 0.5*comp.get('Mn', 0)*100
            
            Ts = np.linspace(T_min, T_max, 100)
            ferrite_fraction = []
            for T in Ts:
                # Basit model: Cr_eq ve Ni_eq'e göre ferrit oranı
                ff = max(0, min(1, (Cr_eq - 0.5*Ni_eq) / 50))
                ferrite_fraction.append(ff)
            
            self.ax.clear()
            self.ax.plot(ferrite_fraction, Ts, 'b-', lw=2.5)
            self.ax.fill_betweenx(Ts, 0, ferrite_fraction, alpha=0.3, color='blue')
            self.ax.set_xlabel("Ferrit Oranı", color='#cdd6f4')
            self.ax.set_ylabel("Sıcaklık (K)", color='#cdd6f4')
            self.ax.set_title(f"Fe-{int(comp.get('Cr',0)*100)}Cr-{int(comp.get('Ni',0)*100)}Ni", color='#cdd6f4')
            self.canvas.draw()
            
            self.result.setHtml(f"""
            <b>Alaşım Bileşimi:</b><br>
            {', '.join([f'{el}: {v*100:.1f}%' for el,v in comp.items() if v>0])}<br>
            <b>Cr_eşdeğer:</b> {Cr_eq:.1f}<br>
            <b>Ni_eşdeğer:</b> {Ni_eq:.1f}<br>
            <b>Cr/Ni oranı:</b> {Cr_eq/Ni_eq:.2f}<br>
            """)
        except Exception as e:
            self.result.setText(f"Hata: {e}")
