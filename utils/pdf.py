from fpdf import FPDF
import json
import base64

class VehiculePDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Fiche Véhicule', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generer_pdf_vehicule(vehicule):
    """Génère un PDF avec les informations détaillées du véhicule."""
    pdf = VehiculePDF()
    pdf.add_page()
    
    # En-tête avec les informations principales
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f"{vehicule['Marque']} {vehicule['Modele']} ({vehicule['Annee']})", 0, 1)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Prix: {vehicule['Prix']:,.0f} €", 0, 1)
    
    # Caractéristiques techniques
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "Caractéristiques", 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Consommation: {vehicule['Consommation']} L/100km", 0, 1)
    pdf.cell(0, 10, f"Fiabilité: {vehicule['Fiabilite']}/10", 0, 1)
    pdf.cell(0, 10, f"Coût assurance: {vehicule['Cout_Assurance']} €/an", 0, 1)
    
    # Points forts et points faibles
    if 'Points_Forts' in vehicule and vehicule['Points_Forts']:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, "Points forts", 0, 1)
        pdf.set_font('Arial', '', 12)
        for point in vehicule['Points_Forts'].split('\n'):
            if point.strip():
                pdf.cell(0, 10, f"✓ {point.strip()}", 0, 1)
    
    if 'Points_Faibles' in vehicule and vehicule['Points_Faibles']:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, "Points faibles", 0, 1)
        pdf.set_font('Arial', '', 12)
        for point in vehicule['Points_Faibles'].split('\n'):
            if point.strip():
                pdf.cell(0, 10, f"✗ {point.strip()}", 0, 1)
    
    # Notes détaillées
    if 'Notes_Detaillees' in vehicule and vehicule['Notes_Detaillees']:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, "Évaluation détaillée", 0, 1)
        pdf.set_font('Arial', '', 12)
        notes = json.loads(vehicule['Notes_Detaillees'])
        for critere, note in notes.items():
            pdf.cell(0, 10, f"{critere}: {note}/5", 0, 1)
    
    # Red flags
    if 'Red_Flags' in vehicule and vehicule['Red_Flags']:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, "Points d'attention", 0, 1)
        pdf.set_font('Arial', '', 12)
        for flag in vehicule['Red_Flags'].split(','):
            if flag.strip():
                pdf.cell(0, 10, f"• {flag.strip()}", 0, 1)
    
    # Tags
    if 'Tags' in vehicule and vehicule['Tags']:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, "Tags", 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, vehicule['Tags'], 0, 1)
    
    return pdf.output(dest='S').encode('latin1')

def get_download_link(pdf_bytes, filename):
    """Crée un lien de téléchargement pour le PDF."""
    b64 = base64.b64encode(pdf_bytes).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Télécharger le PDF</a>' 