
"""Metrical - ASTM E112 Tane Boyutu & Mikroyapı Analizi"""
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from scipy import ndimage
import os

class MetricalWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Metrical - ASTM E112 Tane Boyutu Analizi")
        self.setMinimumSize(1000, 750)
        self.loaded_image = None
        self._ui()
        self._load_style()
    
    def _load_style(self):
        self.setStyleSheet("QMainWindow{background:#1e1e2e}QLabel{color:#cdd6f4}QGroupBox{color:#cdd6f4;border:1px solid #45475a;border-radius:6px;margin-top:10px;padding-top:14px;font-weight:bold}QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 6px;color:#89b4fa;background:#1e1e2e}QPushButton{background:#89b4fa;color:#1e1e2e;border-radius:4px;padding:8px 16px;font-weight:bold}QPushButton:hover{background:#74c7ec}QLineEdit,QComboBox{background:#313244;color:#cdd6f4;border:1px solid #45475a;border-radius:4px;padding:5px}QTextEdit{background:#313244;color:#cdd6f4;border:1px solid #45475a}")
    
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QHBoxLayout(c)
        
        # Sol panel - görüntü
        left = QWidget()
        left_layout = QVBoxLayout(left)
        self.fig = Figure(figsize=(7,6), facecolor='#1e1e2e')
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.ax = self.fig.add_subplot(111, facecolor='#1e1e2e')
        self.ax.tick_params(colors='#cdd6f4')
        for s in self.ax.spines.values(): s.set_color('#45475a')
        left_layout.addWidget(self.canvas)
        self.btn_load = QPushButton("📂 Görüntü Yükle (SEM/Mikroskop)")
        self.btn_load.clicked.connect(self._load_image)
        left_layout.addWidget(self.btn_load)
        
        # Sağ panel - kontroller
        right = QWidget(); right.setMaximumWidth(350)
        right_layout = QVBoxLayout(right)
        
        ctrl = QGroupBox("Analiz Parametreleri")
        form = QFormLayout(ctrl)
        self.analysis_type = QComboBox()
        self.analysis_type.addItems(["Tane Boyutu (ASTM E112)", "Porozite Oranı", "Dekarbürizasyon Derinliği", "Nodülarite (Küresellik)"])
        form.addRow("Analiz Tipi:", self.analysis_type)
        self.pixel_size = QLineEdit("1.0")
        form.addRow("Piksel Boyutu (µm):", self.pixel_size)
        self.magnification = QLineEdit("100")
        form.addRow("Büyütme (X):", self.magnification)
        self.btn_analyze = QPushButton("🔬 Analizi Başlat")
        self.btn_analyze.clicked.connect(self._run_analysis)
        form.addRow(self.btn_analyze)
        right_layout.addWidget(ctrl)
        
        self.report = QTextEdit()
        self.report.setReadOnly(True)
        right_layout.addWidget(QLabel("📋 Analiz Raporu:"))
        right_layout.addWidget(self.report)
        
        layout.addWidget(left, 3)
        layout.addWidget(right, 1)
    
    def _load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Görüntü Seç", "", "Images (*.png *.jpg *.bmp *.tif *.tiff)")
        if path:
            from matplotlib.image import imread
            self.loaded_image = imread(path)
            if len(self.loaded_image.shape) == 3:
                self.loaded_image = np.mean(self.loaded_image, axis=2)
            self.ax.clear()
            self.ax.imshow(self.loaded_image, cmap='gray')
            self.ax.set_title(f"Yüklendi: {os.path.basename(path)}", color='#cdd6f4')
            self.canvas.draw()
            self.report.setText(f"✅ Görüntü yüklendi: {os.path.basename(path)}\nBoyut: {self.loaded_image.shape}")
    
    def _run_analysis(self):
        if self.loaded_image is None:
            # Sentetik görüntü oluştur
            size = 300
            n_grains = 35
            points = np.random.rand(n_grains, 2) * size
            y, x = np.mgrid[0:size, 0:size]
            distances = np.sqrt((x[:,:,None]-points[:,0])**2+(y[:,:,None]-points[:,1])**2)
            labels = np.argmin(distances, axis=2)
            grain_intensities = np.random.randint(80, 200, n_grains)
            img = grain_intensities[labels]
            from scipy.ndimage import gaussian_filter
            img = gaussian_filter(img, sigma=1.2)
            self.loaded_image = img
            self.ax.clear()
            self.ax.imshow(img, cmap='gray')
            self.ax.set_title("Sentetik Tane Yapısı (Demo)", color='#cdd6f4')
            self.canvas.draw()
        
        img = self.loaded_image
        pixel_um = float(self.pixel_size.text())
        mag = float(self.magnification.text())
        
        # Otsu eşikleme
        from metallurgy.image_analyzer import auto_threshold_otsu, particle_analysis
        binary = auto_threshold_otsu(img)
        particles, labeled = particle_analysis(binary)
        
        if particles:
            areas_um2 = [p['area'] * pixel_um**2 for p in particles]
            diameters = [np.sqrt(4*a/np.pi) for a in areas_um2]
            mean_dia = np.mean(diameters)
            
            # ASTM E112 tane boyutu numarası
            # G = 2*log2(31.7 / d_mm) - 1  (d_mm cinsinden)
            d_mm = mean_dia / 1000
            if d_mm > 0:
                astm_gs = round(2 * np.log2(31.7 / d_mm) - 1, 1)
            else:
                astm_gs = "N/A"
            
            # Sonuçları göster
            self.ax.clear()
            self.ax.imshow(labeled, cmap='nipy_spectral')
            self.ax.set_title(f"Segmentasyon ({len(particles)} tane)", color='#cdd6f4')
            self.canvas.draw()
            
            self.report.setHtml(f"""
            <h3>📊 ASTM E112 Analiz Raporu</h3>
            <table>
            <tr><td><b>Analiz Tipi:</b></td><td>{self.analysis_type.currentText()}</td></tr>
            <tr><td><b>Tane Sayısı:</b></td><td>{len(particles)}</td></tr>
            <tr><td><b>Ortalama Tane Çapı:</b></td><td>{mean_dia:.2f} µm</td></tr>
            <tr><td><b>ASTM Tane Boyutu:</b></td><td>GS = {astm_gs}</td></tr>
            <tr><td><b>Büyütme:</b></td><td>{mag}X</td></tr>
            <tr><td><b>Standart Sapma:</b></td><td>{np.std(diameters):.2f} µm</td></tr>
            </table>
            """)
        else:
            self.report.setText("⚠️ Yeterli tane bulunamadı.")
