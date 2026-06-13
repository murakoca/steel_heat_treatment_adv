"""Alaşım Rehberi Penceresi"""
from PyQt5.QtWidgets import *
from metallurgy.alloy_guide import AlloyGuide

class AlloyWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🧪 Alaşım Rehberi")
        self.setMinimumSize(700, 500)
        self._ui()
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QVBoxLayout(c)
        guide = AlloyGuide()
        data = guide.get_all()
        lbl = QLabel(f"<h2>{data['title']}</h2>"); lbl.setWordWrap(True)
        layout.addWidget(lbl)
        layout.addStretch()
