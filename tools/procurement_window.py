"""Satın Alma Penceresi"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from procurement.calculator import SupplierCost, compare_suppliers
import json, os

class ProcurementWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📊 Satın Alma Rehberi")
        self.setMinimumSize(500, 400)
        self._ui()
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QVBoxLayout(c)
        self.proc_a_price = QLineEdit("100000"); layout.addWidget(QLabel("A Fiyat:")); layout.addWidget(self.proc_a_price)
        self.proc_a_rework = QLineEdit("20000"); layout.addWidget(QLabel("A Yeniden İşleme:")); layout.addWidget(self.proc_a_rework)
        self.proc_a_delay = QLineEdit("15000"); layout.addWidget(QLabel("A Gecikme:")); layout.addWidget(self.proc_a_delay)
        self.proc_a_quality = QLineEdit("10000"); layout.addWidget(QLabel("A Kalite:")); layout.addWidget(self.proc_a_quality)
        self.proc_b_price = QLineEdit("110000"); layout.addWidget(QLabel("B Fiyat:")); layout.addWidget(self.proc_b_price)
        self.proc_b_rework = QLineEdit("5000"); layout.addWidget(QLabel("B Yeniden İşleme:")); layout.addWidget(self.proc_b_rework)
        self.proc_b_delay = QLineEdit("0"); layout.addWidget(QLabel("B Gecikme:")); layout.addWidget(self.proc_b_delay)
        self.proc_b_quality = QLineEdit("0"); layout.addWidget(QLabel("B Kalite:")); layout.addWidget(self.proc_b_quality)
        btn = QPushButton("Hesapla"); btn.clicked.connect(self._calc); layout.addWidget(btn)
        self.result = QLabel(""); layout.addWidget(self.result)
    def _calc(self):
        try:
            a = SupplierCost("A", float(self.proc_a_price.text()), float(self.proc_a_rework.text()), float(self.proc_a_delay.text()), float(self.proc_a_quality.text()))
            b = SupplierCost("B", float(self.proc_b_price.text()), float(self.proc_b_rework.text()), float(self.proc_b_delay.text()), float(self.proc_b_quality.text()))
            w, d = compare_suppliers(a, b)
            self.result.setText(f"{w.name} {d:,.0f} TL daha ekonomik!" if w else "Eşit")
        except: self.result.setText("Hata!")
