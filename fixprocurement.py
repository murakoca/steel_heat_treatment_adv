#!/usr/bin/env python3
"""app/main.py içindeki _build_procurement_ui metodunu onarır"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
main_py = os.path.join(BASE, "app", "main.py")

with open(main_py, 'r', encoding='utf-8') as f:
    content = f.read()

# Hatalı metodun tamamını bul ve sağlam sürümle değiştir
old_method = '''    def _build_procurement_ui(self):
        lang = self.proc_lang; data = self.proc_data[lang]
        while self.proc_scroll_layout.count():
            item = self.proc_scroll_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        title = QLabel(f"<h2>{data['title']}</h2>"); title.setWordWrap(True)
        self.proc_scroll_layout.addWidget(title)
        subtitle = QLabel(f"<i>{data['subtitle']}</i>"); subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color:#a6adc8; font-size:14px; margin-bottom:15px;")
        self.proc_scroll_layout.addWidget(subtitle)
        for key, section in data["sections"].items():
            grp = QGroupBox(section["title"]); grp_lay = QVBoxLayout(grp)
            for line in section["content"]:
                lbl = QLabel(line); lbl.setWordWrap(True)
                if line.startswith("•"): lbl.setStyleSheet("color:#cdd6f4; padding-left:15px;")
                elif line == "": continue
                elif not line.startswith(" ") and line != "": lbl.setStyleSheet("color:#cdd6f4; font-weight:bold;")
                else: lbl.setStyleSheet("color:#cdd6f4;")
                grp_lay.addWidget(lbl)
            self.proc_scroll_layout.addWidget(grp)
        self.proc_scroll_layout.addStretch()
        calc = data["calculator"]
        parent = self.proc_calc_layout.parentWidget()
        if parent:
            old_group = parent.findChild(QGroupBox, "")
            if old_group: old_group.setTitle(calc["title"])
        while self.proc_calc_layout.count():
            item = self.proc_calc_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        a_group = QGroupBox(calc["supplier_a"]); a_layout = QFormLayout(a_group)
        self.proc_a_price = QLineEdit("100000"); a_layout.addRow(f"{calc['purchase_price']} (TL):", self.proc_a_price)
        self.proc_a_rework = QLineEdit("20000"); a_layout.addRow(f"{calc['rework_cost']} (TL):", self.proc_a_rework)
        self.proc_a_delay = QLineEdit("15000"); a_layout.addRow(f"{calc['delay_cost']} (TL):", self.proc_a_delay)
        self.proc_a_quality = QLineEdit("10000"); a_layout.addRow(f"{calc['quality_cost']} (TL):", self.proc_a_quality)
        self.proc_a_total = QLabel(""); a_layout.addRow(f"{calc['total']}:", self.proc_a_total)
        self.proc_calc_layout.addWidget(a_group)
        b_group = QGroupBox(calc["supplier_b"]); b_layout = QFormLayout(b_group)
        self.proc_b_price = QLineEdit("110000"); b_layout.addRow(f"{calc['purchase_price']} (TL):", self.proc_b_price)
        self.proc_b_rework = QLineEdit("5000"); b_layout.addRow(f"{calc['rework_cost']} (TL):", self.proc_b_rework)
        self.proc_b_delay = QLineEdit("0"); b_layout.addRow(f"{calc['delay_cost']} (TL):", self.proc_b_delay)
        self.proc_b_quality = QLineEdit("0"); b_layout.addRow(f"{calc['quality_cost']} (TL):", self.proc_b_quality)
        self.proc_b_total = QLabel(""); b_layout.addRow(f"{calc['total']}:", self.proc_b_total)
        self.proc_calc_layout.addWidget(b_group)
        calc_btn = QPushButton("🔄 Hesapla"); calc_btn.clicked.connect(self._calc_procurement)
        self.proc_calc_layout.addWidget(calc_btn)
        self.proc_result = QLabel("")
        self.proc_result.setStyleSheet("font-size:16px; font-weight:bold; color:#89b4fa; padding:10px;")
        self.proc_calc_layout.addWidget(self.proc_result)
        self._calc_procurement()'''

# Bu metodun satırlarında "self.proc_" sonrası yarım kalmış olabilir.
# Daha güvenli: metodun tamamını sağlam bir kopyayla değiştir.
if 'self.proc_a_price = QLineEdit("100000")' in content:
    print("✅ Procurement metodu zaten düzgün görünüyor, sorun başka yerde olabilir.")
else:
    # Metodu yeniden yaz
    new_method = '''
    def _build_procurement_ui(self):
        lang = self.proc_lang; data = self.proc_data[lang]
        while self.proc_scroll_layout.count():
            item = self.proc_scroll_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        title = QLabel(f"<h2>{data['title']}</h2>"); title.setWordWrap(True)
        self.proc_scroll_layout.addWidget(title)
        subtitle = QLabel(f"<i>{data['subtitle']}</i>"); subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color:#a6adc8; font-size:14px; margin-bottom:15px;")
        self.proc_scroll_layout.addWidget(subtitle)
        for key, section in data["sections"].items():
            grp = QGroupBox(section["title"]); grp_lay = QVBoxLayout(grp)
            for line in section["content"]:
                lbl = QLabel(line); lbl.setWordWrap(True)
                if line.startswith("•"): lbl.setStyleSheet("color:#cdd6f4; padding-left:15px;")
                elif line == "": continue
                elif not line.startswith(" ") and line != "": lbl.setStyleSheet("color:#cdd6f4; font-weight:bold;")
                else: lbl.setStyleSheet("color:#cdd6f4;")
                grp_lay.addWidget(lbl)
            self.proc_scroll_layout.addWidget(grp)
        self.proc_scroll_layout.addStretch()
        calc = data["calculator"]
        parent = self.proc_calc_layout.parentWidget()
        if parent:
            old_group = parent.findChild(QGroupBox, "")
            if old_group: old_group.setTitle(calc["title"])
        while self.proc_calc_layout.count():
            item = self.proc_calc_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        a_group = QGroupBox(calc["supplier_a"]); a_layout = QFormLayout(a_group)
        self.proc_a_price = QLineEdit("100000"); a_layout.addRow(f"{calc['purchase_price']} (TL):", self.proc_a_price)
        self.proc_a_rework = QLineEdit("20000"); a_layout.addRow(f"{calc['rework_cost']} (TL):", self.proc_a_rework)
        self.proc_a_delay = QLineEdit("15000"); a_layout.addRow(f"{calc['delay_cost']} (TL):", self.proc_a_delay)
        self.proc_a_quality = QLineEdit("10000"); a_layout.addRow(f"{calc['quality_cost']} (TL):", self.proc_a_quality)
        self.proc_a_total = QLabel(""); a_layout.addRow(f"{calc['total']}:", self.proc_a_total)
        self.proc_calc_layout.addWidget(a_group)
        b_group = QGroupBox(calc["supplier_b"]); b_layout = QFormLayout(b_group)
        self.proc_b_price = QLineEdit("110000"); b_layout.addRow(f"{calc['purchase_price']} (TL):", self.proc_b_price)
        self.proc_b_rework = QLineEdit("5000"); b_layout.addRow(f"{calc['rework_cost']} (TL):", self.proc_b_rework)
        self.proc_b_delay = QLineEdit("0"); b_layout.addRow(f"{calc['delay_cost']} (TL):", self.proc_b_delay)
        self.proc_b_quality = QLineEdit("0"); b_layout.addRow(f"{calc['quality_cost']} (TL):", self.proc_b_quality)
        self.proc_b_total = QLabel(""); b_layout.addRow(f"{calc['total']}:", self.proc_b_total)
        self.proc_calc_layout.addWidget(b_group)
        calc_btn = QPushButton("🔄 Hesapla"); calc_btn.clicked.connect(self._calc_procurement)
        self.proc_calc_layout.addWidget(calc_btn)
        self.proc_result = QLabel("")
        self.proc_result.setStyleSheet("font-size:16px; font-weight:bold; color:#89b4fa; padding:10px;")
        self.proc_calc_layout.addWidget(self.proc_result)
        self._calc_procurement()'''

    # Eski metodu bul ve değiştir (metod adıyla ara)
    start = content.find('def _build_procurement_ui(self):')
    if start == -1:
        print("❌ _build_procurement_ui metodu bulunamadı.")
    else:
        # Metodun sonunu bul (bir sonraki metod başlangıcı veya sınıf sonu)
        end = content.find('\n    def ', start + 10)  # sonraki metod
        if end == -1:
            end = content.find('\ndef ', start + 10)  # fonksiyon
        if end == -1:
            end = len(content)
        content = content[:start] + new_method + content[end:]
        with open(main_py, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ _build_procurement_ui metodu onarıldı.")