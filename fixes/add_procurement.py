#!/usr/bin/env python3
"""
Satın Alma (Procurement) Rehberi Modülü
- Türkçe / İngilizce dil desteği
- Toplam Maliyet Hesaplayıcı (TCO)
- Tedarikçi karşılaştırma aracı
"""
import os, sys, json

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("=" * 70)
print("📊 SATIN ALMA REHBERİ MODÜLÜ")
print("=" * 70)

# =====================================================================
# 1. SATIN ALMA VERİTABANI (TR + EN)
# =====================================================================
procurement_db = {
    "tr": {
        "title": "📊 Satın Alma Rehberi – Toplam Değer Yaklaşımı",
        "subtitle": "\"Çelik maliyet baskısı altında ayakta kalan satın alma kararları\"",
        "sections": {
            "lower_total_cost": {
                "title": "1. Daha Düşük Toplam Maliyet",
                "content": [
                    "Bir ürünün satın alma fiyatı düşük olabilir ancak:",
                    "• Yeniden işleme (rework) maliyetleri",
                    "• Kalite problemleri",
                    "• Üretim duruşları",
                    "• Teslimat gecikmeleri",
                    "• Garanti ve bakım masrafları",
                    "",
                    "Toplam Maliyet = Satın Alma Fiyatı + İşletme Maliyeti + Kalite Maliyeti + Gecikme Maliyeti"
                ]
            },
            "lower_project_risk": {
                "title": "2. Daha Düşük Proje Riski",
                "content": [
                    "Satın alma kararları sadece maliyet değil risk yönetimidir.",
                    "Riskler:",
                    "• Kalitesiz malzeme",
                    "• Tedarikçi iflası",
                    "• Teslimat gecikmesi",
                    "• Teknik uyumsuzluk",
                    "• Güvenlik problemleri",
                    "",
                    "Profesyonel ekipler tedarikçi geçmişini, sertifikaları, referansları ve finansal durumu inceler."
                ]
            },
            "on_time_delivery": {
                "title": "3. Zamanında Teslimat",
                "content": [
                    "Bir fabrikanın üretim hattı durduğunda maliyetler çok yüksektir.",
                    "Geç teslimat:",
                    "• Üretimi durdurabilir",
                    "• Müşteriye teslimatı geciktirebilir",
                    "• Sözleşme cezalarına yol açabilir",
                    "",
                    "Çoğu profesyonel satın alma yöneticisi, %5 daha pahalı ama zamanında teslim eden tedarikçiyi tercih eder."
                ]
            },
            "best_total_value": {
                "title": "4. En İyi Toplam Değer",
                "content": [
                    "En düşük fiyat ≠ En iyi satın alma kararı",
                    "",
                    "Toplam değer unsurları:",
                    "• Fiyat",
                    "• Kalite",
                    "• Güvenilirlik",
                    "• Teslimat performansı",
                    "• Teknik destek",
                    "• Risk seviyesi",
                    "• Uzun vadeli maliyet",
                    "",
                    "Bu yaklaşıma Değer Odaklı Satın Alma (Value-Based Procurement) denir."
                ]
            },
            "expert_advice": {
                "title": "5. Uzman Tavsiyesi – Daha İyi Sonuçlar",
                "content": [
                    "• Veriye dayalı analiz yapın",
                    "• Uzman görüşü kullanın",
                    "• Sadece teklif fiyatına bakmayın",
                    "• Uzun vadeli sonuçları değerlendirin",
                    "",
                    "İyi satın alma = En ucuz ürünü almak değil, toplam sahip olma maliyetini (TCO) ve riski optimize etmektir."
                ]
            }
        },
        "calculator": {
            "title": "Toplam Maliyet Hesaplayıcı",
            "supplier_a": "Tedarikçi A",
            "supplier_b": "Tedarikçi B",
            "purchase_price": "Satın Alma Fiyatı",
            "rework_cost": "Yeniden İşleme Maliyeti",
            "delay_cost": "Gecikme Maliyeti",
            "quality_cost": "Kalite Kaybı Maliyeti",
            "total": "Gerçek Toplam Maliyet",
            "cheaper": "daha ekonomik!"
        }
    },
    "en": {
        "title": "📊 Procurement Guide – Total Value Approach",
        "subtitle": "\"Procurement decisions that hold up under steel-cost pressure\"",
        "sections": {
            "lower_total_cost": {
                "title": "1. Lower Total Cost",
                "content": [
                    "A product's purchase price may be low, but:",
                    "• Rework costs may arise",
                    "• Quality problems may occur",
                    "• Production may stop",
                    "• Delivery delays may happen",
                    "• Warranty and maintenance costs may increase",
                    "",
                    "Total Cost = Purchase Price + Operating Cost + Quality Cost + Delay Cost"
                ]
            },
            "lower_project_risk": {
                "title": "2. Lower Project Risk",
                "content": [
                    "Procurement decisions are not just about cost – they are about risk management.",
                    "Risks:",
                    "• Poor quality materials",
                    "• Supplier bankruptcy",
                    "• Delivery delays",
                    "• Technical incompatibility",
                    "• Safety issues",
                    "",
                    "Professional teams examine supplier history, certifications, references, and financial status."
                ]
            },
            "on_time_delivery": {
                "title": "3. On-Time Delivery",
                "content": [
                    "When a production line stops, costs skyrocket.",
                    "Late delivery can:",
                    "• Stop production",
                    "• Delay customer delivery",
                    "• Lead to contract penalties",
                    "",
                    "Most managers prefer a supplier who is 5% more expensive but delivers on time."
                ]
            },
            "best_total_value": {
                "title": "4. Best Total Value",
                "content": [
                    "Lowest price ≠ Best procurement decision",
                    "",
                    "Total value components:",
                    "• Price",
                    "• Quality",
                    "• Reliability",
                    "• Delivery performance",
                    "• Technical support",
                    "• Risk level",
                    "• Long-term cost",
                    "",
                    "This is called Value-Based Procurement."
                ]
            },
            "expert_advice": {
                "title": "5. Practical Insights – Better Outcomes",
                "content": [
                    "• Perform data-driven analysis",
                    "• Use expert opinion",
                    "• Don't just look at the bid price",
                    "• Evaluate long-term results",
                    "",
                    "Good procurement = Not buying the cheapest, but optimizing TCO and risk."
                ]
            }
        },
        "calculator": {
            "title": "Total Cost Calculator",
            "supplier_a": "Supplier A",
            "supplier_b": "Supplier B",
            "purchase_price": "Purchase Price",
            "rework_cost": "Rework Cost",
            "delay_cost": "Delay Cost",
            "quality_cost": "Quality Loss Cost",
            "total": "True Total Cost",
            "cheaper": "is more economical!"
        }
    }
}

write_file("database/procurement_guide.json", json.dumps(procurement_db, indent=2, ensure_ascii=False))
print("✅ database/procurement_guide.json")

# =====================================================================
# 2. PROCUREMENT MODÜLÜ
# =====================================================================
write_file("procurement/__init__.py", "")
write_file("procurement/calculator.py", '''"""Satın Alma Toplam Maliyet Hesaplayıcı"""
from dataclasses import dataclass

@dataclass
class SupplierCost:
    name: str
    purchase_price: float = 0.0
    rework_cost: float = 0.0
    delay_cost: float = 0.0
    quality_cost: float = 0.0
    
    @property
    def total(self) -> float:
        return self.purchase_price + self.rework_cost + self.delay_cost + self.quality_cost

def compare_suppliers(a: SupplierCost, b: SupplierCost) -> tuple:
    """İki tedarikçiyi karşılaştır, (kazanan, fark) döndür"""
    if a.total < b.total:
        return a, b.total - a.total
    elif b.total < a.total:
        return b, a.total - b.total
    return None, 0.0
''')
print("✅ procurement/calculator.py")

# =====================================================================
# 3. GUI'YE SATIN ALMA SEKMESİ EKLE
# =====================================================================
main_py = os.path.join(BASE, "app", "main.py")
if not os.path.exists(main_py):
    print("❌ app/main.py bulunamadı!")
    sys.exit(1)

with open(main_py, 'r', encoding='utf-8') as f:
    content = f.read()

# Import ekle
if "from procurement.calculator import" not in content:
    old = "from metallurgy.interactive_fec import FeCDiagram"
    new = "from metallurgy.interactive_fec import FeCDiagram\nfrom procurement.calculator import SupplierCost, compare_suppliers"
    if old in content:
        content = content.replace(old, new)
        print("✅ Procurement import eklendi")

# Procurement sekmesini ekle
procurement_tab = r'''
        # ===== SATIN ALMA REHBERİ SEKMESİ =====
        proc_tab = QWidget()
        proc_layout = QVBoxLayout(proc_tab)
        
        # Dil butonu
        lang_layout = QHBoxLayout()
        self.proc_lang = "tr"
        self.proc_tr_btn = QPushButton("🇹🇷 Türkçe")
        self.proc_tr_btn.setCheckable(True)
        self.proc_tr_btn.setChecked(True)
        self.proc_tr_btn.clicked.connect(lambda: self._switch_proc_lang("tr"))
        self.proc_en_btn = QPushButton("🇬🇧 English")
        self.proc_en_btn.setCheckable(True)
        self.proc_en_btn.clicked.connect(lambda: self._switch_proc_lang("en"))
        lang_layout.addWidget(self.proc_tr_btn)
        lang_layout.addWidget(self.proc_en_btn)
        lang_layout.addStretch()
        proc_layout.addLayout(lang_layout)
        
        # İçerik alanı (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.proc_scroll_layout = QVBoxLayout(scroll_content)
        scroll.setWidget(scroll_content)
        proc_layout.addWidget(scroll, 1)
        
        # Hesaplayıcı alanı
        calc_group = QGroupBox("")
        self.proc_calc_layout = QVBoxLayout(calc_group)
        proc_layout.addWidget(calc_group)
        
        # Veriyi yükle
        with open(os.path.join(BASE_DIR, "..", "database", "procurement_guide.json"), encoding='utf-8') as f:
            self.proc_data = json.load(f)
        
        # İlk yüklemeyi yap
        self._build_procurement_ui()
        
        tabs.addTab(proc_tab, "📊 Satın Alma")
'''

# Mevcut sekmelerden sonra ekle
last_tab_marker = 'tabs.addTab(ree_tab, "🧪 REE")'
if last_tab_marker in content:
    content = content.replace(last_tab_marker, last_tab_marker + "\n" + procurement_tab)
    print("✅ Satın Alma sekmesi eklendi")
else:
    # Fe-C sekmesinden sonra dene
    alt_marker = 'tabs.addTab(fec_tab, "🔬 Fe–C Diyagramı")'
    if alt_marker in content:
        content = content.replace(alt_marker, alt_marker + "\n" + procurement_tab)
        print("✅ Satın Alma sekmesi eklendi (Fe-C sonrası)")

# Metodları ekle
proc_methods = '''
    def _switch_proc_lang(self, lang):
        """Dil değiştir"""
        self.proc_lang = lang
        self.proc_tr_btn.setChecked(lang == "tr")
        self.proc_en_btn.setChecked(lang == "en")
        self._build_procurement_ui()
    
    def _build_procurement_ui(self):
        """Satın alma arayüzünü yeniden oluştur"""
        lang = self.proc_lang
        data = self.proc_data[lang]
        
        # Scroll içeriğini temizle
        while self.proc_scroll_layout.count():
            item = self.proc_scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Başlık
        title = QLabel(f"<h2>{data['title']}</h2>")
        title.setWordWrap(True)
        self.proc_scroll_layout.addWidget(title)
        
        subtitle = QLabel(f"<i>{data['subtitle']}</i>")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color:#a6adc8; font-size:14px; margin-bottom:15px;")
        self.proc_scroll_layout.addWidget(subtitle)
        
        # Bölümler
        for key, section in data["sections"].items():
            grp = QGroupBox(section["title"])
            grp_lay = QVBoxLayout(grp)
            for line in section["content"]:
                if line.startswith("•"):
                    lbl = QLabel(f"  {line}")
                    lbl.setStyleSheet("color:#cdd6f4; padding-left:15px;")
                elif line == "":
                    lbl = QLabel("")
                else:
                    lbl = QLabel(line)
                    lbl.setStyleSheet("color:#cdd6f4; font-weight:bold;" if not line.startswith(" ") else "color:#cdd6f4;")
                lbl.setWordWrap(True)
                grp_lay.addWidget(lbl)
            self.proc_scroll_layout.addWidget(grp)
        
        self.proc_scroll_layout.addStretch()
        
        # Hesaplayıcıyı güncelle
        self._build_calculator(lang)
    
    def _build_calculator(self, lang):
        """Toplam maliyet hesaplayıcıyı oluştur"""
        data = self.proc_data[lang]
        calc = data["calculator"]
        
        # Mevcut layout'u temizle (başlığı koru)
        parent = self.proc_calc_layout.parentWidget()
        if parent:
            old_group = parent.findChild(QGroupBox, "")
            if old_group:
                old_group.setTitle(calc["title"])
        
        # Layout'u temizle
        while self.proc_calc_layout.count():
            item = self.proc_calc_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Tedarikçi A
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
        
        # Tedarikçi B
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
        
        # Hesapla butonu
        calc_btn = QPushButton("🔄 Hesapla")
        calc_btn.clicked.connect(self._calc_procurement)
        self.proc_calc_layout.addWidget(calc_btn)
        
        # Sonuç
        self.proc_result = QLabel("")
        self.proc_result.setStyleSheet("font-size:16px; font-weight:bold; color:#89b4fa; padding:10px;")
        self.proc_calc_layout.addWidget(self.proc_result)
        
        # İlk hesaplamayı yap
        self._calc_procurement()
    
    def _calc_procurement(self):
        """Tedarikçi maliyetlerini hesapla ve karşılaştır"""
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

if '_switch_proc_lang' not in content:
    marker = 'def _show_element(self, num):'
    if marker in content:
        content = content.replace(marker, proc_methods + '\n    ' + marker)
        print("✅ Procurement metodları eklendi")

# Kaydet
with open(main_py, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "=" * 70)
print("🎉 SATIN ALMA REHBERİ BAŞARIYLA EKLENDİ!")
print("=" * 70)
print("\nYeni Özellikler:")
print("  📊 Satın Alma Rehberi sekmesi")
print("  🇹🇷🇬🇧 Türkçe / İngilizce dil desteği")
print("  📖 5 bölümlü rehber (Toplam Maliyet, Risk, Teslimat, Değer, Uzman Tavsiyesi)")
print("  🧮 İnteraktif TCO hesaplayıcı")
print("  📉 Tedarikçi A vs B karşılaştırma")
print("\nÇalıştır: python main.py")