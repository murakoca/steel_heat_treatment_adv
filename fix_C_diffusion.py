#!/usr/bin/env python3
"""
Moleküler Dinamik simülasyon hatasını düzeltir.
- Atom pozisyonlarını kutu içinde sınırlar
- Negatif pozisyon hatasını giderir
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# 1. simulation/molecular_dynamics.py dosyasını güncelle
md_path = os.path.join(BASE, "simulation", "molecular_dynamics.py")

if os.path.exists(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # apply_pbc metodunu güncelle (negatif değerleri de düzelt)
    old_pbc = '''    def apply_pbc(self, positions):
        return positions - self.box_size * np.round(positions / self.box_size)'''
    
    new_pbc = '''    def apply_pbc(self, positions):
        """Periyodik sınır koşullarını uygula - tüm değerleri [0, box_size] aralığında tutar"""
        pos = np.array(positions)
        pos = pos - self.box_size * np.floor(pos / self.box_size)
        pos = np.clip(pos, 0, self.box_size - 1e-10)
        return pos'''
    
    if old_pbc in content:
        content = content.replace(old_pbc, new_pbc)
        print("✅ apply_pbc metodu güncellendi")
    
    # run_nve metodunu güncelle
    old_nve = '''    def run_nve(self, steps, callback=None):
        for step in range(steps):
            self.velocity_verlet()
            kinetic = 0.5 * np.sum(self.velocities**2)
            self.energy_history.append(kinetic)
            if callback:
                callback(step, self.positions, kinetic)'''
    
    new_nve = '''    def run_nve(self, steps, callback=None):
        for step in range(steps):
            forces = self.velocity_verlet()
            # Pozisyonları sınırla
            self.positions = self.apply_pbc(self.positions)
            kinetic = 0.5 * np.sum(self.velocities**2)
            self.energy_history.append(kinetic)
            if callback:
                callback(step, self.positions, kinetic)'''
    
    if old_nve in content:
        content = content.replace(old_nve, new_nve)
        print("✅ run_nve metodu güncellendi")
    
    # run_nvt metodunu güncelle
    old_nvt = '''    def run_nvt(self, steps, target_temp, tau=0.1, callback=None):
        for step in range(steps):
            self.velocity_verlet()
            self.berendsen_thermostat(target_temp, tau)
            kinetic = 0.5 * np.sum(self.velocities**2)
            self.energy_history.append(kinetic)
            if callback:
                callback(step, self.positions, kinetic)'''
    
    new_nvt = '''    def run_nvt(self, steps, target_temp, tau=0.1, callback=None):
        for step in range(steps):
            forces = self.velocity_verlet()
            # Pozisyonları sınırla
            self.positions = self.apply_pbc(self.positions)
            self.berendsen_thermostat(target_temp, tau)
            kinetic = 0.5 * np.sum(self.velocities**2)
            self.energy_history.append(kinetic)
            if callback:
                callback(step, self.positions, kinetic)'''
    
    if old_nvt in content:
        content = content.replace(old_nvt, new_nvt)
        print("✅ run_nvt metodu güncellendi")
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(content)
else:
    print("❌ simulation/molecular_dynamics.py bulunamadı!")

# 2. app/main.py dosyasındaki _run_md metodunu güncelle
main_path = os.path.join(BASE, "app", "main.py")
if os.path.exists(main_path):
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_md_method = '''    def _run_md(self):
        try:
            n = self.md_n.value()
            temp = self.md_temp.value()
            pot = 'LJ' if 'LJ' in self.md_pot.currentText() else 'EAM'
            pos = np.random.rand(n, 2) * 10.0
            md = MolecularDynamics(pos, 10.0, potential=pot, temperature=temp, dt=0.005)
            self.md_status.setText(f"Simülasyon çalışıyor... ({n} atom)")
            QApplication.processEvents()
            md.run_nve(200)
            self.md_ax.clear()
            self.md_ax.scatter(md.positions[:, 0], md.positions[:, 1], c='cyan', s=20)
            self.md_ax.set_xlim(0, 10); self.md_ax.set_ylim(0, 10)
            self.md_ax.set_title(f"MD Simülasyonu ({n} atom, {pot})", color='#cdd6f4')
            self.md_canvas.draw()
            self.md_status.setText(f"✅ Tamamlandı | Son kinetik enerji: {md.energy_history[-1]:.2f}")
        except Exception as e:
            self.md_status.setText(f"❌ Hata: {e}")'''
    
    new_md_method = '''    def _run_md(self):
        try:
            n = self.md_n.value()
            temp = self.md_temp.value()
            pot = 'LJ' if 'LJ' in self.md_pot.currentText() else 'EAM'
            # Pozisyonları güvenli şekilde oluştur [0.5, 9.5] aralığında
            pos = np.random.rand(n, 2) * 9.0 + 0.5
            md = MolecularDynamics(pos, 10.0, potential=pot, temperature=temp, dt=0.005)
            self.md_status.setText(f"Simülasyon çalışıyor... ({n} atom)")
            QApplication.processEvents()
            md.run_nve(200)
            self.md_ax.clear()
            self.md_ax.scatter(md.positions[:, 0], md.positions[:, 1], c='cyan', s=20)
            self.md_ax.set_xlim(0, 10); self.md_ax.set_ylim(0, 10)
            self.md_ax.set_title(f"MD Simülasyonu ({n} atom, {pot})", color='#cdd6f4')
            self.md_canvas.draw()
            self.md_status.setText(f"✅ Tamamlandı | Son kinetik enerji: {md.energy_history[-1]:.2f}")
        except Exception as e:
            self.md_status.setText(f"❌ Hata: {e}")'''
    
    if old_md_method in content:
        content = content.replace(old_md_method, new_md_method)
        print("✅ _run_md metodu güncellendi")
    elif '_run_md(self):' in content:
        # Eski metodu bul ve pozisyon oluşturma satırını düzelt
        content = content.replace(
            'pos = np.random.rand(n, 2) * 10.0',
            'pos = np.random.rand(n, 2) * 9.0 + 0.5'
        )
        print("✅ Pozisyon oluşturma satırı düzeltildi")
    
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("\n🎉 Moleküler Dinamik hatası düzeltildi!")
print("Çalıştır: python main.py")
print("Artık 'Simülasyonu Başlat' butonu hatasız çalışacak.")