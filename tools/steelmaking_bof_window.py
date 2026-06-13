
"""BOF Çelik Üretimi ve İkincil Metalurji Penceresi"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from simulation.steelmaking_sim import (
    calculate_decarburization,
    calculate_dephosphorization,
    calculate_desulfurization,
    calculate_inclusion_modification,
    calculate_ladle_refining,
)

class BOFSteelmakingWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🏭 BOF Çelik Üretimi ve İkincil Metalurji")
        self.setMinimumSize(1000, 750)
        self._ui()
        self._load_style()

    def _load_style(self):
        self.setStyleSheet("""
            QMainWindow { background: #1e1e2e; }
            QLabel { color: #cdd6f4; }
            QGroupBox { color: #cdd6f4; border: 1px solid #45475a; border-radius: 6px; margin-top: 12px; padding-top: 14px; font-weight: bold; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 6px; color: #89b4fa; background: #1e1e2e; }
            QPushButton { background: #89b4fa; color: #1e1e2e; border-radius: 4px; padding: 8px 16px; font-weight: bold; }
            QPushButton:hover { background: #74c7ec; }
            QLineEdit, QDoubleSpinBox { background: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 5px; }
            QTextEdit { background: #313244; color: #cdd6f4; border: 1px solid #45475a; }
            QTabWidget::pane { border: 1px solid #45475a; background: #1e1e2e; }
        """)

    def _ui(self):
        c = QWidget()
        self.setCentralWidget(c)
        main_layout = QVBoxLayout(c)

        # Üst panel – BOF girdileri
        top = QGroupBox("BOF Parametreleri ve Sıcak Metal")
        top_layout = QHBoxLayout(top)

        # Sıcak metal bileşimi
        hm_group = QGroupBox("Sıcak Metal Bileşimi (%)")
        hm_layout = QFormLayout(hm_group)
        self.hm_C = QDoubleSpinBox(); self.hm_C.setRange(3.0, 5.0); self.hm_C.setValue(4.5); self.hm_C.setSingleStep(0.1)
        hm_layout.addRow("C :", self.hm_C)
        self.hm_Si = QDoubleSpinBox(); self.hm_Si.setRange(0.1, 2.0); self.hm_Si.setValue(0.8); self.hm_Si.setSingleStep(0.1)
        hm_layout.addRow("Si :", self.hm_Si)
        self.hm_Mn = QDoubleSpinBox(); self.hm_Mn.setRange(0.1, 1.5); self.hm_Mn.setValue(0.5); self.hm_Mn.setSingleStep(0.1)
        hm_layout.addRow("Mn :", self.hm_Mn)
        self.hm_P = QDoubleSpinBox(); self.hm_P.setRange(0.01, 0.30); self.hm_P.setValue(0.10); self.hm_P.setSingleStep(0.01)
        hm_layout.addRow("P :", self.hm_P)
        self.hm_S = QDoubleSpinBox(); self.hm_S.setRange(0.01, 0.10); self.hm_S.setValue(0.04); self.hm_S.setSingleStep(0.01)
        hm_layout.addRow("S :", self.hm_S)
        top_layout.addWidget(hm_group)

        # BOF işletme parametreleri
        bof_group = QGroupBox("BOF İşletme")
        bof_layout = QFormLayout(bof_group)
        self.bof_target_C = QDoubleSpinBox(); self.bof_target_C.setRange(0.01, 1.0); self.bof_target_C.setValue(0.05); self.bof_target_C.setSingleStep(0.01)
        bof_layout.addRow("Hedef C (%):", self.bof_target_C)
        self.bof_O2 = QDoubleSpinBox(); self.bof_O2.setRange(10, 100); self.bof_O2.setValue(50); self.bof_O2.setSuffix(" Nm³/t")
        bof_layout.addRow("Oksijen:", self.bof_O2)
        self.bof_CaO = QDoubleSpinBox(); self.bof_CaO.setRange(20, 100); self.bof_CaO.setValue(50); self.bof_CaO.setSuffix(" kg/t")
        bof_layout.addRow("Kireç (CaO):", self.bof_CaO)
        self.bof_temp = QDoubleSpinBox(); self.bof_temp.setRange(1550, 1750); self.bof_temp.setValue(1650); self.bof_temp.setSuffix(" °C")
        bof_layout.addRow("Sıcaklık:", self.bof_temp)
        self.bof_FeO = QDoubleSpinBox(); self.bof_FeO.setRange(5, 40); self.bof_FeO.setValue(20); self.bof_FeO.setSuffix(" %")
        bof_layout.addRow("Cüruf FeO:", self.bof_FeO)
        top_layout.addWidget(bof_group)

        # İkincil metalurji
        sec_group = QGroupBox("İkincil Metalurji (Ladil)")
        sec_layout = QFormLayout(sec_group)
        self.sec_CaO = QDoubleSpinBox(); self.sec_CaO.setRange(10, 80); self.sec_CaO.setValue(30); self.sec_CaO.setSuffix(" kg/t")
        sec_layout.addRow("CaO (ladil):", self.sec_CaO)
        self.sec_Al = QDoubleSpinBox(); self.sec_Al.setRange(0.1, 3.0); self.sec_Al.setValue(1.0); self.sec_Al.setSuffix(" kg/t")
        sec_layout.addRow("Al ilavesi:", self.sec_Al)
        self.sec_Ca = QDoubleSpinBox(); self.sec_Ca.setRange(0.05, 1.0); self.sec_Ca.setValue(0.3); self.sec_Ca.setSuffix(" kg/t")
        sec_layout.addRow("Ca enjeksiyonu:", self.sec_Ca)
        top_layout.addWidget(sec_group)

        main_layout.addWidget(top)

        # Buton
        self.btn_calc = QPushButton("🏭 BOF Simülasyonunu Çalıştır")
        self.btn_calc.clicked.connect(self._run_simulation)
        self.btn_calc.setMinimumHeight(45)
        main_layout.addWidget(self.btn_calc)

        # Sonuç raporu
        self.report = QTextEdit()
        self.report.setReadOnly(True)
        main_layout.addWidget(self.report)

        self.statusBar().showMessage("Hazır – Parametreleri girin ve simülasyonu çalıştırın.")

    def _run_simulation(self):
        """Ana BOF simülasyonu"""
        try:
            # Girdileri al
            C_init = self.hm_C.value()
            C_target = self.bof_target_C.value()
            O2 = self.bof_O2.value()
            CaO_bof = self.bof_CaO.value()
            T = self.bof_temp.value()
            FeO = self.bof_FeO.value()
            P_init = self.hm_P.value()
            S_init = self.hm_S.value()

            # Dekarbürizasyon
            decarb = calculate_decarburization(C_init, C_target, O2)

            # Fosfor giderme
            dephos = calculate_dephosphorization(P_init, CaO_bof, FeO, T)

            # Kükürt giderme (BOF)
            desulf = calculate_desulfurization(S_init, CaO_bof, FeO, T)

            # İkincil metalurji
            ladle = calculate_ladle_refining(desulf["final_S"], self.sec_CaO.value(), self.sec_Al.value())

            # Kalıntı modifikasyonu
            Al2O3_estimated = self.sec_Al.value() * 0.5
            inclusion = calculate_inclusion_modification(Al2O3_estimated, self.sec_Ca.value())

            # Baziklik
            basicity = CaO_bof / 15

            # Rapor
            self.report.setHtml(f"""
            <h2>🏭 BOF Çelik Üretimi Simülasyon Raporu</h2>
            <table border='1' cellpadding='6' style='border-collapse:collapse; width:100%; color:#cdd6f4;'>
            <tr style='background:#45475a;'><td colspan='2'><b>BOF Prosesi</b></td></tr>
            <tr><td>Giderilen Karbon</td><td>{decarb['C_removed']:.2f} kg/t</td></tr>
            <tr><td>CO Oluşumu</td><td>{decarb['CO']:.1f} kg/t</td></tr>
            <tr><td>CO₂ Oluşumu</td><td>{decarb['CO2']:.1f} kg/t</td></tr>
            <tr><td>Oksijen Tüketimi</td><td>{decarb['O2_used']:.1f} kg/t</td></tr>
            <tr><td>Cüruf Bazikliği (CaO/SiO₂)</td><td>{basicity:.1f}</td></tr>
            <tr style='background:#45475a;'><td colspan='2'><b>Fosfor Giderme</b></td></tr>
            <tr><td>Giderilen P</td><td>{dephos['P_removed']:.3f} %</td></tr>
            <tr><td>Nihai P</td><td>{dephos['final_P']:.3f} %</td></tr>
            <tr><td>Verim</td><td>%{dephos['efficiency']*100:.1f}</td></tr>
            <tr style='background:#45475a;'><td colspan='2'><b>Kükürt Giderme (BOF)</b></td></tr>
            <tr><td>Giderilen S</td><td>{desulf['S_removed']:.3f} %</td></tr>
            <tr><td>Nihai S</td><td>{desulf['final_S']:.3f} %</td></tr>
            <tr style='background:#45475a;'><td colspan='2'><b>İkincil Metalurji (Ladil)</b></td></tr>
            <tr><td>İlave S Giderme</td><td>{ladle['S_removed']:.3f} %</td></tr>
            <tr><td>Nihai S (ladil sonrası)</td><td>{ladle['final_S']:.3f} %</td></tr>
            <tr><td>Kalıntı Değerlendirmesi</td><td>{ladle['inclusion_rating']}</td></tr>
            <tr style='background:#45475a;'><td colspan='2'><b>Kalıntı Mühendisliği</b></td></tr>
            <tr><td>Modifiye Edilen Al₂O₃</td><td>{inclusion['modified']:.2f} kg/t</td></tr>
            <tr><td>Dökülebilirlik</td><td>{inclusion['castability']}</td></tr>
            </table>
            <p><i>✅ BOF çelik üretimi başarıyla simüle edildi.</i></p>
            """)
            self.statusBar().showMessage("✅ Simülasyon tamamlandı.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))
