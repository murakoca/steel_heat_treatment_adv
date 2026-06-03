"""TTT / CCT Diyagram Çizimi"""
import numpy as np
import json, os

def load_ttt_data(steel_name):
    path = os.path.join(os.path.dirname(__file__), "..", "database", "ttt_data", f"{steel_name}_ttt.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def draw_ttt(ax, ttt_data):
    """TTT diyagramını çiz (basitleştirilmiş C-egrileri)"""
    if not ttt_data:
        ax.text(0.5, 0.5, "TTT verisi yok", transform=ax.transAxes, ha='center')
        return
    ps = ttt_data.get("pearlite_start")
    bs = ttt_data.get("bainite_start")
    Ms = ttt_data.get("Ms", 300)
    if ps:
        T = ps["T"]; t = ps["t"]
        ax.plot(t, T, 'b-o', lw=2, markersize=4, label='Perlit Başlangıcı')
    if bs:
        T = bs["T"]; t = bs["t"]
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
