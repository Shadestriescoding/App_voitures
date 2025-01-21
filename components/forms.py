import streamlit as st
from datetime import datetime
from utils.data import sauvegarder_donnees

def afficher_formulaire_ajout(df, marques_df, equipements_df, infos_annonce=None):
    """
    Affiche le formulaire d'ajout d'un véhicule.
    Retourne le DataFrame mis à jour si un véhicule est ajouté.
    """
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
                    'Lien_Annonce': infos_annonce['url'] if infos_annonce else "",
                    'Image_URL': infos_annonce['image_url'] if infos_annonce else "",
                    'Status': "En attente",
                    'Selection_Franck': False,
                    'Notes': notes,
                    'Notes_Detaillees': "",
                    'Red_Flags': "",
                    'Tags': "",
                    'Points_Forts': "",
                    'Points_Faibles': "",
                    'Score_Match': 0,
                    'Coup_de_Coeur': False
                }
                df = pd.concat([df, pd.DataFrame([nouveau_vehicule])], ignore_index=True)
                sauvegarder_donnees(df)
                st.success("✅ Véhicule ajouté avec succès!")
                st.balloons()
                st.session_state.page = "galerie"
    
    return df

def afficher_formulaire_config(recherches_validees):
    """
    Affiche le formulaire de configuration des critères de recherche.
    """
    st.title("⚙️ Configuration de la recherche")
    
    # Nom de la recherche
    nom_recherche = st.text_input(
        "📝 Nom de la recherche",
        help="Donnez un nom à cette configuration pour la sauvegarder"
    )
    
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
        
        # Sélection des équipements
        equipements_souhaites = st.text_area(
            "Équipements souhaités",
            value=st.session_state.config_criteres['equipements']['valeur'],
            help="Listez les équipements souhaités (séparés par des virgules)"
        )
        st.session_state.config_criteres['equipements']['valeur'] = equipements_souhaites
        
        st.session_state.config_criteres['equipements']['poids'] = st.slider(
            "Importance des équipements",
            1, 10, st.session_state.config_criteres['equipements']['poids']
        )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Sauvegarder cette configuration", use_container_width=True):
            if nom_recherche:
                recherches_validees[nom_recherche] = st.session_state.config_criteres.copy()
                st.success(f"✅ Configuration '{nom_recherche}' sauvegardée!")
                st.balloons()
            else:
                st.error("❌ Veuillez donner un nom à cette configuration")
    
    with col2:
        if st.button("🔄 Réinitialiser", use_container_width=True):
            st.session_state.config_criteres = {
                'budget': {'valeur': 15000, 'poids': 5},
                'annee_min': {'valeur': 2000, 'poids': 3},
                'conso_max': {'valeur': 10.0, 'poids': 4},
                'fiabilite_min': {'valeur': 7, 'poids': 4},
                'assurance_max': {'valeur': 1000, 'poids': 3},
                'equipements': {'valeur': '', 'poids': 2}
            }
            st.success("✅ Configuration réinitialisée aux valeurs par défaut")
            st.rerun() 