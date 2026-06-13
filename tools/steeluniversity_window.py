
"""Steeluniversity - İnteraktif Çelik Eğitim Platformu"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class SteeluniversityWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Steeluniversity - Çelik Eğitim Platformu")
        self.setMinimumSize(800, 600)
        self._ui()
        self._load_style()
    
    def _load_style(self):
        self.setStyleSheet("QMainWindow{background:#1e1e2e}QLabel{color:#cdd6f4}QGroupBox{color:#cdd6f4;border:1px solid #45475a;border-radius:6px;margin-top:10px;padding-top:14px;font-weight:bold}QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 6px;color:#89b4fa;background:#1e1e2e}QPushButton{background:#89b4fa;color:#1e1e2e;border-radius:4px;padding:8px 16px;font-weight:bold}QTextEdit{background:#313244;color:#cdd6f4;border:1px solid #45475a}")
    
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QVBoxLayout(c)
        
        tabs = QTabWidget()
        
        # EAF Simülatörü sekmesi
        eaf_tab = QWidget()
        eaf_layout = QVBoxLayout(eaf_tab)
        eaf_text = QTextEdit(); eaf_text.setReadOnly(True)
        eaf_text.setHtml("""
        <h2>⚡ Elektrik Ark Ocağı (EAF) Simülatörü</h2>
        <p>Bu interaktif simülatör, EAF çelik üretim sürecini adım adım deneyimlemenizi sağlar.</p>
        <ol>
        <li><b>Hurda Şarjı:</b> Ağır hurda, hafif hurda, pik demir oranlarını belirleyin</li>
        <li><b>Ergitme:</b> Elektrotları devreye alın, gücü ayarlayın</li>
        <li><b>Oksijen Üfleme:</b> Karbon giderme için oksijen seviyesini ayarlayın</li>
        <li><b>Cüruf Yapma:</b> Kireç ilavesi ile cüruf oluşturun</li>
        <li><b>Döküm:</b> Sıvı çeliği potaya alın</li>
        </ol>
        <p><i>Tam simülasyon için Steelmaking aracını kullanın.</i></p>
        """)
        eaf_layout.addWidget(eaf_text)
        tabs.addTab(eaf_tab, "⚡ EAF")
        
        # İkincil Metalurji sekmesi
        sec_tab = QWidget()
        sec_layout = QVBoxLayout(sec_tab)
        sec_text = QTextEdit(); sec_text.setReadOnly(True)
        sec_text.setHtml("""
        <h2>🔄 İkincil Metalurji</h2>
        <ul>
        <li>Pota Ocağı (LF): Sıcaklık kontrolü, alaşımlama</li>
        <li>Vakum Degaz (VD): Hidrojen ve azot giderme</li>
        <li>Kalsiyum Enjeksiyonu: Kalıntı kontrolü</li>
        </ul>
        """)
        sec_layout.addWidget(sec_text)
        tabs.addTab(sec_tab, "🔄 İkincil Metalurji")
        
        layout.addWidget(tabs)
