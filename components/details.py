import streamlit as st
import json
import base64
from fpdf import FPDF
from utils.data import sauvegarder_donnees

class VehiculePDF(FPDF):
    """Classe personnalisée pour générer un PDF de fiche véhicule."""
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Fiche Véhicule', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generer_pdf_vehicule(vehicule):
    """
    Génère un PDF contenant les informations détaillées d'un véhicule.
    """
    pdf = VehiculePDF()
    pdf.add_page()
    
    # En-tête avec les informations principales
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f"{vehicule['Marque']} {vehicule['Modele']} ({vehicule['Annee']})", 0, 1)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Prix: {vehicule['Prix']:,.0f} €", 0, 1)
    
    # Score de correspondance
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f"Score de correspondance: {vehicule['Score_Match']:.1f}%", 0, 1)
    
    # Caractéristiques techniques
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "Caractéristiques", 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Consommation: {vehicule['Consommation']} L/100km", 0, 1)
    pdf.cell(0, 10, f"Fiabilité: {vehicule['Fiabilite']}/10", 0, 1)
    pdf.cell(0, 10, f"Coût assurance: {vehicule['Cout_Assurance']} €/an", 0, 1)
    
    # Équipements
    if vehicule['Equipements']:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, "Équipements", 0, 1)
        pdf.set_font('Arial', '', 12)
        for equip in vehicule['Equipements'].split(','):
            if equip.strip():
                pdf.cell(0, 10, f"• {equip.strip()}", 0, 1)
    
    # Points forts et points faibles
    if vehicule.get('Points_Forts'):
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, "Points forts", 0, 1)
        pdf.set_font('Arial', '', 12)
        for point in vehicule['Points_Forts'].split('\n'):
            if point.strip():
                pdf.cell(0, 10, f"✓ {point.strip()}", 0, 1)
    
    if vehicule.get('Points_Faibles'):
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, "Points faibles", 0, 1)
        pdf.set_font('Arial', '', 12)
        for point in vehicule['Points_Faibles'].split('\n'):
            if point.strip():
                pdf.cell(0, 10, f"✗ {point.strip()}", 0, 1)
    
    # Notes détaillées
    if vehicule.get('Notes_Detaillees'):
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, "Évaluation détaillée", 0, 1)
        pdf.set_font('Arial', '', 12)
        notes = json.loads(vehicule['Notes_Detaillees'])
        for critere, note in notes.items():
            pdf.cell(0, 10, f"{critere}: {note}/5", 0, 1)
    
    # Red flags
    if vehicule.get('Red_Flags'):
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, "Points d'attention", 0, 1)
        pdf.set_font('Arial', '', 12)
        for flag in vehicule['Red_Flags'].split(','):
            if flag.strip():
                pdf.cell(0, 10, f"• {flag.strip()}", 0, 1)
    
    # Tags
    if vehicule.get('Tags'):
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, "Tags", 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, vehicule['Tags'], 0, 1)
    
    return pdf.output(dest='S').encode('latin1')

def get_download_link(pdf_bytes, filename):
    """
    Crée un lien de téléchargement pour un fichier PDF.
    """
    b64 = base64.b64encode(pdf_bytes).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Télécharger le PDF</a>'

def afficher_details_vehicule(vehicule, idx, df):
    """
    Affiche la page de détails d'un véhicule.
    """
    st.title(f"{vehicule['Marque']} {vehicule['Modele']}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if vehicule['Image_URL']:
            st.image(vehicule['Image_URL'], use_column_width=True)
        
        # Points forts et points faibles
        st.subheader("💪 Points forts et points faibles")
        col_plus, col_moins = st.columns(2)
        
        with col_plus:
            st.markdown("#### ✅ Points forts")
            points_forts = st.text_area(
                "Listez les points forts (un par ligne)",
                value=vehicule['Points_Forts'] if 'Points_Forts' in vehicule else "",
                help="Ex: Faible kilométrage, Carnet d'entretien complet...",
                height=150
            )
            if points_forts != vehicule.get('Points_Forts', ""):
                df.at[idx, 'Points_Forts'] = points_forts
                sauvegarder_donnees(df)
        
        with col_moins:
            st.markdown("#### ❌ Points faibles")
            points_faibles = st.text_area(
                "Listez les points faibles (un par ligne)",
                value=vehicule['Points_Faibles'] if 'Points_Faibles' in vehicule else "",
                help="Ex: Consommation élevée, Entretien coûteux...",
                height=150
            )
            if points_faibles != vehicule.get('Points_Faibles', ""):
                df.at[idx, 'Points_Faibles'] = points_faibles
                sauvegarder_donnees(df)
        
        st.markdown("---")
        
        # Système de notation avancé
        st.subheader("📊 Évaluation détaillée")
        criteres = {
            "État général": "État extérieur et intérieur du véhicule",
            "Prix": "Rapport qualité/prix",
            "Négociation": "Marge de négociation possible",
            "Documentation": "Disponibilité et qualité des documents",
            "Entretien": "Historique et suivi d'entretien"
        }
        
        notes = {}
        if 'Notes_Detaillees' in vehicule and vehicule['Notes_Detaillees']:
            notes = json.loads(vehicule['Notes_Detaillees'])
        
        notes_modifiees = False
        for critere, description in criteres.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{critere}**")
                st.caption(description)
            with col2:
                note = st.select_slider(
                    f"Note {critere}",
                    options=[1, 2, 3, 4, 5],
                    value=notes.get(critere, 3),
                    key=f"note_{critere}",
                    label_visibility="collapsed"
                )
                if critere not in notes or notes[critere] != note:
                    notes[critere] = note
                    notes_modifiees = True
        
        if notes_modifiees:
            df.at[idx, 'Notes_Detaillees'] = json.dumps(notes)
            sauvegarder_donnees(df)
    
    with col2:
        st.markdown(f"""
        ### Informations
        - **Année** : {vehicule['Annee']}
        - **Prix** : {vehicule['Prix']:,.0f} €
        - **Consommation** : {vehicule['Consommation']} L/100km
        - **Coût assurance** : {vehicule['Cout_Assurance']} €/an
        - **Fiabilité** : {vehicule['Fiabilite']}/10
        - **Score** : {vehicule['Score_Match']:.1f}%
        
        ### Équipements
        {vehicule['Equipements']}
        
        ### Liens
        [Voir l'annonce]({vehicule['Lien_Annonce']})
        """)
        
        # Red flags
        st.subheader("⚠️ Points d'attention")
        red_flags = st.text_area(
            "Listez les points d'attention (séparés par des virgules)",
            value=vehicule['Red_Flags'] if 'Red_Flags' in vehicule else "",
            help="Ex: Kilométrage suspect, Traces de rouille..."
        )
        if red_flags != vehicule.get('Red_Flags', ""):
            df.at[idx, 'Red_Flags'] = red_flags
            sauvegarder_donnees(df)
        
        # Tags personnalisés
        st.subheader("🏷️ Tags")
        tags = st.text_input(
            "Ajoutez des tags (séparés par des virgules)",
            value=vehicule['Tags'] if 'Tags' in vehicule else "",
            help="Ex: première main, faible kilométrage, sport..."
        )
        if tags != vehicule.get('Tags', ""):
            df.at[idx, 'Tags'] = tags
            sauvegarder_donnees(df)
        
        # Export PDF
        st.markdown("### 📄 Export")
        if st.button("Générer la fiche PDF"):
            pdf_bytes = generer_pdf_vehicule(vehicule)
            st.markdown(
                get_download_link(pdf_bytes, f"fiche_{vehicule['Marque']}_{vehicule['Modele']}.pdf"),
                unsafe_allow_html=True
            )
    
    if st.button("← Retour à la galerie"):
        st.session_state.page = "galerie"
        st.session_state.selected_car = None 