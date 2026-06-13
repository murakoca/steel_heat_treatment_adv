"""Karbon Difüzyonu Profili (basitleştirilmiş, sağlam)"""
import numpy as np

def simulate_carburizing(T_celsius, time_hours, Cs, C0, depth_mm=5.0):
    """
    T_celsius : sementasyon sıcaklığı (°C)
    time_hours: süre (saat)
    Cs        : yüzey karbon potansiyeli (% ağırlıkça)
    C0        : başlangıç karbon içeriği (% ağırlıkça)
    depth_mm  : hesaplanacak maksimum derinlik (mm)
    """
    # Basit bir difüzyon profili (hata fonksiyonu yerine üstel yaklaşım)
    x_mm = np.linspace(0, depth_mm, 200)

    # Sıcaklık ve süreye bağlı nüfuziyet derinliği (basitleştirilmiş)
    penetration = 0.5 * np.sqrt(time_hours) * np.exp(-5000 / (T_celsius + 273))

    # Profil: yüzeyde Cs, derinlikte C0'a yaklaşır
    profile = C0 + (Cs - C0) * np.exp(-x_mm / (penetration + 1e-6))
    return x_mm, profile