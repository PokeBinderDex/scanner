from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import base64
from PIL import Image
import io

# Import de votre script existant (gardé intact)
from pokemon_detector import detect_pokemon_name_best_match, detect_pokemon_name

app = Flask(__name__)
CORS(app)  # Pour permettre les requêtes depuis GitHub Pages

@app.route('/api/detect-pokemon', methods=['POST'])
def detect_pokemon():
    try:
        # Récupération des paramètres
        lang = request.form.get('lang', 'en')
        similarity_threshold = int(request.form.get('similarity_threshold', 72))
        size_tolerance = float(request.form.get('size_tolerance', 0.3))
        return_best_only = request.form.get('return_best_only', 'false').lower() == 'true'
        
        # Récupération de l'image
        if 'image' not in request.files:
            return jsonify({'error': 'Aucune image fournie'}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'Aucune image sélectionnée'}), 400
        
        # Sauvegarde temporaire de l'image
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            image_file.save(tmp_file.name)
            temp_path = tmp_file.name
        
        try:
            # Appel de votre fonction existante (gardée intacte)
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
            # Nettoyage du fichier temporaire
            os.unlink(temp_path)
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK', 'message': 'API Pokemon Scanner is running'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)