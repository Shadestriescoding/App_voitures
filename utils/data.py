import pandas as pd
import os
from datetime import datetime
import json

def charger_donnees():
    """
    Charge les données des véhicules et des recherches depuis les fichiers JSON.
    """
    # Création des dossiers si nécessaire
    os.makedirs('data/saved', exist_ok=True)
    
    # Chargement des véhicules
    try:
        with open('data/saved/vehicules.json', 'r', encoding='utf-8') as f:
            vehicules = json.load(f)
            df = pd.DataFrame(vehicules)
    except (FileNotFoundError, json.JSONDecodeError):
        df = pd.DataFrame(columns=[
            'Prix', 'Marque', 'Modele', 'Annee', 'Image_URL', 'Motorisation',
            'Puissance', 'Transmission', 'Categorie', 'Type_Vendeur', 'Note_Vendeur',
            'Distance', 'Equipements', 'URL', 'Date_Ajout', 'Status', 'Selection_Franck',
            'Points_Forts', 'Points_Faibles', 'Red_Flags', 'Tags', 'Notes', 'Score_Match',
            'Coup_de_Coeur'
        ])
        
    # Initialisation de la colonne Score_Match si elle n'existe pas
    if 'Score_Match' not in df.columns:
        df['Score_Match'] = 0.0
    
    # Chargement des recherches
    try:
        with open('data/saved/recherches.json', 'r', encoding='utf-8') as f:
            recherches = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        recherches = {}
    
    return df, recherches

def charger_references():
    """
    Charge les données de référence depuis les fichiers CSV.
    """
    marques_df = pd.read_csv('data/marques.csv')
    equipements_df = pd.read_csv('data/equipements.csv')
    return marques_df, equipements_df

def sauvegarder_donnees(df, recherches=None):
    """
    Sauvegarde les données des véhicules et des recherches dans les fichiers JSON.
    """
    # Création du dossier si nécessaire
    os.makedirs('data/saved', exist_ok=True)
    
    # Sauvegarde des véhicules
    vehicules = df.to_dict('records')
    with open('data/saved/vehicules.json', 'w', encoding='utf-8') as f:
        json.dump(vehicules, f, ensure_ascii=False, indent=2)
    
    # Sauvegarde des recherches si fournies
    if recherches is not None:
        with open('data/saved/recherches.json', 'w', encoding='utf-8') as f:
            json.dump(recherches, f, ensure_ascii=False, indent=2)

def ajouter_vehicule(df, infos_vehicule):
    """
    Ajoute un nouveau véhicule au DataFrame et sauvegarde les données.
    """
    # Ajout des champs supplémentaires
    infos_vehicule.update({
        'Date_Ajout': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Status': 'Nouveau',
        'Selection_Franck': False,
        'Points_Forts': '',
        'Points_Faibles': '',
        'Red_Flags': '',
        'Tags': '',
        'Notes': ''
    })
    
    # Conversion en DataFrame d'une seule ligne
    nouvelle_ligne = pd.DataFrame([infos_vehicule])
    
    # Concaténation avec le DataFrame existant
    df_maj = pd.concat([df, nouvelle_ligne], ignore_index=True)
    
    # Sauvegarde des données
    sauvegarder_donnees(df_maj)
    
    return df_maj

def sauvegarder_recherche(nom, criteres, recherches):
    """
    Sauvegarde une nouvelle recherche avec ses critères.
    """
    recherches[nom] = {
        'criteres': criteres,
        'date_creation': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'vehicules_associes': []
    }
    
    # Sauvegarde dans le fichier JSON
    with open('data/saved/recherches.json', 'w', encoding='utf-8') as f:
        json.dump(recherches, f, ensure_ascii=False, indent=2)
    
    return recherches

def associer_vehicule_recherche(nom_recherche, index_vehicule, recherches):
    """
    Associe un véhicule à une recherche existante.
    """
    if nom_recherche in recherches:
        if index_vehicule not in recherches[nom_recherche]['vehicules_associes']:
            recherches[nom_recherche]['vehicules_associes'].append(index_vehicule)
            
            # Sauvegarde dans le fichier JSON
            with open('data/saved/recherches.json', 'w', encoding='utf-8') as f:
                json.dump(recherches, f, ensure_ascii=False, indent=2)
    
    return recherches

def dissocier_vehicule_recherche(nom_recherche, index_vehicule, recherches):
    """
    Retire un véhicule d'une recherche existante.
    """
    if nom_recherche in recherches:
        if index_vehicule in recherches[nom_recherche]['vehicules_associes']:
            recherches[nom_recherche]['vehicules_associes'].remove(index_vehicule)
            
            # Sauvegarde dans le fichier JSON
            with open('data/saved/recherches.json', 'w', encoding='utf-8') as f:
                json.dump(recherches, f, ensure_ascii=False, indent=2)
    
    return recherches

def mettre_a_jour_vehicule(df, index, updates):
    """
    Met à jour les informations d'un véhicule existant.
    """
    for key, value in updates.items():
        df.at[index, key] = value
    
    # Sauvegarde des données
    sauvegarder_donnees(df)
    
    return df

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