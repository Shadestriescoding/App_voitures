import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

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
    .main {
        padding: 2rem;
    }
    .stForm {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
    }
    .car-image {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    .car-image:hover {
        transform: scale(1.02);
    }
    .car-card {
        padding: 1rem;
        border-radius: 10px;
        background: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Fonction pour extraire l'image d'une annonce
def extraire_image_annonce(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        domain = urlparse(url).netloc
        
        default_images = {
            'www.lacentrale.fr': 'https://images.caradisiac.com/logos/5/0/6/2/275062/S7-guide-occasion-bmw-serie-3-e46-1998-2005-une-valeur-sure-175822.jpg',
            'www.leboncoin.fr': 'https://images.caradisiac.com/logos/5/0/6/2/275062/S7-guide-occasion-bmw-serie-3-e46-1998-2005-une-valeur-sure-175822.jpg',
            'www.autoscout24.fr': 'https://images.caradisiac.com/logos/5/0/6/2/275062/S7-guide-occasion-bmw-serie-3-e46-1998-2005-une-valeur-sure-175822.jpg'
        }
        
        return default_images.get(domain, 'https://via.placeholder.com/400x300?text=Image+non+disponible')
        
    except Exception as e:
        st.warning(f"Impossible d'extraire l'image de l'annonce : {str(e)}")
        return 'https://via.placeholder.com/400x300?text=Image+non+disponible'

# Fonction pour charger les données
@st.cache_data
def charger_donnees():
    if os.path.exists('data.csv'):
        return pd.read_csv('data.csv')
    return pd.DataFrame(columns=[
        'Marque', 'Modele', 'Annee', 'Prix', 'Consommation',
        'Cout_Assurance', 'Equipements', 'Fiabilite',
        'Date_Ajout', 'Lien_Annonce', 'Image_URL'
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
                st.markdown(f"""
                <div class="car-card">
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
        elif nom == 'annee_min':
            if vehicule['Annee'] >= critere['valeur']:
                score += critere['poids']
        elif nom == 'conso_max':
            if vehicule['Consommation'] <= critere['valeur']:
                score += critere['poids']
        elif nom == 'fiabilite_min':
            if vehicule['Fiabilite'] >= critere['valeur']:
                score += critere['poids']
        elif nom == 'assurance_max':
            if vehicule['Cout_Assurance'] <= critere['valeur']:
                score += critere['poids']
        elif nom == 'equipements':
            equips_vehicule = set(map(str.strip, vehicule['Equipements'].lower().split(',')))
            equips_souhaites = set(map(str.strip, critere['valeur'].lower().split(',')))
            if equips_souhaites:
                score += critere['poids'] * len(equips_vehicule.intersection(equips_souhaites)) / len(equips_souhaites)
    
    return (score / poids_total) * 100

# Chargement des données
df = charger_donnees()

# Initialisation de la session state
if 'page' not in st.session_state:
    st.session_state.page = "galerie"
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'selected_car' not in st.session_state:
    st.session_state.selected_car = None

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
    
    # Barre de recherche
    search = st.text_input("🔍 Rechercher un modèle", 
                          value=st.session_state.search_query,
                          help="Ex: BMW E46, Mercedes C200...")
    
    # Filtres
    st.subheader("Filtres")
    marques = st.multiselect("Marque", options=sorted(df['Marque'].unique()) if not df.empty else [])
    
    prix_range = st.slider(
        "Prix (€)",
        min_value=int(df['Prix'].min()) if not df.empty else 0,
        max_value=int(df['Prix'].max()) if not df.empty else 100000,
        value=(int(df['Prix'].min()) if not df.empty else 0, 
               int(df['Prix'].max()) if not df.empty else 100000)
    )
    
    annee_range = st.slider(
        "Année",
        min_value=int(df['Annee'].min()) if not df.empty else 1998,
        max_value=int(df['Annee'].max()) if not df.empty else datetime.now().year,
        value=(int(df['Annee'].min()) if not df.empty else 1998,
               int(df['Annee'].max()) if not df.empty else datetime.now().year)
    )
    
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
if search:
    search = search.lower()
    df_filtered = df_filtered[
        df_filtered['Marque'].str.lower().str.contains(search) |
        df_filtered['Modele'].str.lower().str.contains(search)
    ]
if marques:
    df_filtered = df_filtered[df_filtered['Marque'].isin(marques)]
df_filtered = df_filtered[
    (df_filtered['Prix'] >= prix_range[0]) &
    (df_filtered['Prix'] <= prix_range[1]) &
    (df_filtered['Annee'] >= annee_range[0]) &
    (df_filtered['Annee'] <= annee_range[1])
]

# Affichage de la page principale
if st.session_state.page == "galerie":
    st.title("🖼️ Galerie des véhicules")
    afficher_galerie(df_filtered)

elif st.session_state.page == "ajouter":
    st.title("📝 Ajouter un véhicule")
    
    with st.form("formulaire_vehicule"):
        col1, col2 = st.columns(2)
        
        with col1:
            marque = st.text_input("Marque", help="Ex: BMW, Mercedes, Audi...")
            modele = st.text_input("Modèle", help="Ex: E46 330i, C200, A4...")
            annee = st.number_input("Année", 
                                  min_value=1998, 
                                  max_value=datetime.now().year,
                                  value=2020)
            prix = st.number_input("Prix (€)", 
                                 min_value=0, 
                                 value=10000)
            
        with col2:
            consommation = st.number_input("Consommation (L/100 km)",
                                         min_value=0.0,
                                         max_value=30.0,
                                         value=7.0,
                                         step=0.1)
            cout_assurance = st.number_input("Coût Assurance (€/an)",
                                           min_value=0,
                                           value=500)
            fiabilite = st.slider("Fiabilité", 1, 10, 5)
            
        equipements = st.text_area("Équipements",
                                 help="Liste des équipements, séparés par des virgules")
        lien_annonce = st.text_input("Lien de l'annonce",
                                   help="URL de l'annonce (La Centrale, LeBonCoin, AutoScout24...)")
        
        submit = st.form_submit_button("Ajouter ce véhicule")
        
        if submit:
            if not marque or not modele:
                st.error("❌ La marque et le modèle sont obligatoires!")
            else:
                image_url = extraire_image_annonce(lien_annonce) if lien_annonce else ""
                
                nouveau_vehicule = {
                    'Marque': marque,
                    'Modele': modele,
                    'Annee': annee,
                    'Prix': prix,
                    'Consommation': consommation,
                    'Cout_Assurance': cout_assurance,
                    'Equipements': equipements,
                    'Fiabilite': fiabilite,
                    'Date_Ajout': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'Lien_Annonce': lien_annonce,
                    'Image_URL': image_url
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
    
    if st.button("← Retour à la galerie"):
        st.session_state.page = "galerie"
        st.session_state.selected_car = None

elif st.session_state.page == "config":
    st.title("⚙️ Configuration de la recherche")
    
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
        
        st.session_state.config_criteres['equipements']['valeur'] = st.text_area(
            "Équipements souhaités (séparés par des virgules)",
            value=st.session_state.config_criteres['equipements']['valeur'],
            help="Ex: climatisation, gps, cuir, régulateur"
        )
        st.session_state.config_criteres['equipements']['poids'] = st.slider(
            "Importance des équipements",
            1, 10, st.session_state.config_criteres['equipements']['poids']
        )
    
    st.markdown("---")
    
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