
"""Mipar - ML Destekli Mikroyapı Analizi"""
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from scipy import ndimage
import os

class MiparWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mipar - ML Mikroyapı Analizi")
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
        self.btn_load = QPushButton("📂 Görüntü Yükle")
        self.btn_load.clicked.connect(self._load_image)
        left_layout.addWidget(self.btn_load)
        
        right = QWidget(); right.setMaximumWidth(300)
        right_layout = QVBoxLayout(right)
        ctrl = QGroupBox("Segmentasyon")
        form = QFormLayout(ctrl)
        self.method = QComboBox()
        self.method.addItems(["K-Means", "Watershed", "Otsu + Morfoloji"])
        form.addRow("Yöntem:", self.method)
        self.n_clusters = QLineEdit("3"); form.addRow("Küme Sayısı:", self.n_clusters)
        self.btn_seg = QPushButton("🤖 Segmentasyon Yap")
        self.btn_seg.clicked.connect(self._segment)
        form.addRow(self.btn_seg)
        right_layout.addWidget(ctrl)
        self.result = QTextEdit(); self.result.setReadOnly(True)
        right_layout.addWidget(self.result)
        
        layout.addWidget(left, 3)
        layout.addWidget(right, 1)
    
    def _load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Görüntü Seç", "", "Images (*.png *.jpg *.bmp)")
        if path:
            from matplotlib.image import imread
            self.loaded_image = imread(path)
            if len(self.loaded_image.shape) == 3:
                self.loaded_image = np.mean(self.loaded_image, axis=2)
            self.ax.clear()
            self.ax.imshow(self.loaded_image, cmap='gray')
            self.canvas.draw()
    
    def _segment(self):
        if self.loaded_image is None:
            size = 200; n = 25
            points = np.random.rand(n,2)*size
            y,x = np.mgrid[0:size,0:size]
            d = np.sqrt((x[:,:,None]-points[:,0])**2+(y[:,:,None]-points[:,1])**2)
            labels = np.argmin(d,axis=2)
            self.loaded_image = np.random.randint(60,200,n)[labels]
            from scipy.ndimage import gaussian_filter
            self.loaded_image = gaussian_filter(self.loaded_image, sigma=1)
        
        img = self.loaded_image
        k = int(self.n_clusters.text())
        
        from sklearn.cluster import KMeans
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        segmented = km.fit_predict(img.reshape(-1, 1)).reshape(img.shape)
        
        self.ax.clear()
        self.ax.imshow(segmented, cmap='viridis')
        self.ax.set_title(f"K-Means (k={k})", color='#cdd6f4')
        self.canvas.draw()
        
        unique, counts = np.unique(segmented, return_counts=True)
        self.result.setHtml(f"<b>Küme Sayısı:</b> {k}<br>" + 
                           "<br>".join([f"Küme {u}: %{c/segmented.size*100:.1f}" for u,c in zip(unique,counts)]))
