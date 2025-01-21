def calculer_score_vehicule(vehicule, criteres):
    """
    Calcule le score de correspondance d'un véhicule par rapport aux critères définis.
    Retourne un score entre 0 et 100.
    """
    score = 0
    poids_total = sum(critere['poids'] for critere in criteres.values())
    
    for nom, critere in criteres.items():
        if nom == 'budget':
            if vehicule['Prix'] <= critere['valeur']:
                score += critere['poids']
            else:
                # Score partiel si proche du budget (tolérance de 20%)
                depassement = (vehicule['Prix'] - critere['valeur']) / critere['valeur']
                if depassement <= 0.2:
                    score += critere['poids'] * (1 - depassement)
        
        elif nom == 'annee_min':
            if vehicule['Annee'] >= critere['valeur']:
                score += critere['poids']
            else:
                # Score partiel si proche de l'année minimale (tolérance de 2 ans)
                diff_annees = critere['valeur'] - vehicule['Annee']
                if diff_annees <= 2:
                    score += critere['poids'] * (1 - diff_annees/2)
        
        elif nom == 'conso_max':
            if vehicule['Consommation'] <= critere['valeur']:
                score += critere['poids']
            else:
                # Score partiel si proche de la consommation max (tolérance de 20%)
                depassement = (vehicule['Consommation'] - critere['valeur']) / critere['valeur']
                if depassement <= 0.2:
                    score += critere['poids'] * (1 - depassement)
        
        elif nom == 'fiabilite_min':
            if vehicule['Fiabilite'] >= critere['valeur']:
                score += critere['poids']
            else:
                # Score partiel si proche de la fiabilité minimale (tolérance de 2 points)
                diff = critere['valeur'] - vehicule['Fiabilite']
                if diff <= 2:
                    score += critere['poids'] * (1 - diff/2)
        
        elif nom == 'assurance_max':
            if vehicule['Cout_Assurance'] <= critere['valeur']:
                score += critere['poids']
            else:
                # Score partiel si proche du coût max (tolérance de 20%)
                depassement = (vehicule['Cout_Assurance'] - critere['valeur']) / critere['valeur']
                if depassement <= 0.2:
                    score += critere['poids'] * (1 - depassement)
        
        elif nom == 'equipements':
            if critere['valeur']:  # Si des équipements sont spécifiés
                equips_vehicule = set(map(str.strip, vehicule['Equipements'].lower().split(',')))
                equips_souhaites = set(map(str.strip, critere['valeur'].lower().split(',')))
                if equips_souhaites:
                    # Calcul du ratio d'équipements correspondants
                    match_ratio = len(equips_vehicule.intersection(equips_souhaites)) / len(equips_souhaites)
                    score += critere['poids'] * match_ratio
            else:
                # Si aucun équipement n'est spécifié, on accorde le score complet
                score += critere['poids']
    
    # Normalisation du score sur 100
    score_final = (score / poids_total) * 100
    
    # Bonus pour les véhicules "coup de cœur"
    if vehicule.get('Coup_de_Coeur', False):
        score_final = min(100, score_final * 1.1)  # Bonus de 10%, plafonné à 100
    
    return round(score_final, 1) 