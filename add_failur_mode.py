#!/usr/bin/env python3
"""
MALZEME HATA MODLARI MODÜLÜ
- Kırılma, Yorulma, Sürünme, Korozyon, Darbe, Aşınma
- Türkçe / İngilizce içerik
"""
import os, sys, json

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✅ {path}")

print("=" * 60)
print("🔧 MALZEME HATA MODLARI MODÜLÜ")
print("=" * 60)

# =====================================================================
# 1. VERİTABANI (JSON) - TR + EN
# =====================================================================
FAILURE_MODES = {
    "title": {
        "tr": "Malzeme Hata Modlarına Giriş",
        "en": "Introduction to Material Failure Modes"
    },
    "intro": {
        "tr": [
            "Her mühendislik malzemesinin sınırları vardır.",
            "Bu sınırlar şunlardan kaynaklanabilir: Aşırı gerilim, uzun süreli ısıya maruz kalma, kimyasal saldırı.",
            "Malzemelerin neden ve nasıl hasara uğradığını anlamak şunları önlememizi sağlar: Tehlikeli arızalar, hizmet ömrünü uzatma."
        ],
        "en": [
            "Every engineering material has its limits.",
            "These limits can arise from: Excessive stress, prolonged heat exposure, chemical attack.",
            "Understanding why and how materials fail allows us to prevent: Dangerous failures, extend service life."
        ]
    },
    "modes": {
        "fracture": {
            "icon": "💥",
            "title": {"tr": "Kırılma: Uyarılı veya Uyarısız", "en": "Fracture: With or Without Warning"},
            "content": {
                "tr": [
                    "Gerilme, malzemenin dayanımını aştığında oluşur.",
                    "Gevrek: Çatlaklar çok az uyarı ile hızla ilerler.",
                    "Sünek: Malzeme kırılmadan önce şekil değiştirir (boyun verme)."
                ],
                "en": [
                    "Occurs when stress exceeds material strength.",
                    "Brittle: Cracks propagate rapidly with little warning.",
                    "Ductile: Material deforms (necking) before fracture."
                ]
            }
        },
        "fatigue": {
            "icon": "🔄",
            "title": {"tr": "Yorulma: Tekrarlı Gerilme", "en": "Fatigue: Repeated Stress"},
            "content": {
                "tr": [
                    "Çevrimsel yükleme altında, genellikle akma dayanımının altında çatlaklar oluşur.",
                    "Gerilme yükseltici bölgelerde başlar ve ani kırılmaya kadar yavaşça büyür.",
                    "Köprülerde, uçak kanatlarında yaygındır."
                ],
                "en": [
                    "Cracks form under cyclic loading, usually below yield strength.",
                    "Starts at stress concentration areas and slowly grows until sudden fracture.",
                    "Common in bridges, aircraft wings."
                ]
            }
        },
        "creep": {
            "icon": "⏳",
            "title": {"tr": "Sürünme: Zamana Bağlı Şekil Değiştirme", "en": "Creep: Time-Dependent Deformation"},
            "content": {
                "tr": [
                    "Yüksek sıcaklıkta sabit yük altında kademeli, kalıcı deformasyon.",
                    "Türbin kanatlarında, buhar hatlarında görülür.",
                    "Üç aşamalıdır: Birincil, ikincil (kararlı), üçüncül (hızlanan)."
                ],
                "en": [
                    "Gradual, permanent deformation under constant load at high temperature.",
                    "Seen in turbine blades, steam lines.",
                    "Three stages: Primary, secondary (steady-state), tertiary (accelerating)."
                ]
            }
        },
        "corrosion": {
            "icon": "🧪",
            "title": {"tr": "Korozyonla İlişkili Hatalar", "en": "Corrosion-Related Failures"},
            "content": {
                "tr": [
                    "Gerilmeli korozyon çatlaması (SCC) ve korozyon yorulması, kimyasal ve mekanik gerilmeyi birleştirir.",
                    "SCC: Çekme gerilimi altındaki metallerde aşındırıcı ortamlara maruz kalındığında çatlaklar oluşur.",
                    "Korozyon Yorulması: Yorulma, aşındırıcı koşullar nedeniyle kötüleşir."
                ],
                "en": [
                    "Stress corrosion cracking (SCC) and corrosion fatigue combine chemical and mechanical stress.",
                    "SCC: Cracks form in metals under tensile stress when exposed to corrosive environments.",
                    "Corrosion Fatigue: Fatigue worsened by corrosive conditions."
                ]
            }
        },
        "impact": {
            "icon": "💢",
            "title": {"tr": "Şok Yükleme Nedeniyle Darbe Hatası", "en": "Impact Failure from Shock Loading"},
            "content": {
                "tr": [
                    "Ani kuvvetler (örneğin düşme, çarpışma) hızlı kırılmaya neden olabilir.",
                    "Tokluk, bu tür hasarlara direnmek için kritiktir."
                ],
                "en": [
                    "Sudden forces (e.g., drops, collisions) can cause rapid fracture.",
                    "Toughness is critical to resist such failures."
                ]
            }
        },
        "wear": {
            "icon": "🔧",
            "title": {"tr": "Aşınma: Yüzey Hasarı", "en": "Wear: Surface Damage"},
            "content": {
                "tr": [
                    "Sürtünme, kayma veya aşındırma nedeniyle kademeli malzeme kaybı.",
                    "Yapışmalı (Adhesive): Malzeme bir yüzeyden diğerine aktarılır.",
                    "Aşındırıcı (Abrasive): Sert parçacıklar daha yumuşak yüzeyleri aşındırır."
                ],
                "en": [
                    "Gradual material loss due to friction, sliding, or abrasion.",
                    "Adhesive: Material transfers from one surface to another.",
                    "Abrasive: Hard particles wear away softer surfaces."
                ]
            }
        }
    },
    "fractography": {
        "title": {"tr": "Kırık Yüzeyi Analiz Araçları (Fraktografi)", "en": "Fracture Surface Analysis Tools (Fractography)"},
        "content": {
            "tr": "Kırık yüzeyleri, hasarın kök nedenlerini belirlemek için SEM, optik mikroskopi ve görsel inceleme kullanılarak analiz edilir.",
            "en": "Fracture surfaces are analyzed using SEM, optical microscopy, and visual inspection to determine root causes of failure."
        }
    },
    "prevention": {
        "title": {"tr": "Önleme Stratejileri", "en": "Prevention Strategies"},
        "items": {
            "tr": [
                "Daha iyi yorulma veya sürünme direncine sahip malzemeler kullanın.",
                "Koruyucu kaplamalar uygulayın.",
                "Gerilme yoğunlaşmasını azaltmak için yeniden tasarım yapın.",
                "Doğru üretim ve muayeneyi sağlayın."
            ],
            "en": [
                "Use materials with better fatigue or creep resistance.",
                "Apply protective coatings.",
                "Redesign to reduce stress concentration.",
                "Ensure proper manufacturing and inspection."
            ]
        }
    }
}

write_file("database/failure_modes.json", json.dumps(FAILURE_MODES, indent=2, ensure_ascii=False))

# =====================================================================
# 2. MODÜL
# =====================================================================
write_file("metallurgy/failure_modes.py", '''"""Malzeme Hata Modları Modülü"""
import json, os

class FailureModes:
    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, "..", "database", "failure_modes.json")
        with open(path, encoding='utf-8') as f:
            self.data = json.load(f)
    
    def get_all(self): return self.data
    def get_modes(self): return self.data["modes"]
    def get_intro(self): return self.data["intro"]
    def get_prevention(self): return self.data["prevention"]
    def get_fractography(self): return self.data["fractography"]
''')
print("✅ metallurgy/failure_modes.py")

# =====================================================================
# 3. GUI'YE SEKMESİ EKLEME
# =====================================================================
main_py = os.path.join(BASE, "app", "main.py")
if not os.path.exists(main_py):
    print("❌ app/main.py bulunamadı!")
    sys.exit(1)

with open(main_py, 'r', encoding='utf-8') as f:
    content = f.read()

# Import ekle
if "from metallurgy.failure_modes import FailureModes" not in content:
    old = "from metallurgy.alloy_guide import AlloyGuide"
    new = "from metallurgy.alloy_guide import AlloyGuide\nfrom metallurgy.failure_modes import FailureModes"
    if old in content:
        content = content.replace(old, new)
        print("✅ FailureModes import eklendi")
    else:
        # Alternatif
        old2 = "from metallurgy.ree import REEDatabase"
        new2 = "from metallurgy.ree import REEDatabase\nfrom metallurgy.failure_modes import FailureModes"
        if old2 in content:
            content = content.replace(old2, new2)
            print("✅ FailureModes import eklendi (alternatif)")

# Hata Modları sekmesini ekle
failure_tab_code = '''
        # ===== MALZEME HATA MODLARI SEKMESİ =====
        self.failure_db = FailureModes()
        failure_data = self.failure_db.get_all()
        
        failure_tab = QWidget()
        failure_layout = QVBoxLayout(failure_tab)
        
        # Scroll alan
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll.setWidget(scroll_content)
        failure_layout.addWidget(scroll)
        
        # Başlık
        self.failure_title = QLabel()
        self.failure_title.setStyleSheet("font-size:18px; font-weight:bold; color:#89b4fa;")
        self.failure_title.setWordWrap(True)
        scroll_layout.addWidget(self.failure_title)
        
        # Giriş
        self.failure_intro = QTextEdit()
        self.failure_intro.setReadOnly(True)
        self.failure_intro.setMaximumHeight(120)
        self.failure_intro.setStyleSheet("font-size:13px; color:#cdd6f4; background-color:#313244; border:1px solid #45475a; border-radius:4px; padding:8px;")
        scroll_layout.addWidget(self.failure_intro)
        
        # Hata modları - grid şeklinde kartlar
        modes = failure_data["modes"]
        modes_widget = QWidget()
        modes_grid = QGridLayout(modes_widget)
        modes_grid.setSpacing(10)
        
        row = 0
        col = 0
        for key, mode_data in modes.items():
            card = QGroupBox()
            card_layout = QVBoxLayout(card)
            
            # Başlık
            self.__setattr__(f"failure_card_{key}_title", QLabel())
            card_title = self.__getattribute__(f"failure_card_{key}_title")
            card_title.setStyleSheet("font-weight:bold; color:#89b4fa; font-size:13px;")
            card_title.setWordWrap(True)
            card_layout.addWidget(card_title)
            
            # İçerik
            self.__setattr__(f"failure_card_{key}_content", QLabel())
            card_content = self.__getattribute__(f"failure_card_{key}_content")
            card_content.setWordWrap(True)
            card_content.setStyleSheet("color:#cdd6f4; font-size:11px;")
            card_layout.addWidget(card_content)
            
            card.setStyleSheet("QGroupBox { background-color:#313244; border:1px solid #45475a; border-radius:6px; padding:10px; }")
            modes_grid.addWidget(card, row, col)
            
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        scroll_layout.addWidget(modes_widget)
        
        # Fraktografi
        self.failure_fractography_title = QLabel()
        self.failure_fractography_title.setStyleSheet("font-size:14px; font-weight:bold; color:#89b4fa; margin-top:15px;")
        self.failure_fractography_title.setWordWrap(True)
        scroll_layout.addWidget(self.failure_fractography_title)
        
        self.failure_fractography_content = QLabel()
        self.failure_fractography_content.setWordWrap(True)
        self.failure_fractography_content.setStyleSheet("color:#cdd6f4; font-size:12px; padding:8px; background-color:#313244; border-radius:4px;")
        scroll_layout.addWidget(self.failure_fractography_content)
        
        # Önleme Stratejileri
        self.failure_prevention_title = QLabel()
        self.failure_prevention_title.setStyleSheet("font-size:14px; font-weight:bold; color:#89b4fa; margin-top:15px;")
        self.failure_prevention_title.setWordWrap(True)
        scroll_layout.addWidget(self.failure_prevention_title)
        
        self.failure_prevention_list = QLabel()
        self.failure_prevention_list.setWordWrap(True)
        self.failure_prevention_list.setStyleSheet("color:#cdd6f4; font-size:12px; padding:8px; background-color:#313244; border-radius:4px;")
        scroll_layout.addWidget(self.failure_prevention_list)
        
        scroll_layout.addStretch()
        tabs.addTab(failure_tab, "🔧 Hata Modları")
        
        # İlk çeviriyi yap
        self._translate_failure_modes()
'''

# Alaşım Rehberi sekmesinden sonra ekle
marker = 'tabs.addTab(alloy_tab, self.lang_manager.tr("alloy_tab"))'
if marker in content:
    content = content.replace(marker, marker + "\n" + failure_tab_code)
    print("✅ Hata Modları sekmesi eklendi")
elif 'tabs.addTab(alloy_tab, "🧪 Alaşım Rehberi")' in content:
    marker2 = 'tabs.addTab(alloy_tab, "🧪 Alaşım Rehberi")'
    content = content.replace(marker2, marker2 + "\n" + failure_tab_code)
    print("✅ Hata Modları sekmesi eklendi (alternatif)")
else:
    print("⚠️ Uygun ekleme noktası bulunamadı, manuel ekleyin")

# _translate_failure_modes metodunu ekle
translate_method = '''
    def _translate_failure_modes(self):
        """Hata modları sekmesindeki metinleri güncelle"""
        lang = self.lang_manager.current_lang
        data = self.failure_db.get_all()
        
        self.failure_title.setText(data["title"][lang])
        
        # Giriş
        intro_html = "<ul>"
        for item in data["intro"][lang]:
            intro_html += f"<li>{item}</li>"
        intro_html += "</ul>"
        self.failure_intro.setHtml(intro_html)
        
        # Hata modu kartları
        for key, mode_data in data["modes"].items():
            icon = mode_data["icon"]
            title_text = f"{icon} {mode_data['title'][lang]}"
            content_text = "\n".join([f"• {line}" for line in mode_data["content"][lang]])
            
            title_widget = self.__getattribute__(f"failure_card_{key}_title")
            content_widget = self.__getattribute__(f"failure_card_{key}_content")
            if title_widget:
                title_widget.setText(title_text)
            if content_widget:
                content_widget.setText(content_text)
        
        # Fraktografi
        self.failure_fractography_title.setText(data["fractography"]["title"][lang])
        self.failure_fractography_content.setText(data["fractography"]["content"][lang])
        
        # Önleme
        self.failure_prevention_title.setText(data["prevention"]["title"][lang])
        prevention_text = "\n".join([f"• {item}" for item in data["prevention"]["items"][lang]])
        self.failure_prevention_list.setText(prevention_text)
'''

# _retranslate_ui metodunu güncelle - failure sekmesini de ekle
if '_retranslate_ui' in content:
    old_retranslate = 'def _retranslate_ui(self):'
    # _retranslate_ui sonuna failure çevirisini ekle
    if '_translate_failure_modes()' not in content:
        # _retranslate_ui içinde son satıra ekle
        old_end = 'self.statusBar().showMessage(self.lang_manager.tr("ready"))'
        if old_end in content:
            content = content.replace(
                old_end,
                'self._translate_failure_modes()\n        ' + old_end
            )
            print("✅ _retranslate_ui güncellendi (failure modları)")
else:
    # _retranslate_ui yoksa ekle
    print("⚠️ _retranslate_ui metodu bulunamadı")

# _translate_failure_modes metodunu ekle
if '_translate_failure_modes' not in content:
    marker_method = 'def _toggle_language(self):'
    if marker_method in content:
        content = content.replace(marker_method, translate_method + '\n    ' + marker_method)
        print("✅ _translate_failure_modes metodu eklendi")
    else:
        # def main() öncesine ekle
        marker_main = '\ndef main():'
        if marker_main in content:
            content = content.replace(marker_main, '\n' + translate_method + '\n' + marker_main)
            print("✅ _translate_failure_modes metodu eklendi (main öncesi)")

with open(main_py, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "=" * 60)
print("🎉 MALZEME HATA MODLARI BAŞARIYLA EKLENDİ!")
print("=" * 60)
print("\nYeni sekme: 🔧 Hata Modları")
print("İçerik:")
print("  - Kırılma (Gevrek/Sünek)")
print("  - Yorulma")
print("  - Sürünme")
print("  - Korozyon (SCC, korozyon yorulması)")
print("  - Darbe hatası")
print("  - Aşınma (Yapışmalı/Aşındırıcı)")
print("  - Fraktografi")
print("  - Önleme stratejileri")
print("\nÇalıştır: python main.py")