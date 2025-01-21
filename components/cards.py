import streamlit as st

def afficher_carte_vehicule(vehicule, idx, df, sauvegarder_donnees):
    """
    Affiche une carte détaillée pour un véhicule.
    """
    # Détermination de la classe CSS en fonction du score
    card_class = "car-card premium-card" if vehicule['Score_Match'] >= 80 else "car-card"
    
    # Construction du HTML pour la carte
    html = f"""
    <div class="{card_class}">
        <div class="badge-container">
            <div class="match-badge">Match {vehicule['Score_Match']:.0f}%</div>
            {"<div class='favorite-badge'>❤️ Coup de cœur</div>" if vehicule.get('Coup_de_Coeur', False) else ""}
        </div>
        
        <h3 style="font-size: 1.4em; margin-bottom: 1rem;">{vehicule['Marque']} {vehicule['Modele']}</h3>
        
        <div class="car-info">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 1.1em;">Année {vehicule['Annee']}</span>
                <span class="car-price">{vehicule['Prix']:,.0f} €</span>
            </div>
            
            <div class="car-stats">
                <span title="Fiabilité">🔋 {vehicule['Fiabilite']}/10</span>
                <span title="Consommation">⛽ {vehicule['Consommation']}L/100km</span>
                <span title="Assurance">🛡️ {vehicule['Cout_Assurance']}€/an</span>
            </div>
        </div>
    """
    
    # Ajout des points forts/faibles s'ils existent
    if vehicule.get('Points_Forts') or vehicule.get('Points_Faibles'):
        html += '<div class="points-container">'
        if vehicule.get('Points_Forts'):
            points = [p.strip() for p in vehicule['Points_Forts'].split('\n') if p.strip()][:2]
            if points:
                html += '<div class="points-forts">'
                for point in points:
                    html += f'<div>✓ {point}</div>'
                html += '</div>'
        
        if vehicule.get('Points_Faibles'):
            points = [p.strip() for p in vehicule['Points_Faibles'].split('\n') if p.strip()][:2]
            if points:
                html += '<div class="points-faibles">'
                for point in points:
                    html += f'<div>✗ {point}</div>'
                html += '</div>'
        html += '</div>'
    
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
    
    # Affichage de l'image si disponible
    if vehicule['Image_URL']:
        st.image(vehicule['Image_URL'], use_column_width=True)
    
    # Boutons d'action
    col1, col2, col3 = st.columns(3)
    with col1:
        if vehicule['Lien_Annonce']:
            st.markdown(f"<a href='{vehicule['Lien_Annonce']}' target='_blank' class='action-button'>🔗 Annonce</a>", unsafe_allow_html=True)
    with col2:
        if st.button("📊 Détails", key=f"details_{idx}"):
            st.session_state.page = "details"
            st.session_state.selected_car = idx
    with col3:
        if st.button("❤️", key=f"favorite_{idx}"):
            df.at[idx, 'Coup_de_Coeur'] = not df.at[idx, 'Coup_de_Coeur']
            sauvegarder_donnees(df)
            st.rerun()

def afficher_liste_vehicule(vehicule, idx, df, sauvegarder_donnees):
    """
    Affiche un véhicule au format liste.
    """
    st.markdown(f"""
    <div class="car-card" style="display: flex; gap: 2rem; align-items: center;">
        <div style="flex: 1;">
            <h3>{vehicule['Marque']} {vehicule['Modele']} ({vehicule['Annee']})</h3>
            <div class="car-stats">
                <span>🔋 {vehicule['Fiabilite']}/10</span>
                <span>⛽ {vehicule['Consommation']}L/100km</span>
                <span>💰 {vehicule['Prix']:,.0f} €</span>
            </div>
        </div>
        <div class="action-buttons" style="flex: 0 0 auto;">
            <a href="{vehicule['Lien_Annonce']}" target="_blank" class="action-button">🔗</a>
            <button onclick="details_{idx}()" class="action-button">📊</button>
            <button onclick="favorite_{idx}()" class="action-button">❤️</button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Gestion des clics sur les boutons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Détails", key=f"details_list_{idx}"):
            st.session_state.page = "details"
            st.session_state.selected_car = idx
    with col2:
        if st.button("❤️", key=f"favorite_list_{idx}"):
            df.at[idx, 'Coup_de_Coeur'] = not df.at[idx, 'Coup_de_Coeur']
            sauvegarder_donnees(df)
            st.rerun() 