# syntax=docker/dockerfile:1
FROM python:3.10-slim

# Installer les dépendances système minimales
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*
# Créer et se placer dans le dossier de l'app
WORKDIR /app

# Copier les fichiers requirements et installer les dépendances Python
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir --ignore-installed blinker -r requirements.txt

# Copier tout le code source
COPY . .

# Démarre le handler RunPod
CMD ["sleep", "3600"]
