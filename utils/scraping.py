import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

def extraire_infos_annonce(url):
    """
    Extrait les informations d'une annonce à partir de son URL.
    Supporte actuellement AutoScout24 et LeBonCoin.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        domain = urlparse(url).netloc
        
        if 'autoscout24.fr' in domain:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraction du prix
            prix = soup.find('span', {'class': 'price'})
            prix = int(re.sub(r'[^\d]', '', prix.text)) if prix else 0
            
            # Extraction du titre (marque et modèle)
            titre = soup.find('h1').text.strip()
            marque, modele = titre.split(' ', 1)
            
            # Extraction de l'année
            annee = soup.find('span', {'class': 'year'})
            annee = int(annee.text) if annee else 2000
            
            # Extraction de l'image principale
            image_url = ''
            img = soup.find('img', {'class': 'gallery-picture'})
            if img:
                image_url = img['src']
            
            # Extraction des caractéristiques techniques
            specs = {}
            specs_container = soup.find('div', {'class': 'technical-specifications'})
            if specs_container:
                for item in specs_container.find_all('div', {'class': 'item'}):
                    label = item.find('span', {'class': 'label'})
                    value = item.find('span', {'class': 'value'})
                    if label and value:
                        specs[label.text.strip()] = value.text.strip()
            
            return {
                'prix': prix,
                'marque': marque,
                'modele': modele,
                'annee': annee,
                'image_url': image_url,
                'specs': specs
            }
            
        elif 'leboncoin.fr' in domain:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraction du prix
            prix = soup.find('span', {'class': '_1F5u3'})
            prix = int(re.sub(r'[^\d]', '', prix.text)) if prix else 0
            
            # Extraction du titre
            titre = soup.find('h1', {'class': '_3MDJa'})
            titre = titre.text.strip() if titre else ""
            
            # Tentative d'extraction de la marque et du modèle
            marque = ""
            modele = titre
            marques_communes = ['Peugeot', 'Renault', 'Citroën', 'BMW', 'Audi', 'Mercedes', 'Volkswagen']
            for m in marques_communes:
                if m.lower() in titre.lower():
                    marque = m
                    modele = titre.replace(m, '').strip()
                    break
            
            # Extraction de l'année
            annee_pattern = r'\b(19|20)\d{2}\b'
            annee_match = re.search(annee_pattern, titre)
            annee = int(annee_match.group()) if annee_match else 2000
            
            # Extraction de l'image principale
            image_url = ''
            img = soup.find('img', {'class': '_3GJ1I'})
            if img:
                image_url = img['src']
            
            return {
                'prix': prix,
                'marque': marque,
                'modele': modele,
                'annee': annee,
                'image_url': image_url
            }
            
    except Exception as e:
        print(f"Erreur lors de l'extraction des informations : {str(e)}")
        return None 