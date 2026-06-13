import numpy as np
import json, os

def load_ttt_data(steel_name):
    path = os.path.join(os.path.dirname(__file__), "..", "database", "ttt_data", f"{steel_name}_ttt.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def draw_ttt(ax, ttt_data):
    if not ttt_data:
        ax.text(0.5, 0.5, "TTT verisi yok", transform=ax.transAxes, ha='center')
        return
    ps = ttt_data.get("pearlite_start")
    bs = ttt_data.get("bainite_start")
    Ms = ttt_data.get("Ms", 300)
    if ps:
        T, t = ps["T"], ps["t"]
        ax.plot(t, T, 'b-o', lw=2, markersize=4, label='Perlit Başlangıcı')
    if bs:
        T, t = bs["T"], bs["t"]
        ax.plot(t, T, 'r-s', lw=2, markersize=4, label='Beynit Başlangıcı')
    ax.axhline(Ms, color='orange', ls='--', lw=1.5, label=f'Ms = {Ms}°C')
    ax.set_xscale('log')
    ax.set_xlabel('Zaman (s)')
    ax.set_ylabel('Sıcaklık (°C)')
    ax.set_title('TTT Diyagramı')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(1, 1e4)
    ax.set_ylim(0, 900)

def calculate_ttt(composition, grain_size=10):
    C = composition.get('C', 0) * 100
    Mn = composition.get('Mn', 0) * 100
    Cr = composition.get('Cr', 0) * 100
    Ni = composition.get('Ni', 0) * 100
    Mo = composition.get('Mo', 0) * 100
    T_pearlite = np.linspace(550, 700, 10)
    tau_pearlite = np.exp(2 + 0.5*C + 0.3*Mn + 0.4*Cr) / (grain_size**0.5)
    T_bainite = np.linspace(300, 550, 10)
    tau_bainite = np.exp(3 + 0.8*C + 0.5*Mn + 0.6*Cr + 1.0*Mo) / (grain_size**0.5)
    Ms = 539 - 423*C - 30.4*Mn - 17.7*Ni - 12.1*Cr - 7.5*Mo
    return {'pearlite': {'T': T_pearlite.tolist(), 't': tau_pearlite.tolist()},
            'bainite': {'T': T_bainite.tolist(), 't': tau_bainite.tolist()}, 'Ms': Ms}

def cct_from_ttt(ttt_data, cooling_rates):
    cct = {'pearlite_start': [], 'bainite_start': [], 'martensite_start': []}
    Ms = ttt_data['Ms']
    for rate in cooling_rates:
        T_pearl = np.interp(rate, [0.1, 100], [700, 500])
        T_bain = np.interp(rate, [0.1, 100], [550, 300])
        cct['pearlite_start'].append({'rate': rate, 'T': T_pearl})
        cct['bainite_start'].append({'rate': rate, 'T': T_bain})
        cct['martensite_start'].append({'rate': rate, 'T': Ms})
    return cct

def hardness_from_cct(cooling_rate, composition):
    C = composition.get('C', 0) * 100
    hardness = 200 + 300 * C + 5 * np.log10(cooling_rate + 1)
    return min(hardness, 700)
