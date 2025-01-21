import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuration de la page
st.set_page_config(
    page_title="Gestionnaire de Véhicules",
    page_icon="🚗",
    layout="wide"
)

# Titre de l'application
st.title("🚗 Gestionnaire de Véhicules")

# Fonction pour charger les données
@st.cache_data
def charger_donnees():
    if os.path.exists('data.csv'):
        return pd.read_csv('data.csv')
    return pd.DataFrame(columns=['Marque', 'Modele', 'Annee', 'Prix', 'Consommation', 
                               'Cout_Assurance', 'Equipements', 'Fiabilite'])

# Fonction pour sauvegarder les données
def sauvegarder_donnees(df):
    df.to_csv('data.csv', index=False)

# Chargement des données
df = charger_donnees()

# Création de deux colonnes
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📝 Ajouter un véhicule")
    
    # Formulaire de saisie
    with st.form("formulaire_vehicule"):
        marque = st.text_input("Marque")
        modele = st.text_input("Modèle")
        annee = st.number_input("Année", min_value=1900, max_value=2024, value=2020)
        prix = st.number_input("Prix (€)", min_value=0, value=10000)
        consommation = st.number_input("Consommation (L/100 km)", min_value=0.0, value=7.0)
        cout_assurance = st.number_input("Coût Assurance (€)", min_value=0, value=500)
        equipements = st.text_area("Équipements (séparés par des virgules)")
        fiabilite = st.slider("Fiabilité", 1, 10, 5)
        
        # Bouton de soumission
        submit = st.form_submit_button("Ajouter le véhicule")
        
        if submit:
            nouveau_vehicule = {
                'Marque': marque,
                'Modele': modele,
                'Annee': annee,
                'Prix': prix,
                'Consommation': consommation,
                'Cout_Assurance': cout_assurance,
                'Equipements': equipements,
                'Fiabilite': fiabilite
            }
            df = pd.concat([df, pd.DataFrame([nouveau_vehicule])], ignore_index=True)
            sauvegarder_donnees(df)
            st.success("Véhicule ajouté avec succès!")

with col2:
    st.header("📊 Visualisation des données")
    
    # Affichage du tableau
    st.subheader("Liste des véhicules")
    st.dataframe(df, use_container_width=True)
    
    # Graphique interactif
    st.subheader("Analyse graphique")
    type_graphique = st.selectbox(
        "Choisir le type de graphique",
        ["Prix vs Fiabilité", "Prix vs Année", "Consommation vs Prix"]
    )
    
    if not df.empty:
        if type_graphique == "Prix vs Fiabilité":
            fig = px.scatter(df, x="Prix", y="Fiabilité", 
                           color="Marque", hover_data=['Modele', 'Annee', 'Consommation'],
                           title="Prix en fonction de la fiabilité")
        elif type_graphique == "Prix vs Année":
            fig = px.scatter(df, x="Annee", y="Prix",
                           color="Marque", hover_data=['Modele', 'Fiabilite', 'Consommation'],
                           title="Prix en fonction de l'année")
        else:
            fig = px.scatter(df, x="Consommation", y="Prix",
                           color="Marque", hover_data=['Modele', 'Annee', 'Fiabilite'],
                           title="Prix en fonction de la consommation")
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Ajoutez des véhicules pour voir les graphiques") 