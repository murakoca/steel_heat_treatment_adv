"""Lever Rule Penceresi"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from metallurgy.lever_rule import calculate as lever_calculate, FE_C_EXAMPLES

class LeverWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚖️ Lever Kuralı Hesaplayıcı")
        self.setMinimumSize(500, 400)
        self._ui()
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QVBoxLayout(c)
        form = QFormLayout()
        self.lever_ca = QLineEdit("0.022"); form.addRow("Cα (%):", self.lever_ca)
        self.lever_cb = QLineEdit("6.67"); form.addRow("Cβ (%):", self.lever_cb)
        self.lever_co = QLineEdit("0.8"); form.addRow("Co (%):", self.lever_co)
        layout.addLayout(form)
        btn = QPushButton("Hesapla"); btn.clicked.connect(self._calc); layout.addWidget(btn)
        self.result = QLabel(""); self.result.setWordWrap(True)
        layout.addWidget(self.result)
        layout.addStretch()
    def _calc(self):
        try:
            Ca = float(self.lever_ca.text()); Cb = float(self.lever_cb.text()); Co = float(self.lever_co.text())
            res = lever_calculate(Ca, Cb, Co)
            self.result.setText(f"α: %{res.percent_alpha:.1f}, β: %{res.percent_beta:.1f}")
        except ValueError as e:
            self.result.setText(f"Hata: {e}")
