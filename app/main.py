#!/usr/bin/env python3
"""Isıl İşlem Simülasyon Platformu - Tüm Özellikler"""
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
from metallurgy.ree import REEDatabase
from metallurgy.lever_rule import calculate as lever_calculate, FE_C_EXAMPLES

def load_steel_list():
    with open(DB_PATH) as f:
        return list(json.load(f).keys())

MATERIAL_GUIDE = {
    "Düşük Karbonlu (örn. 1020)": "Yapısal çelikler, araba gövdeleri, borular.",
    "Orta Karbonlu (örn. 1045)": "Şaft, aks, dişli. Isıl işlemle sertleştirilebilir.",
    "Yüksek Karbonlu (örn. 1095)": "Yay, bıçak, kesici takım.",
    "Alaşımlı (örn. 4140)": "Krank mili, iniş takımı.",
    "Paslanmaz (örn. 316)": "Kimya, medikal, mutfak.",
    "Takım Çeliği (örn. H13)": "Sıcak iş kalıpları.",
    "AHSS (örn. DP600)": "Otomotiv panelleri."
}

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
            self.log.emit("Başlatılıyor...")
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
            self.ax.axhline(ms_temp, color='#f38ba8', ls='--', lw=1.5, label=f'Ms={ms_temp}°C')
            self.ax.legend(framealpha=0.3, facecolor='#313244', edgecolor='#45475a', labelcolor='#cdd6f4')
        self.ax.set_xlabel("Zaman (s)"); self.ax.set_ylabel("Sıcaklık (°C)")
        self.ax.set_title("Soğuma Eğrisi"); self.ax.grid(True, alpha=0.15, color='#cdd6f4')
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
        labels = ['Yüzey HRC','Merkez HRC','Yüzey HV','Merkez HV']
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
        self.setWindowTitle("Isıl İşlem Simülasyon Platformu")
        self.setMinimumSize(1400, 900)
        self.steels = load_steel_list()
        self.pt = PeriodicTable()
        self._ui()
        self._load_style()

    def _load_style(self):
        try:
            with open(os.path.join(BASE_DIR, "styles.qss"), encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        except: pass

    def _ui(self):
        c = QWidget(); self.setCentralWidget(c)
        main_layout = QVBoxLayout(c)
        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # ===== SİMÜLASYON =====
        sim_tab = QWidget(); sim_layout = QVBoxLayout(sim_tab)
        top = QGroupBox("Proses Tanımı"); form = QFormLayout(top)
        h1 = QHBoxLayout()
        self.steel_cb = QComboBox(); self.steel_cb.addItems(self.steels)
        self.steel_cb.currentTextChanged.connect(self._show_steel_info)
        h1.addWidget(QLabel("Çelik:")); h1.addWidget(self.steel_cb)
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
        self.run_btn = QPushButton("▶ Simülasyonu Çalıştır")
        self.run_btn.clicked.connect(self._start_sim); self.run_btn.setMinimumHeight(40)
        form.addRow(self.run_btn)
        sim_layout.addWidget(top)
        self.progress = QProgressBar(); self.progress.setVisible(False)
        sim_layout.addWidget(self.progress)
        self.res_tabs = QTabWidget()
        self.cooling_canvas = CoolingCanvas(self); self.res_tabs.addTab(self.cooling_canvas, "Soğuma")
        self.hardness_canvas = HardnessCanvas(self); self.res_tabs.addTab(self.hardness_canvas, "Sertlik")
        ms_tab = QWidget(); ms_lay = QVBoxLayout(ms_tab)
        self.ms_lbl = QLabel(""); ms_lay.addWidget(self.ms_lbl)
        self.ms_table = QTableWidget(0,4)
        self.ms_table.setHorizontalHeaderLabels(["Faz","Oran %","Sertlik HV","C %"])
        self.ms_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        ms_lay.addWidget(self.ms_table)
        self.res_tabs.addTab(ms_tab, "Mikroyapı")
        self.log_txt = QTextEdit(); self.log_txt.setReadOnly(True)
        self.res_tabs.addTab(self.log_txt, "Log")
        sim_layout.addWidget(self.res_tabs)
        tabs.addTab(sim_tab, "🔥 Simülasyon")

        # ===== MALZEME REHBERİ =====
        guide_tab = QWidget(); guide_layout = QVBoxLayout(guide_tab)
        guide_label = QLabel("Malzeme Seçim Rehberi")
        guide_label.setFont(QFont("Segoe UI",14, QFont.Bold))
        guide_layout.addWidget(guide_label)
        for title, desc in MATERIAL_GUIDE.items():
            grp = QGroupBox(title)
            grp_lay = QVBoxLayout(grp)
            lbl = QLabel(desc); lbl.setWordWrap(True)
            grp_lay.addWidget(lbl)
            guide_layout.addWidget(grp)
        guide_layout.addStretch()
        tabs.addTab(guide_tab, "📚 Rehber")

        # ===== PERİYODİK TABLO =====
        periodic_tab = QWidget(); periodic_layout = QVBoxLayout(periodic_tab)
        info_panel = QGroupBox("Element Bilgisi")
        info_layout = QHBoxLayout(info_panel)
        self.elem_info_lbl = QLabel("Bir elemente tıklayın...")
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
        steel_panel = QGroupBox("Alaşım Etkileri")
        steel_layout = QVBoxLayout(steel_panel)
        self.steel_info_text = QTextEdit(); self.steel_info_text.setReadOnly(True)
        self.steel_info_text.setMaximumHeight(200)
        steel_layout.addWidget(self.steel_info_text)
        periodic_layout.addWidget(steel_panel)
        tabs.addTab(periodic_tab, "🧪 Elementler")

        # ===== LEVER RULE =====
        lever_tab = QWidget(); lever_layout = QVBoxLayout(lever_tab)
        info_lbl = QLabel("<h2>⚖️ Kaldıraç Kuralı (Lever Rule)</h2>İki fazlı bölgede faz oranlarını hesaplayın.")
        info_lbl.setWordWrap(True)
        lever_layout.addWidget(info_lbl)
        form_group = QGroupBox("Kompozisyon Değerleri")
        form = QFormLayout(form_group)
        self.lever_ca = QLineEdit("0.022")
        form.addRow("Cα (α fazı %):", self.lever_ca)
        self.lever_cb = QLineEdit("6.67")
        form.addRow("Cβ (β fazı %):", self.lever_cb)
        self.lever_co = QLineEdit("0.8")
        form.addRow("Co (Genel %):", self.lever_co)
        btn_layout = QHBoxLayout()
        calc_btn = QPushButton("Hesapla")
        calc_btn.clicked.connect(self._calc_lever)
        btn_layout.addWidget(calc_btn)
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
        tabs.addTab(lever_tab, "⚖️ Lever Kuralı")

        # ===== REE SEKMESI =====
        self.ree_db = REEDatabase()
        ree_data = self.ree_db.get_all()
        
        ree_tab = QWidget()
        ree_layout = QVBoxLayout(ree_tab)
        
        # Başlık
        title = QLabel("<h2>🧪 Nadir Toprak Elementleri (REE)</h2>")
        title.setWordWrap(True)
        ree_layout.addWidget(title)
        
        # Açıklama
        desc = QTextEdit()
        desc.setReadOnly(True)
        desc.setMaximumHeight(100)
        desc.setHtml(f"<p>{ree_data['description']}</p>"
                     f"<p><b>17 element:</b> {', '.join(ree_data['elements'])}</p>"
                     f"<p><b>Hafif REE:</b> {', '.join(ree_data['light_ree'])}</p>"
                     f"<p><b>Ağır REE:</b> {', '.join(ree_data['heavy_ree'])}</p>")
        ree_layout.addWidget(desc)
        
        # Sekme içinde alt sekmeler
        ree_tabs = QTabWidget()
        
        # --- Uygulamalar ---
        app_tab = QWidget()
        app_layout = QVBoxLayout(app_tab)
        apps = ree_data["applications"]
        for app_name, app_info in apps.items():
            grp = QGroupBox(f"📌 {app_name}")
            grp_lay = QVBoxLayout(grp)
            lbl = QLabel(f"<b>Elementler:</b> {', '.join(app_info['elements'])}<br>"
                        f"<b>Açıklama:</b> {app_info['desc']}")
            lbl.setWordWrap(True)
            grp_lay.addWidget(lbl)
            app_layout.addWidget(grp)
        app_layout.addStretch()
        ree_tabs.addTab(app_tab, "Uygulamalar")
        
        # --- Kullanım Dağılımı ---
        usage_tab = QWidget()
        usage_layout = QVBoxLayout(usage_tab)
        usage_lbl = QLabel("<h3>ABD Nadir Toprak Kullanımı</h3>")
        usage_layout.addWidget(usage_lbl)
        for sector, pct in ree_data["usage_distribution"].items():
            bar = QProgressBar()
            bar.setValue(pct)
            bar.setFormat(f"{sector}: %{pct}")
            usage_layout.addWidget(QLabel(sector))
            usage_layout.addWidget(bar)
        usage_layout.addStretch()
        ree_tabs.addTab(usage_tab, "Kullanım Dağılımı")
        
        # --- Mineraller ve Ekstraksiyon ---
        mineral_tab = QWidget()
        mineral_layout = QVBoxLayout(mineral_tab)
        mineral_layout.addWidget(QLabel("<h3>REE Mineralleri</h3>"))
        for m in ree_data["minerals"]:
            mineral_layout.addWidget(QLabel(f"• <b>{m['name']}</b>: {m['formula']} ({m['type']})"))
        mineral_layout.addWidget(QLabel("<br><h3>Ekstraksiyon Aşamaları</h3>"))
        for i, step in enumerate(ree_data["extraction_steps"], 1):
            mineral_layout.addWidget(QLabel(f"  {i}. {step}"))
        mineral_layout.addWidget(QLabel(f"<br><b>⚠️ Zorluk:</b> {ree_data['separation_challenge']}"))
        mineral_layout.addStretch()
        ree_tabs.addTab(mineral_tab, "Mineraller & İşleme")
        
        ree_layout.addWidget(ree_tabs)
        tabs.addTab(ree_tab, "🧪 REE")


        self.statusBar().showMessage("Hazır")

    def _show_steel_info(self, name):
        try:
            m = Material.from_database(name)
            self.steel_lbl.setText(f"Ms={m.Ms}°C, C=%{m.carbon*100:.2f}")
        except: self.steel_lbl.setText("")

    def _on_proc_changed(self, proc):
        while self.proc_layout.count():
            item = self.proc_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        if proc == "Quenching":
            self.aust_edit = QLineEdit("850"); self.proc_layout.addRow("Östenitleme Sıc. (°C):", self.aust_edit)
            self.media_cb = QComboBox(); self.media_cb.addItems(["Oil","Water","Polymer","Brine"])
            self.proc_layout.addRow("Ortam:", self.media_cb)
            self.ag_cb = QComboBox(); self.ag_cb.addItems(["moderate","still","vigorous"])
            self.proc_layout.addRow("Ajitasyon:", self.ag_cb)
        elif proc == "Tempering":
            self.temp_edit = QLineEdit("300"); self.proc_layout.addRow("Sıcaklık (°C):", self.temp_edit)
            self.time_edit = QLineEdit("3600"); self.proc_layout.addRow("Süre (s):", self.time_edit)
        elif proc == "Carburizing":
            self.ctemp_edit = QLineEdit("930"); self.proc_layout.addRow("Sıcaklık (°C):", self.ctemp_edit)
            self.ctime_edit = QLineEdit("7200"); self.proc_layout.addRow("Süre (s):", self.ctime_edit)
            self.cpot_edit = QLineEdit("0.8"); self.proc_layout.addRow("C Potansiyeli (%):", self.cpot_edit)

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
            QMessageBox.critical(self, "Hata", f"Geçersiz değer: {e}")
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
            mat = Material.from_database(self.steel_cb.currentText())
            self.cooling_canvas.plot(res.cooling_curve, ms_temp=mat.Ms)
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
        QMessageBox.critical(self, "Simülasyon Hatası", msg)

    def _show_element(self, num):
        el = self.pt.get(num)
        if not el: return
        info = f"<b>{el['name']} ({el['sym']})</b><br>"
        info += f"Atom No: {num} | Kütle: {el['mass']} u<br>"
        if el.get('melt') is not None:
            info += f"Erime: {el['melt']}°C | Kaynama: {el['boil']}°C<br>"
        self.elem_info_lbl.setText(info)
        effect = self.pt.get_effect(el['sym'])
        txt = ""
        if effect:
            txt += f"<b>{el['sym']} - Çelikteki Rolü:</b><br>{effect['role']}<br><br>"
            for d in effect['details']: txt += f"• {d}<br>"
            txt += f"<br>Maks: %{effect['max']} | Tipik: {effect['range']}"
        elif el['sym'] == 'Fe':
            txt = "<b>Demir - Çeliğin temeli</b><br>"
        else:
            txt = f"<i>{el['name']} alaşım elementi değil.</i>"
        inter = self.pt.get_interactions(el['sym'])
        if inter:
            txt += "<br><br><b>Etkileşimler:</b><br>"
            for ix in inter:
                other = ix['pair'][1] if ix['pair'][0] == el['sym'] else ix['pair'][0]
                txt += f"• {el['sym']} + {other} → {ix['effect']}<br>"
        self.steel_info_text.setHtml(txt)

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


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 9))
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()