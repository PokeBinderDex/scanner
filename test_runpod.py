"""
Script de test pour l'API RunPod Serverless Pokemon Scanner
"""
import requests
import base64
import json
import os
from PIL import Image
import io

# Configuration
RUNPOD_ENDPOINT = "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync"  # À remplacer
RUNPOD_API_KEY = "your-runpod-api-key"  # À remplacer

def encode_image_to_base64(image_path):
    """Encode une image en base64"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Erreur lors de l'encodage de l'image : {e}")
        return None

def create_test_image():
    """Crée une image de test simple si pas d'image disponible"""
    # Crée une image simple avec du texte "Pikachu"
    img = Image.new('RGB', (300, 100), color='white')
    # Note: Pour un vrai test, utilise une vraie image de carte Pokémon
    img.save('test_pokemon.png')
    return 'test_pokemon.png'

def test_runpod_api(image_path, test_params=None):
    """Test l'API RunPod avec une image"""
    
    if test_params is None:
        test_params = {
            "lang": "en",
            "similarity_threshold": 72,
            "size_tolerance": 0.3,
            "return_best_only": True
        }
    
    # Encode l'image
    print(f"📸 Encodage de l'image : {image_path}")
    img_base64 = encode_image_to_base64(image_path)
    
    if not img_base64:
        print("❌ Impossible d'encoder l'image")
        return None
    
    # Prépare la requête
    payload = {
        "input": {
            "image": img_base64,
            **test_params
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {RUNPOD_API_KEY}"
    }
    
    print("🚀 Envoi de la requête à RunPod...")
    print(f"   Endpoint: {RUNPOD_ENDPOINT}")
    print(f"   Paramètres: {test_params}")
    
    try:
        response = requests.post(RUNPOD_ENDPOINT, json=payload, headers=headers, timeout=120)
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Succès !")
            print("📋 Résultat:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - La requête a pris trop de temps")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de requête: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
    
    return None

def test_local_handler(image_path):
    """Test le handler localement (sans RunPod)"""
    print("🧪 Test local du handler...")
    
    try:
        # Import du handler local
        from handler import handler
        
        # Encode l'image
        img_base64 = encode_image_to_base64(image_path)
        if not img_base64:
            print("❌ Impossible d'encoder l'image pour le test local")
            return
        
        # Simule une requête RunPod
        job = {
            "input": {
                "image": img_base64,
                "lang": "en",
                "similarity_threshold": 72,
                "size_tolerance": 0.3,
                "return_best_only": True
            }
        }
        
        # Appelle le handler
        result = handler(job)
        
        print("✅ Test local réussi !")
        print("📋 Résultat:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except ImportError:
        print("⚠️ handler.py non trouvé - assure-toi d'être dans le bon répertoire")
    except Exception as e:
        print(f"❌ Erreur lors du test local: {e}")

def main():
    """Fonction principale de test"""
    print("🔍 Pokemon Scanner - Test RunPod Serverless")
    print("=" * 50)
    
    # Vérifie si une image de test existe
    test_image = 'test_pokemon.png'
    if not os.path.exists(test_image):
        print("📸 Aucune image de test trouvée, création d'une image simple...")
        test_image = create_test_image()
        print("⚠️ Pour un vrai test, remplace 'test_pokemon.png' par une vraie carte Pokémon")
    
    # Test local d'abord
    print("\n1️⃣ Test local du handler:")
    test_local_handler(test_image)
    
    # Test RunPod si configuré
    print(f"\n2️⃣ Test RunPod API:")
    if RUNPOD_ENDPOINT.startswith("https://") and RUNPOD_API_KEY != "your-runpod-api-key":
        test_runpod_api(test_image)
    else:
        print("⚠️ Configure d'abord RUNPOD_ENDPOINT et RUNPOD_API_KEY dans ce script")
        print("   Tu les trouveras dans ton dashboard RunPod après déploiement")
    
    # Tests avec différents paramètres
    print(f"\n3️⃣ Test avec paramètres différents:")
    if RUNPOD_ENDPOINT.startswith("https://") and RUNPOD_API_KEY != "your-runpod-api-key":
        test_params_custom = {
            "lang": "fr",
            "similarity_threshold": 60,
            "size_tolerance": 0.5,
            "return_best_only": False
        }
        print("   → Test avec seuil plus bas et tolérance plus grande:")
        test_runpod_api(test_image, test_params_custom)
    else:
        print("⚠️ Configure RunPod pour tester différents paramètres")

    print("\n🎯 Tests terminés!")
    print("\n📝 Prochaines étapes:")
    print("   1. Configure RUNPOD_ENDPOINT et RUNPOD_API_KEY")
    print("   2. Utilise une vraie image de carte Pokémon")
    print("   3. Teste différents paramètres selon tes besoins")

if __name__ == "__main__":
    main()