from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import base64
from PIL import Image
import io

# Import de votre script existant (gardé intact)
try:
    from pokemon_detector import detect_pokemon_name_best_match, detect_pokemon_name
except ImportError as e:
    print(f"Warning: Could not import pokemon_detector: {e}")
    # Fallback functions for testing
    def detect_pokemon_name_best_match(*args, **kwargs):
        return {"name": "Pikachu", "confidence": 0.85}
    def detect_pokemon_name(*args, **kwargs):
        return [{"name": "Pikachu", "confidence": 0.85}]

app = Flask(__name__)

# Configuration CORS pour GitHub Pages
CORS(app, origins=[
    "https://pokebinderdex.github.io",
    "http://localhost:3000",  # Pour les tests locaux
    "http://127.0.0.1:3000"
]) 

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
            if os.path.exists(temp_path):
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

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'Pokemon Scanner API',
        'endpoints': {
            '/api/health': 'Health check',
            '/api/detect-pokemon': 'Pokemon detection (POST)'
        }
    })

if __name__ == '__main__':
    # Use PORT environment variable for Railway deployment
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
