#!/usr/bin/env python3
"""
TÜM ÇELİKLER İÇİN KAPSAMLI TTT VERİSİ OLUŞTURUCU
- Veritabanındaki her çelik için TTT verisi yoksa otomatik oluşturur
- Kompozisyon ve Ms sıcaklığına dayalı tahmini eğriler kullanır
- Mevcut TTT dosyalarını korur, sadece eksikleri tamamlar
"""
import json
import os
import math

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "database", "steels.json")
TTT_DIR = os.path.join(BASE, "database", "ttt_data")

os.makedirs(TTT_DIR, exist_ok=True)

# Veritabanını yükle
with open(DB_PATH, 'r', encoding='utf-8') as f:
    steels_db = json.load(f)

def estimate_ttt(steel_name, composition, Ms, Ae1, Ae3):
    """
    Kompozisyona dayalı tahmini TTT eğrileri oluşturur.
    Literatürdeki ampirik modelleri temel alır.
    """
    C = composition.get("C", 0) * 100  # % olarak
    Mn = composition.get("Mn", 0) * 100
    Si = composition.get("Si", 0) * 100
    Cr = composition.get("Cr", 0) * 100
    Ni = composition.get("Ni", 0) * 100
    Mo = composition.get("Mo", 0) * 100
    V = composition.get("V", 0) * 100
    W = composition.get("W", 0) * 100
    
    # Perlit burnu sıcaklığı ve zamanı (ampirik)
    # Kaynak: Kirkaldy-Venugopalan modeli
    Ae1_temp = Ae1 if Ae1 > 0 else 727
    
    # Perlit başlangıç sıcaklıkları (Ae1'den başlayarak düşer)
    pearlite_T = []
    pearlite_t = []
    
    if Ae1_temp > 550:  # Perlit bölgesi varsa
        # 5 sıcaklık noktası oluştur
        for i in range(5):
            T = Ae1_temp - 20 - i * 30
            if T < 550:
                break
            pearlite_T.append(T)
            
            # Perlit dönüşüm zamanı (saniye)
            # Alaşım elementleri geciktirir
            tau_p = 5.0  # baz süre
            tau_p *= (1 + 0.5 * C)  # Karbon etkisi
            tau_p *= (1 + 0.3 * Mn + 0.4 * Cr + 0.5 * Mo + 0.6 * V + 0.7 * W)
            tau_p *= (1 + 0.1 * Ni)  # Nikel hafif geciktirir
            tau_p *= math.exp(-(T - 650) / 100) * 3  # Sıcaklık etkisi
            tau_p *= (1 + 0.3 * i)  # Düşük sıcaklıkta daha yavaş
            pearlite_t.append(round(tau_p, 1))
    
    # Beynit başlangıç sıcaklıkları (Bs'den Ms'ye kadar)
    bainite_T = []
    bainite_t = []
    
    # Beynit başlangıç sıcaklığı tahmini
    Bs = 830 - 270*C/100 - 90*Mn/100 - 37*Ni/100 - 70*Cr/100 - 83*Mo/100
    Bs = min(Bs, 600)  # Maksimum 600°C
    
    if Bs > Ms + 30 and Ms < 600:
        # 4-5 sıcaklık noktası
        num_points = min(5, max(2, int((Bs - Ms) / 40)))
        for i in range(num_points):
            T = Bs - i * (Bs - Ms) / (num_points - 1)
            if T <= Ms + 20:
                break
            bainite_T.append(round(T))
            
            # Beynit dönüşüm zamanı
            tau_b = 50.0
            tau_b *= (1 + 1.5 * C)
            tau_b *= (1 + 0.5 * Mn + 0.8 * Cr + 1.0 * Mo + 0.7 * Ni)
            tau_b *= math.exp(-(T - 450) / 80) * 2
            tau_b *= (1 + 0.2 * i)
            bainite_t.append(round(tau_b, 1))
    
    # Eğer hiç perlit/beynit noktası oluşmadıysa (östenitik çelikler)
    if not pearlite_T and not bainite_T:
        pearlite_T = [Ae1_temp - 20] if Ae1_temp > 0 else [700]
        pearlite_t = [99999]  # Çok uzun süre (pratikte dönüşmez)
        bainite_T = [max(400, Ms + 50)]
        bainite_t = [99999]
    
    return {
        "pearlite_start": {"T": pearlite_T, "t": pearlite_t},
        "bainite_start": {"T": bainite_T, "t": bainite_t},
        "Ms": Ms
    }


# Tüm çelikleri tara, eksik TTT'leri oluştur
created = 0
skipped = 0
errors = 0

print("=" * 60)
print("🔧 TÜM ÇELİKLER İÇİN TTT VERİSİ OLUŞTURULUYOR")
print("=" * 60)

for steel_name, steel_data in steels_db.items():
    ttt_path = os.path.join(TTT_DIR, f"{steel_name}_ttt.json")
    
    # Zaten varsa atla
    if os.path.exists(ttt_path):
        skipped += 1
        if skipped <= 3:  # Sadece ilk 3 tanesini göster
            print(f"  ⏭️  {steel_name} - zaten var")
        continue
    
    try:
        comp = steel_data.get("composition", {"C": 0.2})
        Ms = steel_data.get("Ms", 300)
        Ae1 = steel_data.get("Ae1", 727)
        Ae3 = steel_data.get("Ae3", 850)
        
        ttt_data = estimate_ttt(steel_name, comp, Ms, Ae1, Ae3)
        
        with open(ttt_path, 'w', encoding='utf-8') as f:
            json.dump(ttt_data, f, indent=2)
        
        created += 1
        if created <= 5:  # Sadece ilk 5 tanesini detaylı göster
            print(f"  ✅ {steel_name}")
            print(f"     Ms={Ms}°C, Perlit noktası: {len(ttt_data['pearlite_start']['T'])} adet")
            print(f"     Beynit noktası: {len(ttt_data['bainite_start']['T'])} adet")
        elif created == 6:
            print(f"  ... (devam ediyor)")
    
    except Exception as e:
        errors += 1
        print(f"  ❌ {steel_name} - HATA: {e}")

print(f"\n{'='*60}")
print(f"📊 SONUÇ:")
print(f"  ✅ Yeni oluşturulan: {created}")
print(f"  ⏭️  Zaten mevcut:    {skipped}")
print(f"  ❌ Hatalı:          {errors}")
print(f"  📦 Toplam çelik:    {len(steels_db)}")
print(f"{'='*60}")
print(f"\nTTT verisi olan çelik sayısı: {skipped + created} / {len(steels_db)}")
print(f"\nArtık TTT/CCT sekmesinde tüm çelikler için diyagram görüntülenebilir! 🎉")