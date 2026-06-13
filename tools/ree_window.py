"""REE Penceresi"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from metallurgy.ree import REEDatabase

class REEWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🧪 Nadir Toprak Elementleri")
        self.setMinimumSize(700, 500)
        self._ui()
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QVBoxLayout(c)
        self.ree_db = REEDatabase()
        data = self.ree_db.get_all()
        lbl = QLabel(f"<h2>REE</h2><p>{data['description']}</p><p>17 element: {', '.join(data['elements'])}</p>")
        lbl.setWordWrap(True); layout.addWidget(lbl)
        layout.addStretch()
