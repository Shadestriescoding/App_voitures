import pandas as pd
import os
from datetime import datetime

def charger_donnees():
    """Charge les données des véhicules depuis le fichier CSV."""
    if os.path.exists('data.csv'):
        return pd.read_csv('data.csv')
    return pd.DataFrame(columns=[
        'Marque', 'Modele', 'Annee', 'Prix', 'Consommation',
        'Cout_Assurance', 'Equipements', 'Fiabilite',
        'Date_Ajout', 'Lien_Annonce', 'Image_URL',
        'Status', 'Selection_Franck', 'Notes',
        'Notes_Detaillees', 'Red_Flags', 'Tags',
        'Points_Forts', 'Points_Faibles', 'Score_Match',
        'Coup_de_Coeur'
    ])

def charger_references():
    """Charge les données de référence (marques et équipements)."""
    marques_df = pd.read_csv('data/marques.csv')
    equipements_df = pd.read_csv('data/equipements.csv')
    return marques_df, equipements_df

def sauvegarder_donnees(df):
    """Sauvegarde les données des véhicules dans le fichier CSV."""
    df.to_csv('data.csv', index=False)

def ajouter_vehicule(df, vehicule_data):
    """Ajoute un nouveau véhicule à la base de données."""
    nouveau_vehicule = {
        'Marque': vehicule_data['marque'],
        'Modele': vehicule_data['modele'],
        'Annee': vehicule_data['annee'],
        'Prix': vehicule_data['prix'],
        'Consommation': vehicule_data['consommation'],
        'Cout_Assurance': vehicule_data['cout_assurance'],
        'Equipements': ", ".join(vehicule_data['equipements']),
        'Fiabilite': vehicule_data['fiabilite'],
        'Date_Ajout': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Lien_Annonce': vehicule_data.get('lien_annonce', ""),
        'Image_URL': vehicule_data.get('image_url', ""),
        'Status': "En attente",
        'Selection_Franck': False,
        'Notes': vehicule_data.get('notes', ""),
        'Notes_Detaillees': "",
        'Red_Flags': "",
        'Tags': "",
        'Points_Forts': "",
        'Points_Faibles': "",
        'Score_Match': 0,
        'Coup_de_Coeur': False
    }
    return pd.concat([df, pd.DataFrame([nouveau_vehicule])], ignore_index=True)

def filtrer_vehicules(df, filtres):
    """Filtre les véhicules selon les critères spécifiés."""
    df_filtered = df.copy()
    
    if filtres.get('recherche_active') != "Toutes":
        df_filtered = df_filtered[df_filtered['Notes'] == filtres['recherche_active']]
    
    if filtres.get('search'):
        search = filtres['search'].lower()
        df_filtered = df_filtered[
            df_filtered['Marque'].str.lower().str.contains(search) |
            df_filtered['Modele'].str.lower().str.contains(search)
        ]
    
    if filtres.get('status'):
        df_filtered = df_filtered[df_filtered['Status'].isin(filtres['status'])]
    
    if filtres.get('marques'):
        df_filtered = df_filtered[df_filtered['Marque'].isin(filtres['marques'])]
    
    if filtres.get('prix_range'):
        df_filtered = df_filtered[
            (df_filtered['Prix'] >= filtres['prix_range'][0]) &
            (df_filtered['Prix'] <= filtres['prix_range'][1])
        ]
    
    return df_filtered 