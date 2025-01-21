# 🚗 Gestionnaire de Véhicules

Une application web moderne pour gérer et suivre vos recherches de véhicules, développée avec Streamlit.

## 🌟 Fonctionnalités

- **Galerie de véhicules**
  - Vue en grille ou en liste
  - Tri par différents critères
  - Filtres avancés
  - Badges de score de correspondance
  - Marquage des coups de cœur

- **Ajout de véhicules**
  - Formulaire complet
  - Import automatique depuis AutoScout24
  - Gestion des équipements
  - Notes et commentaires

- **Système de scoring**
  - Calcul automatique des scores de correspondance
  - Critères personnalisables
  - Pondération des critères
  - Bonus pour les coups de cœur

- **Statistiques**
  - Graphiques interactifs
  - Analyse des prix
  - Distribution des scores
  - Corrélations entre critères

- **Export et partage**
  - Génération de fiches PDF
  - Partage de configurations
  - Sauvegarde des recherches

## 🚀 Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/votre-username/gestionnaire-vehicules.git
cd gestionnaire-vehicules
```

2. Créez un environnement virtuel (recommandé) :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Lancez l'application :
```bash
streamlit run streamlit_app.py
```

## 📁 Structure du projet

```
gestionnaire-vehicules/
├── streamlit_app.py      # Point d'entrée de l'application
├── requirements.txt      # Dépendances du projet
├── README.md            # Documentation
├── data/               # Données de référence
│   ├── marques.csv     # Base de données des marques et modèles
│   └── equipements.csv # Liste des équipements possibles
├── utils/              # Utilitaires
│   ├── data.py        # Gestion des données
│   ├── scraping.py    # Extraction d'informations
│   └── scoring.py     # Calcul des scores
└── components/         # Composants de l'interface
    ├── cards.py       # Affichage des cartes véhicules
    ├── forms.py       # Formulaires
    ├── stats.py       # Statistiques et graphiques
    └── details.py     # Page de détails
```

## 🔧 Configuration

- Les critères de recherche sont personnalisables dans l'interface
- Les données sont sauvegardées localement dans `data.csv`
- Les références (marques, modèles, équipements) sont dans le dossier `data/`

## 📊 Données de référence

- `marques.csv` : Base de données des marques et modèles de véhicules
- `equipements.csv` : Liste des équipements possibles avec descriptions

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- [Streamlit](https://streamlit.io/) pour le framework
- [Plotly](https://plotly.com/) pour les graphiques
- [AutoScout24](https://www.autoscout24.fr/) pour les données d'annonces 