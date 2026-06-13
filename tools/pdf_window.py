"""PDF Rapor Penceresi"""
from PyQt5.QtWidgets import *

class PDFWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📄 PDF Rapor")
        self.setMinimumSize(400, 300)
        self._ui()
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QVBoxLayout(c)
        layout.addWidget(QLabel("PDF rapor oluşturmak için önce simülasyon çalıştırın."))
        self.btn = QPushButton("PDF Oluştur"); layout.addWidget(self.btn)
        layout.addStretch()
