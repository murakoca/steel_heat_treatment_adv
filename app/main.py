#!/usr/bin/env python3
"""Isil Islem Simulasyon Platformu - Periyodik Tablolu"""
import sys, os, json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "database", "steels.json")

from models.steel_model import Material
from models.phase_state import SimulationResult, PhaseResult, HardnessResult
from heat_treatment.quenching import Quenching
from heat_treatment.tempering import Tempering
from heat_treatment.carburizing import Carburizing
from simulation.engine import SimulationEngine
from part.geometry import Cylinder, Plate
from furnace.profile import FurnaceProfile
from periodic.table import PeriodicTable

def load_steel_list():
    with open(DB_PATH) as f:
        return list(json.load(f).keys())

class Worker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg

    def run(self):
        try:
            self.log.emit("Baslatiliyor...")
            steel = Material.from_database(self.cfg["steel"])
            pname = self.cfg["process"]
            if pname == "Quenching":
                proc = Quenching(steel, self.cfg["media"], self.cfg["agitation"], self.cfg["aust_temp"])
            elif pname == "Tempering":
                proc = Tempering(steel, self.cfg["temp_temp"], self.cfg["temp_time"])
            elif pname == "Carburizing":
                proc = Carburizing(steel, self.cfg["carb_temp"], self.cfg["carb_time"], self.cfg["carbon_pot"])
            else:
                raise ValueError(pname)
            eng = SimulationEngine(proc)
            result = eng.run(callback=lambda p: self.progress.emit(int(p*100)))
            self.finished.emit(result)
        except Exception as e:
            import traceback
            self.log.emit(traceback.format_exc())
            self.error.emit(str(e))

class CoolingCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = Figure(figsize=(8,5), facecolor='#1e1e2e')
        super().__init__(fig)
        self.ax = fig.add_subplot(111, facecolor='#1e1e2e')
        self.ax.tick_params(colors='#cdd6f4')
        for s in self.ax.spines.values(): s.set_color('#45475a')

    def plot(self, data, ms_temp=None):
        self.ax.clear()
        t, T = data
        self.ax.plot(t, T, 'c-', lw=2.5)
        if ms_temp:
            self.ax.axhline(ms_temp, color='#f38ba8', ls='--', lw=1.5, label=f'Ms={ms_temp}C')
            self.ax.legend(framealpha=0.3, facecolor='#313244', edgecolor='#45475a', labelcolor='#cdd6f4')
        self.ax.set_xlabel("Zaman (s)"); self.ax.set_ylabel("Sicaklik (C)")
        self.ax.set_title("Soguma Egrisi"); self.ax.grid(True, alpha=0.15, color='#cdd6f4')
        self.draw()

class HardnessCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = Figure(figsize=(8,4), facecolor='#1e1e2e')
        super().__init__(fig)
        self.ax = fig.add_subplot(111, facecolor='#1e1e2e')
        self.ax.tick_params(colors='#cdd6f4')
        for s in self.ax.spines.values(): s.set_color('#45475a')

    def plot(self, hardness):
        self.ax.clear()
        labels = ['Yuzey HRC','Merkez HRC','Yuzey HV','Merkez HV']
        vals = [hardness.surface_hrc, hardness.core_hrc, hardness.surface_hv, hardness.core_hv]
        colors = ['#89b4fa','#74c7ec','#f38ba8','#fab387']
        bars = self.ax.bar(labels, vals, color=colors, edgecolor='#45475a')
        for bar, v in zip(bars, vals):
            self.ax.text(bar.get_x()+bar.get_width()/2., bar.get_height()+0.5, f'{v:.1f}', ha='center', color='#cdd6f4', fontsize=9)
        self.ax.set_ylabel("Sertlik"); self.ax.set_title("Sertlik Tahmini")
        self.ax.grid(True, alpha=0.15, axis='y', color='#cdd6f4')
        self.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Isil Islem Simulasyon Platformu")
        self.setMinimumSize(1400, 900)
        self.steels = load_steel_list()
        self.pt = PeriodicTable()
        self._ui()
        self._load_style()

    def _load_style(self):
        try:
            with open(os.path.join(BASE_DIR, "styles.qss")) as f:
                self.setStyleSheet(f.read())
        except: pass

    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        main_layout = QVBoxLayout(c)
        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # ===== SIMULASYON =====
        sim_tab = QWidget(); sim_layout = QVBoxLayout(sim_tab)
        top = QGroupBox("Proses Tanimi"); form = QFormLayout(top)
        h1 = QHBoxLayout()
        self.steel_cb = QComboBox(); self.steel_cb.addItems(self.steels)
        h1.addWidget(QLabel("Celik:")); h1.addWidget(self.steel_cb)
        self.steel_lbl = QLabel(); self.steel_lbl.setStyleSheet("color:#a6adc8;")
        h1.addWidget(self.steel_lbl)
        form.addRow(h1)
        h2 = QHBoxLayout()
        self.proc_cb = QComboBox(); self.proc_cb.addItems(["Quenching","Tempering","Carburizing"])
        self.proc_cb.currentTextChanged.connect(self._on_proc_changed)
        h2.addWidget(QLabel("Proses:")); h2.addWidget(self.proc_cb)
        form.addRow(h2)
        self.proc_params = QWidget(); self.proc_layout = QFormLayout(self.proc_params)
        form.addRow("Parametreler:", self.proc_params)
        self._on_proc_changed("Quenching")
        self.run_btn = QPushButton("Simulasyonu Calistir")
        self.run_btn.clicked.connect(self._start_sim); self.run_btn.setMinimumHeight(40)
        form.addRow(self.run_btn)
        sim_layout.addWidget(top)
        self.progress = QProgressBar(); self.progress.setVisible(False)
        sim_layout.addWidget(self.progress)
        self.res_tabs = QTabWidget()
        self.cooling_canvas = CoolingCanvas(self); self.res_tabs.addTab(self.cooling_canvas, "Soguma")
        self.hardness_canvas = HardnessCanvas(self); self.res_tabs.addTab(self.hardness_canvas, "Sertlik")
        ms_tab = QWidget(); ms_lay = QVBoxLayout(ms_tab)
        self.ms_lbl = QLabel(""); ms_lay.addWidget(self.ms_lbl)
        self.ms_table = QTableWidget(0,4)
        self.ms_table.setHorizontalHeaderLabels(["Faz","Oran %","Sertlik HV","C %"])
        self.ms_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        ms_lay.addWidget(self.ms_table)
        self.res_tabs.addTab(ms_tab, "Mikroyapi")
        self.log_txt = QTextEdit(); self.log_txt.setReadOnly(True)
        self.res_tabs.addTab(self.log_txt, "Log")
        sim_layout.addWidget(self.res_tabs)
        tabs.addTab(sim_tab, "Simulasyon")

        # ===== PERIYODIK TABLO =====
        periodic_tab = QWidget(); periodic_layout = QVBoxLayout(periodic_tab)
        info_panel = QGroupBox("Element Bilgisi")
        info_layout = QHBoxLayout(info_panel)
        self.elem_info_lbl = QLabel("Bir elemente tiklayin...")
        self.elem_info_lbl.setWordWrap(True)
        self.elem_info_lbl.setStyleSheet("font-size:13px; color:#cdd6f4;")
        info_layout.addWidget(self.elem_info_lbl)
        periodic_layout.addWidget(info_panel)
        table_widget = QWidget(); grid = QGridLayout(table_widget); grid.setSpacing(3)
        positions = {
            1:(1,1),2:(1,18),3:(2,1),4:(2,2),5:(2,13),6:(2,14),7:(2,15),8:(2,16),9:(2,17),10:(2,18),
            11:(3,1),12:(3,2),13:(3,13),14:(3,14),15:(3,15),16:(3,16),17:(3,17),18:(3,18),
            19:(4,1),20:(4,2),21:(4,3),22:(4,4),23:(4,5),24:(4,6),25:(4,7),26:(4,8),27:(4,9),28:(4,10),
            29:(4,11),30:(4,12),31:(4,13),32:(4,14),33:(4,15),34:(4,16),35:(4,17),36:(4,18),
            37:(5,1),38:(5,2),39:(5,3),40:(5,4),41:(5,5),42:(5,6),43:(5,7),44:(5,8),45:(5,9),46:(5,10),
            47:(5,11),48:(5,12),49:(5,13),50:(5,14),51:(5,15),52:(5,16),53:(5,17),54:(5,18),
            55:(6,1),56:(6,2),57:(6,3),72:(6,4),73:(6,5),74:(6,6),75:(6,7),76:(6,8),77:(6,9),78:(6,10),
            79:(6,11),80:(6,12),81:(6,13),82:(6,14),83:(6,15),84:(6,16),85:(6,17),86:(6,18),
            87:(7,1),88:(7,2),89:(7,3),104:(7,4),105:(7,5),106:(7,6),107:(7,7),108:(7,8),109:(7,9),110:(7,10),
            111:(7,11),112:(7,12),113:(7,13),114:(7,14),115:(7,15),116:(7,16),117:(7,17),118:(7,18),
            58:(8,4),59:(8,5),60:(8,6),61:(8,7),62:(8,8),63:(8,9),64:(8,10),65:(8,11),66:(8,12),
            67:(8,13),68:(8,14),69:(8,15),70:(8,16),71:(8,17),
            90:(9,4),91:(9,5),92:(9,6),93:(9,7),94:(9,8),95:(9,9),96:(9,10),97:(9,11),98:(9,12),
            99:(9,13),100:(9,14),101:(9,15),102:(9,16),103:(9,17),
        }
        for num, (r, c) in positions.items():
            el = self.pt.get(num)
            if not el: continue
            color = self.pt.get_color(num)
            btn = QPushButton(f"{el['sym']}\n{num}")
            btn.setFixedSize(52, 52)
            btn.setStyleSheet(f"font-size:9px; font-weight:bold; background-color:{color}; color:#1e1e2e; border-radius:3px;")
            btn.clicked.connect(lambda checked, n=num: self._show_element(n))
            btn.setToolTip(f"{el['name']} ({el['sym']})")
            grid.addWidget(btn, r, c)
        periodic_layout.addWidget(table_widget)
        steel_panel = QGroupBox("Alasim Etkileri")
        steel_layout = QVBoxLayout(steel_panel)
        self.steel_info_text = QTextEdit(); self.steel_info_text.setReadOnly(True)
        self.steel_info_text.setMaximumHeight(200)
        steel_layout.addWidget(self.steel_info_text)
        periodic_layout.addWidget(steel_panel)
        tabs.addTab(periodic_tab, "Periyodik Tablo")
        self.statusBar().showMessage("Hazir")

    def _on_proc_changed(self, proc):
        while self.proc_layout.count():
            item = self.proc_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        if proc == "Quenching":
            self.aust_edit = QLineEdit("850"); self.proc_layout.addRow("Ostenitleme Sic. (C):", self.aust_edit)
            self.media_cb = QComboBox(); self.media_cb.addItems(["Oil","Water","Polymer","Brine"])
            self.proc_layout.addRow("Ortam:", self.media_cb)
            self.ag_cb = QComboBox(); self.ag_cb.addItems(["moderate","still","vigorous"])
            self.proc_layout.addRow("Ajitasyon:", self.ag_cb)
        elif proc == "Tempering":
            self.temp_edit = QLineEdit("300"); self.proc_layout.addRow("Sicaklik (C):", self.temp_edit)
            self.time_edit = QLineEdit("3600"); self.proc_layout.addRow("Sure (s):", self.time_edit)
        elif proc == "Carburizing":
            self.ctemp_edit = QLineEdit("930"); self.proc_layout.addRow("Sicaklik (C):", self.ctemp_edit)
            self.ctime_edit = QLineEdit("7200"); self.proc_layout.addRow("Sure (s):", self.ctime_edit)
            self.cpot_edit = QLineEdit("0.8"); self.proc_layout.addRow("C Pot. (%):", self.cpot_edit)

    def _start_sim(self):
        self.run_btn.setEnabled(False); self.progress.setVisible(True); self.progress.setValue(0)
        self.log_txt.clear()
        cfg = {"steel": self.steel_cb.currentText(), "process": self.proc_cb.currentText()}
        try:
            if cfg["process"] == "Quenching":
                cfg["aust_temp"] = float(self.aust_edit.text())
                cfg["media"] = self.media_cb.currentText()
                cfg["agitation"] = self.ag_cb.currentText()
            elif cfg["process"] == "Tempering":
                cfg["temp_temp"] = float(self.temp_edit.text())
                cfg["temp_time"] = float(self.time_edit.text())
            elif cfg["process"] == "Carburizing":
                cfg["carb_temp"] = float(self.ctemp_edit.text())
                cfg["carb_time"] = float(self.ctime_edit.text())
                cfg["carbon_pot"] = float(self.cpot_edit.text())
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))
            self.run_btn.setEnabled(True); self.progress.setVisible(False); return
        self.worker = Worker(cfg)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.log.connect(self.log_txt.append)
        self.worker.finished.connect(self._sim_done)
        self.worker.error.connect(self._sim_err)
        self.worker.start()

    def _sim_done(self, res):
        self.progress.setVisible(False); self.run_btn.setEnabled(True)
        if res.cooling_curve:
            self.cooling_canvas.plot(res.cooling_curve, ms_temp=Material.from_database(self.steel_cb.currentText()).Ms)
        if res.hardness: self.hardness_canvas.plot(res.hardness)
        if res.phases:
            self.ms_table.setRowCount(0)
            for p in res.phases:
                r = self.ms_table.rowCount(); self.ms_table.insertRow(r)
                self.ms_table.setItem(r,0,QTableWidgetItem(p.name))
                self.ms_table.setItem(r,1,QTableWidgetItem(f"{p.fraction*100:.1f}%"))
                self.ms_table.setItem(r,2,QTableWidgetItem(f"{p.hardness_hv:.0f}"))
                self.ms_table.setItem(r,3,QTableWidgetItem(f"{p.carbon_content*100:.2f}"))
            self.ms_lbl.setText(res.microstructure_summary())

    def _sim_err(self, msg):
        self.progress.setVisible(False); self.run_btn.setEnabled(True)
        QMessageBox.critical(self, "Hata", msg)

    def _show_element(self, num):
        el = self.pt.get(num)
        if not el: return
        info = f"<b>{el['name']} ({el['sym']})</b><br>"
        info += f"Atom No: {num} | Kutle: {el['mass']} u<br>"
        if el.get('melt') is not None:
            info += f"Erime: {el['melt']}C | Kaynama: {el['boil']}C<br>"
        self.elem_info_lbl.setText(info)
        effect = self.pt.get_effect(el['sym'])
        txt = ""
        if effect:
            txt += f"<b>{el['sym']} - Celikteki Rolu:</b><br>{effect['role']}<br><br>"
            for d in effect['details']: txt += f"• {d}<br>"
            txt += f"<br>Maks: %{effect['max']} | Tipik: {effect['range']}"
        elif el['sym'] == 'Fe':
            txt = "<b>Demir - Celigin temeli</b><br>"
        else:
            txt = f"<i>{el['name']} alasim elementi degil.</i>"
        inter = self.pt.get_interactions(el['sym'])
        if inter:
            txt += "<br><br><b>Etkilesimler:</b><br>"
            for ix in inter:
                other = ix['pair'][1] if ix['pair'][0] == el['sym'] else ix['pair'][0]
                txt += f"• {el['sym']} + {other} -> {ix['effect']}<br>"
        self.steel_info_text.setHtml(txt)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
