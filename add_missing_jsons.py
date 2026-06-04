#!/usr/bin/env python3
"""
Eksik tüm JSON veritabanlarını oluşturur:
- database/alloy_effects.json
- database/failure_modes.json
- database/translations.json (zaten varsa dokunmaz)
"""
import os, json

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

def write_if_missing(path, content):
    """Dosya yoksa oluştur, varsa dokunma."""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            if isinstance(content, str):
                f.write(content)
            else:
                json.dump(content, f, indent=2, ensure_ascii=False)
        print(f"  ✅ Oluşturuldu: {path}")
    else:
        print(f"  ⏭️  Zaten var: {path}")

# ---------- 1. alloy_effects.json ----------
ALLOY_EFFECTS = {
    "title": "Alaşım Elementlerinin Çelik Üzerindeki Etkisi",
    "intro": "Alaşım elementleri, çeliğin mekanik özelliklerini, sertleşebilirliğini, tokluğunu, korozyon direncini, aşınma direncini ve diğer özelliklerini iyileştirmek için eklenir.",
    "why_alloy": [
        "Mukavemet, sertlik ve aşınma direncini artırır",
        "Sertleşebilirliği ve sertleşme derinliğini artırır",
        "Tokluğu ve sünekliği iyileştirir",
        "Korozyon ve oksidasyon direncini geliştirir",
        "Tane yapısını inceltir ve temizliği iyileştirir",
        "Belirli uygulamalar için özel özellikler sağlar"
    ],
    "classification": {
        "güçlendiriciler": {"title": "GÜÇLENDİRİCİLER", "desc": "Mukavemet, sertlik, aşınma direncini artırır", "elements": ["C","Mn","Si","Cr","Mo","V","Nb","Ti","W","B"]},
        "sertleşebilirlik": {"title": "SERTLEŞEBİLİRLİK ARTIRICILAR", "desc": "Sertleşebilirliği artırır", "elements": ["Mn","Cr","Mo","Ni","Si","B"]},
        "ostenit_stabilizorleri": {"title": "OSTENİT STABİLİZÖRLERİ", "desc": "Osteniti korur", "elements": ["Ni","Mn","C","N"]},
        "ferrit_stabilizorleri": {"title": "FERRİT STABİLİZÖRLERİ", "desc": "Ferriti teşvik eder", "elements": ["Cr","Mo","V","Nb","Ti","W","Si","Al"]}
    },
    "elements": {
        "C": {"name":"Karbon","typical_range":"0.02 – 1.2","strength_hardness":"Mukavemet, sertlik ve aşınma direncini artırır","hardenability":"Sertleşebilirliği büyük ölçüde artırır","ductility_toughness":"Sünekliği azaltır","wear_resistance":"Aşınma direncini artırır","corrosion_resistance":"Doğrudan etkisi yok","other":"En önemli element"},
        "Mn":{"name":"Mangan","typical_range":"0.20 – 1.80","strength_hardness":"Mukavemet ve sertliği artırır","hardenability":"Sertleşebilirliği güçlü şekilde artırır","ductility_toughness":"Tokluğu iyileştirir","wear_resistance":"Aşınma direncini artırır","corrosion_resistance":"Atmosferik korozyon direncini iyileştirir","other":"Deoksidan ve desülfürizör"},
        "Si":{"name":"Silisyum","typical_range":"0.15 – 0.60","strength_hardness":"Mukavemet ve elastikiyet limitini artırır","hardenability":"Sertleşebilirliği hafif artırır","ductility_toughness":"Sünekliği hafif azaltır","wear_resistance":"Aşınma direncini iyileştirir","corrosion_resistance":"Oksidasyon ve tavlanma direncini artırır","other":"Güçlü deoksidan"},
        "Cr":{"name":"Krom","typical_range":"0.50 – 1.50 (Paslanmaz çeliklerde %12'ye kadar)","strength_hardness":"Mukavemet, sertlik ve sıcak mukavemeti artırır","hardenability":"Sertleşebilirliği artırır","ductility_toughness":"Sünekliği hafif azaltır","wear_resistance":"Aşınma direncini büyük ölçüde artırır","corrosion_resistance":"Korozyon direncini büyük ölçüde iyileştirir","other":"Paslanmaz çeliklerde esas"},
        "Ni":{"name":"Nikel","typical_range":"0.50 – 5.00","strength_hardness":"Mukavemeti artırır (orta derecede)","hardenability":"Sertleşebilirliği artırır (orta derecede)","ductility_toughness":"Tokluk ve sünekliği büyük ölçüde iyileştirir","wear_resistance":"Aşınma direncini hafif iyileştirir","corrosion_resistance":"Mükemmel korozyon direnci","other":"Ostenit stabilizörü"},
        "Mo":{"name":"Molibden","typical_range":"0.20 – 1.00","strength_hardness":"Özellikle yüksek sıcaklıkta mukavemeti artırır","hardenability":"Sertleşebilirliği güçlü şekilde artırır","ductility_toughness":"Süneklik üzerinde az etkisi vardır","wear_resistance":"Yüksek sıcaklıkta aşınma direncini iyileştirir","corrosion_resistance":"Çukurlaşma ve yarık korozyonuna direnci iyileştirir","other":"Temper gevrekleşmesini önler"},
        "V":{"name":"Vanadyum","typical_range":"0.05 – 0.30","strength_hardness":"Mukavemet ve aşınma direncini büyük ölçüde artırır","hardenability":"Sertleşebilirliği artırır","ductility_toughness":"Sünekliği büyük ölçüde azaltır","wear_resistance":"Aşınma direncini büyük ölçüde artırır","corrosion_resistance":"Doğrudan etkisi yok","other":"İnce karbürler (VC) oluşturur"},
        "W":{"name":"Tungsten (Volfram)","typical_range":"0.50 – 2.00","strength_hardness":"Mukavemet ve sıcak mukavemeti artırır","hardenability":"Sertleşebilirliği artırır","ductility_toughness":"Sünekliği büyük ölçüde azaltır","wear_resistance":"Aşınma direncini büyük ölçüde artırır","corrosion_resistance":"Doğrudan etkisi yok","other":"Kırmızı sıcak sertliği"},
        "Nb":{"name":"Niyobyum","typical_range":"0.02 – 0.20","strength_hardness":"Mukavemeti artırır","hardenability":"Az etkisi vardır","ductility_toughness":"Tokluğu iyileştirir","wear_resistance":"Aşınma direncini artırır","corrosion_resistance":"Doğrudan etkisi yok","other":"Tane inceltici"},
        "B":{"name":"Bor","typical_range":"0.0005 – 0.0050","strength_hardness":"Hafif artış","hardenability":"Sertleşebilirliği büyük ölçüde artırır","ductility_toughness":"Önemli etkisi yok","wear_resistance":"Önemli etkisi yok","corrosion_resistance":"Doğrudan etkisi yok","other":"Sıkı kontrol edilmeli"},
        "Ti":{"name":"Titanyum","typical_range":"0.01 – 0.05","strength_hardness":"Tane inceltme ile mukavemeti artırır","hardenability":"Az etkisi vardır","ductility_toughness":"Tokluğu iyileştirir","wear_resistance":"Hafif iyileştirme","corrosion_resistance":"Tane sınırı korozyonuna direnci iyileştirir","other":"TiC, TiN oluşturur"},
        "Al":{"name":"Alüminyum","typical_range":"0.02 – 0.10","strength_hardness":"Hafif artış","hardenability":"Az etkisi vardır","ductility_toughness":"Önemli etkisi yok","wear_resistance":"Önemli etkisi yok","corrosion_resistance":"Önemli etkisi yok","other":"Güçlü deoksidan"},
        "Cu":{"name":"Bakır","typical_range":"0.20 – 1.00","strength_hardness":"Hafif artış","hardenability":"Az etkisi vardır","ductility_toughness":"Tokluğu iyileştirir","wear_resistance":"Hafif iyileştirme","corrosion_resistance":"Atmosferik korozyon direncini iyileştirir","other":"Hava koşullarına dayanıklı çeliklerde"},
        "S":{"name":"Kükürt","typical_range":"< 0.05 (düşük tutulmalı)","strength_hardness":"Süneklik ve tokluğu azaltır","hardenability":"Etkisi yok","ductility_toughness":"Tokluğu büyük ölçüde azaltır","wear_resistance":"Aşınma direncini azaltır","corrosion_resistance":"Sıcak kısalığa ve korozyona neden olabilir","other":"MnS kalıntıları (zararlı)"},
        "P":{"name":"Fosfor","typical_range":"< 0.04 (düşük tutulmalı)","strength_hardness":"Mukavemeti hafif artırır","hardenability":"Etkisi yok","ductility_toughness":"Tokluğu büyük ölçüde azaltır","wear_resistance":"Aşınma direncini azaltır","corrosion_resistance":"Soğuk kısalığa ve korozyona neden olur","other":"Zararlı safsızlık"}
    },
    "trends": {
        "Mukavemet / Sertlik": {"up": ["C","Mn","Si","Cr","Mo","V","W","Nb","Ti"], "arrow": "↑"},
        "Süneklik / Tokluk": {"up_inc": ["Mn","Ni"], "up_dec": ["C","Si","Cr","Mo","V","W"], "arrow_inc": "↑", "arrow_dec": "↓"},
        "Sertleşebilirlik": {"up": ["C","Mn","Cr","Mo","Ni","Si","B"], "arrow": "↑"},
        "Aşınma Direnci": {"up": ["C","Cr","Mo","V","W"], "arrow": "↑"},
        "Korozyon Direnci": {"up": ["Cr","Ni","Si","Cu"], "arrow": "↑"},
        "Yüksek Sıcaklık Mukavemeti": {"up": ["Mo","W","Cr","V"], "arrow": "↑"}
    },
    "examples": [
        {"name": "Cr-Mo çelikleri (örn. 1,25Cr-0,5Mo)", "desc": "Yüksek mukavemet ve sertlik, enerji santrallerinde kullanılır."},
        {"name": "Ni-Cr çelikleri (örn. 2Ni-1Cr-0,5Mo)", "desc": "Yüksek tokluk ve mukavemet, yapısal bileşenlerde kullanılır."},
        {"name": "Takım çelikleri (örn. D2, AISI 52100)", "desc": "Yüksek sertlik, aşınma direnci, ısı direnci."},
        {"name": "Paslanmaz çelikler (örn. 18Cr-8Ni)", "desc": "Mükemmel direnç ve görünüm."}
    ],
    "notes": [
        "Bir elementin etkisi, miktarına, mevcut diğer elementlere, ısıl işleme ve işleme yöntemine bağlıdır.",
        "Aşırı ilave zararlı olabilir.",
        "İstenen özellikleri elde etmek için elementlerin uygun kombinasyonu ve kontrolü gereklidir.",
        "İyi tokluk ve süneklik için temiz çelik (düşük S ve P) esastır."
    ]
}

write_if_missing("database/alloy_effects.json", ALLOY_EFFECTS)

# ---------- 2. failure_modes.json ----------
FAILURE_MODES = {
    "title": {"tr": "Malzeme Hata Modlarına Giriş", "en": "Introduction to Material Failure Modes"},
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

write_if_missing("database/failure_modes.json", FAILURE_MODES)

# ---------- 3. translations.json (varsa dokunma) ----------
TRANSLATIONS = {
    "window_title": {"tr": "Isıl İşlem Simülasyon Platformu", "en": "Heat Treatment Simulation Platform"},
    "simulation_tab": {"tr": "🔥 Simülasyon", "en": "🔥 Simulation"},
    "guide_tab": {"tr": "📚 Rehber", "en": "📚 Guide"},
    "periodic_tab": {"tr": "🧪 Elementler", "en": "🧪 Elements"},
    "lever_tab": {"tr": "⚖️ Lever Kuralı", "en": "⚖️ Lever Rule"},
    "fec_tab": {"tr": "🔬 Fe–C Diyagramı", "en": "🔬 Fe–C Diagram"},
    "ree_tab": {"tr": "🧪 REE", "en": "🧪 REE"},
    "procurement_tab": {"tr": "📊 Satın Alma", "en": "📊 Procurement"},
    "pdf_tab": {"tr": "📄 PDF Rapor", "en": "📄 PDF Report"},
    "ttt_tab": {"tr": "📈 TTT/CCT", "en": "📈 TTT/CCT"},
    "distortion_tab": {"tr": "🔧 Distorsiyon", "en": "🔧 Distortion"},
    "diffusion_tab": {"tr": "🧪 Karbon Difüzyonu", "en": "🧪 Carbon Diffusion"},
    "alloy_tab": {"tr": "🧪 Alaşım Rehberi", "en": "🧪 Alloy Guide"},
    "failure_modes_tab": {"tr": "🔧 Hata Modları", "en": "🔧 Failure Modes"},
    "process_group": {"tr": "Proses Tanımı", "en": "Process Definition"},
    "steel_label": {"tr": "Çelik:", "en": "Steel:"},
    "process_label": {"tr": "Proses:", "en": "Process:"},
    "params_label": {"tr": "Parametreler:", "en": "Parameters:"},
    "quenching": {"tr": "Su Verme", "en": "Quenching"},
    "tempering": {"tr": "Temperleme", "en": "Tempering"},
    "carburizing": {"tr": "Sementasyon", "en": "Carburizing"},
    "aust_temp": {"tr": "Östenitleme Sıc. (°C):", "en": "Aust. Temp (°C):"},
    "media": {"tr": "Ortam:", "en": "Media:"},
    "agitation": {"tr": "Ajitasyon:", "en": "Agitation:"},
    "run_btn": {"tr": "▶ Simülasyonu Çalıştır", "en": "▶ Run Simulation"},
    "ready": {"tr": "Hazır", "en": "Ready"},
    "cooling_tab": {"tr": "Soğuma", "en": "Cooling"},
    "hardness_tab": {"tr": "Sertlik", "en": "Hardness"},
    "micro_tab": {"tr": "Mikroyapı", "en": "Microstructure"},
    "log_tab": {"tr": "Log", "en": "Log"}
}
write_if_missing("database/translations.json", TRANSLATIONS)

print("\n🎉 Tüm eksik JSON dosyaları oluşturuldu!")
print("Şimdi uygulamayı başlatabilirsiniz: python main.py")