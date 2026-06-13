#!/usr/bin/env python3
"""Isıl İşlem Simülasyon Platformu – v3.6 FULL I18N"""
import sys, os, json,webbrowser
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

from tools.ironmaking_window import IronmakingWindow
from tools.steelmaking_bof_window import BOFSteelmakingWindow
from tools.bof_principle_window import BOFPrincipleWindow
from models.steel_model import Material
from models.phase_state import SimulationResult, PhaseResult, HardnessResult
from heat_treatment.quenching import Quenching
from heat_treatment.tempering import Tempering
from heat_treatment.carburizing import Carburizing
from simulation.engine import SimulationEngine
from part.geometry import Cylinder, Plate
from furnace.profile import FurnaceProfile
from periodic.table import PeriodicTable
from metallurgy.lever_rule import calculate as lever_calculate, FE_C_EXAMPLES
from metallurgy.ree import REEDatabase
from metallurgy.interactive_fec import FeCDiagram
from procurement.calculator import SupplierCost, compare_suppliers
from reports.pdf_generator import generate_pdf_report
from metallurgy.ttt_cct_plot import load_ttt_data, draw_ttt
from mechanics.distortion_calc import estimate_residual_stress, distortion_risk
from simulation.carburizing_sim import simulate_carburizing
from metallurgy.alloy_guide import AlloyGuide
from metallurgy.failure_modes import FailureModes
from tools.clemex_window import ClemexWindow
from tools.vesta_window import VestaWindow
from tools.comsol_window import ComsolWindow
from tools.mipar_window import MiparWindow
from tools.steeluniversity_window import SteeluniversityWindow
from tools.simufact_window import SimufactWindow
from tools.steelmaking_window import SteelmakingWindow
from tools.pandat_window import PandatWindow
from tools.metrical_window import MetricalWindow
from app.language_manager import LanguageManager
from metallurgy.ttt_cct_plot import calculate_ttt, cct_from_ttt, hardness_from_cct
from metallurgy.image_analyzer import threshold as img_threshold, auto_threshold_otsu, particle_analysis, grain_size_distribution, phase_fraction
from simulation.diffusion_sim import solve_diffusion_1d, matano_plane
from metallurgy.crystal_viewer import generate_lattice, simulate_xrd, CRYSTAL_SYSTEMS
from simulation.casting_sim import chvorinov_rule, solidification_microstructure, cooling_curve as casting_cooling_curve
from metallurgy.alloy_thermodynamics import redlich_kister_excess_gibbs, activity_coefficient, calculate_eutectic
from physics.thermodynamics_advanced import regular_solution_gibbs, equilibrium_composition
from metallurgy.data_analyzer import linear_fit, poly_fit, exp_fit, gaussian_fit, descriptive_stats
from simulation.molecular_dynamics import MolecularDynamics

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
        self.lang_manager = LanguageManager()
        self.setWindowTitle(self.lang_manager.tr("window_title"))
        self.setMinimumSize(1400, 900)
        self.steels = load_steel_list()
        self.pt = PeriodicTable()
        self.fec_sliders = {}
        self.current_result = None
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
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # ===== SİMÜLASYON =====
        sim_tab = QWidget(); sim_layout = QVBoxLayout(sim_tab)
        top = QGroupBox(self.lang_manager.tr("process_group")); form = QFormLayout(top)
        h1 = QHBoxLayout()
        self.steel_cb = QComboBox(); self.steel_cb.addItems(self.steels)
        self.steel_cb.currentTextChanged.connect(self._show_steel_info)
        h1.addWidget(QLabel(self.lang_manager.tr("steel_label"))); h1.addWidget(self.steel_cb)
        self.steel_lbl = QLabel(); self.steel_lbl.setStyleSheet("color:#a6adc8;")
        h1.addWidget(self.steel_lbl)
        form.addRow(h1)
        h2 = QHBoxLayout()
        self.proc_cb = QComboBox()
        self.proc_cb.addItems([self.lang_manager.tr("quenching"), self.lang_manager.tr("tempering"), self.lang_manager.tr("carburizing")])
        self.proc_cb.currentTextChanged.connect(self._on_proc_changed)
        h2.addWidget(QLabel(self.lang_manager.tr("process_label"))); h2.addWidget(self.proc_cb)
        form.addRow(h2)
        self.proc_params = QWidget(); self.proc_layout = QFormLayout(self.proc_params)
        form.addRow(self.lang_manager.tr("params_label"), self.proc_params)
        self._on_proc_changed(self.lang_manager.tr("quenching"))
        self.run_btn = QPushButton(self.lang_manager.tr("run_btn"))
        self.run_btn.clicked.connect(self._start_sim); self.run_btn.setMinimumHeight(40)
        form.addRow(self.run_btn)
        sim_layout.addWidget(top)
        self.progress = QProgressBar(); self.progress.setVisible(False)
        sim_layout.addWidget(self.progress)
        self.res_tabs = QTabWidget()
        self.cooling_canvas = CoolingCanvas(self); self.res_tabs.addTab(self.cooling_canvas, self.lang_manager.tr("cooling_tab"))
        self.hardness_canvas = HardnessCanvas(self); self.res_tabs.addTab(self.hardness_canvas, self.lang_manager.tr("hardness_tab"))
        ms_tab = QWidget(); ms_lay = QVBoxLayout(ms_tab)
        self.ms_lbl = QLabel(""); ms_lay.addWidget(self.ms_lbl)
        self.ms_table = QTableWidget(0,4)
        self.ms_table.setHorizontalHeaderLabels(["Faz","Oran %","Sertlik HV","C %"])
        self.ms_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        ms_lay.addWidget(self.ms_table)
        self.res_tabs.addTab(ms_tab, self.lang_manager.tr("micro_tab"))
        self.log_txt = QTextEdit(); self.log_txt.setReadOnly(True)
        self.res_tabs.addTab(self.log_txt, self.lang_manager.tr("log_tab"))
        sim_layout.addWidget(self.res_tabs)
        self.tabs.addTab(sim_tab, self.lang_manager.tr("simulation_tab"))

        # ===== REHBER =====
        guide_tab = QWidget(); guide_layout = QVBoxLayout(guide_tab)
        self.guide_label = QLabel(self.lang_manager.tr("guide_tab"))
        self.guide_label.setFont(QFont("Segoe UI",14, QFont.Bold))
        guide_layout.addWidget(self.guide_label)
        for title, desc in MATERIAL_GUIDE.items():
            grp = QGroupBox(title)
            grp_lay = QVBoxLayout(grp)
            lbl = QLabel(desc); lbl.setWordWrap(True)
            grp_lay.addWidget(lbl)
            guide_layout.addWidget(grp)
        guide_layout.addStretch()
        self.tabs.addTab(guide_tab, self.lang_manager.tr("guide_tab"))

        # ===== PERİYODİK TABLO =====
        periodic_tab = QWidget(); periodic_layout = QVBoxLayout(periodic_tab)
        info_panel = QGroupBox(self.lang_manager.tr("element_info"))
        info_layout = QHBoxLayout(info_panel)
        self.elem_info_lbl = QLabel(self.lang_manager.tr("click_element"))
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
        steel_panel = QGroupBox(self.lang_manager.tr("alloy_effects"))
        steel_layout = QVBoxLayout(steel_panel)
        self.steel_info_text = QTextEdit(); self.steel_info_text.setReadOnly(True)
        self.steel_info_text.setMaximumHeight(200)
        steel_layout.addWidget(self.steel_info_text)
        periodic_layout.addWidget(steel_panel)
        self.tabs.addTab(periodic_tab, self.lang_manager.tr("periodic_tab"))

        # ===== LEVER RULE =====
        lever_tab = QWidget(); lever_layout = QVBoxLayout(lever_tab)
        self.lever_info_lbl = QLabel(self.lang_manager.tr("lever_info"))
        self.lever_info_lbl.setWordWrap(True)
        lever_layout.addWidget(self.lever_info_lbl)
        form_group = QGroupBox(self.lang_manager.tr("lever_composition"))
        form = QFormLayout(form_group)
        self.lever_ca = QLineEdit("0.022"); form.addRow(self.lang_manager.tr("lever_ca"), self.lever_ca)
        self.lever_cb = QLineEdit("6.67"); form.addRow(self.lang_manager.tr("lever_cb"), self.lever_cb)
        self.lever_co = QLineEdit("0.8"); form.addRow(self.lang_manager.tr("lever_co"), self.lever_co)
        btn_layout = QHBoxLayout()
        calc_btn = QPushButton(self.lang_manager.tr("lever_calculate")); calc_btn.clicked.connect(self._calc_lever)
        btn_layout.addWidget(calc_btn)
        example_cb = QComboBox(); example_cb.addItem(self.lang_manager.tr("lever_examples"))
        for key in FE_C_EXAMPLES: example_cb.addItem(key)
        example_cb.currentTextChanged.connect(lambda t: self._load_lever_example(t))
        btn_layout.addWidget(example_cb); btn_layout.addStretch()
        form.addRow(btn_layout)
        lever_layout.addWidget(form_group)
        result_group = QGroupBox(self.lang_manager.tr("lever_result"))
        result_layout = QVBoxLayout(result_group)
        self.lever_result = QLabel(self.lang_manager.tr("lever_initial_result"))
        self.lever_result.setWordWrap(True)
        self.lever_result.setStyleSheet("font-size:14px; padding:10px;")
        result_layout.addWidget(self.lever_result)
        lever_layout.addWidget(result_group)
        lever_layout.addStretch()
        self.tabs.addTab(lever_tab, self.lang_manager.tr("lever_tab"))

        # ===== REE =====
        self.ree_db = REEDatabase()
        ree_data = self.ree_db.get_all()
        ree_tab = QWidget(); ree_layout = QVBoxLayout(ree_tab)
        title = QLabel(self.lang_manager.tr("ree_title")); title.setWordWrap(True)
        ree_layout.addWidget(title)
        desc = QTextEdit(); desc.setReadOnly(True); desc.setMaximumHeight(100)
        desc.setHtml(f"<p>{ree_data['description']}</p><p><b>17 element:</b> {', '.join(ree_data['elements'])}</p>")
        ree_layout.addWidget(desc)
        ree_tabs = QTabWidget()
        app_tab = QWidget(); app_layout = QVBoxLayout(app_tab)
        for app_name, app_info in ree_data["applications"].items():
            grp = QGroupBox(f"📌 {app_name}")
            grp_lay = QVBoxLayout(grp)
            lbl = QLabel(f"<b>Elementler:</b> {', '.join(app_info['elements'])}<br><b>Açıklama:</b> {app_info['desc']}")
            lbl.setWordWrap(True)
            grp_lay.addWidget(lbl)
            app_layout.addWidget(grp)
        app_layout.addStretch()
        ree_tabs.addTab(app_tab, self.lang_manager.tr("ree_applications_tab"))
        usage_tab = QWidget(); usage_layout = QVBoxLayout(usage_tab)
        usage_lbl = QLabel(self.lang_manager.tr("ree_usage_title")); usage_layout.addWidget(usage_lbl)
        for sector, pct in ree_data["usage_distribution"].items():
            bar = QProgressBar(); bar.setValue(pct); bar.setFormat(f"{sector}: %{pct}")
            usage_layout.addWidget(QLabel(sector)); usage_layout.addWidget(bar)
        usage_layout.addStretch()
        ree_tabs.addTab(usage_tab, self.lang_manager.tr("ree_usage_tab"))
        mineral_tab = QWidget(); mineral_layout = QVBoxLayout(mineral_tab)
        mineral_layout.addWidget(QLabel(self.lang_manager.tr("ree_minerals_title")))
        for m in ree_data["minerals"]:
            mineral_layout.addWidget(QLabel(f"• <b>{m['name']}</b>: {m['formula']} ({m['type']})"))
        mineral_layout.addWidget(QLabel(self.lang_manager.tr("ree_extraction_title")))
        for i, step in enumerate(ree_data["extraction_steps"], 1):
            mineral_layout.addWidget(QLabel(f"  {i}. {step}"))
        mineral_layout.addWidget(QLabel(f"{self.lang_manager.tr('ree_separation_note')} {ree_data['separation_challenge']}"))
        mineral_layout.addStretch()
        ree_tabs.addTab(mineral_tab, self.lang_manager.tr("ree_minerals_tab"))
        ree_layout.addWidget(ree_tabs)
        self.tabs.addTab(ree_tab, self.lang_manager.tr("ree_tab"))

        # ===== İNTERAKTİF Fe–C DİYAGRAMI =====
        self.fec_engine = FeCDiagram()
        fec_tab = QWidget(); fec_layout = QHBoxLayout(fec_tab)
        left_panel = QWidget(); left_layout = QVBoxLayout(left_panel)
        fig = Figure(figsize=(10, 8), facecolor='#1e1e2e')
        self.fec_canvas = FigureCanvasQTAgg(fig)
        self.fec_ax = fig.add_subplot(111, facecolor='#1e1e2e')
        self.fec_ax.tick_params(colors='#cdd6f4', labelsize=10)
        for spine in self.fec_ax.spines.values(): spine.set_color('#45475a')
        self.fec_ax.xaxis.label.set_color('#cdd6f4'); self.fec_ax.yaxis.label.set_color('#cdd6f4')
        self.fec_ax.title.set_color('#cdd6f4')
        left_layout.addWidget(self.fec_canvas)
        right_panel = QWidget(); right_panel.setMaximumWidth(350)
        right_layout = QVBoxLayout(right_panel)
        mat_group = QGroupBox(self.lang_manager.tr("fec_ready_material"))
        mat_layout = QVBoxLayout(mat_group)
        self.fec_material_cb = QComboBox(); self.fec_material_cb.addItem(self.lang_manager.tr("fec_custom"))
        for steel_name in load_steel_list(): self.fec_material_cb.addItem(steel_name)
        self.fec_material_cb.currentTextChanged.connect(self._on_fec_material_changed)
        mat_layout.addWidget(self.fec_material_cb)
        right_layout.addWidget(mat_group)
        elem_group = QGroupBox(self.lang_manager.tr("fec_element_composition"))
        elem_layout = QFormLayout(elem_group)
        self.fec_sliders = {}
        elements = [("C", 0.0, 6.67, 0.77, "Karbon"), ("Mn", 0.0, 2.0, 0.5, "Mangan"),
                    ("Si", 0.0, 2.0, 0.2, "Silisyum"), ("Cr", 0.0, 30.0, 0.0, "Krom"),
                    ("Ni", 0.0, 30.0, 0.0, "Nikel"), ("Mo", 0.0, 10.0, 0.0, "Molibden")]
        for elem, min_v, max_v, default, name in elements:
            row = QHBoxLayout()
            lbl = QLabel(f"{name} ({elem}):"); lbl.setMinimumWidth(80); row.addWidget(lbl)
            slider = QSlider(Qt.Horizontal); slider.setRange(int(min_v*100), int(max_v*100))
            slider.setValue(int(default*100))
            slider.valueChanged.connect(lambda v, e=elem: self._on_fec_slider_changed(e))
            row.addWidget(slider)
            val_lbl = QLabel(f"%{default:.2f}"); val_lbl.setMinimumWidth(50); row.addWidget(val_lbl)
            elem_layout.addRow(row)
            self.fec_sliders[elem] = {"slider": slider, "label": val_lbl, "min": min_v, "max": max_v}
        right_layout.addWidget(elem_group)
        temp_group = QGroupBox(self.lang_manager.tr("fec_temperature"))
        temp_layout = QVBoxLayout(temp_group)
        self.fec_temp_slider = QSlider(Qt.Horizontal); self.fec_temp_slider.setRange(0, 1600)
        self.fec_temp_slider.setValue(727); self.fec_temp_slider.valueChanged.connect(self._on_fec_temp_changed)
        temp_layout.addWidget(self.fec_temp_slider)
        self.fec_temp_lbl = QLabel("727°C"); self.fec_temp_lbl.setAlignment(Qt.AlignCenter)
        self.fec_temp_lbl.setStyleSheet("font-size:16px; font-weight:bold; color:#89b4fa;")
        temp_layout.addWidget(self.fec_temp_lbl)
        right_layout.addWidget(temp_group)
        phase_group = QGroupBox(self.lang_manager.tr("fec_phase_analysis"))
        phase_layout = QVBoxLayout(phase_group)
        self.fec_phase_info = QTextEdit(); self.fec_phase_info.setReadOnly(True)
        self.fec_phase_info.setMaximumHeight(150); self.fec_phase_info.setStyleSheet("font-size:13px;")
        phase_layout.addWidget(self.fec_phase_info)
        right_layout.addWidget(phase_group)
        reset_btn = QPushButton(self.lang_manager.tr("fec_reset")); reset_btn.clicked.connect(self._reset_fec)
        right_layout.addWidget(reset_btn)
        right_layout.addStretch()
        fec_layout.addWidget(left_panel, 3)
        fec_layout.addWidget(right_panel, 1)
        self.tabs.addTab(fec_tab, self.lang_manager.tr("fec_tab"))
        self._redraw_fec()

        # ===== SATIN ALMA =====
        proc_tab = QWidget(); proc_layout = QVBoxLayout(proc_tab)
        lang_layout = QHBoxLayout()
        self.proc_lang = self.lang_manager.current_lang
        self.proc_tr_btn = QPushButton(self.lang_manager.tr("lang_tr")); self.proc_tr_btn.setCheckable(True)
        self.proc_tr_btn.setChecked(self.proc_lang == "tr")
        self.proc_tr_btn.clicked.connect(lambda: self._switch_proc_lang("tr"))
        self.proc_en_btn = QPushButton(self.lang_manager.tr("lang_en")); self.proc_en_btn.setCheckable(True)
        self.proc_en_btn.setChecked(self.proc_lang == "en")
        self.proc_en_btn.clicked.connect(lambda: self._switch_proc_lang("en"))
        lang_layout.addWidget(self.proc_tr_btn); lang_layout.addWidget(self.proc_en_btn)
        lang_layout.addStretch()
        proc_layout.addLayout(lang_layout)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.proc_scroll_layout = QVBoxLayout(scroll_content); scroll.setWidget(scroll_content)
        proc_layout.addWidget(scroll, 1)
        calc_group = QGroupBox("")
        self.proc_calc_layout = QVBoxLayout(calc_group)
        proc_layout.addWidget(calc_group)
        with open(os.path.join(BASE_DIR, "..", "database", "procurement_guide.json"), encoding='utf-8') as f:
            self.proc_data = json.load(f)
        self._build_procurement_ui()
        self.tabs.addTab(proc_tab, self.lang_manager.tr("procurement_tab"))

        # ===== PDF RAPOR =====
        pdf_tab = QWidget(); pdf_layout = QVBoxLayout(pdf_tab)
        pdf_btn = QPushButton(self.lang_manager.tr("pdf_generate")); pdf_btn.clicked.connect(self._generate_pdf_report)
        pdf_layout.addWidget(pdf_btn)
        self.pdf_status = QLabel(""); pdf_layout.addWidget(self.pdf_status)
        pdf_layout.addStretch()
        self.tabs.addTab(pdf_tab, self.lang_manager.tr("pdf_tab"))

        # ===== TTT/CCT =====
        ttt_tab = QWidget(); ttt_layout = QVBoxLayout(ttt_tab)
        ttt_mat_layout = QHBoxLayout()
        ttt_mat_layout.addWidget(QLabel(self.lang_manager.tr("ttt_steel")))
        self.ttt_steel_cb = QComboBox(); self.ttt_steel_cb.addItems(self.steels)
        self.ttt_steel_cb.currentTextChanged.connect(self._draw_ttt_diagram)
        ttt_mat_layout.addWidget(self.ttt_steel_cb); ttt_mat_layout.addStretch()
        ttt_layout.addLayout(ttt_mat_layout)
        ttt_fig = Figure(figsize=(8,6), facecolor='#1e1e2e')
        self.ttt_canvas = FigureCanvasQTAgg(ttt_fig)
        self.ttt_ax = ttt_fig.add_subplot(111, facecolor='#1e1e2e')
        self.ttt_ax.tick_params(colors='#cdd6f4')
        ttt_layout.addWidget(self.ttt_canvas)
        self.tabs.addTab(ttt_tab, self.lang_manager.tr("ttt_tab"))

        # ===== DİSTORSİYON =====
        distort_tab = QWidget(); distort_layout = QFormLayout(distort_tab)
        self.distort_coolrate = QLineEdit("50"); distort_layout.addRow(self.lang_manager.tr("distortion_cooling_rate"), self.distort_coolrate)
        self.distort_mart = QLineEdit("0.8"); distort_layout.addRow(self.lang_manager.tr("distortion_martensite"), self.distort_mart)
        self.distort_carbon = QLineEdit("0.4"); distort_layout.addRow(self.lang_manager.tr("distortion_carbon"), self.distort_carbon)
        self.distort_yield = QLineEdit("800"); distort_layout.addRow(self.lang_manager.tr("distortion_yield"), self.distort_yield)
        self.distort_btn = QPushButton(self.lang_manager.tr("distortion_calculate")); self.distort_btn.clicked.connect(self._calc_distortion)
        distort_layout.addRow(self.distort_btn)
        self.distort_result = QLabel(""); distort_layout.addRow(self.lang_manager.tr("distortion_result_label"), self.distort_result)
        self.tabs.addTab(distort_tab, self.lang_manager.tr("distortion_tab"))



        # ===== ALAŞIM REHBERİ =====
        self.alloy_guide = AlloyGuide()
        alloy_data = self.alloy_guide.get_all()
        alloy_tab = QWidget(); alloy_layout = QVBoxLayout(alloy_tab)
        scroll_alloy = QScrollArea(); scroll_alloy.setWidgetResizable(True)
        scroll_alloy_content = QWidget()
        scroll_alloy_layout = QVBoxLayout(scroll_alloy_content)
        scroll_alloy.setWidget(scroll_alloy_content)
        alloy_layout.addWidget(scroll_alloy)
        title_alloy = QLabel(f"<h2>🧪 {alloy_data['title']}</h2>")
        title_alloy.setWordWrap(True)
        scroll_alloy_layout.addWidget(title_alloy)
        intro_alloy = QLabel(alloy_data['intro'])
        intro_alloy.setWordWrap(True)
        intro_alloy.setStyleSheet("font-size:13px; color:#cdd6f4; margin-bottom:10px;")
        scroll_alloy_layout.addWidget(intro_alloy)
        why_group = QGroupBox(self.lang_manager.tr("why_alloy"))
        why_layout = QVBoxLayout(why_group)
        for item in alloy_data['why_alloy']:
            lbl = QLabel(f"• {item}"); lbl.setWordWrap(True)
            why_layout.addWidget(lbl)
        scroll_alloy_layout.addWidget(why_group)
        scroll_alloy_layout.addStretch()
        self.tabs.addTab(alloy_tab, self.lang_manager.tr("alloy_tab"))

        # ===== HATA MODLARI =====
        self.failure_db = FailureModes()
        failure_data = self.failure_db.get_all()
        failure_tab = QWidget(); failure_layout = QVBoxLayout(failure_tab)
        scroll_fail = QScrollArea(); scroll_fail.setWidgetResizable(True)
        scroll_fail_content = QWidget()
        scroll_fail_layout = QVBoxLayout(scroll_fail_content)
        scroll_fail.setWidget(scroll_fail_content)
        failure_layout.addWidget(scroll_fail)
        self.failure_title = QLabel(self.lang_manager.tr("failure_title"))
        self.failure_title.setStyleSheet("font-size:18px; font-weight:bold; color:#89b4fa;")
        self.failure_title.setWordWrap(True)
        scroll_fail_layout.addWidget(self.failure_title)
        self.failure_intro = QTextEdit()
        self.failure_intro.setReadOnly(True)
        self.failure_intro.setMaximumHeight(120)
        self.failure_intro.setStyleSheet("font-size:13px; color:#cdd6f4; background-color:#313244; border:1px solid #45475a; border-radius:4px; padding:8px;")
        self.failure_intro.setHtml(self.lang_manager.tr("failure_intro"))
        scroll_fail_layout.addWidget(self.failure_intro)
        modes = failure_data["modes"]
        modes_widget = QWidget()
        modes_grid = QGridLayout(modes_widget)
        modes_grid.setSpacing(10)
        row = 0; col = 0
        self.failure_card_widgets = {}
        mode_keys = ["fracture", "fatigue", "creep", "corrosion", "impact", "wear"]
        mode_title_keys = {
            "fracture": "failure_modes_fracture_title",
            "fatigue": "failure_modes_fatigue_title",
            "creep": "failure_modes_creep_title",
            "corrosion": "failure_modes_corrosion_title",
            "impact": "failure_modes_impact_title",
            "wear": "failure_modes_wear_title",
        }
        for key in mode_keys:
            mode_data = modes[key]
            card = QGroupBox()
            card_layout = QVBoxLayout(card)
            title_label = QLabel(self.lang_manager.tr(mode_title_keys[key]))
            title_label.setStyleSheet("font-weight:bold; color:#89b4fa; font-size:13px;")
            title_label.setWordWrap(True)
            card_layout.addWidget(title_label)
            content_label = QLabel("\n".join([f"• {line}" for line in mode_data["content"]["tr"]]))
            content_label.setWordWrap(True)
            content_label.setStyleSheet("color:#cdd6f4; font-size:11px;")
            card_layout.addWidget(content_label)
            card.setStyleSheet("QGroupBox { background-color:#313244; border:1px solid #45475a; border-radius:6px; padding:10px; }")
            modes_grid.addWidget(card, row, col)
            self.failure_card_widgets[key] = (title_label, content_label)
            col += 1
            if col > 2:
                col = 0
                row += 1
        scroll_fail_layout.addWidget(modes_widget)
        self.failure_fractography_title = QLabel(self.lang_manager.tr("failure_fractography_title"))
        self.failure_fractography_title.setStyleSheet("font-size:14px; font-weight:bold; color:#89b4fa; margin-top:15px;")
        self.failure_fractography_title.setWordWrap(True)
        scroll_fail_layout.addWidget(self.failure_fractography_title)
        self.failure_fractography_content = QLabel(failure_data["fractography"]["content"]["tr"])
        self.failure_fractography_content.setWordWrap(True)
        self.failure_fractography_content.setStyleSheet("color:#cdd6f4; font-size:12px; padding:8px; background-color:#313244; border-radius:4px;")
        scroll_fail_layout.addWidget(self.failure_fractography_content)
        self.failure_prevention_title = QLabel(self.lang_manager.tr("failure_prevention_title"))
        self.failure_prevention_title.setStyleSheet("font-size:14px; font-weight:bold; color:#89b4fa; margin-top:15px;")
        self.failure_prevention_title.setWordWrap(True)
        scroll_fail_layout.addWidget(self.failure_prevention_title)
        self.failure_prevention_list = QLabel("\n".join([f"• {item}" for item in failure_data["prevention"]["items"]["tr"]]))
        self.failure_prevention_list.setWordWrap(True)
        self.failure_prevention_list.setStyleSheet("color:#cdd6f4; font-size:12px; padding:8px; background-color:#313244; border-radius:4px;")
        scroll_fail_layout.addWidget(self.failure_prevention_list)
        scroll_fail_layout.addStretch()
        self.tabs.addTab(failure_tab, self.lang_manager.tr("failure_modes_tab"))

        # ===== MOLEKÜLER DİNAMİK (LAMMPS) =====
        md_tab = QWidget()
        md_layout = QVBoxLayout(md_tab)
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Atom Sayısı:"))
        self.md_n = QSpinBox(); self.md_n.setRange(10, 500); self.md_n.setValue(50)
        ctrl.addWidget(self.md_n)
        ctrl.addWidget(QLabel("Sıcaklık (K):"))
        self.md_temp = QDoubleSpinBox(); self.md_temp.setRange(1, 1000); self.md_temp.setValue(300)
        ctrl.addWidget(self.md_temp)
        ctrl.addWidget(QLabel("Potansiyel:"))
        self.md_pot = QComboBox(); self.md_pot.addItems(["LJ (Lennard-Jones)", "EAM (Gömülü Atom)"])
        ctrl.addWidget(self.md_pot)
        self.md_btn = QPushButton("Simülasyonu Başlat")
        self.md_btn.clicked.connect(self._run_md)
        ctrl.addWidget(self.md_btn)
        ctrl.addStretch()
        md_layout.addLayout(ctrl)
        self.md_fig = Figure(figsize=(8, 6), facecolor='#1e1e2e')
        self.md_canvas = FigureCanvasQTAgg(self.md_fig)
        self.md_ax = self.md_fig.add_subplot(111, facecolor='#1e1e2e')
        self.md_ax.tick_params(colors='#cdd6f4')
        for s in self.md_ax.spines.values(): s.set_color('#45475a')
        md_layout.addWidget(self.md_canvas)
        self.md_status = QLabel("Hazır")
        md_layout.addWidget(self.md_status)
        self.tabs.addTab(md_tab, "⚛️ Mol. Dinamik")

        # ===== VERİ ANALİZİ (Origin) =====
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("X (virgülle):"))
        self.fit_x = QLineEdit("1,2,3,4,5,6,7,8,9,10")
        ctrl.addWidget(self.fit_x)
        ctrl.addWidget(QLabel("Y (virgülle):"))
        self.fit_y = QLineEdit("2.1,4.0,5.9,8.1,10.0,12.2,14.0,16.1,18.0,20.2")
        ctrl.addWidget(self.fit_y)
        data_layout.addLayout(ctrl)
        btn = QHBoxLayout()
        for name, func in [("Doğrusal", "_linear_fit"), ("Polinom 2°", "_poly_fit"), ("Üstel", "_exp_fit"), ("Gaussian", "_gauss_fit"), ("İstatistik", "_calc_stats")]:
            b = QPushButton(name)
            b.clicked.connect(getattr(self, func))
            btn.addWidget(b)
        btn.addStretch()
        data_layout.addLayout(btn)
        self.fit_fig = Figure(figsize=(8, 5), facecolor='#1e1e2e')
        self.fit_canvas = FigureCanvasQTAgg(self.fit_fig)
        self.fit_ax = self.fit_fig.add_subplot(111, facecolor='#1e1e2e')
        self.fit_ax.tick_params(colors='#cdd6f4')
        for s in self.fit_ax.spines.values(): s.set_color('#45475a')
        data_layout.addWidget(self.fit_canvas)
        self.fit_result = QTextEdit(); self.fit_result.setReadOnly(True); self.fit_result.setMaximumHeight(100)
        self.fit_result.setStyleSheet("color:#cdd6f4; background:#313244;")
        data_layout.addWidget(self.fit_result)
        self.tabs.addTab(data_tab, "📊 Veri Analizi")

        # ===== TERMODİNAMİK (Thermo-Calc) =====
        thermo_tab = QWidget()
        thermo_layout = QFormLayout(thermo_tab)
        self.thermo_T = QLineEdit("1000"); thermo_layout.addRow("Sıcaklık (K):", self.thermo_T)
        self.thermo_omega = QLineEdit("5000"); thermo_layout.addRow("Omega (J/mol):", self.thermo_omega)
        self.thermo_x0 = QLineEdit("0.5"); thermo_layout.addRow("Başlangıç x:", self.thermo_x0)
        self.thermo_btn = QPushButton("Denge Kompozisyonu Hesapla")
        self.thermo_btn.clicked.connect(self._calc_equilibrium)
        thermo_layout.addRow(self.thermo_btn)
        self.thermo_result = QLabel(""); thermo_layout.addRow("Sonuç:", self.thermo_result)
        self.tabs.addTab(thermo_tab, "🧪 Termodinamik")

        # ===== ALAŞIM TERMODİNAMİĞİ (FactSage) =====
        alloy_tab = QWidget()
        alloy_layout = QFormLayout(alloy_tab)
        self.alloy_x = QLineEdit("0.3"); alloy_layout.addRow("x (mol kesri):", self.alloy_x)
        self.alloy_T = QLineEdit("1000"); alloy_layout.addRow("Sıcaklık (K):", self.alloy_T)
        self.alloy_params = QLineEdit("5000, -2000, 1000"); alloy_layout.addRow("RK parametreleri:", self.alloy_params)
        self.alloy_btn = QPushButton("Aktivite Katsayısı Hesapla")
        self.alloy_btn.clicked.connect(self._calc_activity)
        alloy_layout.addRow(self.alloy_btn)
        self.alloy_result = QLabel(""); alloy_layout.addRow("Sonuç:", self.alloy_result)
        self.tabs.addTab(alloy_tab, "🏗️ Alaşım Termo.")

        # ===== KATILAŞMA / DÖKÜM (Click2Cast) =====
        cast_tab = QWidget()
        cast_layout = QFormLayout(cast_tab)
        self.cast_V = QLineEdit("0.001"); cast_layout.addRow("Hacim (m³):", self.cast_V)
        self.cast_A = QLineEdit("0.06"); cast_layout.addRow("Yüzey Alanı (m²):", self.cast_A)
        self.cast_Cm = QLineEdit("1.0"); cast_layout.addRow("Kalıp Sabiti:", self.cast_Cm)
        self.cast_btn = QPushButton("Katılaşma Süresi Hesapla")
        self.cast_btn.clicked.connect(self._calc_solidification)
        cast_layout.addRow(self.cast_btn)
        self.cast_result = QLabel(""); cast_layout.addRow("Sonuç:", self.cast_result)
        self.tabs.addTab(cast_tab, "🏭 Katılaşma")

        # ===== KRİSTAL YAPI (Crystal Maker) =====
        crystal_tab = QWidget()
        crystal_layout = QVBoxLayout(crystal_tab)
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Sistem:"))
        self.xtal_system = QComboBox(); self.xtal_system.addItems(list(CRYSTAL_SYSTEMS.keys()))
        ctrl.addWidget(self.xtal_system)
        ctrl.addWidget(QLabel("Boyut:"))
        self.xtal_size = QSpinBox(); self.xtal_size.setRange(1, 5); self.xtal_size.setValue(2)
        ctrl.addWidget(self.xtal_size)
        self.xtal_btn = QPushButton("Çiz")
        self.xtal_btn.clicked.connect(self._draw_crystal)
        ctrl.addWidget(self.xtal_btn)
        ctrl.addStretch()
        crystal_layout.addLayout(ctrl)
        self.xtal_fig = Figure(figsize=(8, 6), facecolor='#1e1e2e')
        self.xtal_canvas = FigureCanvasQTAgg(self.xtal_fig)
        self.xtal_ax = self.xtal_fig.add_subplot(111, projection='3d', facecolor='#1e1e2e')
        self.xtal_ax.tick_params(colors='#cdd6f4')
        for s in self.xtal_ax.spines.values(): s.set_color('#45475a')
        crystal_layout.addWidget(self.xtal_canvas)
        self.tabs.addTab(crystal_tab, "🔬 Kristal Yapı")
        self._draw_crystal()

        # ===== DİFÜZYON (Dictra) =====

        # ===== GÖRÜNTÜ ANALİZİ (ImageJ) =====
        img_tab = QWidget()
        img_layout = QVBoxLayout(img_tab)
        btn = QHBoxLayout()
        self.img_load_btn = QPushButton("Görüntü Yükle")
        self.img_load_btn.clicked.connect(self._load_image)
        btn.addWidget(self.img_load_btn)
        self.img_otsu_btn = QPushButton("Otsu Eşikleme")
        self.img_otsu_btn.clicked.connect(self._apply_otsu)
        btn.addWidget(self.img_otsu_btn)
        self.img_particle_btn = QPushButton("Parçacık Analizi")
        self.img_particle_btn.clicked.connect(self._analyze_particles)
        btn.addWidget(self.img_particle_btn)
        btn.addStretch()
        img_layout.addLayout(btn)
        self.img_fig = Figure(figsize=(8, 6), facecolor='#1e1e2e')
        self.img_canvas = FigureCanvasQTAgg(self.img_fig)
        self.img_ax = self.img_fig.add_subplot(111, facecolor='#1e1e2e')
        self.img_ax.tick_params(colors='#cdd6f4')
        img_layout.addWidget(self.img_canvas)
        self.img_status = QLabel("Görüntü yüklenmedi")
        img_layout.addWidget(self.img_status)
        self.tabs.addTab(img_tab, "🖼️ Görüntü Analizi")

        # ===== JMatPro =====
        jmatpro_tab = QWidget()
        jmatpro_layout = QFormLayout(jmatpro_tab)
        self.jmatpro_C = QLineEdit("0.4"); jmatpro_layout.addRow("Karbon (%):", self.jmatpro_C)
        self.jmatpro_Mn = QLineEdit("0.8"); jmatpro_layout.addRow("Mangan (%):", self.jmatpro_Mn)
        self.jmatpro_Cr = QLineEdit("1.0"); jmatpro_layout.addRow("Krom (%):", self.jmatpro_Cr)
        self.jmatpro_btn = QPushButton("TTT ve Sertlik Hesapla")
        self.jmatpro_btn.clicked.connect(self._calc_jmatpro)
        jmatpro_layout.addRow(self.jmatpro_btn)
        self.jmatpro_result = QLabel(""); jmatpro_layout.addRow("Sonuç:", self.jmatpro_result)
        self.tabs.addTab(jmatpro_tab, "📈 JMatPro")

        

        # ===== KARBON DİFÜZYONU (YENİ) =====
        
        form = QFormLayout()
        
    
        


        # ===== ARAÇLAR SEKMESİ (Profesyonel Araçlar) =====
        tools_tab = QWidget(); tools_layout = QVBoxLayout(tools_tab)
        scroll_tools = QScrollArea(); scroll_tools.setWidgetResizable(True)
        scroll_tools_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_tools_content)
        scroll_tools.setWidget(scroll_tools_content)
        tools_layout.addWidget(scroll_tools)

        with open(os.path.join(BASE_DIR, "..", "database", "tools_resources.json"), encoding='utf-8') as f:
            tools_data = json.load(f)

        self.tools_title = QLabel()
        self.tools_title.setStyleSheet("font-size:18px; font-weight:bold; color:#89b4fa;")
        self.tools_title.setWordWrap(True)
        scroll_layout.addWidget(self.tools_title)

        self.tools_intro = QLabel()
        self.tools_intro.setWordWrap(True)
        self.tools_intro.setStyleSheet("font-size:13px; color:#cdd6f4; margin-bottom:15px;")
        scroll_layout.addWidget(self.tools_intro)

        self.tools_widgets = []
        for tool in tools_data["tools"]:
            card = QGroupBox()
            card_layout = QVBoxLayout(card)
            name_lbl = QLabel(tool["name"])
            name_lbl.setStyleSheet("font-weight:bold; font-size:14px; color:#89b4fa;")
            card_layout.addWidget(name_lbl)
            desc_lbl = QLabel()
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet("font-size:12px; color:#cdd6f4;")
            card_layout.addWidget(desc_lbl)
            link_btn = QPushButton(f"🔗 {tool['url']}")
            link_btn.setStyleSheet("QPushButton { background-color:transparent; color:#a6e3a1; border:none; text-decoration:underline; font-size:11px; text-align:left; } QPushButton:hover { color:#89b4fa; }")
            link_btn.setCursor(QCursor(Qt.PointingHandCursor))
            link_btn.clicked.connect(lambda checked, url=tool["url"]: webbrowser.open(url))
            card_layout.addWidget(link_btn)
            card.setStyleSheet("QGroupBox { background-color:#313244; border:1px solid #45475a; border-radius:6px; padding:10px; }")
            scroll_layout.addWidget(card)
            self.tools_widgets.append((name_lbl, desc_lbl))

        # --- Profesyonel Araç Butonları ---
        tools_list = [
            ("📏 Metrical", "Tane boyutu, porozite, dekarbürizasyon analizi", lambda: self._open_tool("metrical")),
            ("🔬 Pandat", "CALPHAD termodinamik ve faz diyagramı", lambda: self._open_tool("pandat")),
            ("🏭 Ironmaking", "Demir üretimi süreci modelleme", lambda: self._open_tool("ironmaking")),
            ("🏭 Steelmaking", "Çelik üretim süreci modelleme", lambda: self._open_tool("steelmaking")),
            ("🔨 Simufact", "Metal şekillendirme simülasyonu", lambda: self._open_tool("simufact")),
            ("🎓 Steeluniversity", "3D eğitim modelleri ve simülatörler", lambda: self._open_tool("steeluni")),
            ("🤖 Mipar", "ML ile otomatik mikroyapı analizi", lambda: self._open_tool("mipar")),
            ("🧪 Comsol", "Korozyon ve SCC modelleme", lambda: self._open_tool("comsol")),
            ("💎 Vesta", "3D kristal yapı görselleştirici", lambda: self._open_tool("vesta")),
            ("📊 Clemex", "AI destekli tane boyutu analizi", lambda: self._open_tool("clemex")),
        ]
        for name, desc, callback in tools_list:
            card = QGroupBox()
            card_layout = QVBoxLayout(card)
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet("font-weight:bold; font-size:14px; color:#89b4fa;")
            card_layout.addWidget(name_lbl)
            desc_lbl = QLabel(desc)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet("font-size:11px; color:#a6adc8;")
            card_layout.addWidget(desc_lbl)
            btn = QPushButton("🔗 Aç")
            btn.setStyleSheet("QPushButton{background:#45475a;color:#cdd6f4;border-radius:4px;padding:4px 12px;}QPushButton:hover{background:#89b4fa;color:#1e1e2e;}")
            btn.clicked.connect(callback)
            card_layout.addWidget(btn)
            card.setStyleSheet("QGroupBox{background:#313244;border:1px solid #45475a;border-radius:6px;padding:8px;}")
            scroll_layout.addWidget(card)

        scroll_layout.addStretch()
        self.tabs.addTab(tools_tab, "🔗 Araçlar")
        self._translate_tools()

        # Dil butonu
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["🇹🇷 Türkçe", "🇬🇧 English"])
        self.lang_combo.setCurrentIndex(0 if self.lang_manager.current_lang == "tr" else 1)
        self.lang_combo.setFixedWidth(130)
        self.lang_combo.setStyleSheet("QComboBox { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 2px 6px; font-weight: bold; } QComboBox:hover { border-color: #89b4fa; } QComboBox QAbstractItemView { background-color: #313244; color: #cdd6f4; selection-background-color: #89b4fa; }")
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        self.statusBar().addPermanentWidget(self.lang_combo)
        self.statusBar().showMessage(self.lang_manager.tr("ready"))

    # ===== PROCUREMENT METODLARI =====
    def _switch_proc_lang(self, lang):
        self.proc_lang = lang
        self.proc_tr_btn.setChecked(lang == "tr"); self.proc_en_btn.setChecked(lang == "en")
        self._build_procurement_ui()

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
        self._calc_procurement()

    def _calc_procurement(self):
        try:
            a = SupplierCost(name="A", purchase_price=float(self.proc_a_price.text()),
                             rework_cost=float(self.proc_a_rework.text()),
                             delay_cost=float(self.proc_a_delay.text()),
                             quality_cost=float(self.proc_a_quality.text()))
            b = SupplierCost(name="B", purchase_price=float(self.proc_b_price.text()),
                             rework_cost=float(self.proc_b_rework.text()),
                             delay_cost=float(self.proc_b_delay.text()),
                             quality_cost=float(self.proc_b_quality.text()))
            self.proc_a_total.setText(f"{a.total:,.0f} TL"); self.proc_b_total.setText(f"{b.total:,.0f} TL")
            winner, diff = compare_suppliers(a, b)
            if winner is None:
                msg = "İki tedarikçi eşit maliyete sahip." if self.proc_lang == "tr" else "Both suppliers have equal cost."
            else:
                cheaper = "daha ekonomik!" if self.proc_lang == "tr" else "is more economical!"
                msg = f"✅ {winner.name} {cheaper} ({diff:,.0f} TL fark)"
            self.proc_result.setText(msg)
        except ValueError:
            self.proc_result.setText("⚠️ Lütfen geçerli sayılar girin.")

    # ===== DİĞER METODLAR =====
    def _show_steel_info(self, name):
        try:
            m = Material.from_database(name)
            self.steel_lbl.setText(f"Ms={m.Ms}°C, C=%{m.carbon*100:.2f}")
        except: self.steel_lbl.setText("")

    def _get_process_name(self):
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
            self.aust_edit = QLineEdit("850")
            self.proc_layout.addRow(self.lang_manager.tr("aust_temp"), self.aust_edit)
            self.media_cb = QComboBox(); self.media_cb.addItems(["Oil","Water","Polymer","Brine"])
            self.proc_layout.addRow(self.lang_manager.tr("media"), self.media_cb)
            self.ag_cb = QComboBox(); self.ag_cb.addItems(["moderate","still","vigorous"])
            self.proc_layout.addRow(self.lang_manager.tr("agitation"), self.ag_cb)
        elif internal == "Tempering":
            self.temp_edit = QLineEdit("300")
            self.proc_layout.addRow(self.lang_manager.tr("aust_temp"), self.temp_edit)
            self.time_edit = QLineEdit("3600")
            self.proc_layout.addRow(self.lang_manager.tr("tempering_time"), self.time_edit)
        elif internal == "Carburizing":
            self.ctemp_edit = QLineEdit("930")
            self.proc_layout.addRow(self.lang_manager.tr("aust_temp"), self.ctemp_edit)
            self.ctime_edit = QLineEdit("7200")
            self.proc_layout.addRow(self.lang_manager.tr("tempering_time"), self.ctime_edit)
            self.cpot_edit = QLineEdit("0.8")
            self.proc_layout.addRow(self.lang_manager.tr("carbon_potential"), self.cpot_edit)

    def _start_sim(self):
        self.run_btn.setEnabled(False); self.progress.setVisible(True); self.progress.setValue(0)
        self.log_txt.clear()
        cfg = {"steel": self.steel_cb.currentText(), "process": self._get_process_name()}
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
        self.current_result = res
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
        info = f"<b>{el['name']} ({el['sym']})</b><br>Atom No: {num} | Kütle: {el['mass']} u<br>"
        if el.get('melt') is not None:
            info += f"Erime: {el['melt']}°C | Kaynama: {el['boil']}°C<br>"
        self.elem_info_lbl.setText(info)
        effect = self.pt.get_effect(el['sym'])
        txt = ""
        if effect:
            txt += f"<b>{el['sym']} - Çelikteki Rolü:</b><br>{effect['role']}<br><br>"
            for d in effect['details']: txt += f"• {d}<br>"
            txt += f"<br>Maks: %{effect['max']} | Tipik: {effect['range']}"
        elif el['sym'] == 'Fe': txt = "<b>Demir - Çeliğin temeli</b><br>"
        else: txt = f"<i>{el['name']} alaşım elementi değil.</i>"
        inter = self.pt.get_interactions(el['sym'])
        if inter:
            txt += "<br><br><b>Etkileşimler:</b><br>"
            for ix in inter:
                other = ix['pair'][1] if ix['pair'][0] == el['sym'] else ix['pair'][0]
                txt += f"• {el['sym']} + {other} → {ix['effect']}<br>"
        self.steel_info_text.setHtml(txt)

    def _calc_lever(self):
        try:
            Ca = float(self.lever_ca.text()); Cb = float(self.lever_cb.text()); Co = float(self.lever_co.text())
            result = lever_calculate(Ca, Cb, Co)
            txt = f"<b>Faz Oranları:</b><br>α fazı: <b>%{result.percent_alpha:.1f}</b><br>β fazı: <b>%{result.percent_beta:.1f}</b><br><br>"
            txt += f"<b>Kaldıraç Kuralı:</b><br>fα = (Cβ - Co) / (Cβ - Cα) = ({Cb} - {Co}) / ({Cb} - {Ca}) = <b>{result.fraction_alpha:.4f}</b><br>"
            txt += f"fβ = (Co - Cα) / (Cβ - Cα) = ({Co} - {Ca}) / ({Cb} - {Ca}) = <b>{result.fraction_beta:.4f}</b>"
            self.lever_result.setText(txt)
        except ValueError as e:
            self.lever_result.setText(f"<span style='color:#f38ba8;'>Hata: {e}</span>")

    def _load_lever_example(self, name):
        if name in FE_C_EXAMPLES:
            ex = FE_C_EXAMPLES[name]
            self.lever_ca.setText(str(ex["Ca"])); self.lever_cb.setText(str(ex["Cb"])); self.lever_co.setText(str(ex["Co"]))
            self._calc_lever()

    def _redraw_fec(self, highlight_T=None):
        if not self.fec_sliders: return
        composition = {}
        for elem, data in self.fec_sliders.items():
            composition[elem] = data["slider"].value() / 100.0
        C_pct = composition.get("C", 0.77)
        T_val = highlight_T if highlight_T else self.fec_temp_slider.value()
        self.fec_ax.clear()
        self.fec_ax.tick_params(colors='#cdd6f4', labelsize=10)
        for spine in self.fec_ax.spines.values(): spine.set_color('#45475a')
        self.fec_ax.xaxis.label.set_color('#cdd6f4'); self.fec_ax.yaxis.label.set_color('#cdd6f4')
        self.fec_ax.title.set_color('#cdd6f4')
        self.fec_engine.draw(self.fec_ax, composition, highlight_point=(C_pct, T_val))
        self.fec_canvas.draw()

    def _on_fec_slider_changed(self, element):
        if element in self.fec_sliders:
            data = self.fec_sliders[element]
            val = data["slider"].value() / 100.0
            data["label"].setText(f"%{val:.2f}")
            self._redraw_fec()
            self._update_fec_phase_info()

    def _on_fec_temp_changed(self):
        T = self.fec_temp_slider.value()
        self.fec_temp_lbl.setText(f"{T}°C")
        self._redraw_fec(highlight_T=T)
        self._update_fec_phase_info()

    def _on_fec_material_changed(self, steel_name):
        if steel_name == self.lang_manager.tr("fec_custom"): return
        try:
            mat = Material.from_database(steel_name)
            comp = mat.composition
            for elem, data in self.fec_sliders.items():
                if elem in comp:
                    val = int(comp[elem] * 100)
                    data["slider"].setValue(val)
                    data["label"].setText(f"%{comp[elem]:.2f}")
                elif elem == "C":
                    val = int(mat.carbon * 100)
                    data["slider"].setValue(val)
                    data["label"].setText(f"%{mat.carbon:.2f}")
            self._redraw_fec()
            self._update_fec_phase_info()
        except Exception as e:
            pass

    def _update_fec_phase_info(self):
        if not self.fec_sliders: return
        composition = {}
        for elem, data in self.fec_sliders.items():
            composition[elem] = data["slider"].value() / 100.0
        C_pct = composition.get("C", 0.77)
        T_val = self.fec_temp_slider.value()
        result = self.fec_engine.get_phases(T_val, C_pct, composition)
        html = f"<h3>{result.description}</h3><table width='100%'><tr><th>Faz</th><th>Oran</th><th>Gösterge</th></tr>"
        colors = {"α": "#89b4fa", "γ": "#f38ba8", "Fe₃C": "#fab387", "Sıvı": "#a6e3a1", "Perlit": "#cba6f7", "Ledeburit": "#f9e2af"}
        for phase, frac in result.fractions.items():
            pct = frac * 100
            color = colors.get(phase.split()[0], "#cdd6f4")
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            html += f"<tr><td>{phase}</td><td>%{pct:.1f}</td><td><span style='color:{color}'>{bar}</span></td></tr>"
        html += "</table>"
        html += f"<p><b>Ötektoid Sıcaklığı:</b> {self.fec_engine.adjust_boundaries(composition)['T_A1']:.0f}°C</p>"
        html += f"<p><b>Ötektoid Bileşimi:</b> %{self.fec_engine.adjust_boundaries(composition)['C_eutectoid']:.3f} C</p>"
        self.fec_phase_info.setHtml(html)

    def _reset_fec(self):
        defaults = {"C": 77, "Mn": 50, "Si": 20, "Cr": 0, "Ni": 0, "Mo": 0}
        for elem, val in defaults.items():
            if elem in self.fec_sliders:
                self.fec_sliders[elem]["slider"].setValue(val)
                self.fec_sliders[elem]["label"].setText(f"%{val/100:.2f}")
        self.fec_temp_slider.setValue(727); self.fec_temp_lbl.setText("727°C")
        self._redraw_fec(); self._update_fec_phase_info()

    def _generate_pdf_report(self):
        if not self.current_result:
            self.pdf_status.setText("Önce simülasyon çalıştırın.")
            return
        try:
            path = generate_pdf_report(self.current_result, Material.from_database(self.steel_cb.currentText()),
                                       {"process": self.proc_cb.currentText(), "aust_temp": getattr(self, 'aust_edit', None)})
            self.pdf_status.setText(f"Rapor oluşturuldu: {path}")
        except Exception as e:
            self.pdf_status.setText(f"Hata: {e}")

    def _draw_ttt_diagram(self):
        steel = self.ttt_steel_cb.currentText()
        ttt_data = load_ttt_data(steel)
        self.ttt_ax.clear()
        self.ttt_ax.tick_params(colors='#cdd6f4')
        draw_ttt(self.ttt_ax, ttt_data)
        self.ttt_canvas.draw()

    def _calc_distortion(self):
        try:
            cr = float(self.distort_coolrate.text())
            fm = float(self.distort_mart.text())
            cp = float(self.distort_carbon.text())
            ys = float(self.distort_yield.text())
            stress = estimate_residual_stress(cr, fm, cp)
            risk = distortion_risk(stress, ys)
            self.distort_result.setText(f"Kalıntı Gerilme: {stress} MPa | Risk: {risk}")
        except ValueError:
            self.distort_result.setText("Geçersiz giriş.")


    def _on_lang_changed(self, index):
        lang = "tr" if index == 0 else "en"
        if lang != self.lang_manager.current_lang:
            self.lang_manager.set_language(lang)
            self._retranslate_ui()

    def _retranslate_ui(self):
        """Tüm arayüz metinlerini güncelle"""
        lang = self.lang_manager.current_lang
        self.setWindowTitle(self.lang_manager.tr("window_title"))

        # Sekme isimleri
        tab_keys = [
            (0, "simulation_tab"), (1, "guide_tab"), (2, "periodic_tab"),
            (3, "lever_tab"), (4, "fec_tab"), (5, "ree_tab"),
            (6, "procurement_tab"), (7, "pdf_tab"), (8, "ttt_tab"),
            (9, "distortion_tab"), (10, "diffusion_tab"), (11, "alloy_tab"),
            (12, "failure_modes_tab")
        ]
        for i, key in tab_keys:
            if i < self.tabs.count():
                self.tabs.setTabText(i, self.lang_manager.tr(key))

        # Proses grubu ve ilgili etiketler
        for child in self.findChildren(QGroupBox):
            if child.title() in ["Proses Tanımı", "Process Definition"]:
                child.setTitle(self.lang_manager.tr("process_group"))
            elif child.title() in ["Element Bilgisi", "Element Info"]:
                child.setTitle(self.lang_manager.tr("element_info"))
            elif child.title() in ["Alaşım Etkileri", "Alloy Effects"]:
                child.setTitle(self.lang_manager.tr("alloy_effects"))
            elif child.title() in ["Kompozisyon Değerleri", "Composition Values"]:
                child.setTitle(self.lang_manager.tr("lever_composition"))
            elif child.title() in ["Sonuç", "Result"]:
                child.setTitle(self.lang_manager.tr("lever_result"))
            elif child.title() in ["📋 Hazır Malzeme Seç", "📋 Select Material"]:
                child.setTitle(self.lang_manager.tr("fec_ready_material"))
            elif child.title() in ["🧪 Element Bileşimi (%)", "🧪 Element Composition (%)"]:
                child.setTitle(self.lang_manager.tr("fec_element_composition"))
            elif child.title() in ["🌡️ Sıcaklık (°C)", "🌡️ Temperature (°C)"]:
                child.setTitle(self.lang_manager.tr("fec_temperature"))
            elif child.title() in ["📊 Faz Analizi", "📊 Phase Analysis"]:
                child.setTitle(self.lang_manager.tr("fec_phase_analysis"))
            elif child.title() in ["❓ NEDEN ALAŞIM ÇELİĞİ?", "❓ WHY ALLOY STEEL?"]:
                child.setTitle(self.lang_manager.tr("why_alloy"))

        # Proses combobox
        current_proc = self._get_process_name()
        self.proc_cb.blockSignals(True)
        self.proc_cb.clear()
        self.proc_cb.addItems([
            self.lang_manager.tr("quenching"),
            self.lang_manager.tr("tempering"),
            self.lang_manager.tr("carburizing")
        ])
        if current_proc == "Quenching":
            self.proc_cb.setCurrentIndex(0)
        elif current_proc == "Tempering":
            self.proc_cb.setCurrentIndex(1)
        elif current_proc == "Carburizing":
            self.proc_cb.setCurrentIndex(2)
        self.proc_cb.blockSignals(False)
        self._on_proc_changed(self.proc_cb.currentText())

        self.run_btn.setText(self.lang_manager.tr("run_btn"))
        self.elem_info_lbl.setText(self.lang_manager.tr("click_element"))
        self.guide_label.setText(self.lang_manager.tr("guide_tab"))
        self.lever_info_lbl.setText(self.lang_manager.tr("lever_info"))
        self.lever_result.setText(self.lang_manager.tr("lever_initial_result"))

        # Fe-C combo box placeholder
        self.fec_material_cb.setItemText(0, self.lang_manager.tr("fec_custom"))

        # Lever example combo
        example_cb = None
        for btn in self.findChildren(QPushButton):
            if btn.text() in ["Hesapla", "Calculate"]:
                btn.setText(self.lang_manager.tr("lever_calculate"))
        # yeniden ekleyelim
        # REE başlıkları
        # PDF buton
        for btn in self.findChildren(QPushButton):
            if btn.text() in ["📄 PDF Rapor Oluştur", "📄 Generate PDF Report"]:
                btn.setText(self.lang_manager.tr("pdf_generate"))
        # Diğer butonları topluca güncellemek için _translate_failure_modes çağrılıyor
        if hasattr(self, '_translate_failure_modes'):
            self._translate_failure_modes()
        self.statusBar().showMessage(self.lang_manager.tr("ready"))

    def _translate_failure_modes(self):
        lang = self.lang_manager.current_lang
        data = self.failure_db.get_all()
        self.failure_title.setText(data["title"][lang])
        intro_html = "<ul>"
        for item in data["intro"][lang]:
            intro_html += f"<li>{item}</li>"
        intro_html += "</ul>"
        self.failure_intro.setHtml(intro_html)
        for key, (title_label, content_label) in self.failure_card_widgets.items():
            mode_data = data["modes"][key]
            title_label.setText(f"{mode_data['icon']} {mode_data['title'][lang]}")
            content_label.setText("\n".join([f"• {line}" for line in mode_data["content"][lang]]))
        self.failure_fractography_title.setText(data["fractography"]["title"][lang])
        self.failure_fractography_content.setText(data["fractography"]["content"][lang])
        self.failure_prevention_title.setText(data["prevention"]["title"][lang])
        self.failure_prevention_list.setText("\n".join([f"• {item}" for item in data["prevention"]["items"][lang]]))
    
    def _open_tool(self, tool_name):
        """Profesyonel araç penceresini açar"""
        windows = {
            "metrical": MetricalWindow,
            "pandat": PandatWindow,
            "steelmaking": SteelmakingWindow,
            "simufact": SimufactWindow,
            "steeluni": SteeluniversityWindow,
            "mipar": MiparWindow,
            "comsol": ComsolWindow,
            "vesta": VestaWindow,
            "clemex": ClemexWindow,
            "ironmaking": IronmakingWindow,
        }
        if tool_name in windows:
            self._tool_window = windows[tool_name](self)
            self._tool_window.show()

    def _translate_tools(self):
        """Araçlar sekmesindeki metinleri güncelle"""
        lang = self.lang_manager.current_lang
        with open(os.path.join(BASE_DIR, "..", "database", "tools_resources.json"), encoding='utf-8') as f:
            tools_data = json.load(f)
        self.tools_title.setText(tools_data["title"][lang])
        self.tools_intro.setText(tools_data["intro"][lang])
        if hasattr(self, 'tools_widgets'):
            for i, (name_lbl, desc_lbl) in enumerate(self.tools_widgets):
                tool = tools_data["tools"][i]
                name_lbl.setText(tool["name"])
                desc_lbl.setText(tool[f"desc_{lang}"])

    # --- Moleküler Dinamik ---
    def _run_md(self):
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
            self.md_status.setText(f"❌ Hata: {e}")

    # --- Veri Analizi (Origin) ---
    def _get_xy(self):
        x = [float(v.strip()) for v in self.fit_x.text().split(',')]
        y = [float(v.strip()) for v in self.fit_y.text().split(',')]
        return np.array(x), np.array(y)

    def _linear_fit(self):
        x, y = self._get_xy()
        r = linear_fit(x, y)
        self.fit_ax.clear(); self.fit_ax.scatter(x, y, c='cyan'); self.fit_ax.plot(x, r['slope']*x + r['intercept'], 'r-')
        self.fit_canvas.draw()
        self.fit_result.setText(f"Doğrusal: y = {r['slope']:.4f}x + {r['intercept']:.4f} | R² = {r['r_squared']:.4f}")

    def _poly_fit(self):
        x, y = self._get_xy()
        r = poly_fit(x, y, 2)
        self.fit_ax.clear(); self.fit_ax.scatter(x, y, c='cyan')
        xs = np.linspace(min(x), max(x), 100)
        self.fit_ax.plot(xs, np.polyval(r['coeffs'], xs), 'r-')
        self.fit_canvas.draw()
        self.fit_result.setText(f"Polinom 2°: R² = {r['r_squared']:.4f}")

    def _exp_fit(self):
        x, y = self._get_xy()
        r = exp_fit(x, y)
        if r:
            self.fit_ax.clear(); self.fit_ax.scatter(x, y, c='cyan')
            xs = np.linspace(min(x), max(x), 100)
            self.fit_ax.plot(xs, r['a']*np.exp(r['b']*xs), 'r-')
            self.fit_canvas.draw()
            self.fit_result.setText(f"Üstel: y = {r['a']:.4f}*exp({r['b']:.4f}x) | R² = {r['r_squared']:.4f}")
        else:
            self.fit_result.setText("Üstel fit başarısız.")

    def _gauss_fit(self):
        x, y = self._get_xy()
        r = gaussian_fit(x, y)
        if r:
            self.fit_ax.clear(); self.fit_ax.scatter(x, y, c='cyan')
            xs = np.linspace(min(x), max(x), 100)
            self.fit_ax.plot(xs, r['amplitude']*np.exp(-(xs-r['mean'])**2/(2*r['sigma']**2)), 'r-')
            self.fit_canvas.draw()
            self.fit_result.setText(f"Gaussian: A={r['amplitude']:.2f}, μ={r['mean']:.2f}, σ={r['sigma']:.2f} | R²={r['r_squared']:.4f}")
        else:
            self.fit_result.setText("Gaussian fit başarısız.")

    def _calc_stats(self):
        _, y = self._get_xy()
        s = descriptive_stats(y)
        self.fit_result.setText(f"Ort: {s['mean']:.4f} | Std: {s['std']:.4f} | Çarpıklık: {s['skew']:.4f} | Basıklık: {s['kurtosis']:.4f}")

    # --- Termodinamik (Thermo-Calc) ---
    def _calc_equilibrium(self):
        try:
            T = float(self.thermo_T.text())
            omega = float(self.thermo_omega.text())
            x0 = float(self.thermo_x0.text())
            x_eq = equilibrium_composition(T, omega, x0)
            self.thermo_result.setText(f"Denge kompozisyonu: x = {x_eq:.4f}")
        except Exception as e:
            self.thermo_result.setText(f"Hata: {e}")

    # --- Alaşım Termodinamiği (FactSage) ---
    def _calc_activity(self):
        try:
            x = float(self.alloy_x.text())
            T = float(self.alloy_T.text())
            params = [float(v.strip()) for v in self.alloy_params.text().split(',')]
            gamma = activity_coefficient(x, T, params)
            self.alloy_result.setText(f"Aktivite katsayısı: γ = {gamma:.6f}")
        except Exception as e:
            self.alloy_result.setText(f"Hata: {e}")

    # --- Katılaşma (Click2Cast) ---
    def _calc_solidification(self):
        try:
            V = float(self.cast_V.text())
            A = float(self.cast_A.text())
            Cm = float(self.cast_Cm.text())
            t = chvorinov_rule(V, A, Cm)
            self.cast_result.setText(f"Katılaşma süresi: t = {t:.2f} s")
        except Exception as e:
            self.cast_result.setText(f"Hata: {e}")

    # --- Kristal Yapı (Crystal Maker) ---
    def _draw_crystal(self):
        try:
            system = self.xtal_system.currentText()
            size = self.xtal_size.value()
            pos = generate_lattice(system, size, size, size)
            self.xtal_ax.clear()
            self.xtal_ax.scatter(pos[:, 0], pos[:, 1], pos[:, 2], c='steelblue', s=50, alpha=0.8)
            self.xtal_ax.set_title(f"{system.upper()} Kristal Yapı", color='#cdd6f4')
            self.xtal_canvas.draw()
        except Exception as e:
            pass

    # --- Difüzyon (Dictra) ---

    def _load_image(self):
        path, _ = QFileDialog.getOpenFileName(None, "Görüntü Seç", "", "Images (*.png *.jpg *.bmp)")
        if path:
            from matplotlib.image import imread
            self._loaded_img = imread(path)
            if len(self._loaded_img.shape) == 3:
                self._loaded_img = np.mean(self._loaded_img, axis=2)
            self.img_ax.clear(); self.img_ax.imshow(self._loaded_img, cmap='gray')
            self.img_canvas.draw()
            self.img_status.setText(f"Yüklendi: {os.path.basename(path)}")

    def _apply_otsu(self):
        if hasattr(self, '_loaded_img'):
            binary = auto_threshold_otsu(self._loaded_img)
            self.img_ax.clear(); self.img_ax.imshow(binary, cmap='gray')
            self.img_canvas.draw()
            self.img_status.setText("Otsu eşikleme uygulandı")

    def _analyze_particles(self):
        if hasattr(self, '_loaded_img'):
            binary = auto_threshold_otsu(self._loaded_img)
            particles, labeled = particle_analysis(binary)
            self.img_ax.clear(); self.img_ax.imshow(labeled, cmap='nipy_spectral')
            self.img_canvas.draw()
            self.img_status.setText(f"✅ {len(particles)} parçacık bulundu")

    # --- JMatPro ---
    def _calc_jmatpro(self):
        try:
            comp = {'C': float(self.jmatpro_C.text())/100, 'Mn': float(self.jmatpro_Mn.text())/100, 'Cr': float(self.jmatpro_Cr.text())/100}
            ttt = calculate_ttt(comp)
            Ms = ttt['Ms']
            hardness = hardness_from_cct(10, comp)
            self.jmatpro_result.setText(f"Ms = {Ms:.0f}°C | Tahmini Sertlik (10°C/s): {hardness:.0f} HV")
        except Exception as e:
            self.jmatpro_result.setText(f"Hata: {e}")

    def _simulate_diffusion(self):
        """Karbon difüzyon profilini hesapla ve çiz"""
        from simulation.carburizing_sim import simulate_carburizing
        try:
            x_mm, profile = simulate_carburizing(T, t_h, Cs, C0)
        except Exception as e:
            QMessageBox.warning(self, "Difüzyon Hatası", str(e))
    
        import numpy as np
        try:
            x_m = np.linspace(0, L, 200)
            profile = C0 + (Cs - C0) * np.exp(-x_m**2 / (4 * D * t + 1e-20))
            profile_pct = profile * 100
        except Exception as e:
            QMessageBox.warning(self, 'Difüzyon Hatası', str(e))

def main():
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setFont(QFont("Segoe UI", 9))
        win = MainWindow()
        win.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
        main()
