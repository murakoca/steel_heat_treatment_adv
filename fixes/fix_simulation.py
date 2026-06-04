#!/usr/bin/env python3
"""Simülasyon sekmesindeki dil uyumsuzluğunu giderir."""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
main_py = os.path.join(BASE, "app", "main.py")

with open(main_py, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. _start_sim metodundaki proses eşleştirmesini düzelt
old_start = """cfg = {"steel": self.steel_cb.currentText(), "process": self.proc_cb.currentText()}
        try:
            if cfg["process"] in [self.lang_manager.tr("quenching"), "Quenching"]:"""

new_start = """cfg = {"steel": self.steel_cb.currentText(), "process": self._get_process_name()}
        try:
            if cfg["process"] == "Quenching":"""

content = content.replace(old_start, new_start)

# 2. _on_proc_changed metodunu düzelt
old_proc = """def _on_proc_changed(self, proc):
        while self.proc_layout.count():
            item = self.proc_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        if proc == self.lang_manager.tr("quenching") or proc == "Quenching":
            self.aust_edit = QLineEdit("850"); self.proc_layout.addRow(self.lang_manager.tr("aust_temp"), self.aust_edit)
            self.media_cb = QComboBox(); self.media_cb.addItems(["Oil","Water","Polymer","Brine"])
            self.proc_layout.addRow(self.lang_manager.tr("media"), self.media_cb)
            self.ag_cb = QComboBox(); self.ag_cb.addItems(["moderate","still","vigorous"])
            self.proc_layout.addRow(self.lang_manager.tr("agitation"), self.ag_cb)
        elif proc == self.lang_manager.tr("tempering") or proc == "Tempering":
            self.temp_edit = QLineEdit("300"); self.proc_layout.addRow("Sıcaklık (°C):", self.temp_edit)
            self.time_edit = QLineEdit("3600"); self.proc_layout.addRow("Süre (s):", self.time_edit)
        elif proc == self.lang_manager.tr("carburizing") or proc == "Carburizing":
            self.ctemp_edit = QLineEdit("930"); self.proc_layout.addRow("Sıcaklık (°C):", self.ctemp_edit)
            self.ctime_edit = QLineEdit("7200"); self.proc_layout.addRow("Süre (s):", self.ctime_edit)
            self.cpot_edit = QLineEdit("0.8"); self.proc_layout.addRow("C Potansiyeli (%):", self.cpot_edit)"""

new_proc = """def _get_process_name(self):
        \"\"\"Seçili prosesin İngilizce adını döndürür.\"\"\"
        display_text = self.proc_cb.currentText()
        if display_text in [self.lang_manager.tr("quenching"), "Quenching"]:
            return "Quenching"
        elif display_text in [self.lang_manager.tr("tempering"), "Tempering"]:
            return "Tempering"
        elif display_text in [self.lang_manager.tr("carburizing"), "Carburizing"]:
            return "Carburizing"
        return "Quenching"

    def _on_proc_changed(self, proc):
        while self.proc_layout.count():
            item = self.proc_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        internal = self._get_process_name()
        if internal == "Quenching":
            self.aust_edit = QLineEdit("850"); self.proc_layout.addRow(self.lang_manager.tr("aust_temp"), self.aust_edit)
            self.media_cb = QComboBox(); self.media_cb.addItems(["Oil","Water","Polymer","Brine"])
            self.proc_layout.addRow(self.lang_manager.tr("media"), self.media_cb)
            self.ag_cb = QComboBox(); self.ag_cb.addItems(["moderate","still","vigorous"])
            self.proc_layout.addRow(self.lang_manager.tr("agitation"), self.ag_cb)
        elif internal == "Tempering":
            self.temp_edit = QLineEdit("300"); self.proc_layout.addRow("Sıcaklık (°C):", self.temp_edit)
            self.time_edit = QLineEdit("3600"); self.proc_layout.addRow("Süre (s):", self.time_edit)
        elif internal == "Carburizing":
            self.ctemp_edit = QLineEdit("930"); self.proc_layout.addRow("Sıcaklık (°C):", self.ctemp_edit)
            self.ctime_edit = QLineEdit("7200"); self.proc_layout.addRow("Süre (s):", self.ctime_edit)
            self.cpot_edit = QLineEdit("0.8"); self.proc_layout.addRow("C Potansiyeli (%):", self.cpot_edit)"""

content = content.replace(old_proc, new_proc)

# 3. Worker.run() içindeki karşılaştırmayı düzelt
old_worker = """pname = self.cfg["process"]
            if pname == "Quenching":
                proc = Quenching(steel, self.cfg["media"], self.cfg["agitation"], self.cfg["aust_temp"])
            elif pname == "Tempering":
                proc = Tempering(steel, self.cfg["temp_temp"], self.cfg["temp_time"])
            elif pname == "Carburizing":
                proc = Carburizing(steel, self.cfg["carb_temp"], self.cfg["carb_time"], self.cfg["carbon_pot"])
            else:
                raise ValueError(pname)"""

# Worker.run() zaten İngilizce bekliyor, _get_process_name() artık İngilizce döndürecek, sorun kalmadı.

with open(main_py, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Simülasyon sekmesi dil uyumluluğu düzeltildi!")
print("Artık 'Su Verme', 'Temperleme', 'Sementasyon' seçiliyken de simülasyon çalışacak.")
print("\nÇalıştır: python main.py")