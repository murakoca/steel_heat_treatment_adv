"""Distorsiyon Penceresi"""
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
