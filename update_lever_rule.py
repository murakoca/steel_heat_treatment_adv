#!/usr/bin/env python3
"""Lever Rule modülünü ve GUI sekmesini ekler - mevcut yapıyı bozmaz"""
import os, json

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# ═══════════════════════════════════════════════════════════
# 1. LEVER RULE MODÜLÜ
# ═══════════════════════════════════════════════════════════
write_file("metallurgy/lever_rule.py", '''"""Kaldıraç Kuralı (Lever Rule) Hesaplamaları"""
from dataclasses import dataclass

@dataclass
class LeverResult:
    phase_alpha_name: str = "α"
    phase_beta_name: str = "β"
    fraction_alpha: float = 0.0
    fraction_beta: float = 0.0
    composition_alpha: float = 0.0
    composition_beta: float = 0.0
    overall_composition: float = 0.0
    
    @property
    def percent_alpha(self): return self.fraction_alpha * 100
    @property
    def percent_beta(self): return self.fraction_beta * 100

def calculate(Ca: float, Cb: float, Co: float) -> LeverResult:
    """Kaldıraç kuralı ile faz oranlarını hesapla"""
    if abs(Cb - Ca) < 1e-10:
        raise ValueError("Faz kompozisyonları aynı olamaz")
    
    f_alpha = (Cb - Co) / (Cb - Ca)
    f_beta = (Co - Ca) / (Cb - Ca)
    
    # 0-1 aralığında olduğundan emin ol
    f_alpha = max(0.0, min(1.0, f_alpha))
    f_beta = max(0.0, min(1.0, f_beta))
    
    return LeverResult(
        fraction_alpha=f_alpha,
        fraction_beta=f_beta,
        composition_alpha=Ca,
        composition_beta=Cb,
        overall_composition=Co
    )

# Fe-C faz diyagramı için örnek noktalar
FE_C_EXAMPLES = {
    "Ötektoid (0.8% C, 727°C)": {"Ca": 0.022, "Cb": 6.67, "Co": 0.8, "alpha": "Ferrit (α)", "beta": "Sementit (Fe₃C)"},
    "Ötektoid Altı (0.4% C)": {"Ca": 0.022, "Cb": 6.67, "Co": 0.4, "alpha": "Ferrit (α)", "beta": "Sementit (Fe₃C)"},
    "Ötektoid Üstü (1.2% C)": {"Ca": 0.022, "Cb": 6.67, "Co": 1.2, "alpha": "Ferrit (α)", "beta": "Sementit (Fe₃C)"},
    "Cu-Ni (30% Ni)": {"Ca": 25, "Cb": 40, "Co": 30, "alpha": "α (Ni-az)", "beta": "Sıvı (Ni-zengin)"},
}
''')
print("✅ metallurgy/lever_rule.py")

# ═══════════════════════════════════════════════════════════
# 2. GUI GÜNCELLEMESİ (akıllı ekleme)
# ═══════════════════════════════════════════════════════════
main_py = os.path.join(BASE, "app", "main.py")

if not os.path.exists(main_py):
    print("❌ app/main.py bulunamadı!")
    exit(1)

with open(main_py, 'r', encoding='utf-8') as f:
    content = f.read()

# 2a. Import ekle
if "from metallurgy.lever_rule import" not in content:
    old = "from periodic.table import PeriodicTable"
    new = "from periodic.table import PeriodicTable\nfrom metallurgy.lever_rule import calculate as lever_calculate, FE_C_EXAMPLES"
    if old in content:
        content = content.replace(old, new)
        print("✅ Lever Rule import eklendi")
    else:
        print("⚠️ Import eklenemedi, manuel ekleyin: from metallurgy.lever_rule import calculate, FE_C_EXAMPLES")

# 2b. Lever Rule sekmesini ekle (Periyodik Tablo sekmesinden sonra)
lever_tab_code = '''
        # ===== LEVER RULE SEKMESI =====
        lever_tab = QWidget()
        lever_layout = QVBoxLayout(lever_tab)
        
        info_lbl = QLabel("<h2>⚖️ Kaldıraç Kuralı (Lever Rule)</h2>"
                         "İki fazlı bölgede faz oranlarını hesaplayın.")
        info_lbl.setWordWrap(True)
        lever_layout.addWidget(info_lbl)
        
        form_group = QGroupBox("Kompozisyon Değerleri")
        form = QFormLayout(form_group)
        
        self.lever_ca = QLineEdit("0.022")
        form.addRow("Cα (α fazı kompozisyonu %):", self.lever_ca)
        self.lever_cb = QLineEdit("6.67")
        form.addRow("Cβ (β fazı kompozisyonu %):", self.lever_cb)
        self.lever_co = QLineEdit("0.8")
        form.addRow("Co (Genel kompozisyon %):", self.lever_co)
        
        btn_layout = QHBoxLayout()
        calc_btn = QPushButton("Hesapla")
        calc_btn.clicked.connect(self._calc_lever)
        btn_layout.addWidget(calc_btn)
        
        # Örnekler
        example_cb = QComboBox()
        example_cb.addItem("--- Örnekler ---")
        for key in FE_C_EXAMPLES:
            example_cb.addItem(key)
        example_cb.currentTextChanged.connect(lambda t: self._load_lever_example(t))
        btn_layout.addWidget(example_cb)
        btn_layout.addStretch()
        form.addRow(btn_layout)
        
        lever_layout.addWidget(form_group)
        
        result_group = QGroupBox("Sonuç")
        result_layout = QVBoxLayout(result_group)
        self.lever_result = QLabel("<i>Değerleri girin ve Hesapla'ya basın...</i>")
        self.lever_result.setWordWrap(True)
        self.lever_result.setStyleSheet("font-size:14px; padding:10px;")
        result_layout.addWidget(self.lever_result)
        lever_layout.addWidget(result_group)
        
        lever_layout.addStretch()
        tabs.addTab(lever_tab, "⚖️ Lever Rule")
'''

marker = 'tabs.addTab(periodic_tab, "'
if marker in content:
    # Periyodik tablo sekmesinden sonraki ilk boşluğa ekle
    # Önce periyodik tablo satırını bul
    lines = content.split('\n')
    new_lines = []
    added = False
    for line in lines:
        new_lines.append(line)
        if marker in line and not added:
            new_lines.append(lever_tab_code)
            added = True
    content = '\n'.join(new_lines)
    print("✅ Lever Rule sekmesi eklendi")
else:
    print("⚠️ Periyodik tablo sekmesi bulunamadı, lever rule sekmesi eklenemedi")

# 2c. _calc_lever ve _load_lever_example metodlarını ekle
new_methods = '''
    def _calc_lever(self):
        try:
            Ca = float(self.lever_ca.text())
            Cb = float(self.lever_cb.text())
            Co = float(self.lever_co.text())
            result = lever_calculate(Ca, Cb, Co)
            txt = f"<b>Faz Oranları:</b><br>"
            txt += f"α fazı: <b>%{result.percent_alpha:.1f}</b><br>"
            txt += f"β fazı: <b>%{result.percent_beta:.1f}</b><br><br>"
            txt += f"<b>Kaldıraç Kuralı:</b><br>"
            txt += f"fα = (Cβ - Co) / (Cβ - Cα) = ({Cb} - {Co}) / ({Cb} - {Ca}) = <b>{result.fraction_alpha:.4f}</b><br>"
            txt += f"fβ = (Co - Cα) / (Cβ - Cα) = ({Co} - {Ca}) / ({Cb} - {Ca}) = <b>{result.fraction_beta:.4f}</b>"
            self.lever_result.setText(txt)
        except ValueError as e:
            self.lever_result.setText(f"<span style='color:#f38ba8;'>Hata: {e}</span>")

    def _load_lever_example(self, name):
        if name in FE_C_EXAMPLES:
            ex = FE_C_EXAMPLES[name]
            self.lever_ca.setText(str(ex["Ca"]))
            self.lever_cb.setText(str(ex["Cb"]))
            self.lever_co.setText(str(ex["Co"]))
            self._calc_lever()
'''

if '_calc_lever' not in content:
    # _show_element metodundan sonra ekle
    marker2 = 'def _show_element(self, num):'
    if marker2 in content:
        content = content.replace(marker2, new_methods + '\n    ' + marker2)
        print("✅ Lever Rule metodları eklendi")
    else:
        # En sona ekle (main fonksiyonundan önce)
        marker3 = 'def main():'
        if marker3 in content:
            content = content.replace(marker3, new_methods + '\n\n' + marker3)
            print("✅ Lever Rule metodları eklendi (main öncesi)")
        else:
            print("⚠️ Metodlar eklenemedi")

# Kaydet
with open(main_py, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n🎉 Güncelleme tamamlandı!")
print("Çalıştır: python main.py")
print("Yeni sekme: ⚖️ Lever Rule")