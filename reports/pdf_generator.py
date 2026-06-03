"""PDF Rapor Üretici"""
from fpdf import FPDF
import os, datetime, json

def generate_pdf_report(sim_result, material, process_params, output_path="simulasyon_raporu.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Isil Islem Simulasyon Raporu", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Tarih: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.cell(0, 8, f"Malzeme: {material.name}", ln=True)
    pdf.cell(0, 8, f"Bilesim: {json.dumps(material.composition)}", ln=True)
    pdf.cell(0, 8, f"Proses: {process_params.get('process','')} / Sicaklik: {process_params.get('aust_temp','')}°C", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, "Faz Dagilimi:", ln=True)
    pdf.set_font("Arial", "", 11)
    for p in sim_result.phases:
        pdf.cell(0, 7, f"  {p.name}: %{p.fraction*100:.1f} - Sertlik: {p.hardness_hv:.0f} HV", ln=True)
    if sim_result.hardness:
        pdf.ln(3)
        pdf.cell(0, 7, f"Yuzey Sertligi: {sim_result.hardness.surface_hrc:.1f} HRC", ln=True)
        pdf.cell(0, 7, f"Merkez Sertligi: {sim_result.hardness.core_hrc:.1f} HRC", ln=True)
    pdf.output(output_path)
    return os.path.abspath(output_path)