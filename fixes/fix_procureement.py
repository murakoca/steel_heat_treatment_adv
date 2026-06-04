#!/usr/bin/env python3
"""Procurement modülü için eksik metodları ekler"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
main_py = os.path.join(BASE, "app", "main.py")

with open(main_py, 'r', encoding='utf-8') as f:
    content = f.read()

# Eksik metodları tanımla
missing_methods = '''
    def _switch_proc_lang(self, lang):
        """Dil değiştir"""
        self.proc_lang = lang
        self.proc_tr_btn.setChecked(lang == "tr")
        self.proc_en_btn.setChecked(lang == "en")
        self._build_procurement_ui()
    
    def _build_procurement_ui(self):
        """Satın alma arayüzünü yeniden oluştur"""
        import json
        lang = self.proc_lang
        data = self.proc_data[lang]
        
        while self.proc_scroll_layout.count():
            item = self.proc_scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        title = QLabel(f"<h2>{data['title']}</h2>")
        title.setWordWrap(True)
        self.proc_scroll_layout.addWidget(title)
        
        subtitle = QLabel(f"<i>{data['subtitle']}</i>")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color:#a6adc8; font-size:14px; margin-bottom:15px;")
        self.proc_scroll_layout.addWidget(subtitle)
        
        for key, section in data["sections"].items():
            grp = QGroupBox(section["title"])
            grp_lay = QVBoxLayout(grp)
            for line in section["content"]:
                lbl = QLabel(line)
                lbl.setWordWrap(True)
                if line.startswith("•"):
                    lbl.setStyleSheet("color:#cdd6f4; padding-left:15px;")
                elif line == "":
                    continue
                elif not line.startswith(" ") and line != "":
                    lbl.setStyleSheet("color:#cdd6f4; font-weight:bold;")
                else:
                    lbl.setStyleSheet("color:#cdd6f4;")
                grp_lay.addWidget(lbl)
            self.proc_scroll_layout.addWidget(grp)
        
        self.proc_scroll_layout.addStretch()
        
        calc = data["calculator"]
        parent = self.proc_calc_layout.parentWidget()
        if parent:
            old_group = parent.findChild(QGroupBox, "")
            if old_group:
                old_group.setTitle(calc["title"])
        
        while self.proc_calc_layout.count():
            item = self.proc_calc_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        a_group = QGroupBox(calc["supplier_a"])
        a_layout = QFormLayout(a_group)
        self.proc_a_price = QLineEdit("100000")
        a_layout.addRow(f"{calc['purchase_price']} (TL):", self.proc_a_price)
        self.proc_a_rework = QLineEdit("20000")
        a_layout.addRow(f"{calc['rework_cost']} (TL):", self.proc_a_rework)
        self.proc_a_delay = QLineEdit("15000")
        a_layout.addRow(f"{calc['delay_cost']} (TL):", self.proc_a_delay)
        self.proc_a_quality = QLineEdit("10000")
        a_layout.addRow(f"{calc['quality_cost']} (TL):", self.proc_a_quality)
        self.proc_a_total = QLabel("")
        a_layout.addRow(f"{calc['total']}:", self.proc_a_total)
        self.proc_calc_layout.addWidget(a_group)
        
        b_group = QGroupBox(calc["supplier_b"])
        b_layout = QFormLayout(b_group)
        self.proc_b_price = QLineEdit("110000")
        b_layout.addRow(f"{calc['purchase_price']} (TL):", self.proc_b_price)
        self.proc_b_rework = QLineEdit("5000")
        b_layout.addRow(f"{calc['rework_cost']} (TL):", self.proc_b_rework)
        self.proc_b_delay = QLineEdit("0")
        b_layout.addRow(f"{calc['delay_cost']} (TL):", self.proc_b_delay)
        self.proc_b_quality = QLineEdit("0")
        b_layout.addRow(f"{calc['quality_cost']} (TL):", self.proc_b_quality)
        self.proc_b_total = QLabel("")
        b_layout.addRow(f"{calc['total']}:", self.proc_b_total)
        self.proc_calc_layout.addWidget(b_group)
        
        calc_btn = QPushButton("🔄 Hesapla")
        calc_btn.clicked.connect(self._calc_procurement)
        self.proc_calc_layout.addWidget(calc_btn)
        
        self.proc_result = QLabel("")
        self.proc_result.setStyleSheet("font-size:16px; font-weight:bold; color:#89b4fa; padding:10px;")
        self.proc_calc_layout.addWidget(self.proc_result)
        
        self._calc_procurement()
    
    def _calc_procurement(self):
        """Tedarikçi maliyetlerini hesapla"""
        try:
            a = SupplierCost(
                name="A",
                purchase_price=float(self.proc_a_price.text()),
                rework_cost=float(self.proc_a_rework.text()),
                delay_cost=float(self.proc_a_delay.text()),
                quality_cost=float(self.proc_a_quality.text())
            )
            b = SupplierCost(
                name="B",
                purchase_price=float(self.proc_b_price.text()),
                rework_cost=float(self.proc_b_rework.text()),
                delay_cost=float(self.proc_b_delay.text()),
                quality_cost=float(self.proc_b_quality.text())
            )
            
            self.proc_a_total.setText(f"{a.total:,.0f} TL")
            self.proc_b_total.setText(f"{b.total:,.0f} TL")
            
            winner, diff = compare_suppliers(a, b)
            lang = self.proc_lang
            if winner is None:
                msg = "İki tedarikçi eşit maliyete sahip." if lang == "tr" else "Both suppliers have equal cost."
            else:
                cheaper = "daha ekonomik!" if lang == "tr" else "is more economical!"
                msg = f"✅ {winner.name} {cheaper} ({diff:,.0f} TL fark)"
            
            self.proc_result.setText(msg)
        except ValueError:
            self.proc_result.setText("⚠️ Lütfen geçerli sayılar girin.")
'''

# Metodları ekle (eğer yoksa)
if '_switch_proc_lang' not in content:
    # def main() satırından önce ekle
    marker = '\n\ndef main():'
    if marker in content:
        content = content.replace(marker, missing_methods + marker)
        print("✅ Eksik metodlar eklendi (main öncesi)")
    else:
        # Sınıf sonunu bul
        last_method = content.rfind('    def ')
        if last_method > 0:
            # Son metodun bitişini bul
            insert_pos = content.find('\n\n', last_method)
            if insert_pos < 0:
                insert_pos = len(content)
            content = content[:insert_pos] + missing_methods + content[insert_pos:]
            print("✅ Eksik metodlar eklendi (sınıf sonu)")
        else:
            print("❌ Uygun ekleme noktası bulunamadı")
else:
    print("⏭️ Metodlar zaten mevcut")

# Kaydet
with open(main_py, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n🎉 Düzeltme tamamlandı! Şimdi çalıştır: python main.py")