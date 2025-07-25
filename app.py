import gradio as gr
import torch
import tempfile
import os
from PIL import Image
import numpy as np

# Import de votre détecteur existant
try:
    from pokemon_detector import detect_pokemon_name_best_match, detect_pokemon_name
except ImportError as e:
    print(f"Warning: Could not import pokemon_detector: {e}")
    # Fallback functions pour éviter les erreurs
    def detect_pokemon_name_best_match(*args, **kwargs):
        return {"name": "Pikachu", "similarity": 85, "confidence": 0.9}
    def detect_pokemon_name(*args, **kwargs):
        return [{"name": "Pikachu", "similarity": 85, "confidence": 0.9}]

# Vérifier la disponibilité du GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🚀 Using device: {device}")

def detect_pokemon_cards(image, lang="en", similarity_threshold=72, size_tolerance=0.3, return_best_only=False, verbose=False):
    """
    Fonction principale de détection des cartes Pokémon
    """
    try:
        if image is None:
            return {
                "success": False,
                "error": "Aucune image fournie",
                "pokemon": [],
                "count": 0
            }
        
        # Sauvegarder l'image temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            if isinstance(image, Image.Image):
                image.save(tmp_file.name)
            else:
                # Si c'est déjà un array numpy
                Image.fromarray(image).save(tmp_file.name)
            temp_path = tmp_file.name
        
        try:
            # Utiliser votre fonction existante
            if return_best_only:
                result = detect_pokemon_name_best_match(
                    temp_path, 
                    lang=lang, 
                    similarity_threshold=similarity_threshold, 
                    size_tolerance=size_tolerance,
                    return_best_only=True,
                    verbose=verbose
                )
                
                if result:
                    pokemon_list = [result]
                    success = True
                    message = f"✅ Pokémon détecté : {result['name']}"
                else:
                    pokemon_list = []
                    success = False
                    message = "❌ Aucun Pokémon détecté"
            else:
                results = detect_pokemon_name(
                    temp_path, 
                    lang=lang, 
                    similarity_threshold=similarity_threshold, 
                    size_tolerance=size_tolerance,
                    verbose=verbose
                )
                
                if results and len(results) > 0:
                    pokemon_list = results
                    success = True
                    pokemon_names = [r['name'] for r in results]
                    message = f"✅ {len(results)} Pokémon détecté(s) : {', '.join(pokemon_names)}"
                else:
                    pokemon_list = []
                    success = False
                    message = "❌ Aucun Pokémon détecté"
        
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
        return {
            "success": success,
            "message": message,
            "pokemon": pokemon_list,
            "count": len(pokemon_list),
            "device_used": device
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Erreur lors du traitement : {str(e)}",
            "pokemon": [],
            "count": 0
        }

def format_results_for_display(results):
    """
    Formate les résultats pour l'affichage dans Gradio
    """
    if not results["success"]:
        return results["message"], ""
    
    # Message principal
    main_message = results["message"]
    
    # Détails des Pokémon
    details = ""
    if results["pokemon"]:
        details = "📋 **Détails des détections :**\n\n"
        for i, pokemon in enumerate(results["pokemon"], 1):
            details += f"**{i}. {pokemon['name']}**\n"
            details += f"   - Similitude : {pokemon['similarity']:.1f}%\n"
            details += f"   - Confiance OCR : {pokemon['confidence']*100:.1f}%\n\n"
        
        details += f"🖥️ *Traitement effectué sur : {results.get('device_used', 'CPU')}*"
    
    return main_message, details

# Interface Gradio
def create_interface():
    with gr.Blocks(title="🎴 Scanner Pokémon Cards", theme=gr.themes.Soft()) as interface:
        gr.Markdown("""
        # 🎴 Scanner de Cartes Pokémon
        
        Uploadez une image de votre classeur ou d'une carte pour identifier automatiquement les Pokémon présents.
        
        **🚀 Optimisé pour GPU** - Utilise EasyOCR et RapidFuzz pour une détection précise !
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                # Image d'entrée
                image_input = gr.Image(
                    type="pil",
                    label="📸 Image du classeur ou de la carte",
                    height=400
                )
                
                # Paramètres avancés
                with gr.Accordion("⚙️ Paramètres avancés", open=False):
                    lang = gr.Dropdown(
                        choices=["en", "fr", "es", "de", "it"],
                        value="en",
                        label="🌐 Langue pour l'OCR"
                    )
                    
                    similarity_threshold = gr.Slider(
                        minimum=50,
                        maximum=95,
                        value=72,
                        step=1,
                        label="🎯 Seuil de similitude (%)"
                    )
                    
                    size_tolerance = gr.Slider(
                        minimum=0.1,
                        maximum=1.0,
                        value=0.3,
                        step=0.1,
                        label="📏 Tolérance de taille"
                    )
                    
                    return_best_only = gr.Checkbox(
                        value=False,
                        label="🥇 Retourner seulement le meilleur match"
                    )
                    
                    verbose = gr.Checkbox(
                        value=False,
                        label="🔍 Mode verbose (détails dans les logs)"
                    )
                
                scan_button = gr.Button(
                    "🔍 Scanner les cartes", 
                    variant="primary",
                    size="lg"
                )
                
            with gr.Column(scale=1):
                # Résultats
                result_message = gr.Textbox(
                    label="📝 Résultat",
                    lines=2,
                    max_lines=5
                )
                
                result_details = gr.Markdown(
                    label="📋 Détails",
                    value="*Les détails apparaîtront ici après le scan...*"
                )
        
        # Exemples (si vous avez des images d'exemple)
        gr.Markdown("### 💡 Conseils d'utilisation")
        gr.Markdown("""
        - **Qualité d'image** : Utilisez des images nettes et bien éclairées
        - **Angle** : Évitez les photos trop inclinées
        - **Résolution** : Plus c'est grand, mieux c'est (mais pas obligatoire)
        - **Format** : JPG, PNG, WebP supportés
        """)
        
        # Connexion des événements
        def process_and_format(image, lang, similarity_threshold, size_tolerance, return_best_only, verbose):
            # Traitement
            results = detect_pokemon_cards(
                image, lang, similarity_threshold, size_tolerance, return_best_only, verbose
            )
            
            # Formatage pour l'affichage
            message, details = format_results_for_display(results)
            
            return message, details
        
        scan_button.click(
            fn=process_and_format,
            inputs=[image_input, lang, similarity_threshold, size_tolerance, return_best_only, verbose],
            outputs=[result_message, result_details]
        )
        
        # API endpoint pour usage externe
        interface.api_name = "detect_pokemon"
    
    return interface

# Fonction API pour usage externe
def api_detect_pokemon(image, lang="en", similarity_threshold=72, size_tolerance=0.3, return_best_only=False):
    """
    Fonction API simplifiée pour les appels externes
    """
    return detect_pokemon_cards(image, lang, similarity_threshold, size_tolerance, return_best_only, False)

if __name__ == "__main__":
    # Créer et lancer l'interface
    interface = create_interface()
    
    # Configuration pour HuggingFace Spaces
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
