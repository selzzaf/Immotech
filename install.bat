@echo off
REM ======================================================
REM Script d'installation automatique - Immotech (Windows)
REM ======================================================
REM 
REM Ce script automatise l'installation de la plateforme
REM Immotech sur les systèmes Windows.
REM 
REM Usage: install.bat
REM ======================================================

echo 🏠 Installation d'Immotech - Plateforme de Gestion Immobilière
echo ==========================================================

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé. Veuillez l'installer d'abord.
    echo 📖 Téléchargez Python depuis: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python détecté
python --version

REM Vérifier que pip est installé
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip n'est pas installé. Veuillez l'installer d'abord.
    pause
    exit /b 1
)

echo ✅ pip détecté
pip --version

REM Vérifier que MongoDB est installé
mongod --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  MongoDB n'est pas installé.
    echo 📖 Veuillez installer MongoDB depuis: https://docs.mongodb.com/manual/installation/
    echo    Ou utilisez Docker: docker run -d -p 27017:27017 --name mongodb mongo:latest
    set /p continue="Continuer sans MongoDB ? (y/N): "
    if /i not "%continue%"=="y" (
        pause
        exit /b 1
    )
) else (
    echo ✅ MongoDB détecté
    mongod --version
)

REM Créer l'environnement virtuel
echo 🔧 Création de l'environnement virtuel...
if exist venv (
    echo ⚠️  L'environnement virtuel existe déjà. Suppression...
    rmdir /s /q venv
)

python -m venv venv
if errorlevel 1 (
    echo ❌ Erreur lors de la création de l'environnement virtuel
    pause
    exit /b 1
)
echo ✅ Environnement virtuel créé

REM Activer l'environnement virtuel
echo 🔧 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Erreur lors de l'activation de l'environnement virtuel
    pause
    exit /b 1
)
echo ✅ Environnement virtuel activé

REM Mettre à jour pip
echo 🔧 Mise à jour de pip...
python -m pip install --upgrade pip
echo ✅ pip mis à jour

REM Installer les dépendances
echo 🔧 Installation des dépendances...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Erreur lors de l'installation des dépendances
    pause
    exit /b 1
)
echo ✅ Dépendances installées

REM Créer le fichier .env s'il n'existe pas
if not exist .env (
    echo 🔧 Création du fichier de configuration .env...
    copy env.example .env
    echo ✅ Fichier .env créé
    echo ⚠️  N'oubliez pas de configurer vos variables d'environnement dans .env
) else (
    echo ✅ Fichier .env existe déjà
)

REM Créer les dossiers nécessaires
echo 🔧 Création des dossiers nécessaires...
if not exist "Immotech\static\uploads" mkdir "Immotech\static\uploads"
if not exist "Immotech\static\contracts" mkdir "Immotech\static\contracts"
echo. > "Immotech\static\uploads\.gitkeep"
echo. > "Immotech\static\contracts\.gitkeep"
echo ✅ Dossiers créés

REM Vérifier que MongoDB est en cours d'exécution
mongod --version >nul 2>&1
if not errorlevel 1 (
    echo 🔧 Vérification de MongoDB...
    tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
    if "%ERRORLEVEL%"=="0" (
        echo ✅ MongoDB est en cours d'exécution
    ) else (
        echo ⚠️  MongoDB n'est pas en cours d'exécution
        echo 📖 Démarrez MongoDB depuis le service Windows
        echo    Ou: mongod --dbpath C:\data\db
    )
)

echo.
echo 🎉 Installation terminée avec succès !
echo.
echo 📋 Prochaines étapes:
echo 1. Configurez vos variables d'environnement dans .env
echo 2. Assurez-vous que MongoDB est en cours d'exécution
echo 3. Lancez l'application: python Immotech\app.py
echo 4. Ouvrez votre navigateur sur: http://127.0.0.1:5000
echo.
echo 📚 Documentation: https://github.com/username/immotech#readme
echo.
echo 🚀 Bon développement !
pause 