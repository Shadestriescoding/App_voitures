import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import json

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
            
            # Extraction de la motorisation
            motorisation = None
            if 'Carburant' in specs:
                motorisation = specs['Carburant']
            elif 'Type de carburant' in specs:
                motorisation = specs['Type de carburant']
            
            # Extraction de la puissance
            puissance = None
            if 'Puissance' in specs:
                puissance_match = re.search(r'(\d+)\s*ch', specs['Puissance'])
                if puissance_match:
                    puissance = int(puissance_match.group(1))
            
            # Extraction de la transmission
            transmission = None
            if 'Boîte de vitesses' in specs:
                transmission = 'Automatique' if 'automatique' in specs['Boîte de vitesses'].lower() else 'Manuelle'
            
            # Extraction de la catégorie
            categorie = None
            if 'Type de véhicule' in specs:
                categorie = specs['Type de véhicule']
            
            # Informations sur le vendeur
            type_vendeur = 'Professionnel' if soup.find('div', {'class': 'dealer-info'}) else 'Particulier'
            note_vendeur = 0
            note_element = soup.find('div', {'class': 'rating'})
            if note_element:
                note_match = re.search(r'(\d+(?:\.\d+)?)', note_element.text)
                if note_match:
                    note_vendeur = float(note_match.group(1))
            
            # Extraction de la distance
            distance = None
            localisation = soup.find('div', {'class': 'location'})
            if localisation:
                distance_match = re.search(r'(\d+)\s*km', localisation.text)
                if distance_match:
                    distance = int(distance_match.group(1))
            
            # Extraction des équipements
            equipements = []
            equip_container = soup.find('div', {'class': 'equipment'})
            if equip_container:
                for equip in equip_container.find_all('li'):
                    equipements.append(equip.text.strip())
            
            return {
                'prix': prix,
                'marque': marque,
                'modele': modele,
                'annee': annee,
                'image_url': image_url,
                'motorisation': motorisation,
                'puissance': puissance,
                'transmission': transmission,
                'categorie': categorie,
                'type_vendeur': type_vendeur,
                'note_vendeur': note_vendeur,
                'distance': distance,
                'equipements': ', '.join(equipements),
                'specs': specs,
                'url': url
            }
            
        elif 'leboncoin.fr' in domain:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraction du prix
            prix = soup.find('span', {'class': '_1F5u3'})
            prix = int(re.sub(r'[^\d]', '', prix.text)) if prix else 0
            
            # Extraction du titre et des informations
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
            
            # Extraction des caractéristiques depuis le JSON-LD
            script = soup.find('script', {'type': 'application/ld+json'})
            specs = {}
            if script:
                try:
                    data = json.loads(script.string)
                    if 'vehicle' in data:
                        specs = data['vehicle']
                except:
                    pass
            
            # Extraction de la motorisation
            motorisation = None
            if 'fuelType' in specs:
                motorisation = specs['fuelType']
            
            # Extraction de la puissance
            puissance = None
            if 'enginePower' in specs:
                puissance = int(specs['enginePower'])
            
            # Extraction de la transmission
            transmission = None
            if 'transmissionType' in specs:
                transmission = 'Automatique' if 'auto' in specs['transmissionType'].lower() else 'Manuelle'
            
            # Extraction de la catégorie
            categorie = None
            if 'bodyType' in specs:
                categorie = specs['bodyType']
            
            # Informations sur le vendeur
            type_vendeur = 'Professionnel' if soup.find('div', {'class': 'shopLogo'}) else 'Particulier'
            note_vendeur = 0
            note_element = soup.find('div', {'class': 'sellerRating'})
            if note_element:
                note_match = re.search(r'(\d+(?:\.\d+)?)', note_element.text)
                if note_match:
                    note_vendeur = float(note_match.group(1))
            
            # Extraction de la distance
            distance = None
            localisation = soup.find('div', {'class': '_1yzJv'})
            if localisation:
                distance_match = re.search(r'(\d+)\s*km', localisation.text)
                if distance_match:
                    distance = int(distance_match.group(1))
            
            # Extraction des équipements
            equipements = []
            equip_container = soup.find('div', {'class': '_3eNLO'})
            if equip_container:
                for equip in equip_container.find_all('div', {'class': '_3Jxf3'}):
                    equipements.append(equip.text.strip())
            
            return {
                'prix': prix,
                'marque': marque,
                'modele': modele,
                'annee': annee,
                'image_url': image_url,
                'motorisation': motorisation,
                'puissance': puissance,
                'transmission': transmission,
                'categorie': categorie,
                'type_vendeur': type_vendeur,
                'note_vendeur': note_vendeur,
                'distance': distance,
                'equipements': ', '.join(equipements),
                'specs': specs,
                'url': url
            }
            
    except Exception as e:
        print(f"Erreur lors de l'extraction des informations : {str(e)}")
        return None 