import streamlit as st
from datetime import datetime
from utils.data import sauvegarder_donnees, charger_references, sauvegarder_recherche

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

def afficher_formulaire_config(recherches):
    """
    Affiche le formulaire de configuration des critères de recherche.
    """
    st.title("⚙️ Configuration de la recherche")
    
    # Chargement des données de référence
    marques_df, equipements_df = charger_references()
    
    # Nom de la recherche
    nom_recherche = st.text_input(
        "📝 Nom de la recherche",
        help="Donnez un nom à cette configuration pour la sauvegarder"
    )
    
    # Affichage des recherches existantes
    if recherches:
        st.subheader("Recherches sauvegardées")
        for nom, config in recherches.items():
            with st.expander(f"📋 {nom} ({config['date_creation']})"):
                st.json(config['criteres'])
                if config['vehicules_associes']:
                    st.write(f"🚗 {len(config['vehicules_associes'])} véhicules associés")
                if st.button(f"Charger '{nom}'"):
                    st.session_state.config_criteres = config['criteres'].copy()
                    st.rerun()
    
    st.markdown("""
    Définissez vos critères de recherche et leur importance relative pour trouver le véhicule idéal.
    Pour chaque critère, vous pouvez définir :
    - Sa valeur ou plage de valeurs souhaitée
    - Son importance (de 0 à 10) : plus l'importance est élevée, plus le critère influencera le score final
    - Si le critère est obligatoire ou optionnel
    """)
    
    # Création des onglets pour organiser les critères
    tab1, tab2, tab3, tab4 = st.tabs(["Critères principaux", "Caractéristiques techniques", "Vendeur", "Équipements"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Budget et année")
            
            # Budget avec plage et importance
            st.markdown("##### 💰 Budget")
            col_budget1, col_budget2 = st.columns(2)
            with col_budget1:
                budget_min, budget_max = st.slider(
                    "Plage de budget (€)",
                    min_value=0,
                    max_value=100000,
                    value=(st.session_state.config_criteres.get('budget_min', {'valeur': 5000})['valeur'],
                           st.session_state.config_criteres.get('budget_max', {'valeur': 20000})['valeur']),
                    step=1000
                )
            with col_budget2:
                budget_min = st.number_input(
                    "Budget minimum (€)",
                    min_value=0,
                    max_value=100000,
                    value=budget_min,
                    step=1000
                )
                budget_max = st.number_input(
                    "Budget maximum (€)",
                    min_value=0,
                    max_value=100000,
                    value=budget_max,
                    step=1000
                )
            
            col_budget_imp1, col_budget_imp2 = st.columns(2)
            with col_budget_imp1:
                budget_poids = st.slider(
                    "Importance du budget",
                    min_value=0,
                    max_value=10,
                    value=5,
                    help="0 = ignoré, 10 = très important"
                )
            with col_budget_imp2:
                budget_poids = st.number_input(
                    "Importance (0-10)",
                    min_value=0,
                    max_value=10,
                    value=budget_poids
                )
            
            budget_obligatoire = st.checkbox("Budget obligatoire", value=True)
            st.session_state.config_criteres['budget_min'] = {
                'valeur': budget_min,
                'poids': budget_poids if not budget_obligatoire else 10,
                'obligatoire': budget_obligatoire
            }
            st.session_state.config_criteres['budget_max'] = {
                'valeur': budget_max,
                'poids': budget_poids if not budget_obligatoire else 10,
                'obligatoire': budget_obligatoire
            }
            
            # Année avec plage et importance
            st.markdown("##### 📅 Année")
            col_annee1, col_annee2 = st.columns(2)
            with col_annee1:
                annee_min, annee_max = st.slider(
                    "Plage d'années",
                    min_value=1990,
                    max_value=datetime.now().year,
                    value=(st.session_state.config_criteres.get('annee_min', {'valeur': 2015})['valeur'],
                           st.session_state.config_criteres.get('annee_max', {'valeur': datetime.now().year})['valeur'])
                )
            with col_annee2:
                annee_min = st.number_input(
                    "Année minimum",
                    min_value=1990,
                    max_value=datetime.now().year,
                    value=annee_min
                )
                annee_max = st.number_input(
                    "Année maximum",
                    min_value=1990,
                    max_value=datetime.now().year,
                    value=annee_max
                )
            
            col_annee_imp1, col_annee_imp2 = st.columns(2)
            with col_annee_imp1:
                annee_poids = st.slider(
                    "Importance de l'année",
                    min_value=0,
                    max_value=10,
                    value=3,
                    help="0 = ignoré, 10 = très important"
                )
            with col_annee_imp2:
                annee_poids = st.number_input(
                    "Importance année (0-10)",
                    min_value=0,
                    max_value=10,
                    value=annee_poids
                )
            
            annee_obligatoire = st.checkbox("Année obligatoire")
            st.session_state.config_criteres['annee_min'] = {
                'valeur': annee_min,
                'poids': annee_poids if not annee_obligatoire else 10,
                'obligatoire': annee_obligatoire
            }
            st.session_state.config_criteres['annee_max'] = {
                'valeur': annee_max,
                'poids': annee_poids if not annee_obligatoire else 10,
                'obligatoire': annee_obligatoire
            }
        
        with col2:
            st.subheader("Marque et modèle")
            
            # Sélection multiple de marques avec importance
            st.markdown("##### 🏢 Marques")
            marques_selectionnees = st.multiselect(
                "Marques préférées",
                options=sorted(marques_df['marque'].unique()),
                default=st.session_state.config_criteres.get('marques', {'valeur': []})['valeur']
            )
            marques_poids = st.slider(
                "Importance des marques",
                min_value=0,
                max_value=10,
                value=4,
                help="0 = ignoré, 10 = très important"
            )
            marques_obligatoire = st.checkbox("Marques obligatoires")
            st.session_state.config_criteres['marques'] = {
                'valeur': marques_selectionnees,
                'poids': marques_poids if not marques_obligatoire else 10,
                'obligatoire': marques_obligatoire
            }
            
            # Catégories avec importance
            st.markdown("##### 🚗 Catégories")
            categories = st.multiselect(
                "Catégories",
                options=sorted(marques_df['categorie'].unique()),
                default=st.session_state.config_criteres.get('categories', {'valeur': []})['valeur']
            )
            categories_poids = st.slider(
                "Importance des catégories",
                min_value=0,
                max_value=10,
                value=3,
                help="0 = ignoré, 10 = très important"
            )
            categories_obligatoire = st.checkbox("Catégories obligatoires")
            st.session_state.config_criteres['categories'] = {
                'valeur': categories,
                'poids': categories_poids if not categories_obligatoire else 10,
                'obligatoire': categories_obligatoire
            }
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Motorisation")
            
            # Type de motorisation avec importance
            st.markdown("##### ⚡ Type de motorisation")
            motorisations = st.multiselect(
                "Types de motorisation",
                options=["Essence", "Diesel", "Hybride", "Électrique"],
                default=st.session_state.config_criteres.get('motorisations', {'valeur': []})['valeur']
            )
            motorisations_poids = st.slider(
                "Importance de la motorisation",
                min_value=0,
                max_value=10,
                value=4,
                help="0 = ignoré, 10 = très important"
            )
            motorisations_obligatoire = st.checkbox("Motorisation obligatoire")
            st.session_state.config_criteres['motorisations'] = {
                'valeur': motorisations,
                'poids': motorisations_poids if not motorisations_obligatoire else 10,
                'obligatoire': motorisations_obligatoire
            }
            
            # Puissance avec importance
            st.markdown("##### 💪 Puissance")
            col_puiss1, col_puiss2 = st.columns(2)
            with col_puiss1:
                puissance_min, puissance_max = st.slider(
                    "Plage de puissance (ch)",
                    min_value=70,
                    max_value=500,
                    value=(st.session_state.config_criteres.get('puissance_min', {'valeur': 100})['valeur'],
                           st.session_state.config_criteres.get('puissance_max', {'valeur': 300})['valeur'])
                )
            with col_puiss2:
                puissance_min = st.number_input(
                    "Puissance minimum (ch)",
                    min_value=70,
                    max_value=500,
                    value=puissance_min
                )
                puissance_max = st.number_input(
                    "Puissance maximum (ch)",
                    min_value=70,
                    max_value=500,
                    value=puissance_max
                )
            
            col_puiss_imp1, col_puiss_imp2 = st.columns(2)
            with col_puiss_imp1:
                puissance_poids = st.slider(
                    "Importance de la puissance",
                    min_value=0,
                    max_value=10,
                    value=3,
                    help="0 = ignoré, 10 = très important"
                )
            with col_puiss_imp2:
                puissance_poids = st.number_input(
                    "Importance puissance (0-10)",
                    min_value=0,
                    max_value=10,
                    value=puissance_poids
                )
            
            puissance_obligatoire = st.checkbox("Puissance obligatoire")
            st.session_state.config_criteres['puissance_min'] = {
                'valeur': puissance_min,
                'poids': puissance_poids if not puissance_obligatoire else 10,
                'obligatoire': puissance_obligatoire
            }
            st.session_state.config_criteres['puissance_max'] = {
                'valeur': puissance_max,
                'poids': puissance_poids if not puissance_obligatoire else 10,
                'obligatoire': puissance_obligatoire
            }
            
            # Transmission avec importance
            st.markdown("##### 🔄 Transmission")
            transmissions = st.multiselect(
                "Type de transmission",
                options=["Manuelle", "Automatique"],
                default=st.session_state.config_criteres.get('transmissions', {'valeur': []})['valeur']
            )
            transmissions_poids = st.slider(
                "Importance de la transmission",
                min_value=0,
                max_value=10,
                value=3,
                help="0 = ignoré, 10 = très important"
            )
            transmissions_obligatoire = st.checkbox("Transmission obligatoire")
            st.session_state.config_criteres['transmissions'] = {
                'valeur': transmissions,
                'poids': transmissions_poids if not transmissions_obligatoire else 10,
                'obligatoire': transmissions_obligatoire
            }
        
        with col2:
            st.subheader("Consommation et coûts")
            
            # Consommation avec importance
            st.markdown("##### ⛽ Consommation")
            col_conso1, col_conso2 = st.columns(2)
            with col_conso1:
                conso_max = st.slider(
                    "Consommation maximum (L/100km)",
                    min_value=0.0,
                    max_value=20.0,
                    value=float(st.session_state.config_criteres['conso_max']['valeur']),
                    step=0.5
                )
            with col_conso2:
                conso_max = st.number_input(
                    "Consommation max (L/100km)",
                    min_value=0.0,
                    max_value=20.0,
                    value=conso_max,
                    step=0.1
                )
            
            col_conso_imp1, col_conso_imp2 = st.columns(2)
            with col_conso_imp1:
                conso_poids = st.slider(
                    "Importance de la consommation",
                    min_value=0,
                    max_value=10,
                    value=4,
                    help="0 = ignoré, 10 = très important"
                )
            with col_conso_imp2:
                conso_poids = st.number_input(
                    "Importance conso (0-10)",
                    min_value=0,
                    max_value=10,
                    value=conso_poids
                )
            
            conso_obligatoire = st.checkbox("Consommation obligatoire")
            st.session_state.config_criteres['conso_max'] = {
                'valeur': conso_max,
                'poids': conso_poids if not conso_obligatoire else 10,
                'obligatoire': conso_obligatoire
            }
            
            # Coût d'assurance avec importance
            st.markdown("##### 🛡️ Assurance")
            col_assur1, col_assur2 = st.columns(2)
            with col_assur1:
                assurance_max = st.slider(
                    "Coût d'assurance maximum (€/an)",
                    min_value=0,
                    max_value=3000,
                    value=st.session_state.config_criteres['assurance_max']['valeur'],
                    step=100
                )
            with col_assur2:
                assurance_max = st.number_input(
                    "Assurance max (€/an)",
                    min_value=0,
                    max_value=3000,
                    value=assurance_max,
                    step=50
                )
            
            col_assur_imp1, col_assur_imp2 = st.columns(2)
            with col_assur_imp1:
                assurance_poids = st.slider(
                    "Importance de l'assurance",
                    min_value=0,
                    max_value=10,
                    value=3,
                    help="0 = ignoré, 10 = très important"
                )
            with col_assur_imp2:
                assurance_poids = st.number_input(
                    "Importance assurance (0-10)",
                    min_value=0,
                    max_value=10,
                    value=assurance_poids
                )
            
            assurance_obligatoire = st.checkbox("Assurance obligatoire")
            st.session_state.config_criteres['assurance_max'] = {
                'valeur': assurance_max,
                'poids': assurance_poids if not assurance_obligatoire else 10,
                'obligatoire': assurance_obligatoire
            }
    
    with tab3:
        st.subheader("Critères vendeur")
        
        # Type de vendeur avec importance
        st.markdown("##### 👤 Type de vendeur")
        vendeurs = st.multiselect(
            "Type de vendeur",
            options=["Particulier", "Professionnel"],
            default=st.session_state.config_criteres.get('type_vendeur', {'valeur': []})['valeur']
        )
        vendeur_poids = st.slider(
            "Importance du type de vendeur",
            min_value=0,
            max_value=10,
            value=3,
            help="0 = ignoré, 10 = très important"
        )
        vendeur_obligatoire = st.checkbox("Type de vendeur obligatoire")
        st.session_state.config_criteres['type_vendeur'] = {
            'valeur': vendeurs,
            'poids': vendeur_poids if not vendeur_obligatoire else 10,
            'obligatoire': vendeur_obligatoire
        }
        
        # Note vendeur avec importance
        st.markdown("##### ⭐ Note vendeur")
        note_vendeur = st.slider(
            "Note minimale du vendeur",
            min_value=0.0,
            max_value=5.0,
            value=st.session_state.config_criteres.get('note_vendeur', {'valeur': 4.0})['valeur'],
            step=0.5
        )
        note_poids = st.slider(
            "Importance de la note vendeur",
            min_value=0,
            max_value=10,
            value=3,
            help="0 = ignoré, 10 = très important"
        )
        note_obligatoire = st.checkbox("Note vendeur obligatoire")
        st.session_state.config_criteres['note_vendeur'] = {
            'valeur': note_vendeur,
            'poids': note_poids if not note_obligatoire else 10,
            'obligatoire': note_obligatoire
        }
        
        # Distance avec importance
        st.markdown("##### 📍 Distance")
        distance_max = st.number_input(
            "Distance maximale (km)",
            min_value=0,
            value=st.session_state.config_criteres.get('distance_max', {'valeur': 100})['valeur'],
            step=50
        )
        distance_poids = st.slider(
            "Importance de la distance",
            min_value=0,
            max_value=10,
            value=2,
            help="0 = ignoré, 10 = très important"
        )
        distance_obligatoire = st.checkbox("Distance obligatoire")
        st.session_state.config_criteres['distance_max'] = {
            'valeur': distance_max,
            'poids': distance_poids if not distance_obligatoire else 10,
            'obligatoire': distance_obligatoire
        }
    
    with tab4:
        st.subheader("Équipements souhaités")
        
        # Sélection des équipements par catégorie avec importance individuelle
        for categorie in equipements_df['categorie'].unique():
            st.markdown(f"#### {categorie}")
            equips = equipements_df[equipements_df['categorie'] == categorie]['equipement'].tolist()
            
            # Création d'un dictionnaire pour stocker les équipements et leurs poids
            equips_config = {}
            
            for equip in equips:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    selected = st.checkbox(equip, help=equipements_df[equipements_df['equipement'] == equip]['description'].iloc[0])
                with col2:
                    if selected:
                        poids = st.slider(
                            f"Importance {equip}",
                            min_value=0,
                            max_value=10,
                            value=2,
                            help="0 = souhaité, 10 = indispensable",
                            key=f"poids_{categorie}_{equip}"
                        )
                    else:
                        poids = 0
                with col3:
                    if selected:
                        obligatoire = st.checkbox(f"Obligatoire {equip}", key=f"oblig_{categorie}_{equip}")
                    else:
                        obligatoire = False
                
                if selected:
                    equips_config[equip] = {
                        'poids': poids if not obligatoire else 10,
                        'obligatoire': obligatoire
                    }
            
            st.session_state.config_criteres[f'equipements_{categorie.lower()}'] = {
                'valeur': list(equips_config.keys()),
                'poids_individuels': equips_config
            }
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Sauvegarder cette configuration", use_container_width=True):
            if nom_recherche:
                if nom_recherche in recherches:
                    if st.checkbox("Cette recherche existe déjà. Voulez-vous la remplacer ?"):
                        recherches = sauvegarder_recherche(nom_recherche, st.session_state.config_criteres, recherches)
                        st.success(f"✅ Configuration '{nom_recherche}' mise à jour!")
                        st.balloons()
                else:
                    recherches = sauvegarder_recherche(nom_recherche, st.session_state.config_criteres, recherches)
                    st.success(f"✅ Configuration '{nom_recherche}' sauvegardée!")
                    st.balloons()
            else:
                st.error("❌ Veuillez donner un nom à cette configuration")
    
    with col2:
        if st.button("🔄 Réinitialiser", use_container_width=True):
            st.session_state.config_criteres = {
                'budget_min': {'valeur': 5000, 'poids': 5, 'obligatoire': True},
                'budget_max': {'valeur': 20000, 'poids': 5, 'obligatoire': True},
                'annee_min': {'valeur': 2015, 'poids': 3, 'obligatoire': False},
                'annee_max': {'valeur': datetime.now().year, 'poids': 3, 'obligatoire': False},
                'marques': {'valeur': [], 'poids': 4, 'obligatoire': False},
                'categories': {'valeur': [], 'poids': 3, 'obligatoire': False},
                'motorisations': {'valeur': [], 'poids': 4, 'obligatoire': False},
                'puissance_min': {'valeur': 100, 'poids': 3, 'obligatoire': False},
                'puissance_max': {'valeur': 300, 'poids': 3, 'obligatoire': False},
                'transmissions': {'valeur': [], 'poids': 3, 'obligatoire': False},
                'conso_max': {'valeur': 8.0, 'poids': 4, 'obligatoire': False},
                'assurance_max': {'valeur': 1000, 'poids': 3, 'obligatoire': False},
                'type_vendeur': {'valeur': [], 'poids': 3, 'obligatoire': False},
                'note_vendeur': {'valeur': 4.0, 'poids': 3, 'obligatoire': False},
                'distance_max': {'valeur': 100, 'poids': 2, 'obligatoire': False}
            }
            st.success("✅ Configuration réinitialisée aux valeurs par défaut")
            st.rerun() 