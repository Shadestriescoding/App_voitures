# 🚗 Gestionnaire de Véhicules

Application Streamlit permettant de gérer et visualiser une collection de véhicules, avec stockage des données dans un fichier CSV.

## ✨ Fonctionnalités

- **Saisie des données** via un formulaire intuitif
  - Marque et modèle du véhicule
  - Année de mise en circulation (1998-2024)
  - Prix et coût d'assurance
  - Consommation moyenne
  - Équipements
  - Note de fiabilité

- **Visualisation interactive**
  - Tableau filtrable par marque et année
  - Graphiques dynamiques avec Plotly
  - Statistiques rapides (moyennes)

- **Stockage persistant**
  - Sauvegarde automatique dans `data.csv`
  - Format compatible Excel/LibreOffice

## 🚀 Installation

1. Clonez ce dépôt :
```bash
git clone https://github.com/Shadestriescoding/App_voitures.git
cd App_voitures
```

2. Créez un environnement virtuel (recommandé) :
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Lancez l'application :
```bash
streamlit run streamlit_app.py
```

L'application sera accessible à l'adresse : http://localhost:8501

## 📊 Utilisation

1. **Ajout d'un véhicule**
   - Remplissez le formulaire à gauche
   - Cliquez sur "Ajouter ce véhicule"
   - Une confirmation s'affiche

2. **Consultation des données**
   - Utilisez les filtres du tableau
   - Explorez les différents graphiques
   - Consultez les statistiques

## 🌍 Déploiement sur Streamlit Cloud

1. Créez un compte sur [Streamlit Cloud](https://streamlit.io/cloud)
2. Connectez votre compte GitHub
3. Sélectionnez ce dépôt pour le déploiement
4. L'application sera accessible publiquement à l'adresse : https://appvoitures-aznirqvwpszinfp7vtf9vv.streamlit.app

## 📁 Structure du Projet

```
App_voitures/
├── streamlit_app.py  # Application Streamlit
├── data.csv          # Base de données
├── requirements.txt  # Dépendances
└── README.md        # Documentation
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Ouvrir une issue pour signaler un bug
- Proposer une nouvelle fonctionnalité
- Soumettre une pull request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails. 