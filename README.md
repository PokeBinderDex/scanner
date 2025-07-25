---
title: Pokemon Card Scanner
emoji: 🎴
colorFrom: blue
colorTo: yellow
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
hardware: t4-small
---

# 🎴 Pokemon Card Scanner

Scanner de cartes Pokémon utilisant l'intelligence artificielle pour identifier automatiquement les Pokémon dans vos classeurs ou cartes individuelles.

## 🚀 Fonctionnalités

- **🔍 Détection automatique** : Utilise EasyOCR pour extraire le texte des cartes
- **🎯 Correspondance intelligente** : RapidFuzz pour matcher avec la base Pokédex
- **⚡ Optimisé GPU** : Utilise le GPU T4 pour des performances rapides
- **🌐 Multi-langues** : Support de l'OCR en plusieurs langues
- **⚙️ Paramètres ajustables** : Seuils de similitude et tolérance personnalisables

## 📖 Utilisation

1. **Uploadez votre image** : Glissez-déposez ou cliquez pour sélectionner
2. **Ajustez les paramètres** (optionnel) : Langue, seuils, etc.
3. **Cliquez sur "Scanner"** : L'IA analyse votre image
4. **Consultez les résultats** : Noms des Pokémon avec scores de confiance

## 🎯 Conseils pour de meilleurs résultats

- Utilisez des images **nettes et bien éclairées**
- Évitez les **angles trop prononcés**
- Les **noms doivent être visibles** et lisibles
- Format recommandé : **PNG ou JPG**

## 🔧 API

Ce Space expose également une API REST utilisable :

```python
import requests

# Exemple d'appel API
files = {'image': open('ma_carte.jpg', 'rb')}
data = {
    'lang': 'en',
    'similarity_threshold': 72,
    'return_best_only': False
}

response = requests.post('https://YOUR_USERNAME-pokemon-card-scanner.hf.space/api/detect_pokemon', 
                        files=files, data=data)
result = response.json()
```

## 🛠️ Technologies utilisées

- **EasyOCR** : Reconnaissance optique de caractères
- **RapidFuzz** : Correspondance floue de chaînes
- **OpenCV** : Traitement d'images
- **Gradio** : Interface utilisateur web
- **PyTorch** : Backend d'apprentissage automatique

## 📝 À propos

Développé pour la communauté Pokémon, ce scanner aide à cataloguer rapidement vos collections de cartes. Parfait pour les collectionneurs et les joueurs !

---

*🚀 Optimisé pour Hugging Face Spaces avec GPU T4*
