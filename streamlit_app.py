import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import fpdf
from fpdf import FPDF
import json
import base64

# Configuration de la page
st.set_page_config(
    page_title="Gestionnaire de Véhicules",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles CSS personnalisés
st.markdown("""
    <style>
    /* Styles globaux */
    .main {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Animation d'entrée */
    @keyframes slideIn {
        from {
            transform: translateY(20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    /* Cartes véhicules */
    .car-card {
        padding: 1.8rem;
        border-radius: 20px;
        background: linear-gradient(145deg, #ffffff, #f5f7fa);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: slideIn 0.5s ease-out;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    .car-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
    }
    
    .premium-card {
        background: linear-gradient(145deg, #fff9e6, #fff2cc);
        border: 2px solid #ffd700;
        position: relative;
        overflow: hidden;
    }
    
    .premium-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #ffd700, #ffa500);
    }
    
    /* Badges et statuts */
    .badge-container {
        position: absolute;
        top: 20px;
        right: 20px;
        display: flex;
        flex-direction: column;
        gap: 10px;
        z-index: 2;
    }
    
    .match-badge {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        padding: 8px 16px;
        border-radius: 30px;
        font-size: 0.95em;
        font-weight: 600;
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
        animation: pulse 2s infinite;
        backdrop-filter: blur(4px);
    }
    
    .favorite-badge {
        background: linear-gradient(135deg, #FF4B82, #FF6B6B);
        color: white;
        padding: 8px 16px;
        border-radius: 30px;
        font-size: 0.95em;
        font-weight: 600;
        box-shadow: 0 4px 8px rgba(255, 75, 130, 0.3);
        backdrop-filter: blur(4px);
    }
    
    /* Informations véhicule */
    .car-info {
        margin-top: 1.5rem;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 15px;
        backdrop-filter: blur(4px);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .car-price {
        font-size: 1.5em;
        font-weight: 700;
        color: #2196F3;
        text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.1);
        letter-spacing: -0.5px;
    }
    
    .car-stats {
        display: flex;
        gap: 1.5rem;
        margin-top: 1rem;
        color: #555;
        font-size: 1em;
        padding: 0.8rem;
        background: rgba(0, 0, 0, 0.02);
        border-radius: 12px;
    }
    
    .car-stats span {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Points forts/faibles */
    .points-container {
        margin-top: 1.2rem;
        display: grid;
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .points-forts, .points-faibles {
        padding: 1rem;
        border-radius: 12px;
        font-size: 0.95em;
        line-height: 1.5;
        backdrop-filter: blur(4px);
    }
    
    .points-forts {
        background: rgba(76, 175, 80, 0.1);
        border-left: 4px solid #4CAF50;
        color: #2e7d32;
    }
    
    .points-faibles {
        background: rgba(244, 67, 54, 0.1);
        border-left: 4px solid #f44336;
        color: #d32f2f;
    }
    
    /* Boutons et actions */
    .action-buttons {
        display: flex;
        gap: 1rem;
        margin-top: 1.5rem;
    }
    
    .action-button {
        padding: 0.8rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
        text-align: center;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        cursor: pointer;
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Formulaires et entrées */
    .stTextInput, .stNumberInput, .stSelectbox {
        background: white;
        border-radius: 12px;
        border: 1px solid rgba(0, 0, 0, 0.1);
        padding: 0.8rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput:focus, .stNumberInput:focus, .stSelectbox:focus {
        border-color: #2196F3;
        box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
    }
    
    /* Animations */
    @keyframes pulse {
        0% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
        100% {
            transform: scale(1);
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .car-card {
            padding: 1.2rem;
        }
        
        .car-stats {
            flex-direction: column;
            gap: 0.8rem;
        }
        
        .badge-container {
            position: static;
            margin-bottom: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Nouvelle classe pour le PDF personnalisé
class VehiculePDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Fiche Véhicule', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# Fonction pour créer un PDF
def generer_pdf_vehicule(vehicule):
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
    if 'Notes_Detaillees' in vehicule:
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
            pdf.cell(0, 10, f"• {flag.strip()}", 0, 1)
    
    # Tags
    if 'Tags' in vehicule and vehicule['Tags']:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, "Tags", 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, vehicule['Tags'], 0, 1)
    
    return pdf.output(dest='S').encode('latin1')

# Fonction pour créer un lien de téléchargement
def get_download_link(pdf_bytes, filename):
    b64 = base64.b64encode(pdf_bytes).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Télécharger le PDF</a>'

# Chargement des données de référence
@st.cache_data
def charger_references():
    marques_df = pd.read_csv('data/marques.csv')
    equipements_df = pd.read_csv('data/equipements.csv')
    return marques_df, equipements_df

# Fonction pour extraire les informations d'une annonce
def extraire_infos_annonce(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        domain = urlparse(url).netloc
        
        if 'autoscout24.fr' in domain:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraction des informations (à adapter selon la structure du site)
            prix = soup.find('span', {'class': 'price'})
            prix = int(re.sub(r'[^\d]', '', prix.text)) if prix else 0
            
            titre = soup.find('h1').text.strip()
            marque, modele = titre.split(' ', 1)
            
            annee = soup.find('span', {'class': 'year'})
            annee = int(annee.text) if annee else 2000
            
            return {
                'prix': prix,
                'marque': marque,
                'modele': modele,
                'annee': annee,
                'image_url': soup.find('img', {'class': 'gallery-picture'})['src'] if soup.find('img', {'class': 'gallery-picture'}) else ''
            }
            
        elif 'leboncoin.fr' in domain:
            # Similaire pour LeBonCoin
            pass
            
    except Exception as e:
        st.warning(f"Impossible d'extraire les informations de l'annonce : {str(e)}")
        return None

# Fonction pour charger les données
@st.cache_data
def charger_donnees():
    if os.path.exists('data.csv'):
        return pd.read_csv('data.csv')
    return pd.DataFrame(columns=[
        'Marque', 'Modele', 'Annee', 'Prix', 'Consommation',
        'Cout_Assurance', 'Equipements', 'Fiabilite',
        'Date_Ajout', 'Lien_Annonce', 'Image_URL',
        'Status', 'Selection_Franck', 'Notes',
        'Notes_Detaillees', 'Red_Flags', 'Tags',
        'Points_Forts', 'Points_Faibles'
    ])

# Fonction pour sauvegarder les données
def sauvegarder_donnees(df):
    df.to_csv('data.csv', index=False)

# Fonction pour afficher la galerie
def afficher_galerie(df_filtered):
    if df_filtered.empty:
        st.info("🔍 Aucun véhicule ne correspond à votre recherche.")
        return
        
    # Affichage en grille avec 3 colonnes
    cols = st.columns(3)
    for idx, row in df_filtered.iterrows():
        with cols[idx % 3]:
            with st.container():
                # Status badge
                status_class = {
                    "Validé": "status-validated",
                    "Rejeté": "status-rejected",
                    "En attente": "status-pending"
                }.get(row['Status'], "status-pending")
                
                st.markdown(f"""
                <div class="car-card">
                    <div class="{status_class}">{row['Status']}</div>
                    <h3>{row['Marque']} {row['Modele']}</h3>
                    <p>Année: {row['Annee']} | Prix: {row['Prix']:,.0f} €</p>
                </div>
                """, unsafe_allow_html=True)
                
                if row['Image_URL']:
                    st.image(row['Image_URL'], 
                            use_column_width=True,
                            caption=f"Fiabilité: {row['Fiabilite']}/10 | Conso: {row['Consommation']}L/100km")
                
                col1, col2 = st.columns(2)
                with col1:
                    if row['Lien_Annonce']:
                        st.markdown(f"[Voir l'annonce]({row['Lien_Annonce']})")
                with col2:
                    if st.button(f"📊 Détails", key=f"details_{idx}"):
                        st.session_state.page = "details"
                        st.session_state.selected_car = idx
                st.markdown("---")

# Fonction pour calculer le score de correspondance
def calculer_score_vehicule(vehicule, criteres):
    score = 0
    poids_total = sum(critere['poids'] for critere in criteres.values())
    
    for nom, critere in criteres.items():
        if nom == 'budget':
            if vehicule['Prix'] <= critere['valeur']:
                score += critere['poids']
            else:
                # Score partiel si proche du budget
                depassement = (vehicule['Prix'] - critere['valeur']) / critere['valeur']
        elif nom == 'annee_min':
            if vehicule['Annee'] >= critere['valeur']:
                score += critere['poids']
            else:
                # Score partiel si proche de l'année minimale
                diff_annees = critere['valeur'] - vehicule['Annee']
                if diff_annees <= 2:  # 2 ans de différence max
                    score += critere['poids'] * (1 - diff_annees/2)
        elif nom == 'conso_max':
            if vehicule['Consommation'] <= critere['valeur']:
                score += critere['poids']
            else:
                # Score partiel si proche de la consommation max
                depassement = (vehicule['Consommation'] - critere['valeur']) / critere['valeur']
                if depassement <= 0.2:  # 20% de dépassement max
                    score += critere['poids'] * (1 - depassement)
        elif nom == 'fiabilite_min':
            if vehicule['Fiabilite'] >= critere['valeur']:
                score += critere['poids']
            else:
                # Score partiel si proche de la fiabilité minimale
                diff = critere['valeur'] - vehicule['Fiabilite']
                if diff <= 2:  # 2 points de différence max
                    score += critere['poids'] * (1 - diff/2)
        elif nom == 'assurance_max':
            if vehicule['Cout_Assurance'] <= critere['valeur']:
                score += critere['poids']
            else:
                # Score partiel si proche du coût max
                depassement = (vehicule['Cout_Assurance'] - critere['valeur']) / critere['valeur']
                if depassement <= 0.2:  # 20% de dépassement max
                    score += critere['poids'] * (1 - depassement)
        elif nom == 'equipements':
            equips_vehicule = set(map(str.strip, vehicule['Equipements'].lower().split(',')))
            equips_souhaites = set(map(str.strip, critere['valeur'].lower().split(',')))
            if equips_souhaites:
                match_ratio = len(equips_vehicule.intersection(equips_souhaites)) / len(equips_souhaites)
                score += critere['poids'] * match_ratio
    
    return (score / poids_total) * 100

# Chargement des données
df = charger_donnees()
marques_df, equipements_df = charger_references()

# Initialisation de la session state
if 'page' not in st.session_state:
    st.session_state.page = "galerie"
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'selected_car' not in st.session_state:
    st.session_state.selected_car = None
if 'recherche_active' not in st.session_state:
    st.session_state.recherche_active = None
if 'recherches_validees' not in st.session_state:
    st.session_state.recherches_validees = {}

# Ajout des variables de session pour la configuration
if 'config_criteres' not in st.session_state:
    st.session_state.config_criteres = {
        'budget': {'valeur': 15000, 'poids': 5},
        'annee_min': {'valeur': 2000, 'poids': 3},
        'conso_max': {'valeur': 10.0, 'poids': 4},
        'fiabilite_min': {'valeur': 7, 'poids': 4},
        'assurance_max': {'valeur': 1000, 'poids': 3},
        'equipements': {'valeur': '', 'poids': 2}
    }

# Barre latérale pour la navigation et les filtres
with st.sidebar:
    st.title("🚗 Navigation")
    
    # Affichage des recherches validées
    if st.session_state.recherches_validees:
        st.subheader("📌 Recherches validées")
        for nom_recherche, config in st.session_state.recherches_validees.items():
            if st.button(f"🎯 {nom_recherche}", key=f"recherche_{nom_recherche}"):
                st.session_state.config_criteres = config
                st.success(f"Configuration '{nom_recherche}' chargée!")
                st.rerun()
        st.markdown("---")
    
    # Sélection de la recherche active
    recherches = ["Toutes"] + (df['Notes'].unique().tolist() if not df.empty else [])
    st.session_state.recherche_active = st.selectbox(
        "Recherche active",
        recherches,
        index=0
    )
    
    # Barre de recherche
    search = st.text_input("🔍 Rechercher un modèle", 
                          value=st.session_state.search_query,
                          help="Ex: BMW E46, Mercedes C200...")
    
    # Filtres
    st.subheader("Filtres")
    status = st.multiselect(
        "Statut",
        ["En attente", "Validé", "Rejeté"]
    )
    
    marques = st.multiselect(
        "Marque",
        sorted(marques_df['marque'].unique())
    )
    
    prix_range = st.slider(
        "Prix (€)",
        min_value=int(df['Prix'].min()) if not df.empty else 0,
        max_value=int(df['Prix'].max()) if not df.empty else 100000,
        value=(int(df['Prix'].min()) if not df.empty else 0,
               int(df['Prix'].max()) if not df.empty else 100000)
    
    # Navigation
    st.markdown("---")
    if st.button("🖼️ Galerie", use_container_width=True):
        st.session_state.page = "galerie"
    if st.button("📝 Ajouter un véhicule", use_container_width=True):
        st.session_state.page = "ajouter"
    if st.button("📊 Statistiques", use_container_width=True):
        st.session_state.page = "stats"
    if st.button("⚙️ Configuration recherche", use_container_width=True):
        st.session_state.page = "config"

# Filtrage des données
df_filtered = df.copy()

if st.session_state.recherche_active != "Toutes":
    df_filtered = df_filtered[df_filtered['Notes'] == st.session_state.recherche_active]

if search:
    search = search.lower()
    df_filtered = df_filtered[
        df_filtered['Marque'].str.lower().str.contains(search) |
        df_filtered['Modele'].str.lower().str.contains(search)
    ]

if status:
    df_filtered = df_filtered[df_filtered['Status'].isin(status)]

if marques:
    df_filtered = df_filtered[df_filtered['Marque'].isin(marques)]

df_filtered = df_filtered[
    (df_filtered['Prix'] >= prix_range[0]) &
    (df_filtered['Prix'] <= prix_range[1])
]

# Affichage de la page principale
if st.session_state.page == "galerie":
    st.title("🖼️ Galerie des véhicules")
    
    # Calcul des scores pour tous les véhicules
    for idx, vehicule in df_filtered.iterrows():
        score = calculer_score_vehicule(vehicule, st.session_state.config_criteres)
        df_filtered.at[idx, 'Score_Match'] = score
    
    # Barre de tri et filtres
    col_tri, col_vue = st.columns([2, 1])
    with col_tri:
        tri = st.selectbox(
            "Trier par",
            ["Score de correspondance ↓", "Date d'ajout ↓", "Prix ↑", "Prix ↓", "Année ↓", "Fiabilité ↓"],
            help="Choisissez comment trier les véhicules"
        )
    
    with col_vue:
        vue = st.radio(
            "Vue",
            ["Grille", "Liste"],
            horizontal=True,
            help="Choisissez le mode d'affichage"
        )
    
    # Tri des véhicules
    if tri == "Score de correspondance ↓":
        df_filtered = df_filtered.sort_values('Score_Match', ascending=False)
    elif tri == "Date d'ajout ↓":
        df_filtered = df_filtered.sort_values('Date_Ajout', ascending=False)
    elif tri == "Prix ↑":
        df_filtered = df_filtered.sort_values('Prix')
    elif tri == "Prix ↓":
        df_filtered = df_filtered.sort_values('Prix', ascending=False)
    elif tri == "Année ↓":
        df_filtered = df_filtered.sort_values('Annee', ascending=False)
    elif tri == "Fiabilité ↓":
        df_filtered = df_filtered.sort_values('Fiabilite', ascending=False)
    
    # Affichage des véhicules
    if vue == "Grille":
        cols = st.columns(3)
        for idx, row in df_filtered.iterrows():
            with cols[idx % 3]:
                afficher_carte_vehicule(row, idx)
    else:
        for idx, row in df_filtered.iterrows():
            afficher_liste_vehicule(row, idx)

def afficher_carte_vehicule(row, idx):
    card_class = "car-card premium-card" if row['Score_Match'] >= 80 else "car-card"
    
    # HTML pour la carte
    html = f"""
    <div class="{card_class}">
        <div class="badge-container">
            <div class="match-badge">Match {row['Score_Match']:.0f}%</div>
            {"<div class='favorite-badge'>❤️ Coup de cœur</div>" if row.get('Coup_de_Coeur', False) else ""}
        </div>
        
        <h3 style="font-size: 1.4em; margin-bottom: 1rem;">{row['Marque']} {row['Modele']}</h3>
        
        <div class="car-info">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 1.1em;">Année {row['Annee']}</span>
                <span class="car-price">{row['Prix']:,.0f} €</span>
            </div>
            
            <div class="car-stats">
                <span title="Fiabilité">🔋 {row['Fiabilite']}/10</span>
                <span title="Consommation">⛽ {row['Consommation']}L/100km</span>
                <span title="Assurance">🛡️ {row['Cout_Assurance']}€/an</span>
            </div>
        </div>
    """
    
    # Ajout des points forts/faibles s'ils existent
    if row.get('Points_Forts') or row.get('Points_Faibles'):
        html += '<div class="points-container">'
        if row.get('Points_Forts'):
            points = [p.strip() for p in row['Points_Forts'].split('\n') if p.strip()][:2]
            if points:
                html += '<div class="points-forts">'
                for point in points:
                    html += f'<div>✓ {point}</div>'
                html += '</div>'
        
        if row.get('Points_Faibles'):
            points = [p.strip() for p in row['Points_Faibles'].split('\n') if p.strip()][:2]
            if points:
                html += '<div class="points-faibles">'
                for point in points:
                    html += f'<div>✗ {point}</div>'
                html += '</div>'
        html += '</div>'
    
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
    
    # Boutons d'action
    col1, col2, col3 = st.columns(3)
    with col1:
        if row['Lien_Annonce']:
            st.markdown(f"<a href='{row['Lien_Annonce']}' target='_blank' class='action-button'>🔗 Annonce</a>", unsafe_allow_html=True)
    with col2:
        if st.button("📊 Détails", key=f"details_{idx}"):
            st.session_state.page = "details"
            st.session_state.selected_car = idx
    with col3:
        if st.button("❤️", key=f"favorite_{idx}"):
            df.at[idx, 'Coup_de_Coeur'] = not df.at[idx, 'Coup_de_Coeur']
            sauvegarder_donnees(df)
            st.rerun()

def afficher_liste_vehicule(row, idx):
    st.markdown(f"""
    <div class="car-card" style="display: flex; gap: 2rem; align-items: center;">
        <div style="flex: 1;">
            <h3>{row['Marque']} {row['Modele']} ({row['Annee']})</h3>
            <div class="car-stats">
                <span>🔋 {row['Fiabilite']}/10</span>
                <span>⛽ {row['Consommation']}L/100km</span>
                <span>💰 {row['Prix']:,.0f} €</span>
            </div>
        </div>
        <div class="action-buttons" style="flex: 0 0 auto;">
            <a href="{row['Lien_Annonce']}" target="_blank" class="action-button">🔗</a>
            <button onclick="details_{idx}()" class="action-button">📊</button>
            <button onclick="favorite_{idx}()" class="action-button">❤️</button>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == "ajouter":
    st.title("📝 Ajouter un véhicule")
    
    # Option pour ajouter via URL
    url_annonce = st.text_input(
        "URL de l'annonce (AutoScout24, LeBonCoin)", 
        help="Collez l'URL de l'annonce pour remplir automatiquement les informations"
    )
    
    infos_annonce = None
    if url_annonce:
        infos_annonce = extraire_infos_annonce(url_annonce)
        if infos_annonce:
            st.success("✅ Informations extraites avec succès!")
    
    with st.form("formulaire_vehicule"):
        col1, col2 = st.columns(2)
        
        with col1:
            marque = st.selectbox(
                "Marque",
                options=sorted(marques_df['marque'].unique()),
                index=0 if not infos_annonce else list(marques_df['marque'].unique()).index(infos_annonce['marque'])
            )
            
            modeles_disponibles = marques_df[marques_df['marque'] == marque]['modele'].unique()
            modele = st.selectbox(
                "Modèle",
                options=modeles_disponibles,
                index=0 if not infos_annonce else list(modeles_disponibles).index(infos_annonce['modele'])
            )
            
            annee = st.number_input(
                "Année",
                min_value=1998,
                max_value=datetime.now().year,
                value=infos_annonce['annee'] if infos_annonce else 2020
            )
            
            prix = st.number_input(
                "Prix (€)",
                min_value=0,
                value=infos_annonce['prix'] if infos_annonce else 10000
            )
        
        with col2:
            consommation = st.number_input(
                "Consommation (L/100 km)",
                min_value=0.0,
                max_value=30.0,
                value=7.0,
                step=0.1
            )
            
            cout_assurance = st.number_input(
                "Coût Assurance (€/an)",
                min_value=0,
                value=500
            )
            
            fiabilite = st.slider(
                "Fiabilité",
                1, 10, 5
            )
        
        # Sélection des équipements
        st.subheader("Équipements")
        equipements_selectionnes = []
        
        for categorie in equipements_df['categorie'].unique():
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{categorie}**")
            with col2:
                equips = equipements_df[equipements_df['categorie'] == categorie]['equipement'].tolist()
                for equip in equips:
                    if st.checkbox(equip, help=equipements_df[equipements_df['equipement'] == equip]['description'].iloc[0]):
                        equipements_selectionnes.append(equip)
        
        notes = st.text_area(
            "Notes/Commentaires",
            help="Ajoutez des notes ou commentaires sur le véhicule"
        )
        
        recherche = st.text_input(
            "Nom de la recherche",
            help="Donnez un nom à cette recherche pour regrouper les véhicules similaires"
        )
        
        submit = st.form_submit_button("Ajouter ce véhicule")
        
        if submit:
            if not marque or not modele:
                st.error("❌ La marque et le modèle sont obligatoires!")
            else:
                nouveau_vehicule = {
                    'Marque': marque,
                    'Modele': modele,
                    'Annee': annee,
                    'Prix': prix,
                    'Consommation': consommation,
                    'Cout_Assurance': cout_assurance,
                    'Equipements': ", ".join(equipements_selectionnes),
                    'Fiabilite': fiabilite,
                    'Date_Ajout': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'Lien_Annonce': url_annonce,
                    'Image_URL': infos_annonce['image_url'] if infos_annonce else "",
                    'Status': "En attente",
                    'Selection_Franck': False,
                    'Notes': notes,
                    'Recherche': recherche
                }
                df = pd.concat([df, pd.DataFrame([nouveau_vehicule])], ignore_index=True)
                sauvegarder_donnees(df)
                st.success("✅ Véhicule ajouté avec succès!")
                st.balloons()
                st.session_state.page = "galerie"

elif st.session_state.page == "stats":
    st.title("📊 Statistiques")
    
    if df_filtered.empty:
        st.info("Aucune donnée disponible pour les statistiques.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Prix moyen", f"{df_filtered['Prix'].mean():,.0f} €")
        with col2:
            st.metric("Consommation moyenne", f"{df_filtered['Consommation'].mean():.1f} L/100km")
        with col3:
            st.metric("Note moyenne", f"{df_filtered['Fiabilite'].mean():.1f}/10")
        
        # Graphiques
        st.subheader("Analyse des prix")
        fig1 = px.box(df_filtered, x="Marque", y="Prix", title="Distribution des prix par marque")
        st.plotly_chart(fig1, use_container_width=True)
        
        st.subheader("Évolution temporelle")
        fig2 = px.scatter(df_filtered, 
                         x="Annee", 
                         y="Prix",
                         color="Marque",
                         size="Fiabilite",
                         hover_data=['Modele', 'Consommation'],
                         title="Évolution des prix selon l'année")
        st.plotly_chart(fig2, use_container_width=True)

elif st.session_state.page == "details" and st.session_state.selected_car is not None:
    voiture = df_filtered.iloc[st.session_state.selected_car]
    st.title(f"{voiture['Marque']} {voiture['Modele']}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if voiture['Image_URL']:
            st.image(voiture['Image_URL'], use_column_width=True)
        
        # Points forts et points faibles
        st.subheader("💪 Points forts et points faibles")
        col_plus, col_moins = st.columns(2)
        
        with col_plus:
            st.markdown("#### ✅ Points forts")
            points_forts = st.text_area(
                "Listez les points forts (un par ligne)",
                value=voiture['Points_Forts'] if 'Points_Forts' in voiture else "",
                help="Ex: Faible kilométrage, Carnet d'entretien complet...",
                height=150
            )
            if points_forts != voiture.get('Points_Forts', ""):
                df.at[st.session_state.selected_car, 'Points_Forts'] = points_forts
                sauvegarder_donnees(df)
        
        with col_moins:
            st.markdown("#### ❌ Points faibles")
            points_faibles = st.text_area(
                "Listez les points faibles (un par ligne)",
                value=voiture['Points_Faibles'] if 'Points_Faibles' in voiture else "",
                help="Ex: Consommation élevée, Entretien coûteux...",
                height=150
            )
            if points_faibles != voiture.get('Points_Faibles', ""):
                df.at[st.session_state.selected_car, 'Points_Faibles'] = points_faibles
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
        if 'Notes_Detaillees' in voiture and voiture['Notes_Detaillees']:
            notes = json.loads(voiture['Notes_Detaillees'])
        
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
            df.at[st.session_state.selected_car, 'Notes_Detaillees'] = json.dumps(notes)
            sauvegarder_donnees(df)
        
        # Red flags
        st.subheader("⚠️ Points d'attention")
        red_flags = st.text_area(
            "Listez les points d'attention (un par ligne)",
            value=voiture['Red_Flags'] if 'Red_Flags' in voiture else "",
            help="Ex: Kilométrage suspect, Traces de rouille..."
        )
        if red_flags != voiture.get('Red_Flags', ""):
            df.at[st.session_state.selected_car, 'Red_Flags'] = red_flags
            sauvegarder_donnees(df)
        
        # Tags personnalisés
        st.subheader("🏷️ Tags")
        tags = st.text_input(
            "Ajoutez des tags (séparés par des virgules)",
            value=voiture['Tags'] if 'Tags' in voiture else "",
            help="Ex: première main, faible kilométrage, sport..."
        )
        if tags != voiture.get('Tags', ""):
            df.at[st.session_state.selected_car, 'Tags'] = tags
            sauvegarder_donnees(df)
    
    with col2:
        st.markdown(f"""
        ### Informations
        - **Année** : {voiture['Annee']}
        - **Prix** : {voiture['Prix']:,.0f} €
        - **Consommation** : {voiture['Consommation']} L/100km
        - **Coût assurance** : {voiture['Cout_Assurance']} €/an
        - **Fiabilité** : {voiture['Fiabilite']}/10
        
        ### Équipements
        {voiture['Equipements']}
        
        ### Liens
        [Voir l'annonce]({voiture['Lien_Annonce']})
        """)
        
        # Export PDF
        st.markdown("### 📄 Export")
        if st.button("Générer la fiche PDF"):
            pdf_bytes = generer_pdf_vehicule(voiture)
            st.markdown(
                get_download_link(pdf_bytes, f"fiche_{voiture['Marque']}_{voiture['Modele']}.pdf"),
                unsafe_allow_html=True
            )
        
        # Partage de configuration
        if st.button("📤 Partager cette configuration"):
            config_share = {
                'marque': voiture['Marque'],
                'modele': voiture['Modele'],
                'annee': voiture['Annee'],
                'prix': voiture['Prix'],
                'equipements': voiture['Equipements'].split(','),
                'notes': json.loads(voiture['Notes_Detaillees']) if 'Notes_Detaillees' in voiture else {},
                'tags': voiture['Tags'].split(',') if 'Tags' in voiture else []
            }
            st.code(json.dumps(config_share, indent=2, ensure_ascii=False))
            st.info("Copiez ce code pour partager la configuration")
    
    if st.button("← Retour à la galerie"):
        st.session_state.page = "galerie"
        st.session_state.selected_car = None

elif st.session_state.page == "config":
    st.title("⚙️ Configuration de la recherche")
    
    # Nom de la recherche
    nom_recherche = st.text_input("📝 Nom de la recherche", 
                                 help="Donnez un nom à cette configuration pour la sauvegarder")
    
    st.markdown("""
    Définissez vos critères de recherche et leur importance relative pour trouver le véhicule idéal.
    Plus le poids est élevé, plus le critère sera important dans le calcul du score de correspondance.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Critères principaux")
        
        st.session_state.config_criteres['budget']['valeur'] = st.number_input(
            "Budget maximum (€)",
            min_value=0,
            value=st.session_state.config_criteres['budget']['valeur'],
            step=1000
        )
        st.session_state.config_criteres['budget']['poids'] = st.slider(
            "Importance du budget",
            1, 10, st.session_state.config_criteres['budget']['poids']
        )
        
        st.session_state.config_criteres['annee_min']['valeur'] = st.number_input(
            "Année minimum",
            min_value=1998,
            max_value=datetime.now().year,
            value=st.session_state.config_criteres['annee_min']['valeur']
        )
        st.session_state.config_criteres['annee_min']['poids'] = st.slider(
            "Importance de l'année",
            1, 10, st.session_state.config_criteres['annee_min']['poids']
        )
        
        st.session_state.config_criteres['fiabilite_min']['valeur'] = st.number_input(
            "Fiabilité minimum (1-10)",
            min_value=1,
            max_value=10,
            value=st.session_state.config_criteres['fiabilite_min']['valeur']
        )
        st.session_state.config_criteres['fiabilite_min']['poids'] = st.slider(
            "Importance de la fiabilité",
            1, 10, st.session_state.config_criteres['fiabilite_min']['poids']
        )
    
    with col2:
        st.subheader("Critères secondaires")
        
        st.session_state.config_criteres['conso_max']['valeur'] = st.number_input(
            "Consommation maximum (L/100km)",
            min_value=0.0,
            max_value=30.0,
            value=float(st.session_state.config_criteres['conso_max']['valeur']),
            step=0.5
        )
        st.session_state.config_criteres['conso_max']['poids'] = st.slider(
            "Importance de la consommation",
            1, 10, st.session_state.config_criteres['conso_max']['poids']
        )
        
        st.session_state.config_criteres['assurance_max']['valeur'] = st.number_input(
            "Coût d'assurance maximum (€/an)",
            min_value=0,
            value=st.session_state.config_criteres['assurance_max']['valeur'],
            step=100
        )
        st.session_state.config_criteres['assurance_max']['poids'] = st.slider(
            "Importance de l'assurance",
            1, 10, st.session_state.config_criteres['assurance_max']['poids']
        )
        
        # Sélection des équipements avec autocomplétion
        equipements_disponibles = equipements_df['equipement'].tolist()
        equipements_selectionnes = st.multiselect(
            "Équipements souhaités",
            options=equipements_disponibles,
            default=[],
            help="Sélectionnez les équipements souhaités dans la liste"
        )
        
        equipements_supplementaires = st.text_input(
            "Équipements supplémentaires",
            help="Ajoutez d'autres équipements non listés (séparés par des virgules)"
        )
        
        # Combinaison des équipements sélectionnés et supplémentaires
        tous_equipements = equipements_selectionnes.copy()
        if equipements_supplementaires:
            tous_equipements.extend([e.strip() for e in equipements_supplementaires.split(',')])
        
        st.session_state.config_criteres['equipements']['valeur'] = ", ".join(tous_equipements)
        st.session_state.config_criteres['equipements']['poids'] = st.slider(
            "Importance des équipements",
            1, 10, st.session_state.config_criteres['equipements']['poids']
        )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Sauvegarder cette configuration", use_container_width=True):
            if nom_recherche:
                st.session_state.recherches_validees[nom_recherche] = st.session_state.config_criteres.copy()
                st.success(f"✅ Configuration '{nom_recherche}' sauvegardée!")
                st.balloons()
            else:
                st.error("❌ Veuillez donner un nom à cette configuration")
    
    with col2:
        if st.button("🔍 Rechercher les véhicules correspondants", use_container_width=True):
            # Calcul des scores pour chaque véhicule
            scores = []
            for idx, vehicule in df.iterrows():
                score = calculer_score_vehicule(vehicule, st.session_state.config_criteres)
                scores.append({
                    'vehicule': vehicule,
                    'score': score
                })
            
            # Tri par score décroissant
            scores.sort(key=lambda x: x['score'], reverse=True)
            
            # Affichage des résultats
            st.subheader("🏆 Véhicules recommandés")
            
            for i, item in enumerate(scores[:5]):  # Top 5 des véhicules
                vehicule = item['vehicule']
                score = item['score']
                
                with st.container():
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        if vehicule['Image_URL']:
                            st.image(vehicule['Image_URL'], use_column_width=True)
                    
                    with col2:
                        st.markdown(f"""
                        ### {vehicule['Marque']} {vehicule['Modele']} ({vehicule['Annee']})
                        - **Score de correspondance** : {score:.1f}%
                        - **Prix** : {vehicule['Prix']:,.0f} €
                        - **Fiabilité** : {vehicule['Fiabilite']}/10
                        - **Consommation** : {vehicule['Consommation']} L/100km
                        - **Assurance** : {vehicule['Cout_Assurance']} €/an
                        
                        [Voir l'annonce]({vehicule['Lien_Annonce']}) | [Voir les détails](.)
                        """)
                    st.markdown("---") 

# Affichage de la recherche active
if st.session_state.recherche_active != "Toutes":
    st.markdown(f"""
    <div class="search-active">
        <h3>🎯 Recherche active : {st.session_state.recherche_active}</h3>
        <p>Affichage des véhicules correspondant à cette recherche</p>
    </div>
    """, unsafe_allow_html=True) 