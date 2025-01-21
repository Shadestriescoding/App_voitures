import streamlit as st
from utils.data import charger_donnees, charger_references, sauvegarder_donnees, filtrer_vehicules
from utils.scraping import extraire_infos_annonce
from utils.scoring import calculer_score_vehicule
from components.cards import afficher_carte_vehicule, afficher_liste_vehicule
from components.forms import afficher_formulaire_ajout, afficher_formulaire_config
from components.stats import afficher_statistiques
from components.details import afficher_details_vehicule

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

# Initialisation des variables de session
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

# Configuration des critères par défaut
if 'config_criteres' not in st.session_state:
    st.session_state.config_criteres = {
        'budget': {'valeur': 15000, 'poids': 5},
        'annee_min': {'valeur': 2000, 'poids': 3},
        'conso_max': {'valeur': 10.0, 'poids': 4},
        'fiabilite_min': {'valeur': 7, 'poids': 4},
        'assurance_max': {'valeur': 1000, 'poids': 3},
        'equipements': {'valeur': '', 'poids': 2}
    }

# Chargement des données
df, recherches = charger_donnees()
marques_df, equipements_df = charger_references()

# Barre latérale
with st.sidebar:
    st.title("🚗 Navigation")
    
    # Recherches validées
    if st.session_state.recherches_validees:
        st.subheader("📌 Recherches validées")
        for nom_recherche, config in st.session_state.recherches_validees.items():
            if st.button(f"🎯 {nom_recherche}", key=f"recherche_{nom_recherche}"):
                st.session_state.config_criteres = config
                st.success(f"Configuration '{nom_recherche}' chargée!")
                st.rerun()
        st.markdown("---")
    
    # Sélection de la recherche active
    recherches_keys = list(recherches.keys())
    st.session_state.recherche_active = st.selectbox(
        "Recherche active",
        ["Toutes les annonces"] + recherches_keys,
        index=0
    )
    
    # Barre de recherche
    search = st.text_input(
        "🔍 Rechercher un modèle",
        value=st.session_state.search_query,
        help="Ex: BMW E46, Mercedes C200..."
    )
    
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
    
    # Filtres de prix
    min_prix = int(df['Prix'].min()) if not df.empty else 0
    max_prix = int(df['Prix'].max()) if not df.empty else 100000
    prix_range = st.slider(
        "Prix (€)",
        min_value=min_prix,
        max_value=max_prix,
        value=(min_prix, max_prix)
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
filtres = {
    'recherche_active': st.session_state.recherche_active,
    'search': search,
    'status': status,
    'marques': marques,
    'prix_range': prix_range
}
df_filtered = filtrer_vehicules(df, filtres)

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
                afficher_carte_vehicule(row, idx, df, sauvegarder_donnees)
    else:
        for idx, row in df_filtered.iterrows():
            afficher_liste_vehicule(row, idx, df, sauvegarder_donnees)

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
    
    df = afficher_formulaire_ajout(df, marques_df, equipements_df, infos_annonce)

elif st.session_state.page == "stats":
    st.title("📊 Statistiques")
    afficher_statistiques(df_filtered)

elif st.session_state.page == "config":
    afficher_formulaire_config(st.session_state.recherches_validees)

elif st.session_state.page == "details" and st.session_state.selected_car is not None:
    afficher_details_vehicule(df_filtered.iloc[st.session_state.selected_car], st.session_state.selected_car, df)

# Affichage de la recherche active
if st.session_state.recherche_active != "Toutes les annonces":
    st.markdown(f"""
    <div class="search-active">
        <h3>🎯 Recherche active : {st.session_state.recherche_active}</h3>
        <p>Affichage des véhicules correspondant à cette recherche</p>
    </div>
    """, unsafe_allow_html=True) 