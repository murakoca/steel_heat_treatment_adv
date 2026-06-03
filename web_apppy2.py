"""Web Tabanlı Isıl İşlem API ve Basit Arayüz"""
from flask import Flask, request, render_template_string
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models.steel_model import Material
from heat_treatment.quenching import Quenching
from simulation.engine import SimulationEngine

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html><head><title>Isil Islem Simulasyonu</title>
<meta charset='utf-8'>
<style>
body { font-family:Arial; margin:40px; background:#1e1e2e; color:#cdd6f4; }
select, input, button { padding:8px; margin:5px; border-radius:5px; border:1px solid #45475a; background:#313244; color:#cdd6f4; }
.result { margin-top:20px; padding:15px; background:#313244; border-radius:8px; }
</style></head><body>
<h2>🔥 Isil Islem Simulasyonu</h2>
<form method='POST'>
    <label>Celik:</label>
    <select name='steel'>
        {% for s in steels %}
        <option value='{{s}}'>{{s}}</option>
        {% endfor %}
    </select><br>
    <label>Medya:</label>
    <select name='media'>
        <option>Oil</option><option>Water</option><option>Polymer</option><option>Brine</option>
    </select><br>
    <label>Sicaklik (°C):</label><input type='number' name='temp' value='850'><br>
    <button type='submit'>Simule Et</button>
</form>
{% if result %}
<div class='result'>
    <h3>Sonuc</h3>
    <p>{{ result }}</p>
</div>
{% endif %}
</body></html>
"""

def get_steels():
    with open(os.path.join(os.path.dirname(__file__), 'database', 'steels.json')) as f:
        return list(json.load(f).keys())

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        steel_name = request.form['steel']
        media = request.form['media']
        temp = float(request.form['temp'])
        mat = Material.from_database(steel_name)
        q = Quenching(mat, media, "moderate", temp)
        eng = SimulationEngine(q)
        res = eng.run()
        phases_str = ", ".join([f"{p['name']}: %{p['fraction']*100:.1f}" for p in res.phases])
        result = f"{mat.name} | Sertlik: {res.hardness.surface:.0f} HRC | Fazlar: {phases_str}"
    return render_template_string(HTML_TEMPLATE, steels=get_steels(), result=result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)