# Étape 1: Base avec Python
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Mettre à jour les paquets et installer les dépendances système (Tesseract pour l'OCR)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-fra \
    tesseract-ocr-ara \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier des dépendances Python et les installer
# Fait en premier pour utiliser le cache Docker si les dépendances ne changent pas
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Télécharger le modèle spaCy
RUN python -m spacy download fr_core_news_sm

# Copier le reste du code de l'application
COPY . .

# Créer les répertoires nécessaires pour les données (non versionnées)
RUN mkdir -p /app/data/uploads /app/data/reports

# Exposer le port sur lequel l'application s'exécutera
EXPOSE 5000

# Commande pour lancer l'application en production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
