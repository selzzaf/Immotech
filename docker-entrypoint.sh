#!/bin/bash

# ======================================================
# Script d'entrée Docker - Immotech
# ======================================================
# 
# Ce script gère les tâches de démarrage et la
# configuration de l'environnement pour le conteneur Docker.
# ======================================================

set -e

echo "🏠 Démarrage d'Immotech dans Docker..."

# Vérifier les variables d'environnement requises
if [ -z "$MONGODB_URI" ]; then
    echo "⚠️  MONGODB_URI non définie, utilisation de la valeur par défaut"
    export MONGODB_URI="mongodb://localhost:27017/"
fi

if [ -z "$DATABASE_NAME" ]; then
    echo "⚠️  DATABASE_NAME non définie, utilisation de la valeur par défaut"
    export DATABASE_NAME="immotech"
fi

if [ -z "$SECRET_KEY" ]; then
    echo "⚠️  SECRET_KEY non définie, génération d'une clé aléatoire"
    export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
fi

# Créer les dossiers nécessaires s'ils n'existent pas
mkdir -p Immotech/static/uploads
mkdir -p Immotech/static/contracts

# Vérifier les permissions
chmod 755 Immotech/static/uploads
chmod 755 Immotech/static/contracts

echo "✅ Configuration terminée"
echo "🔧 Variables d'environnement:"
echo "   - MONGODB_URI: $MONGODB_URI"
echo "   - DATABASE_NAME: $DATABASE_NAME"
echo "   - SECRET_KEY: [masquée]"

# Exécuter la commande passée en argument
exec "$@" 