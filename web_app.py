"""Web Tabanlı Isıl İşlem Simülasyon Platformu – Tüm Özellikler"""
from flask import Flask, request, render_template_string, send_file, jsonify
import json, os, sys, io, base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.steel_model import Material
from heat_treatment.quenching import Quenching
from heat_treatment.tempering import Tempering
from heat_treatment.carburizing import Carburizing
from simulation.engine import SimulationEngine
from metallurgy.lever_rule import calculate as lever_calculate, FE_C_EXAMPLES
from metallurgy.ree import REEDatabase
from metallurgy.interactive_fec import FeCDiagram
from metallurgy.ttt_cct_plot import load_ttt_data, draw_ttt
from metallurgy.alloy_guide import AlloyGuide
from metallurgy.failure_modes import FailureModes
from procurement.calculator import SupplierCost, compare_suppliers
from reports.pdf_generator import generate_pdf_report
from periodic.table import PeriodicTable

app = Flask(__name__)
pt = PeriodicTable()
fec_engine = FeCDiagram()
ree_db = REEDatabase()
alloy_guide = AlloyGuide()
failure_db = FailureModes()

def get_steels():
    with open(os.path.join(os.path.dirname(__file__), 'database', 'steels.json')) as f:
        return list(json.load(f).keys())

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', facecolor='#1e1e2e', edgecolor='none')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

# ── Ana Şablon ──
BASE_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Steel Heat Treatment Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1e1e2e; color: #cdd6f4; }
        .navbar { background: #313244; padding: 12px 20px; display: flex; gap: 8px; flex-wrap: wrap; border-bottom: 2px solid #45475a; }
        .navbar a { color: #a6adc8; text-decoration: none; padding: 6px 14px; border-radius: 6px; font-size: 14px; font-weight: bold; }
        .navbar a:hover { background: #45475a; color: #89b4fa; }
        .navbar a.active { background: #89b4fa; color: #1e1e2e; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        h2 { color: #89b4fa; margin-bottom: 15px; }
        .card { background: #313244; border-radius: 10px; padding: 20px; margin-bottom: 20px; border: 1px solid #45475a; }
        select, input, button { padding: 8px 12px; margin: 4px; border-radius: 6px; border: 1px solid #45475a; background: #313244; color: #cdd6f4; }
        button { background: #89b4fa; color: #1e1e2e; font-weight: bold; cursor: pointer; border: none; }
        button:hover { background: #74c7ec; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { padding: 8px 12px; border: 1px solid #45475a; text-align: left; }
        th { background: #45475a; color: #cdd6f4; }
        .phase-bar { height: 20px; border-radius: 10px; background: #45475a; overflow: hidden; }
        .phase-fill { height: 100%; border-radius: 10px; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
        @media (max-width: 800px) { .grid-2, .grid-3 { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="navbar">
        <a href="/" class="{{ 'active' if active == 'sim' else '' }}">🔥 Simülasyon</a>
        <a href="/periodic" class="{{ 'active' if active == 'periodic' else '' }}">🧪 Periyodik</a>
        <a href="/fec" class="{{ 'active' if active == 'fec' else '' }}">🔬 Fe-C</a>
        <a href="/lever" class="{{ 'active' if active == 'lever' else '' }}">⚖️ Lever</a>
        <a href="/ttt" class="{{ 'active' if active == 'ttt' else '' }}">📈 TTT/CCT</a>
        <a href="/alloy" class="{{ 'active' if active == 'alloy' else '' }}">🧪 Alaşım</a>
        <a href="/failure" class="{{ 'active' if active == 'failure' else '' }}">🔧 Hata</a>
        <a href="/procurement" class="{{ 'active' if active == 'proc' else '' }}">📊 Satın Alma</a>
        <a href="/ree" class="{{ 'active' if active == 'ree' else '' }}">🧪 REE</a>
        <a href="/pdf" class="{{ 'active' if active == 'pdf' else '' }}">📄 PDF</a>
    </div>
    <div class="container">
        {{ content | safe }}
    </div>
</body>
</html>
"""

# ── Ana Sayfa (Simülasyon) ──
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
        phases = "".join(
            f"<tr><td>{p.name}</td><td>%{p.fraction*100:.1f}</td><td>{p.hardness_hv:.0f} HV</td></tr>"
            for p in res.phases
        )
        result = f"""
        <div class="card">
            <h3>Sonuç: {mat.name}</h3>
            <p>Yüzey Sertliği: <b>{res.hardness.surface_hrc:.1f} HRC</b> | Merkez: <b>{res.hardness.core_hrc:.1f} HRC</b></p>
            <table><tr><th>Faz</th><th>Oran</th><th>Sertlik</th></tr>{phases}</table>
        </div>"""
    content = f"""
    <h2>🔥 Isıl İşlem Simülasyonu</h2>
    <div class="card">
        <form method="POST">
            <label>Çelik:</label>
            <select name="steel">{''.join(f'<option value="{s}">{s}</option>' for s in get_steels())}</select><br>
            <label>Medya:</label>
            <select name="media"><option>Oil</option><option>Water</option><option>Polymer</option><option>Brine</option></select><br>
            <label>Sıcaklık (°C):</label><input type="number" name="temp" value="850"><br>
            <button type="submit">Simüle Et</button>
        </form>
        {result or ''}
    </div>"""
    return render_template_string(BASE_HTML, active='sim', content=content)

# ── Periyodik Tablo ──
@app.route('/periodic')
def periodic():
    elements_html = ""
    for num in range(1, 119):
        el = pt.get(num)
        if el:
            color = pt.get_color(num)
            elements_html += f"""
            <div class="element-card" style="background:{color}; color:#1e1e2e; padding:8px; border-radius:6px; text-align:center; cursor:pointer;"
                 onclick="alert('{el['name']} ({el['sym']})\\nAtom No: {num}\\nKütle: {el['mass']} u\\n{el.get('elec','')}')">
                <b>{el['sym']}</b><br><small>{num}</small>
            </div>"""
    content = f"""
    <h2>🧪 Periyodik Tablo</h2>
    <div class="card" style="display:grid; grid-template-columns: repeat(18, 1fr); gap:4px; max-width:1000px;">
        {elements_html}
    </div>"""
    return render_template_string(BASE_HTML, active='periodic', content=content)

# ── Fe-C Diyagramı ──
@app.route('/fec')
def fec():
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_facecolor('#1e1e2e')
    ax.tick_params(colors='#cdd6f4')
    for spine in ax.spines.values(): spine.set_color('#45475a')
    fec_engine.draw(ax, {"C": 0.77}, highlight_point=(0.77, 727))
    img = fig_to_base64(fig)
    plt.close(fig)
    content = f"""
    <h2>🔬 Fe-C Faz Diyagramı</h2>
    <div class="card"><img src="data:image/png;base64,{img}" style="width:100%; max-width:900px;"></div>"""
    return render_template_string(BASE_HTML, active='fec', content=content)

# ── Lever Rule ──
@app.route('/lever', methods=['GET', 'POST'])
def lever():
    result = ""
    if request.method == 'POST':
        Ca = float(request.form['Ca'])
        Cb = float(request.form['Cb'])
        Co = float(request.form['Co'])
        try:
            res = lever_calculate(Ca, Cb, Co)
            result = f"""
            <div class="card">
                <p>α fazı: <b>%{res.percent_alpha:.1f}</b></p>
                <p>β fazı: <b>%{res.percent_beta:.1f}</b></p>
                <p>fα = (Cβ - Co) / (Cβ - Cα) = ({Cb} - {Co}) / ({Cb} - {Ca}) = <b>{res.fraction_alpha:.4f}</b></p>
                <p>fβ = (Co - Cα) / (Cβ - Cα) = ({Co} - {Ca}) / ({Cb} - {Ca}) = <b>{res.fraction_beta:.4f}</b></p>
            </div>"""
        except Exception as e:
            result = f"<p style='color:#f38ba8;'>Hata: {e}</p>"
    content = f"""
    <h2>⚖️ Lever Rule (Kaldıraç Kuralı)</h2>
    <div class="card">
        <form method="POST">
            <label>Cα (α fazı %):</label><input type="number" step="any" name="Ca" value="0.022"><br>
            <label>Cβ (β fazı %):</label><input type="number" step="any" name="Cb" value="6.67"><br>
            <label>Co (Genel %):</label><input type="number" step="any" name="Co" value="0.8"><br>
            <button type="submit">Hesapla</button>
        </form>
        {result}
    </div>"""
    return render_template_string(BASE_HTML, active='lever', content=content)

# ── TTT/CCT ──
@app.route('/ttt', methods=['GET', 'POST'])
def ttt():
    steel = request.form.get('steel', 'AISI_4140')
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_facecolor('#1e1e2e')
    ax.tick_params(colors='#cdd6f4')
    for spine in ax.spines.values(): spine.set_color('#45475a')
    ax.xaxis.label.set_color('#cdd6f4'); ax.yaxis.label.set_color('#cdd6f4')
    ax.title.set_color('#cdd6f4')
    ttt_data = load_ttt_data(steel)
    draw_ttt(ax, ttt_data)
    img = fig_to_base64(fig)
    plt.close(fig)
    content = f"""
    <h2>📈 TTT/CCT Diyagramı</h2>
    <div class="card">
        <form method="POST">
            <label>Çelik:</label>
            <select name="steel" onchange="this.form.submit()">
                {''.join(f'<option value="{s}" {"selected" if s==steel else ""}>{s}</option>' for s in get_steels())}
            </select>
        </form>
        <img src="data:image/png;base64,{img}" style="width:100%; max-width:800px; margin-top:15px;">
    </div>"""
    return render_template_string(BASE_HTML, active='ttt', content=content)

# ── Alaşım Rehberi ──
@app.route('/alloy')
def alloy():
    data = alloy_guide.get_all()
    elements_html = ""
    for sym, el in data['elements'].items():
        elements_html += f"""
        <tr>
            <td><b>{el['name']} ({sym})</b></td>
            <td>{el['typical_range']}</td>
            <td>{el['strength_hardness']}</td>
            <td>{el['hardenability']}</td>
            <td>{el['ductility_toughness']}</td>
            <td>{el['wear_resistance']}</td>
            <td>{el['corrosion_resistance']}</td>
        </tr>"""
    content = f"""
    <h2>🧪 Alaşım Elementlerinin Çelik Üzerindeki Etkisi</h2>
    <div class="card">
        <p>{data['intro']}</p>
        <h3>Neden Alaşım Çeliği?</h3>
        <ul>{''.join(f'<li>{item}</li>' for item in data['why_alloy'])}</ul>
        <h3>Element Etkileri</h3>
        <div style="overflow-x:auto;">
        <table>
            <tr><th>Element</th><th>Tipik %</th><th>Mukavemet</th><th>Sertleşebilirlik</th><th>Tokluk</th><th>Aşınma</th><th>Korozyon</th></tr>
            {elements_html}
        </table></div>
    </div>"""
    return render_template_string(BASE_HTML, active='alloy', content=content)

# ── Hata Modları ──
@app.route('/failure')
def failure():
    data = failure_db.get_all()
    modes_html = ""
    for key, mode in data['modes'].items():
        modes_html += f"""
        <div class="card">
            <h3>{mode['icon']} {mode['title']['tr']}</h3>
            <ul>{''.join(f'<li>{line}</li>' for line in mode['content']['tr'])}</ul>
        </div>"""
    content = f"""
    <h2>🔧 Malzeme Hata Modları</h2>
    <p>{data['intro']['tr'][0]}</p>
    <div class="grid-2">{modes_html}</div>
    <div class="card">
        <h3>{data['fractography']['title']['tr']}</h3>
        <p>{data['fractography']['content']['tr']}</p>
        <h3>{data['prevention']['title']['tr']}</h3>
        <ul>{''.join(f'<li>{item}</li>' for item in data['prevention']['items']['tr'])}</ul>
    </div>"""
    return render_template_string(BASE_HTML, active='failure', content=content)

# ── Satın Alma Rehberi ──
@app.route('/procurement', methods=['GET', 'POST'])
def procurement():
    result = ""
    if request.method == 'POST':
        a = SupplierCost("A", float(request.form['a_price']), float(request.form['a_rework']),
                         float(request.form['a_delay']), float(request.form['a_quality']))
        b = SupplierCost("B", float(request.form['b_price']), float(request.form['b_rework']),
                         float(request.form['b_delay']), float(request.form['b_quality']))
        winner, diff = compare_suppliers(a, b)
        result = f"""
        <div class="card">
            <p>Tedarikçi A Toplam: <b>{a.total:,.0f} TL</b></p>
            <p>Tedarikçi B Toplam: <b>{b.total:,.0f} TL</b></p>
            <p style="font-size:18px; color:#89b4fa;">✅ {winner.name} {diff:,.0f} TL daha ekonomik!</p>
        </div>"""
    content = f"""
    <h2>📊 Satın Alma Rehberi – TCO Hesaplayıcı</h2>
    <div class="grid-2">
        <div class="card">
            <h3>Tedarikçi A</h3>
            <form method="POST">
                <label>Satın Alma Fiyatı (TL):</label><input type="number" name="a_price" value="100000"><br>
                <label>Yeniden İşleme (TL):</label><input type="number" name="a_rework" value="20000"><br>
                <label>Gecikme (TL):</label><input type="number" name="a_delay" value="15000"><br>
                <label>Kalite Kaybı (TL):</label><input type="number" name="a_quality" value="10000"><br>
                <hr>
                <h3>Tedarikçi B</h3>
                <label>Satın Alma Fiyatı (TL):</label><input type="number" name="b_price" value="110000"><br>
                <label>Yeniden İşleme (TL):</label><input type="number" name="b_rework" value="5000"><br>
                <label>Gecikme (TL):</label><input type="number" name="b_delay" value="0"><br>
                <label>Kalite Kaybı (TL):</label><input type="number" name="b_quality" value="0"><br>
                <button type="submit">Hesapla</button>
            </form>
        </div>
        {result}
    </div>"""
    return render_template_string(BASE_HTML, active='proc', content=content)

# ── REE ──
@app.route('/ree')
def ree():
    data = ree_db.get_all()
    apps_html = ""
    for app_name, app_info in data['applications'].items():
        apps_html += f"""
        <div class="card">
            <h3>📌 {app_name}</h3>
            <p><b>Elementler:</b> {', '.join(app_info['elements'])}</p>
            <p>{app_info['desc']}</p>
        </div>"""
    content = f"""
    <h2>🧪 Nadir Toprak Elementleri (REE)</h2>
    <p>{data['description']}</p>
    <p><b>17 element:</b> {', '.join(data['elements'])}</p>
    <h3>Uygulamalar</h3>
    <div class="grid-2">{apps_html}</div>"""
    return render_template_string(BASE_HTML, active='ree', content=content)

# ── PDF Rapor ──
@app.route('/pdf', methods=['GET', 'POST'])
def pdf():
    msg = ""
    if request.method == 'POST':
        steel_name = request.form['steel']
        media = request.form['media']
        temp = float(request.form['temp'])
        mat = Material.from_database(steel_name)
        q = Quenching(mat, media, "moderate", temp)
        eng = SimulationEngine(q)
        res = eng.run()
        path = generate_pdf_report(res, mat, {"process": "Quenching", "aust_temp": temp})
        return send_file(path, as_attachment=True)
    content = f"""
    <h2>📄 PDF Rapor Oluştur</h2>
    <div class="card">
        <form method="POST">
            <label>Çelik:</label>
            <select name="steel">{''.join(f'<option value="{s}">{s}</option>' for s in get_steels())}</select><br>
            <label>Medya:</label>
            <select name="media"><option>Oil</option><option>Water</option><option>Polymer</option><option>Brine</option></select><br>
            <label>Sıcaklık (°C):</label><input type="number" name="temp" value="850"><br>
            <button type="submit">PDF İndir</button>
        </form>
        {msg}
    </div>"""
    return render_template_string(BASE_HTML, active='pdf', content=content)

if __name__ == '__main__':
    app.run(debug=True, port=5000)