def calculer_score_vehicule(vehicule, criteres):
    """
    Calcule le score de correspondance d'un véhicule par rapport aux critères définis.
    Retourne un score entre 0 et 100, ou 0 si un critère obligatoire n'est pas respecté.
    """
    score = 0
    poids_total = sum(critere['poids'] for critere in criteres.values() if isinstance(critere, dict) and 'poids' in critere)
    
    # Vérification des critères obligatoires
    for nom, critere in criteres.items():
        if isinstance(critere, dict) and critere.get('obligatoire', False):
            if nom == 'budget_min' and vehicule['Prix'] < critere['valeur']:
                return 0
            elif nom == 'budget_max' and vehicule['Prix'] > critere['valeur']:
                return 0
            elif nom == 'annee_min' and vehicule['Annee'] < critere['valeur']:
                return 0
            elif nom == 'annee_max' and vehicule['Annee'] > critere['valeur']:
                return 0
            elif nom == 'marques' and critere['valeur'] and vehicule['Marque'] not in critere['valeur']:
                return 0
            elif nom == 'categories' and critere['valeur'] and vehicule.get('Categorie') not in critere['valeur']:
                return 0
            elif nom == 'motorisations' and critere['valeur'] and vehicule.get('Motorisation') not in critere['valeur']:
                return 0
            elif nom == 'puissance_min' and vehicule.get('Puissance', 0) < critere['valeur']:
                return 0
            elif nom == 'puissance_max' and vehicule.get('Puissance', 0) > critere['valeur']:
                return 0
            elif nom == 'transmissions' and critere['valeur'] and vehicule.get('Transmission') not in critere['valeur']:
                return 0
            elif nom == 'conso_max' and vehicule['Consommation'] > critere['valeur']:
                return 0
            elif nom == 'assurance_max' and vehicule['Cout_Assurance'] > critere['valeur']:
                return 0
            elif nom == 'type_vendeur' and critere['valeur'] and vehicule.get('Type_Vendeur') not in critere['valeur']:
                return 0
            elif nom == 'note_vendeur' and vehicule.get('Note_Vendeur', 0) < critere['valeur']:
                return 0
            elif nom == 'distance_max' and vehicule.get('Distance', 0) > critere['valeur']:
                return 0
    
    # Calcul du score pour les critères non obligatoires
    # Budget
    if 'budget_min' in criteres and 'budget_max' in criteres:
        if criteres['budget_min']['valeur'] <= vehicule['Prix'] <= criteres['budget_max']['valeur']:
            score += (criteres['budget_min']['poids'] + criteres['budget_max']['poids']) / 2
        else:
            # Score partiel si proche des limites (tolérance de 20%)
            if vehicule['Prix'] < criteres['budget_min']['valeur']:
                ecart = (criteres['budget_min']['valeur'] - vehicule['Prix']) / criteres['budget_min']['valeur']
                if ecart <= 0.2:
                    score += (criteres['budget_min']['poids'] + criteres['budget_max']['poids']) / 2 * (1 - ecart)
            else:
                ecart = (vehicule['Prix'] - criteres['budget_max']['valeur']) / criteres['budget_max']['valeur']
                if ecart <= 0.2:
                    score += (criteres['budget_min']['poids'] + criteres['budget_max']['poids']) / 2 * (1 - ecart)
    
    # Année
    if 'annee_min' in criteres and 'annee_max' in criteres:
        if criteres['annee_min']['valeur'] <= vehicule['Annee'] <= criteres['annee_max']['valeur']:
            score += (criteres['annee_min']['poids'] + criteres['annee_max']['poids']) / 2
        else:
            # Score partiel si proche des limites (tolérance de 2 ans)
            if vehicule['Annee'] < criteres['annee_min']['valeur']:
                diff = criteres['annee_min']['valeur'] - vehicule['Annee']
                if diff <= 2:
                    score += (criteres['annee_min']['poids'] + criteres['annee_max']['poids']) / 2 * (1 - diff/2)
            else:
                diff = vehicule['Annee'] - criteres['annee_max']['valeur']
                if diff <= 2:
                    score += (criteres['annee_min']['poids'] + criteres['annee_max']['poids']) / 2 * (1 - diff/2)
    
    # Marques
    if 'marques' in criteres and criteres['marques']['valeur']:
        if vehicule['Marque'] in criteres['marques']['valeur']:
            score += criteres['marques']['poids']
    
    # Catégories
    if 'categories' in criteres and criteres['categories']['valeur']:
        if vehicule.get('Categorie') in criteres['categories']['valeur']:
            score += criteres['categories']['poids']
    
    # Motorisation
    if 'motorisations' in criteres and criteres['motorisations']['valeur']:
        if vehicule.get('Motorisation') in criteres['motorisations']['valeur']:
            score += criteres['motorisations']['poids']
    
    # Puissance
    if 'puissance_min' in criteres and 'puissance_max' in criteres and vehicule.get('Puissance'):
        if criteres['puissance_min']['valeur'] <= vehicule['Puissance'] <= criteres['puissance_max']['valeur']:
            score += (criteres['puissance_min']['poids'] + criteres['puissance_max']['poids']) / 2
    
    # Transmission
    if 'transmissions' in criteres and criteres['transmissions']['valeur']:
        if vehicule.get('Transmission') in criteres['transmissions']['valeur']:
            score += criteres['transmissions']['poids']
    
    # Consommation
    if 'conso_max' in criteres:
        if vehicule['Consommation'] <= criteres['conso_max']['valeur']:
            score += criteres['conso_max']['poids']
        else:
            # Score partiel si proche de la consommation max (tolérance de 20%)
            depassement = (vehicule['Consommation'] - criteres['conso_max']['valeur']) / criteres['conso_max']['valeur']
            if depassement <= 0.2:
                score += criteres['conso_max']['poids'] * (1 - depassement)
    
    # Assurance
    if 'assurance_max' in criteres:
        if vehicule['Cout_Assurance'] <= criteres['assurance_max']['valeur']:
            score += criteres['assurance_max']['poids']
        else:
            # Score partiel si proche du coût max (tolérance de 20%)
            depassement = (vehicule['Cout_Assurance'] - criteres['assurance_max']['valeur']) / criteres['assurance_max']['valeur']
            if depassement <= 0.2:
                score += criteres['assurance_max']['poids'] * (1 - depassement)
    
    # Type de vendeur
    if 'type_vendeur' in criteres and criteres['type_vendeur']['valeur']:
        if vehicule.get('Type_Vendeur') in criteres['type_vendeur']['valeur']:
            score += criteres['type_vendeur']['poids']
    
    # Note vendeur
    if 'note_vendeur' in criteres and vehicule.get('Note_Vendeur'):
        if vehicule['Note_Vendeur'] >= criteres['note_vendeur']['valeur']:
            score += criteres['note_vendeur']['poids']
        else:
            # Score partiel si proche de la note minimale (tolérance de 1 point)
            diff = criteres['note_vendeur']['valeur'] - vehicule['Note_Vendeur']
            if diff <= 1:
                score += criteres['note_vendeur']['poids'] * (1 - diff)
    
    # Distance
    if 'distance_max' in criteres and vehicule.get('Distance'):
        if vehicule['Distance'] <= criteres['distance_max']['valeur']:
            score += criteres['distance_max']['poids']
        else:
            # Score partiel si proche de la distance max (tolérance de 20%)
            depassement = (vehicule['Distance'] - criteres['distance_max']['valeur']) / criteres['distance_max']['valeur']
            if depassement <= 0.2:
                score += criteres['distance_max']['poids'] * (1 - depassement)
    
    # Équipements par catégorie avec poids individuels
    equips_vehicule = set(map(str.strip, vehicule['Equipements'].lower().split(',')))
    for categorie in ['securite', 'confort', 'multimedia', 'exterieur', 'pratique']:
        critere_key = f'equipements_{categorie}'
        if critere_key in criteres and criteres[critere_key]['valeur']:
            score_equipements = 0
            poids_total_equipements = 0
            
            # Vérification des équipements obligatoires
            for equip, config in criteres[critere_key]['poids_individuels'].items():
                if config.get('obligatoire', False) and equip.lower() not in equips_vehicule:
                    return 0
            
            # Calcul du score pour les équipements non obligatoires
            for equip, config in criteres[critere_key]['poids_individuels'].items():
                if not config.get('obligatoire', False):
                    poids = config['poids']
                    poids_total_equipements += poids
                    if equip.lower() in equips_vehicule:
                        score_equipements += poids
            
            if poids_total_equipements > 0:
                score += (score_equipements / poids_total_equipements) * 2  # Poids de base de 2 pour les équipements
    
    # Normalisation du score sur 100
    score_final = (score / poids_total) * 100
    
    # Bonus pour les véhicules "coup de cœur"
    if vehicule.get('Coup_de_Coeur', False):
        score_final = min(100, score_final * 1.1)  # Bonus de 10%, plafonné à 100
    
    return round(score_final, 1) 