import runpod
import json
import base64
import tempfile
import os
from PIL import Image
import io
import traceback

# Import de ton code existant
from pokemon_detector import detect_pokemon_name_best_match, detect_pokemon_name

def handler(job):
    """
    Handler principal pour RunPod Serverless
    Input format attendu:
    {
        "input": {
            "image": "base64_string",  # Image en base64
            "lang": "en",              # Optionnel
            "similarity_threshold": 72, # Optionnel
            "size_tolerance": 0.3,     # Optionnel
            "return_best_only": true   # Optionnel
        }
    }
    """
    try:
        job_input = job["input"]
        
        # Récupération des paramètres avec valeurs par défaut
        lang = job_input.get('lang', 'en')
        similarity_threshold = int(job_input.get('similarity_threshold', 72))
        size_tolerance = float(job_input.get('size_tolerance', 0.3))
        return_best_only = job_input.get('return_best_only', False)
        
        # Validation de l'image
        if 'image' not in job_input:
            return {"error": "Aucune image fournie"}
        
        # Décodage de l'image base64
        try:
            image_data = base64.b64decode(job_input['image'])
            image = Image.open(io.BytesIO(image_data))
        except Exception as e:
            return {"error": f"Erreur décodage image: {str(e)}"}
        
        # Sauvegarde temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            image.save(tmp_file.name, 'PNG')
            temp_path = tmp_file.name
        
        try:
            # Appel de ta fonction existante
            if return_best_only:
                result = detect_pokemon_name_best_match(
                    temp_path, 
                    lang=lang, 
                    similarity_threshold=similarity_threshold, 
                    size_tolerance=size_tolerance,
                    return_best_only=True
                )
                
                if result:
                    response = {
                        'success': True,
                        'pokemon': result,
                        'count': 1
                    }
                else:
                    response = {
                        'success': False,
                        'message': 'Aucun Pokémon détecté'
                    }
            else:
                results = detect_pokemon_name(
                    temp_path, 
                    lang=lang, 
                    similarity_threshold=similarity_threshold, 
                    size_tolerance=size_tolerance
                )
                
                if results:
                    response = {
                        'success': True,
                        'pokemon': results,
                        'count': len(results)
                    }
                else:
                    response = {
                        'success': False,
                        'message': 'Aucun Pokémon détecté'
                    }
        
        finally:
            # Nettoyage
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
        return response
    
    except Exception as e:
        return {"error": f"Erreur serveur: {str(e)}", "traceback": traceback.format_exc()}

# Point d'entrée RunPod
runpod.serverless.start({"handler": handler})