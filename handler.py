import runpod
import json
import base64
import tempfile
import os
from PIL import Image
import io
import traceback
import time

print("🚀 [STARTUP] Handler starting...")
print(f"🐍 [STARTUP] Python version: {os.sys.version}")
print(f"📁 [STARTUP] Working directory: {os.getcwd()}")

# Import de ton code existant
try:
    print("📦 [STARTUP] Importing pokemon_detector...")
    from pokemon_detector import detect_pokemon_name_best_match, detect_pokemon_name
    print("✅ [STARTUP] pokemon_detector imported successfully")
except Exception as e:
    print(f"❌ [STARTUP] Import error: {e}")
    print(f"❌ [STARTUP] Traceback: {traceback.format_exc()}")

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
    start_time = time.time()
    print(f"🎯 [HANDLER] New job received at {time.strftime('%H:%M:%S')}")
    
    try:
        job_input = job["input"]
        print(f"📥 [HANDLER] Input keys: {list(job_input.keys())}")
        
        # Récupération des paramètres avec valeurs par défaut
        lang = job_input.get('lang', 'en')
        similarity_threshold = int(job_input.get('similarity_threshold', 72))
        size_tolerance = float(job_input.get('size_tolerance', 0.3))
        return_best_only = job_input.get('return_best_only', False)
        
        print(f"🔧 [HANDLER] Parameters: lang={lang}, threshold={similarity_threshold}, tolerance={size_tolerance}, best_only={return_best_only}")
        
        # Validation de l'image
        if 'image' not in job_input:
            print("❌ [HANDLER] No image provided")
            return {"error": "Aucune image fournie"}
        
        # Décodage de l'image base64
        print("🖼️ [HANDLER] Decoding base64 image...")
        try:
            image_data = base64.b64decode(job_input['image'])
            image = Image.open(io.BytesIO(image_data))
            print(f"✅ [HANDLER] Image decoded successfully: {image.size} pixels, mode: {image.mode}")
        except Exception as e:
            print(f"❌ [HANDLER] Image decode error: {e}")
            return {"error": f"Erreur décodage image: {str(e)}"}
        
        # Sauvegarde temporaire
        print("💾 [HANDLER] Saving temporary file...")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            image.save(tmp_file.name, 'PNG')
            temp_path = tmp_file.name
        print(f"📁 [HANDLER] Temp file saved: {temp_path}")
        
        try:
            # Appel de ta fonction existante
            print(f"🔍 [HANDLER] Starting Pokemon detection (best_only={return_best_only})...")
            detection_start = time.time()
            
            if return_best_only:
                result = detect_pokemon_name_best_match(
                    temp_path, 
                    lang=lang, 
                    similarity_threshold=similarity_threshold, 
                    size_tolerance=size_tolerance,
                    return_best_only=True,
                    verbose=True  # Active les logs de ton code
                )
                
                detection_time = time.time() - detection_start
                print(f"⏱️ [HANDLER] Detection completed in {detection_time:.2f}s")
                
                if result:
                    print(f"✅ [HANDLER] Pokemon found: {result}")
                    response = {
                        'success': True,
                        'pokemon': result,
                        'count': 1,
                        'detection_time': detection_time
                    }
                else:
                    print("❌ [HANDLER] No Pokemon detected")
                    response = {
                        'success': False,
                        'message': 'Aucun Pokémon détecté',
                        'detection_time': detection_time
                    }
            else:
                results = detect_pokemon_name(
                    temp_path, 
                    lang=lang, 
                    similarity_threshold=similarity_threshold, 
                    size_tolerance=size_tolerance,
                    verbose=True  # Active les logs de ton code
                )
                
                detection_time = time.time() - detection_start
                print(f"⏱️ [HANDLER] Detection completed in {detection_time:.2f}s")
                
                if results:
                    print(f"✅ [HANDLER] {len(results)} Pokemon found: {[r['name'] for r in results]}")
                    response = {
                        'success': True,
                        'pokemon': results,
                        'count': len(results),
                        'detection_time': detection_time
                    }
                else:
                    print("❌ [HANDLER] No Pokemon detected")
                    response = {
                        'success': False,
                        'message': 'Aucun Pokémon détecté',
                        'detection_time': detection_time
                    }
        
        finally:
            # Nettoyage
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                print(f"🗑️ [HANDLER] Temp file cleaned: {temp_path}")
        
        total_time = time.time() - start_time
        print(f"🎉 [HANDLER] Job completed in {total_time:.2f}s total")
        response['total_time'] = total_time
        
        return response
    
    except Exception as e:
        total_time = time.time() - start_time
        error_msg = f"Erreur serveur: {str(e)}"
        error_trace = traceback.format_exc()
        
        print(f"💥 [HANDLER] ERROR after {total_time:.2f}s: {error_msg}")
        print(f"📄 [HANDLER] Traceback: {error_trace}")
        
        return {
            "error": error_msg, 
            "traceback": error_trace,
            "total_time": total_time
        }

# Point d'entrée RunPod
print("🔌 [STARTUP] Starting RunPod serverless...")
runpod.serverless.start({"handler": handler})
