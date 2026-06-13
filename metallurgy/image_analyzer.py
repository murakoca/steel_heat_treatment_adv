
"""Bilimsel Görüntü Analizi (ImageJ benzeri)"""
import numpy as np
from scipy import ndimage

def threshold(image, value=128):
    return (image > value).astype(np.uint8) * 255

def auto_threshold_otsu(image):
    if image.max() <= 1:
        image = (image * 255).astype(np.uint8)
    hist, _ = np.histogram(image.flatten(), 256, [0, 256])
    total = image.size
    sum_all = np.sum(np.arange(256) * hist)
    sum_b, w_b = 0, 0
    max_var, best = 0, 128
    for t in range(256):
        w_b += hist[t]
        if w_b == 0: continue
        w_f = total - w_b
        if w_f == 0: break
        sum_b += t * hist[t]
        mean_b = sum_b / w_b
        mean_f = (sum_all - sum_b) / w_f
        var = w_b * w_f * (mean_b - mean_f)**2
        if var > max_var:
            max_var = var
            best = t
    return threshold(image, best)

def particle_analysis(binary):
    labeled, n = ndimage.label(binary > 0)
    particles = []
    for i in range(1, n+1):
        area = np.sum(labeled == i)
        if area > 10:
            y, x = np.where(labeled == i)
            particles.append({'id': i, 'area': area, 'diameter': np.sqrt(4*area/np.pi)})
    return particles, labeled

def grain_size_distribution(labels, pixel_size=1.0):
    areas = []
    for label in range(1, labels.max()+1):
        area = np.sum(labels == label) * pixel_size**2
        if area > 0: areas.append(area)
    return np.array(areas)

def phase_fraction(binary):
    return np.sum(binary > 0) / binary.size
