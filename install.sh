#!/bin/bash

# ======================================================
# Script d'installation automatique - Immotech
# ======================================================
# 
# Ce script automatise l'installation de la plateforme
# Immotech sur les systèmes Linux et macOS.
# 
# Usage: ./install.sh
# ======================================================

set -e  # Arrêter le script en cas d'erreur

echo "🏠 Installation d'Immotech - Plateforme de Gestion Immobilière"
echo "=========================================================="

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

echo "✅ Python 3 détecté: $(python3 --version)"

# Vérifier que pip est installé
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

echo "✅ pip3 détecté: $(pip3 --version)"

# Vérifier que MongoDB est installé
if ! command -v mongod &> /dev/null; then
    echo "⚠️  MongoDB n'est pas installé."
    echo "📖 Veuillez installer MongoDB depuis: https://docs.mongodb.com/manual/installation/"
    echo "   Ou utilisez Docker: docker run -d -p 27017:27017 --name mongodb mongo:latest"
    read -p "Continuer sans MongoDB ? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ MongoDB détecté: $(mongod --version | head -n 1)"
fi

# Créer l'environnement virtuel
echo "🔧 Création de l'environnement virtuel..."
if [ -d "venv" ]; then
    echo "⚠️  L'environnement virtuel existe déjà. Suppression..."
    rm -rf venv
fi

python3 -m venv venv
echo "✅ Environnement virtuel créé"

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate
echo "✅ Environnement virtuel activé"

# Mettre à jour pip
echo "🔧 Mise à jour de pip..."
pip install --upgrade pip
echo "✅ pip mis à jour"

# Installer les dépendances
echo "🔧 Installation des dépendances..."
pip install -r requirements.txt
echo "✅ Dépendances installées"

# Créer le fichier .env s'il n'existe pas
if [ ! -f ".env" ]; then
    echo "🔧 Création du fichier de configuration .env..."
    cp env.example .env
    echo "✅ Fichier .env créé"
    echo "⚠️  N'oubliez pas de configurer vos variables d'environnement dans .env"
else
    echo "✅ Fichier .env existe déjà"
fi

# Créer les dossiers nécessaires
echo "🔧 Création des dossiers nécessaires..."
mkdir -p Immotech/static/uploads
mkdir -p Immotech/static/contracts
touch Immotech/static/uploads/.gitkeep
touch Immotech/static/contracts/.gitkeep
echo "✅ Dossiers créés"

# Vérifier que MongoDB est en cours d'exécution
if command -v mongod &> /dev/null; then
    echo "🔧 Vérification de MongoDB..."
    if pgrep -x "mongod" > /dev/null; then
        echo "✅ MongoDB est en cours d'exécution"
    else
        echo "⚠️  MongoDB n'est pas en cours d'exécution"
        echo "📖 Démarrez MongoDB avec: sudo systemctl start mongod"
        echo "   Ou: mongod --dbpath /path/to/data/db"
    fi
fi

echo ""
echo "🎉 Installation terminée avec succès !"
echo ""
echo "📋 Prochaines étapes:"
echo "1. Configurez vos variables d'environnement dans .env"
echo "2. Assurez-vous que MongoDB est en cours d'exécution"
echo "3. Lancez l'application: python Immotech/app.py"
echo "4. Ouvrez votre navigateur sur: http://127.0.0.1:5000"
echo ""
echo "📚 Documentation: https://github.com/username/immotech#readme"
echo ""
echo "🚀 Bon développement !" 