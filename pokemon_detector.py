import easyocr
import cv2
from rapidfuzz import process, fuzz
from pokedex import pokedex1  # liste des noms de Pokémon (str)
import numpy as np

def calculate_text_size(bbox):
    """Calcule la taille approximative du texte basée sur la bounding box"""
    # bbox est un array de 4 points [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    points = np.array(bbox)
    
    # Calcul de la largeur et hauteur
    width = np.max(points[:, 0]) - np.min(points[:, 0])
    height = np.max(points[:, 1]) - np.min(points[:, 1])
    
    # Aire comme proxy de la taille du texte
    area = width * height
    return area, width, height

def detect_pokemon_name(image_path, lang='en', similarity_threshold=72, size_tolerance=0.3, verbose=False):
    """
    Détecte le nom de Pokémon en se concentrant sur les textes de taille similaire
    
    Args:
        image_path: Chemin vers l'image
        lang: Langue pour l'OCR ('en', 'fr', etc.)
        similarity_threshold: Seuil de similitude minimum
        size_tolerance: Tolérance pour la taille (0.3 = ±30% de la taille de référence)
        verbose: Si True, affiche les détails du processus
    
    Returns:
        Liste des noms de Pokémon détectés ou None si aucun
    """
    image = cv2.imread(image_path)
    if image is None:
        if verbose:
            print(f"❌ Impossible de charger l'image : {image_path}")
        return None
    
    h, w, _ = image.shape
    final_result = None
    
    reader = easyocr.Reader([lang], gpu=False)
    results = reader.readtext(image)
    
    # Première passe : analyser tous les textes et leurs tailles
    text_data = []
    for result in results:
        bbox, text, confidence = result
        cleaned_text = ''.join([c for c in text if c.isalpha()])
        
        if not cleaned_text:
            continue
            
        area, width, height = calculate_text_size(bbox)
        text_data.append({
            'bbox': bbox,
            'text': text,
            'cleaned_text': cleaned_text,
            'confidence': confidence,
            'area': area,
            'width': width,
            'height': height
        })
    
    # Trier par taille décroissante (les plus gros textes d'abord)
    text_data.sort(key=lambda x: x['area'], reverse=True)
    
    if verbose:
        print("\n=== PREMIÈRE PASSE : Recherche du Pokémon de référence ===")
    
    reference_pokemon = None
    reference_size = None
    
    # Chercher le premier Pokémon dans les plus gros textes
    for data in text_data:
        if verbose:
            print(f"- Texte : {data['text']} → nettoyé : {data['cleaned_text']}")
            print(f"  Confiance OCR : {data['confidence']*100:.2f}% | Taille : {data['area']:.0f} (W:{data['width']:.0f}, H:{data['height']:.0f})")
        
        match, score, *_ = process.extractOne(data['cleaned_text'], pokedex1, scorer=fuzz.ratio)
        
        if verbose:
            print(f"  ➤ Comparé à pokédex : {match} (similitude : {score}%)")
        
        if score > similarity_threshold:
            reference_pokemon = match
            reference_size = data['area']
            if verbose:
                print(f"  ✅ POKÉMON DE RÉFÉRENCE TROUVÉ : {reference_pokemon}")
                print(f"  📏 Taille de référence : {reference_size:.0f}")
            break
    
    if reference_pokemon is None:
        if verbose:
            print("\n❌ Aucun Pokémon de référence trouvé.")
        return None
    
    # Deuxième passe : se concentrer sur les textes de taille similaire
    if verbose:
        print(f"\n=== DEUXIÈME PASSE : Recherche dans les textes de taille similaire ===")
    
    size_min = reference_size * (1 - size_tolerance)
    size_max = reference_size * (1 + size_tolerance)
    
    if verbose:
        print(f"Recherche dans la plage de taille : {size_min:.0f} - {size_max:.0f}")
    
    best_matches = []
    best_scores = []
    best_confidences = []
    
    for data in text_data:
        # Filtrer par taille
        if not (size_min <= data['area'] <= size_max):
            continue
            
        if verbose:
            print(f"- Texte (taille compatible) : {data['text']} → {data['cleaned_text']}")
            print(f"  Confiance OCR : {data['confidence']*100:.2f}% | Taille : {data['area']:.0f}")
        
        match, score, *_ = process.extractOne(data['cleaned_text'], pokedex1, scorer=fuzz.ratio)
        
        if verbose:
            print(f"  ➤ Comparé à pokédex : {match} (similitude : {score}%)")
        
        if score > similarity_threshold and data['confidence'] > 0.15:
            best_matches.append(match)
            best_scores.append(score)
            best_confidences.append(data['confidence'])
            if verbose:
                print(f"  ✅ MATCH VALIDÉ")
    
    if len(best_matches) > 0:
        if verbose:
            print(f"\n🎯 RÉSULTATS FINAUX : {len(best_matches)} Pokémon(s) trouvé(s)")
            for i, (match, score, conf) in enumerate(zip(best_matches, best_scores, best_confidences)):
                print(f"  {i+1}. {match} (similitude: {score}%, confiance OCR: {conf*100:.2f}%)")
        
        # Retourner des objets avec plus d'informations pour l'API
        final_result = []
        for match, score, conf in zip(best_matches, best_scores, best_confidences):
            final_result.append({
                'name': match,
                'similarity': score,
                'confidence': conf
            })
    else:
        if verbose:
            print("\n❌ Aucun nom trouvé avec une similitude suffisante dans la plage de taille.")
    
    return final_result

def detect_pokemon_name_best_match(image_path, lang='en', similarity_threshold=72, 
                                  size_tolerance=0.3, return_best_only=True, verbose=False):
    """
    Version optimisée qui retourne soit le meilleur match, soit tous les matches
    
    Args:
        return_best_only: Si True, retourne seulement le meilleur match
        verbose: Si True, affiche les détails du processus
    
    Returns:
        Soit un seul résultat (dict), soit une liste de résultats, soit None
    """
    result = detect_pokemon_name(image_path, lang, similarity_threshold, size_tolerance, verbose)
    
    if result is None or len(result) == 0:
        return None
    
    if return_best_only and len(result) > 1:
        # Retourner le meilleur basé sur une combinaison score + confiance
        best_result = max(result, key=lambda x: x['similarity'] * 0.7 + x['confidence'] * 30)
        return best_result
    
    return result

# Fonction utilitaire pour l'API
def detect_pokemon_simple(image_path, **kwargs):
    """
    Version simplifiée qui retourne juste les noms (compatibilité ascendante)
    """
    results = detect_pokemon_name(image_path, **kwargs)
    if results:
        return [r['name'] for r in results]
    return None

# Exemples d'utilisation
if __name__ == "__main__":
    image_path = "g4.png"
    
    print("--- Test standard ---")
    resultat = detect_pokemon_name(image_path, verbose=True)
    print(f"Résultat : {resultat}")
    
    print("\n--- Test avec tolérance plus large (±50%) ---")
    resultat_large = detect_pokemon_name(image_path, similarity_threshold=75, size_tolerance=0.8, verbose=True)
    print(f"Résultat avec tolérance large : {resultat_large}")
    
    print("\n--- Test meilleur match seulement ---")
    meilleur = detect_pokemon_name_best_match(image_path, return_best_only=True, verbose=True)
    print(f"Meilleur match : {meilleur}")