"""Hata Modları Penceresi"""
from PyQt5.QtWidgets import *
from metallurgy.failure_modes import FailureModes

class FailureWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔧 Hata Modları")
        self.setMinimumSize(700, 500)
        self._ui()
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QVBoxLayout(c)
        db = FailureModes()
        data = db.get_all()
        lbl = QLabel(f"<h2>{data['title']['tr']}</h2>"); lbl.setWordWrap(True)
        layout.addWidget(lbl)
        layout.addStretch()
