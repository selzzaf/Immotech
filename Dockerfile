# ======================================================
# Dockerfile - Immotech Plateforme de Gestion Immobilière
# ======================================================
# 
# Ce Dockerfile permet de containeriser l'application
# Immotech pour un déploiement facile et reproductible.
# 
# Usage: docker build -t immotech .
#        docker run -p 5000:5000 immotech
# ======================================================

# Utiliser Python 3.11 comme image de base
FROM python:3.11-slim

# Définir les variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=Immotech/app.py \
    FLASK_ENV=production

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libffi-dev \
        libssl-dev \
        pkg-config \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Créer les dossiers nécessaires
RUN mkdir -p Immotech/static/uploads \
    && mkdir -p Immotech/static/contracts \
    && touch Immotech/static/uploads/.gitkeep \
    && touch Immotech/static/contracts/.gitkeep

# Créer un utilisateur non-root pour la sécurité
RUN groupadd -r immotech && useradd -r -g immotech immotech \
    && chown -R immotech:immotech /app

# Changer vers l'utilisateur non-root
USER immotech

# Exposer le port
EXPOSE 5000

# Script de démarrage
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Point d'entrée
ENTRYPOINT ["docker-entrypoint.sh"]

# Commande par défaut
CMD ["python", "Immotech/app.py"] 