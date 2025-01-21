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
    }
    </style>
    """, unsafe_allow_html=True)

# Titre de l'application
st.title("🚗 Gestionnaire de Véhicules")
st.markdown("---")

# Fonction pour extraire l'image d'une annonce
def extraire_image_annonce(url):
    try:
        # Headers pour simuler un navigateur
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Analyse du domaine
        domain = urlparse(url).netloc
        
        # URL d'image par défaut selon le site
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

# Chargement des données
df = charger_donnees()

# Création de deux colonnes principales
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📝 Ajouter un véhicule")
    
    # Formulaire de saisie
    with st.form("formulaire_vehicule"):
        marque = st.text_input("Marque", help="Ex: BMW, Mercedes, Audi...")
        modele = st.text_input("Modèle", help="Ex: E46 330i, C200, A4...")
        annee = st.number_input("Année", 
                              min_value=1998, 
                              max_value=datetime.now().year,
                              value=2020,
                              help="Année de mise en circulation")
        
        prix = st.number_input("Prix (€)", 
                             min_value=0, 
                             value=10000,
                             help="Prix en euros")
        
        consommation = st.number_input("Consommation (L/100 km)",
                                     min_value=0.0,
                                     max_value=30.0,
                                     value=7.0,
                                     step=0.1,
                                     help="Consommation moyenne en L/100km")
        
        cout_assurance = st.number_input("Coût Assurance (€/an)",
                                       min_value=0,
                                       value=500,
                                       help="Coût annuel de l'assurance")
        
        equipements = st.text_area("Équipements",
                                 help="Liste des équipements, séparés par des virgules")
        
        fiabilite = st.slider("Fiabilité",
                            min_value=1,
                            max_value=10,
                            value=5,
                            help="Note de fiabilité sur 10")
        
        lien_annonce = st.text_input("Lien de l'annonce",
                                   help="URL de l'annonce (La Centrale, LeBonCoin, AutoScout24...)")
        
        # Bouton de soumission
        submit = st.form_submit_button("Ajouter ce véhicule")
        
        if submit:
            if not marque or not modele:
                st.error("❌ La marque et le modèle sont obligatoires!")
            else:
                # Extraction de l'image si un lien est fourni
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

with col2:
    st.header("📊 Visualisation des données")
    
    if df.empty:
        st.info("🔍 Aucun véhicule enregistré. Utilisez le formulaire pour ajouter votre premier véhicule!")
    else:
        # Onglets pour la visualisation
        tab1, tab2, tab3 = st.tabs(["📋 Tableau des véhicules", "🖼️ Galerie", "📈 Graphiques"])
        
        with tab1:
            # Filtres pour le tableau
            col_filtre1, col_filtre2 = st.columns(2)
            with col_filtre1:
                marque_filter = st.multiselect(
                    "Filtrer par marque",
                    options=sorted(df['Marque'].unique())
                )
            
            with col_filtre2:
                annee_range = st.slider(
                    "Filtrer par année",
                    min_value=int(df['Annee'].min()),
                    max_value=int(df['Annee'].max()),
                    value=(int(df['Annee'].min()), int(df['Annee'].max()))
                )
            
            # Application des filtres
            df_filtered = df.copy()
            if marque_filter:
                df_filtered = df_filtered[df_filtered['Marque'].isin(marque_filter)]
            df_filtered = df_filtered[
                (df_filtered['Annee'] >= annee_range[0]) &
                (df_filtered['Annee'] <= annee_range[1])
            ]
            
            # Affichage du tableau filtré avec lien cliquable
            st.dataframe(
                df_filtered.style.format({
                    'Lien_Annonce': lambda x: f'<a href="{x}" target="_blank">Voir l\'annonce</a>' if x else ''
                }),
                use_container_width=True,
                hide_index=True
            )
        
        with tab2:
            st.subheader("🚗 Galerie des véhicules")
            
            # Affichage des véhicules en grille
            cols = st.columns(3)
            for idx, row in df_filtered.iterrows():
                with cols[idx % 3]:
                    st.markdown(f"**{row['Marque']} {row['Modele']} ({row['Annee']})**")
                    if row['Image_URL']:
                        st.image(row['Image_URL'], 
                                use_column_width=True,
                                caption=f"Prix: {row['Prix']:,.0f} €")
                    if row['Lien_Annonce']:
                        st.markdown(f"[Voir l'annonce]({row['Lien_Annonce']})")
                    st.markdown("---")
        
        with tab3:
            # Sélection du type de graphique
            type_graphique = st.selectbox(
                "Type de graphique",
                ["Prix vs Fiabilité", "Prix vs Année", "Consommation vs Prix"]
            )
            
            if type_graphique == "Prix vs Fiabilité":
                fig = px.scatter(df_filtered, 
                               x="Prix",
                               y="Fiabilite",
                               color="Marque",
                               size="Annee",
                               hover_data=['Modele', 'Consommation', 'Cout_Assurance'],
                               title="Relation Prix / Fiabilité par marque")
            elif type_graphique == "Prix vs Année":
                fig = px.scatter(df_filtered,
                               x="Annee",
                               y="Prix",
                               color="Marque",
                               size="Fiabilite",
                               hover_data=['Modele', 'Consommation', 'Cout_Assurance'],
                               title="Évolution des prix selon l'année")
            else:
                fig = px.scatter(df_filtered,
                               x="Consommation",
                               y="Prix",
                               color="Marque",
                               size="Fiabilite",
                               hover_data=['Modele', 'Annee', 'Cout_Assurance'],
                               title="Relation Prix / Consommation")
            
            # Personnalisation du graphique
            fig.update_layout(
                height=600,
                hovermode='closest',
                showlegend=True,
                template="plotly_white"
            )
            
            # Affichage du graphique
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistiques rapides
            st.subheader("📈 Statistiques rapides")
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            
            with col_stats1:
                st.metric("Prix moyen", f"{df_filtered['Prix'].mean():,.0f} €")
            with col_stats2:
                st.metric("Consommation moyenne", f"{df_filtered['Consommation'].mean():.1f} L/100km")
            with col_stats3:
                st.metric("Note moyenne", f"{df_filtered['Fiabilite'].mean():.1f}/10") 