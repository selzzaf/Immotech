# Immotech - Plateforme de Gestion Immobilière

## 📋 Description

Immotech est une plateforme web complète de gestion immobilière développée avec Flask et MongoDB. Elle permet aux agents immobiliers, propriétaires et clients de gérer efficacement les transactions immobilières, les visites, les messages et les analyses de marché.

## ✨ Fonctionnalités Principales

### 🏠 Gestion des Biens Immobiliers
- Ajout, modification et suppression de propriétés
- Système de recherche avancée avec filtres multiples
- Gestion des images et documents
- Validation des biens par les agents
- Suggestions de prix par les agents

### 👥 Gestion des Utilisateurs
- Système d'authentification sécurisé
- Rôles multiples : Client, Agent, Propriétaire, Administrateur
- Profils utilisateurs personnalisés
- Gestion des permissions par rôle

### 💬 Communication
- Système de messagerie interne
- Notifications en temps réel
- Demandes de visite intégrées
- Chatbot d'assistance intelligent

### 📊 Analyses et Rapports
- Tableau de bord administrateur
- Analyses de marché détaillées
- Statistiques utilisateur
- Rapports de performance

### 🔄 Gestion des Transactions
- Création et suivi des transactions
- Système de réservation
- Gestion des contrats
- Traitement des paiements

### 📅 Gestion des Visites
- Programmation de visites
- Confirmation et annulation
- Notifications automatiques
- Suivi des statuts

## 🛠️ Technologies Utilisées

- **Backend**: Flask (Python)
- **Base de données**: MongoDB
- **Authentification**: Flask-Login
- **Interface**: HTML/CSS/JavaScript (Bootstrap)
- **Serveur**: Waitress (Production)
- **Chatbot**: IA personnalisée
- **Analyses**: Pandas, NumPy, Matplotlib

## 📦 Installation

### Prérequis
- Python 3.8+
- MongoDB
- pip

### Étapes d'installation

1. **Cloner le repository**
   ```bash
   git clone https://github.com/username/immotech.git
   cd immotech
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration de la base de données**
   - Assurez-vous que MongoDB est installé et en cours d'exécution
   - Créez un fichier `.env` à la racine du projet avec les variables suivantes :
   ```env
   MONGODB_URI=mongodb://localhost:27017/
   DATABASE_NAME=immotech
   SECRET_KEY=votre_cle_secrete_ici
   ```

5. **Lancer l'application**
   ```bash
   python Immotech/app.py
   ```

6. **Accéder à l'application**
   - Ouvrez votre navigateur et allez sur `http://127.0.0.1:5000`

## 🚀 Utilisation

### Création d'un compte
1. Accédez à la page d'inscription
2. Choisissez votre rôle (Client, Agent, Propriétaire)
3. Remplissez les informations requises
4. Connectez-vous avec vos identifiants

### Ajout d'un bien immobilier (Propriétaire/Agent)
1. Connectez-vous avec un compte Propriétaire ou Agent
2. Accédez à "Ajouter un bien"
3. Remplissez les informations du bien
4. Ajoutez des images si nécessaire
5. Publiez le bien

### Recherche de biens (Client)
1. Utilisez la barre de recherche sur la page d'accueil
2. Appliquez des filtres (prix, surface, localisation, etc.)
3. Consultez les détails des biens
4. Contactez l'agent ou le propriétaire

### Gestion des visites
1. Demandez une visite depuis la page d'un bien
2. Les agents peuvent confirmer ou modifier les rendez-vous
3. Recevez des notifications de statut

## 📁 Structure du Projet

```
immotech/
├── Immotech/
│   ├── app.py                 # Application principale Flask
│   ├── chatbot.py             # Module du chatbot intelligent
│   ├── analytics.py           # Module d'analyses et statistiques
│   ├── transactions.py        # Gestionnaire de transactions
│   ├── templates/             # Templates HTML
│   ├── static/                # Fichiers statiques (CSS, JS, images)
│   └── semgmtapp/             # Modules supplémentaires
├── requirements.txt           # Dépendances Python
├── .env                      # Variables d'environnement
└── README.md                 # Ce fichier
```

## 🔧 Configuration

### Variables d'environnement
- `MONGODB_URI`: URI de connexion MongoDB
- `DATABASE_NAME`: Nom de la base de données
- `SECRET_KEY`: Clé secrète pour les sessions Flask

### Configuration MongoDB
- Assurez-vous que MongoDB est installé et en cours d'exécution
- Les collections seront créées automatiquement lors de la première utilisation

## 🧪 Tests

Pour exécuter les tests (si disponibles) :
```bash
python -m pytest tests/
```

## 📈 Déploiement

### Déploiement local
```bash
python Immotech/app.py
```

### Déploiement en production
1. Configurez un serveur web (Nginx/Apache)
2. Utilisez Gunicorn ou Waitress comme serveur WSGI
3. Configurez les variables d'environnement de production
4. Activez HTTPS

## 🤝 Contribution

1. Fork le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Auteurs

- **Développeur** - *Développement initial*

## 🙏 Remerciements

- Flask et sa communauté
- MongoDB pour la base de données
- Bootstrap pour l'interface utilisateur
- Tous les contributeurs open source

## 📞 Support

Pour toute question ou problème :
- Ouvrez une issue sur GitHub
- Contactez-nous via email

---

**Note**: Ce projet est en développement actif. Les fonctionnalités peuvent évoluer. 