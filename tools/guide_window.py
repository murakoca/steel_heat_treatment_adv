"""Malzeme Rehberi Penceresi"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

MATERIAL_GUIDE = {
    "Düşük Karbonlu (örn. 1020)": "Yapısal çelikler, araba gövdeleri, borular.",
    "Orta Karbonlu (örn. 1045)": "Şaft, aks, dişli. Isıl işlemle sertleştirilebilir.",
    "Yüksek Karbonlu (örn. 1095)": "Yay, bıçak, kesici takım.",
    "Alaşımlı (örn. 4140)": "Krank mili, iniş takımı.",
    "Paslanmaz (örn. 316)": "Kimya, medikal, mutfak.",
    "Takım Çeliği (örn. H13)": "Sıcak iş kalıpları.",
    "AHSS (örn. DP600)": "Otomotiv panelleri."
}

class GuideWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📚 Malzeme Seçim Rehberi")
        self.setMinimumSize(600, 500)
        self._ui()
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QVBoxLayout(c)
        label = QLabel("Malzeme Seçim Rehberi")
        label.setStyleSheet("font-size:16px; font-weight:bold; color:#89b4fa;")
        layout.addWidget(label)
        for title, desc in MATERIAL_GUIDE.items():
            grp = QGroupBox(title)
            grp.setStyleSheet("QGroupBox{color:#cdd6f4;border:1px solid #45475a;border-radius:6px;margin-top:8px;padding-top:10px;font-weight:bold}")
            grp_lay = QVBoxLayout(grp)
            lbl = QLabel(desc); lbl.setWordWrap(True); lbl.setStyleSheet("color:#cdd6f4")
            grp_lay.addWidget(lbl)
            layout.addWidget(grp)
        layout.addStretch()
