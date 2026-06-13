
"""BOF Çalışma Prensibi – Görsel Anlatım"""
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc, Rectangle, Polygon, Circle, Ellipse
import matplotlib.pyplot as plt

class BOFPrincipleWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("BOF Çalışma Prensibi – Oksijen Konvertörü")
        self.setMinimumSize(1100, 800)
        self._ui()
        self._load_style()

    def _load_style(self):
        self.setStyleSheet("""
            QMainWindow { background: #1e1e2e; }
            QLabel { color: #cdd6f4; }
            QGroupBox { color: #cdd6f4; border: 1px solid #45475a; border-radius: 6px; margin-top: 12px; padding-top: 14px; font-weight: bold; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 6px; color: #89b4fa; background: #1e1e2e; }
            QPushButton { background: #89b4fa; color: #1e1e2e; border-radius: 4px; padding: 8px 16px; font-weight: bold; }
            QPushButton:hover { background: #74c7ec; }
            QTextEdit { background: #313244; color: #cdd6f4; border: 1px solid #45475a; }
        """)

    def _ui(self):
        c = QWidget()
        self.setCentralWidget(c)
        main_layout = QVBoxLayout(c)

        # Üst başlık
        title = QLabel("<h1>🏭 Bazik Oksijen Fırını (BOF) Çalışma Prensibi</h1>")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Sekmeler
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Sekme 1: BOF Diyagramı
        self._create_diagram_tab()
        # Sekme 2: Reaksiyonlar
        self._create_reactions_tab()
        # Sekme 3: Akış Şeması
        self._create_flowchart_tab()
        # Sekme 4: Yapısal Detay
        self._create_structure_tab()

        self.statusBar().showMessage("BOF: Kontrollü oksidasyon ile çelik üretimi")

    def _create_diagram_tab(self):
        """BOF'un şematik çizimi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        fig = Figure(figsize=(10, 7), facecolor='#1e1e2e')
        canvas = FigureCanvasQTAgg(fig)
        ax = fig.add_subplot(111, facecolor='#1e1e2e')
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 12)
        ax.axis('off')

        # Konvertör gövdesi
        vessel = FancyBboxPatch((2.5, 1), 5, 9, boxstyle="round,pad=0.5", 
                                facecolor='#45475a', edgecolor='#89b4fa', linewidth=3)
        ax.add_patch(vessel)

        # Refrakter kaplama (iç)
        inner = FancyBboxPatch((3, 1.5), 4, 8, boxstyle="round,pad=0.4",
                               facecolor='#fab387', edgecolor='#f38ba8', linewidth=2, alpha=0.5)
        ax.add_patch(inner)
        ax.text(5, 5.5, 'REFRACTER\nMgO, Dolomit', ha='center', va='center',
                color='#1e1e2e', fontsize=8, fontweight='bold')

        # Sıvı metal
        metal = Rectangle((3.3, 1.8), 3.4, 3, facecolor='#f38ba8', alpha=0.7, edgecolor='#fab387', linewidth=2)
        ax.add_patch(metal)
        ax.text(5, 3.3, 'SIVI HAM DEMİR\n(~%4 C)', ha='center', va='center',
                color='#1e1e2e', fontsize=9, fontweight='bold')

        # Cüruf tabakası
        slag = Rectangle((3.3, 4.8), 3.4, 1.2, facecolor='#a6e3a1', alpha=0.8, edgecolor='#74c7ec', linewidth=2)
        ax.add_patch(slag)
        ax.text(5, 5.4, 'CÜRUF (SLAG)\nCaO·SiO₂·P₂O₅', ha='center', va='center',
                color='#1e1e2e', fontsize=8, fontweight='bold')

        # Oksijen mızrağı
        lance = Rectangle((4.7, 10), 0.6, 2, facecolor='#89b4fa', edgecolor='#cdd6f4', linewidth=2)
        ax.add_patch(lance)
        ax.text(5, 11.2, 'O₂ LANCE\n(%99 Saf O₂)', ha='center', va='center',
                color='#1e1e2e', fontsize=8, fontweight='bold')

        # Oksijen jeti
        for i in range(3):
            jet = FancyArrowPatch((5, 10), (5, 7.2 - i*0.3), arrowstyle='->', 
                                  color='#89b4fa', linewidth=2, alpha=0.6)
            ax.add_patch(jet)

        # Kabarcıklar
        for bx, by in [(4, 3), (5.5, 2.5), (6, 3.5), (3.8, 2.8)]:
            bubble = Circle((bx, by), 0.25, facecolor='none', edgecolor='#cdd6f4', linewidth=1.5, alpha=0.6)
            ax.add_patch(bubble)
        ax.text(6.5, 3, 'CO↑\nCO₂↑', color='#cdd6f4', fontsize=7)

        # Eğme mekanizması göstergesi
        ax.annotate('Eğme\nMekanizması', xy=(1.8, 5.5), fontsize=8, color='#a6adc8',
                    ha='center', arrowprops=dict(arrowstyle='->', color='#a6adc8'))

        # Etiketler
        ax.text(1.5, 9, '① Çelik Gövde', color='#89b4fa', fontsize=8)
        ax.text(1.5, 8.3, '② Refrakter', color='#fab387', fontsize=8)
        ax.text(1.5, 7.6, '③ O₂ Mızrağı', color='#89b4fa', fontsize=8)
        ax.text(1.5, 6.9, '④ Cüruf', color='#a6e3a1', fontsize=8)
        ax.text(1.5, 6.2, '⑤ Sıvı Metal', color='#f38ba8', fontsize=8)

        # Girdi okları
        ax.annotate('Hurda\nÇelik', xy=(3, 0.5), fontsize=8, color='#74c7ec', ha='center')
        ax.annotate('Kireç\n(CaO)', xy=(7, 0.5), fontsize=8, color='#a6e3a1', ha='center')
        ax.annotate('Sıvı Ham\nDemir', xy=(5, 0.2), fontsize=8, color='#f38ba8', ha='center')

        ax.set_title('BOF Konvertörü – Kesit Görünümü', color='#cdd6f4', fontsize=14, fontweight='bold', pad=20)
        layout.addWidget(canvas)
        self.tabs.addTab(tab, "🔍 BOF Diyagramı")

    def _create_reactions_tab(self):
        """Kimyasal reaksiyonlar"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        text = QTextEdit()
        text.setReadOnly(True)
        text.setHtml("""
        <h2>⚗️ BOF İçinde Gerçekleşen Reaksiyonlar</h2>

        <h3>🔥 Dekarbürizasyon (Karbon Giderme)</h3>
        <p>C + ½O₂ → CO &nbsp;&nbsp;|&nbsp;&nbsp; C + O₂ → CO₂</p>
        <p>CO gazı kabarcıklar halinde yükselir. Amaç karbonu %4'ten %0.05-0.2'ye düşürmektir.</p>

        <h3>🧪 Silisyum Oksidasyonu</h3>
        <p>Si + O₂ → SiO₂</p>
        <p>SiO₂ cürufa geçer. CaO ile birleşerek cürufun akışkanlığını artırır.</p>

        <h3>🧪 Manganez Oksidasyonu</h3>
        <p>2Mn + O₂ → 2MnO</p>

        <h3>🧪 Fosfor Giderme</h3>
        <p>4P + 5O₂ → 2P₂O₅</p>
        <p>P₂O₅ + 4CaO → 4CaO·P₂O₅ (cürufa geçer)</p>
        <p><b>Koşullar:</b> Yüksek FeO, yüksek baziklik (CaO/SiO₂ = 2.5-4), düşük sıcaklık</p>

        <h3>🧪 Kükürt Giderme (Sınırlı)</h3>
        <p>CaO + FeS → CaS + FeO</p>
        <p>Asıl kükürt giderme ikincil metalurjide (ladil fırınında) yapılır.</p>

        <h3>🌡️ Sıcaklık Kontrolü</h3>
        <p>Tüm reaksiyonlar <b>ekzotermiktir</b> (ısı verir). Bu nedenle dışarıdan ısıtmaya gerek kalmaz.</p>
        <p>Sıcaklık 1600-1700°C arasında tutulur. Aşırı ısınmayı önlemek için hurda çelik eklenir (ısı emici).</p>
        """)
        layout.addWidget(text)
        self.tabs.addTab(tab, "⚗️ Reaksiyonlar")

    def _create_flowchart_tab(self):
        """Akış şeması"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        fig = Figure(figsize=(10, 10), facecolor='#1e1e2e')
        canvas = FigureCanvasQTAgg(fig)
        ax = fig.add_subplot(111, facecolor='#1e1e2e')
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 13)
        ax.axis('off')

        steps = [
            (5, 12, 'YÜKSEK FIRIN', '#f38ba8'),
            (5, 10.8, 'Sıvı Ham Demir\n(~%4 C)', '#fab387'),
            (5, 9.5, '+ Hurda Çelik\n+ Kireç (CaO)', '#a6e3a1'),
            (5, 8.2, 'SAF OKSİJEN ÜFLENİR\n(%99 O₂)', '#89b4fa'),
            (5, 6.8, 'Karbon ve Safsızlıklar\nOksitlenir', '#74c7ec'),
            (5, 5.5, 'CÜRUF OLUŞUR\n(Yüzeyde Yüzer)', '#a6e3a1'),
            (5, 4.2, 'Cüruf Boşaltılır', '#f9e2af'),
            (5, 3.0, 'SIVI ÇELİK POTA\nALINIR', '#f38ba8'),
            (5, 1.8, '+ Alaşım Elementleri\n(Ni, Cr, Mo, V...)', '#89b4fa'),
            (5, 0.6, 'SÜREKLİ DÖKÜM\n→ Kütük / Slab', '#74c7ec'),
        ]

        for i, (x, y, text, color) in enumerate(steps):
            box = FancyBboxPatch((x-2.5, y-0.4), 5, 0.8, boxstyle="round,pad=0.1",
                                 facecolor=color, edgecolor='white', linewidth=1.5, alpha=0.9)
            ax.add_patch(box)
            ax.text(x, y, text, ha='center', va='center', fontsize=8, color='#1e1e2e', fontweight='bold')

        # Oklar
        for i in range(len(steps)-1):
            y1 = steps[i][1] - 0.4
            y2 = steps[i+1][1] + 0.4
            arrow = FancyArrowPatch((5, y1), (5, y2), arrowstyle='->',
                                    color='#cdd6f4', linewidth=2)
            ax.add_patch(arrow)

        ax.set_title('BOF Çelik Üretim Akış Şeması', color='#cdd6f4', fontsize=14, fontweight='bold', pad=10)
        layout.addWidget(canvas)
        self.tabs.addTab(tab, "📋 Akış Şeması")

    def _create_structure_tab(self):
        """Yapısal detaylar"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        text = QTextEdit()
        text.setReadOnly(True)
        text.setHtml("""
        <h2>🏗️ Konvertörün Yapısı</h2>

        <h3>A) Çelik Gövde</h3>
        <p>Dış kısmı kalın çelikten yapılmıştır. Mekanik dayanım sağlar, yüzlerce tonluk yükü taşır. Sıcak metal ile doğrudan temas etmez.</p>

        <h3>B) Refrakter Kaplama</h3>
        <p>İç yüzey 50-100 cm kalınlığında refrakter tuğlalarla kaplıdır.</p>
        <p><b>Malzemeler:</b> MgO, Dolomit, Magnezit</p>
        <p><b>Görevleri:</b> 1700°C'ye dayanmak, kimyasal aşınmayı önlemek, konvertör ömrünü uzatmak.</p>
        <p>⚠️ Bu kaplama zamanla aşınır ve belirli sayıda dökümden sonra değiştirilir.</p>

        <h3>C) Oksijen Mızrağı (Lance)</h3>
        <p>Üstten aşağı sarkar. İçinden %99 saf oksijen süpersonik hızda üflenir.</p>

        <h3>D) Eğme Mekanizması</h3>
        <p>Konvertör iki büyük mil üzerinde döner:</p>
        <ul>
        <li>Şarj için eğilir</li>
        <li>Cüruf boşaltmak için eğilir</li>
        <li>Çelik boşaltmak için tekrar eğilir</li>
        </ul>

        <h3>❓ Neden Hava Yerine Saf Oksijen?</h3>
        <p>Hava %79 azot içerir. Azot çeliğin kalitesini düşürür ve reaksiyonları yavaşlatır. Bu yüzden %99 saf oksijen kullanılır.</p>

        <h3>🎯 En Önemli Mühendislik Noktası</h3>
        <p>Bu prosesin temel mantığı, erimiş demiri yeniden eritmek <b>değil</b>; <b>kontrollü oksidasyon</b> yoluyla içindeki karbon ve diğer istenmeyen elementleri uzaklaştırıp, ardından gerekli alaşım elementlerini ekleyerek istenen özellikte çelik üretmektir. BOF, esasen çok büyük ölçekli ve yüksek sıcaklıkta çalışan bir <b>kimyasal reaksiyon reaktörüdür</b>.</p>
        """)
        layout.addWidget(text)
        self.tabs.addTab(tab, "🏗️ Yapısal Detay")
