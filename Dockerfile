# Image de base avec CUDA et Python
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Définir le répertoire de travail
WORKDIR /app

# Installation des dépendances système pour OpenCV et EasyOCR
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    libfontconfig1 \
    libxss1 \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers requirements et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip

# Fix pour le conflit blinker dans l'image de base RunPod
RUN pip install --no-cache-dir --force-reinstall blinker>=1.6.0

# Installation des requirements avec ignore des conflits
RUN pip install --no-cache-dir --no-deps -r requirements.txt || true
RUN pip install --no-cache-dir -r requirements.txt --force-reinstall

# Copier tout le code source
COPY . .

# Pré-télécharger les modèles EasyOCR pour éviter le téléchargement à chaque démarrage
RUN python -c "import easyocr; reader = easyocr.Reader(['en', 'fr'], gpu=False)"

# Exposer le port (même si RunPod Serverless n'en a pas besoin)
EXPOSE 8080

# Commande par défaut pour RunPod Serverless
CMD ["python", "handler.py"]
