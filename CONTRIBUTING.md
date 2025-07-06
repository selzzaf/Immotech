# Guide de Contribution - Immotech

Merci de votre intérêt pour contribuer au projet Immotech ! Ce document vous guidera à travers le processus de contribution.

## 🚀 Comment Contribuer

### 1. Fork et Clone

1. Fork le repository sur GitHub
2. Clone votre fork localement :
   ```bash
   git clone https://github.com/username/immotech.git
   cd immotech
   ```

### 2. Configuration de l'Environnement

1. Créez un environnement virtuel :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Configurez les variables d'environnement :
   ```bash
   cp env.example .env
   # Éditez .env avec vos paramètres
   ```

### 3. Création d'une Branche

Créez une branche pour votre fonctionnalité :
```bash
git checkout -b feature/nom-de-votre-fonctionnalite
```

### 4. Développement

- Suivez les conventions de code (voir section ci-dessous)
- Ajoutez des tests pour les nouvelles fonctionnalités
- Mettez à jour la documentation si nécessaire
- Assurez-vous que tous les tests passent

### 5. Commit et Push

```bash
git add .
git commit -m "feat: ajouter une nouvelle fonctionnalité"
git push origin feature/nom-de-votre-fonctionnalite
```

### 6. Pull Request

1. Allez sur GitHub et créez une Pull Request
2. Remplissez le template de PR
3. Attendez la review

## 📝 Conventions de Code

### Style Python

- Suivez PEP 8
- Utilisez des noms de variables et fonctions descriptifs
- Ajoutez des docstrings pour toutes les fonctions
- Limitez les lignes à 79 caractères

### Structure des Fichiers

```
immotech/
├── Immotech/
│   ├── app.py              # Application principale
│   ├── chatbot.py          # Module chatbot
│   ├── analytics.py        # Module analyses
│   ├── transactions.py     # Module transactions
│   ├── templates/          # Templates HTML
│   └── static/             # Fichiers statiques
├── tests/                  # Tests unitaires
├── docs/                   # Documentation
└── requirements.txt        # Dépendances
```

### Messages de Commit

Utilisez le format conventionnel :
- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `docs:` documentation
- `style:` formatage
- `refactor:` refactoring
- `test:` tests
- `chore:` maintenance

Exemples :
```
feat: ajouter système de notifications
fix: corriger bug d'authentification
docs: mettre à jour README
```

## 🧪 Tests

### Exécution des Tests

```bash
# Tous les tests
python -m pytest

# Tests spécifiques
python -m pytest tests/test_auth.py

# Avec couverture
python -m pytest --cov=Immotech
```

### Écriture de Tests

- Créez des tests pour chaque nouvelle fonctionnalité
- Utilisez des fixtures pour les données de test
- Testez les cas d'erreur et les cas limites

Exemple :
```python
def test_user_registration():
    """Test l'inscription d'un nouvel utilisateur"""
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'Inscription réussie' in response.data.decode()
```

## 📚 Documentation

### Mise à Jour de la Documentation

- Mettez à jour le README.md si vous ajoutez des fonctionnalités
- Ajoutez des commentaires dans le code
- Documentez les nouvelles API

### Format des Commentaires

```python
def create_user(username, email, password):
    """
    Crée un nouvel utilisateur dans la base de données.
    
    Args:
        username (str): Nom d'utilisateur unique
        email (str): Adresse email valide
        password (str): Mot de passe sécurisé
        
    Returns:
        dict: Données de l'utilisateur créé
        
    Raises:
        ValueError: Si l'email existe déjà
    """
    # Code de la fonction
```

## 🐛 Signaler un Bug

### Avant de Signaler

1. Vérifiez que le bug n'a pas déjà été signalé
2. Testez avec la dernière version
3. Reproduisez le bug de manière cohérente

### Template de Bug Report

```markdown
**Description du Bug**
Description claire et concise du bug.

**Étapes pour Reproduire**
1. Aller à '...'
2. Cliquer sur '...'
3. Voir l'erreur

**Comportement Attendu**
Description de ce qui devrait se passer.

**Captures d'Écran**
Si applicable, ajoutez des captures d'écran.

**Environnement**
- OS: [ex: Windows 10]
- Navigateur: [ex: Chrome 90]
- Version: [ex: 1.0.0]

**Informations Supplémentaires**
Toute autre information pertinente.
```

## 💡 Proposer une Fonctionnalité

### Template de Feature Request

```markdown
**Problème à Résoudre**
Description claire du problème que cette fonctionnalité résoudrait.

**Solution Proposée**
Description de la solution souhaitée.

**Alternatives Considérées**
Autres solutions que vous avez considérées.

**Informations Supplémentaires**
Contexte, captures d'écran, etc.
```

## 🔒 Sécurité

### Signaler une Vulnérabilité

Si vous découvrez une vulnérabilité de sécurité :

1. **NE PAS** créer une issue publique
2. Contactez-nous directement par email
3. Incluez les détails de la vulnérabilité
4. Nous vous répondrons dans les 48h

## 📋 Checklist de PR

Avant de soumettre votre PR, vérifiez :

- [ ] Le code suit les conventions de style
- [ ] Les tests passent
- [ ] La documentation est mise à jour
- [ ] Les nouvelles fonctionnalités sont testées
- [ ] Le code est commenté
- [ ] Les variables d'environnement sont documentées

## 🎉 Reconnaissance

Tous les contributeurs seront mentionnés dans :
- Le fichier CONTRIBUTORS.md
- Les releases GitHub
- La documentation du projet

## 📞 Questions ?

Si vous avez des questions :
- Ouvrez une issue avec le label "question"
- Consultez la documentation
- Contactez l'équipe de maintenance

---

Merci de contribuer à Immotech ! 🏠✨ 