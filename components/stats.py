import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def afficher_statistiques(df):
    """
    Affiche les statistiques et graphiques pour les véhicules filtrés.
    """
    if df.empty:
        st.info("Aucune donnée disponible pour les statistiques.")
        return
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Prix moyen",
            f"{df['Prix'].mean():,.0f} €",
            delta=f"{(df['Prix'].mean() - df['Prix'].median()):,.0f} €"
        )
    with col2:
        st.metric(
            "Consommation moyenne",
            f"{df['Consommation'].mean():.1f} L/100km",
            delta=f"{(df['Consommation'].mean() - df['Consommation'].median()):.1f} L"
        )
    with col3:
        st.metric(
            "Fiabilité moyenne",
            f"{df['Fiabilite'].mean():.1f}/10",
            delta=f"{(df['Fiabilite'].mean() - df['Fiabilite'].median()):.1f}"
        )
    with col4:
        st.metric(
            "Score moyen",
            f"{df['Score_Match'].mean():.1f}%",
            delta=f"{(df['Score_Match'].mean() - df['Score_Match'].median()):.1f}%"
        )
    
    # Distribution des prix par marque
    st.subheader("📊 Distribution des prix par marque")
    fig_prix = px.box(
        df,
        x="Marque",
        y="Prix",
        color="Marque",
        title="Distribution des prix par marque",
        labels={"Prix": "Prix (€)", "Marque": ""},
        height=500
    )
    fig_prix.update_layout(showlegend=False)
    st.plotly_chart(fig_prix, use_container_width=True)
    
    # Évolution temporelle des prix
    st.subheader("📈 Évolution des prix selon l'année")
    fig_evolution = px.scatter(
        df,
        x="Annee",
        y="Prix",
        color="Marque",
        size="Fiabilite",
        hover_data=['Modele', 'Consommation', 'Score_Match'],
        title="Évolution des prix selon l'année",
        labels={
            "Prix": "Prix (€)",
            "Annee": "Année",
            "Fiabilite": "Fiabilité"
        },
        height=500
    )
    st.plotly_chart(fig_evolution, use_container_width=True)
    
    # Analyse des scores
    st.subheader("🎯 Analyse des scores de correspondance")
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution des scores
        fig_scores = go.Figure()
        fig_scores.add_trace(go.Histogram(
            x=df['Score_Match'],
            nbinsx=20,
            name="Distribution des scores"
        ))
        fig_scores.update_layout(
            title="Distribution des scores de correspondance",
            xaxis_title="Score (%)",
            yaxis_title="Nombre de véhicules",
            height=400
        )
        st.plotly_chart(fig_scores, use_container_width=True)
    
    with col2:
        # Scores moyens par marque
        scores_marque = df.groupby('Marque')['Score_Match'].mean().sort_values(ascending=True)
        fig_scores_marque = go.Figure()
        fig_scores_marque.add_trace(go.Bar(
            y=scores_marque.index,
            x=scores_marque.values,
            orientation='h',
            name="Score moyen"
        ))
        fig_scores_marque.update_layout(
            title="Scores moyens par marque",
            xaxis_title="Score moyen (%)",
            yaxis_title="",
            height=400
        )
        st.plotly_chart(fig_scores_marque, use_container_width=True)
    
    # Matrice de corrélation
    st.subheader("🔄 Corrélations entre les critères")
    colonnes_correlation = ['Prix', 'Annee', 'Consommation', 'Cout_Assurance', 'Fiabilite', 'Score_Match']
    correlation = df[colonnes_correlation].corr()
    
    fig_correlation = px.imshow(
        correlation,
        labels=dict(color="Corrélation"),
        color_continuous_scale="RdBu",
        title="Matrice de corrélation entre les critères",
        height=500
    )
    fig_correlation.update_layout(
        xaxis_title="",
        yaxis_title=""
    )
    st.plotly_chart(fig_correlation, use_container_width=True)
    
    # Statistiques détaillées
    with st.expander("📋 Statistiques détaillées"):
        stats = df.describe()
        stats.index = ['Nombre', 'Moyenne', 'Écart-type', 'Minimum', '25%', 'Médiane', '75%', 'Maximum']
        st.dataframe(stats.round(2), use_container_width=True)
        
        st.markdown("### 🏆 Top 5 des véhicules")
        top_5 = df.nlargest(5, 'Score_Match')[['Marque', 'Modele', 'Prix', 'Score_Match']]
        st.dataframe(
            top_5.style.format({
                'Prix': '{:,.0f} €',
                'Score_Match': '{:.1f}%'
            }),
            use_container_width=True
        ) 