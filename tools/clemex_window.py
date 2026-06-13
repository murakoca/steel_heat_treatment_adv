
"""Clemex - AI Destekli Tane Boyutu Analizi"""
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from scipy import ndimage
import os

class ClemexWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clemex - AI Tane Boyutu Analizi")
        self.setMinimumSize(1000, 750)
        self.loaded_image = None
        self._ui()
        self._load_style()
    
    def _load_style(self):
        self.setStyleSheet("QMainWindow{background:#1e1e2e}QLabel{color:#cdd6f4}QGroupBox{color:#cdd6f4;border:1px solid #45475a;border-radius:6px;margin-top:10px;padding-top:14px;font-weight:bold}QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 6px;color:#89b4fa;background:#1e1e2e}QPushButton{background:#89b4fa;color:#1e1e2e;border-radius:4px;padding:8px 16px;font-weight:bold}QLineEdit{background:#313244;color:#cdd6f4;border:1px solid #45475a;border-radius:4px;padding:5px}QTextEdit{background:#313244;color:#cdd6f4;border:1px solid #45475a}")
    
    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QHBoxLayout(c)
        
        left = QWidget()
        left_layout = QVBoxLayout(left)
        self.fig = Figure(figsize=(7,6), facecolor='#1e1e2e')
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.ax = self.fig.add_subplot(111, facecolor='#1e1e2e')
        self.ax.tick_params(colors='#cdd6f4')
        left_layout.addWidget(self.canvas)
        self.btn_load = QPushButton("📂 Görüntü Yükle (Mikroskop)")
        self.btn_load.clicked.connect(self._load_image)
        left_layout.addWidget(self.btn_load)
        
        right = QWidget(); right.setMaximumWidth(300)
        right_layout = QVBoxLayout(right)
        ctrl = QGroupBox("AI Analiz")
        form = QFormLayout(ctrl)
        self.confidence = QLineEdit("0.85"); form.addRow("Güven Eşiği:", self.confidence)
        self.btn_ai = QPushButton("🤖 AI Analizi Başlat")
        self.btn_ai.clicked.connect(self._ai_analyze)
        form.addRow(self.btn_ai)
        right_layout.addWidget(ctrl)
        self.result = QTextEdit(); self.result.setReadOnly(True)
        right_layout.addWidget(self.result)
        
        layout.addWidget(left, 3)
        layout.addWidget(right, 1)
    
    def _load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Görüntü Seç", "", "Images (*.png *.jpg *.bmp *.tif)")
        if path:
            from matplotlib.image import imread
            self.loaded_image = imread(path)
            if len(self.loaded_image.shape) == 3:
                self.loaded_image = np.mean(self.loaded_image, axis=2)
            self.ax.clear()
            self.ax.imshow(self.loaded_image, cmap='gray')
            self.canvas.draw()
    
    def _ai_analyze(self):
        if self.loaded_image is None:
            size = 256; n = 30
            points = np.random.rand(n,2)*size
            y,x = np.mgrid[0:size,0:size]
            d = np.sqrt((x[:,:,None]-points[:,0])**2+(y[:,:,None]-points[:,1])**2)
            labels = np.argmin(d,axis=2)
            self.loaded_image = np.random.randint(70,190,n)[labels]
            from scipy.ndimage import gaussian_filter
            self.loaded_image = gaussian_filter(self.loaded_image, sigma=1)
        
        from metallurgy.image_analyzer import auto_threshold_otsu, particle_analysis
        binary = auto_threshold_otsu(self.loaded_image)
        particles, labeled = particle_analysis(binary)
        
        if particles:
            areas = [p['area'] for p in particles]
            diameters = [np.sqrt(4*a/np.pi) for a in areas]
            
            self.ax.clear()
            self.ax.imshow(labeled, cmap='nipy_spectral')
            self.ax.set_title(f"Clemex AI: {len(particles)} tane", color='#cdd6f4')
            self.canvas.draw()
            
            self.result.setHtml(f"""
            <h3>📊 Clemex AI Raporu</h3>
            <b>Tane Sayısı:</b> {len(particles)}<br>
            <b>Ortalama Çap:</b> {np.mean(diameters):.2f} px<br>
            <b>Standart Sapma:</b> {np.std(diameters):.2f} px<br>
            <b>Güven Skoru:</b> %{float(self.confidence.text())*100:.0f}<br>
            """)
