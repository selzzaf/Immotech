# Guide de Déploiement - Immotech

Ce guide vous accompagne dans le déploiement de la plateforme Immotech en production.

## 🚀 Options de Déploiement

### 1. Déploiement Local (Développement)

#### Prérequis
- Python 3.8+
- MongoDB
- pip

#### Étapes
```bash
# Cloner le repository
git clone https://github.com/username/immotech.git
cd immotech

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
cp env.example .env
# Éditer .env avec vos paramètres

# Lancer l'application
python Immotech/app.py
```

### 2. Déploiement avec Docker

#### Prérequis
- Docker
- Docker Compose

#### Étapes
```bash
# Cloner le repository
git clone https://github.com/username/immotech.git
cd immotech

# Construire et lancer avec Docker Compose
docker-compose up -d

# Vérifier les services
docker-compose ps

# Voir les logs
docker-compose logs -f app
```

#### Variables d'environnement Docker
```bash
# Créer un fichier .env pour Docker
SECRET_KEY=votre_cle_secrete_tres_securisee
MONGODB_URI=mongodb://admin:password123@mongodb:27017/immotech?authSource=admin
DATABASE_NAME=immotech
FLASK_ENV=production
```

### 3. Déploiement sur Serveur VPS

#### Prérequis
- Serveur Ubuntu 20.04+ ou CentOS 8+
- Accès SSH
- MongoDB installé

#### Étapes

1. **Préparer le serveur**
```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer Python et pip
sudo apt install python3 python3-pip python3-venv -y

# Installer MongoDB
sudo apt install mongodb -y
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

2. **Déployer l'application**
```bash
# Cloner le repository
git clone https://github.com/username/immotech.git
cd immotech

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
cp env.example .env
nano .env  # Éditer avec vos paramètres
```

3. **Configurer le service systemd**
```bash
# Créer le fichier de service
sudo nano /etc/systemd/system/immotech.service
```

Contenu du fichier service :
```ini
[Unit]
Description=Immotech Real Estate Platform
After=network.target mongodb.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/immotech
Environment=PATH=/path/to/immotech/venv/bin
ExecStart=/path/to/immotech/venv/bin/python Immotech/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

4. **Activer et démarrer le service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable immotech
sudo systemctl start immotech
sudo systemctl status immotech
```

### 4. Déploiement avec Nginx (Production)

#### Configuration Nginx
```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/immotech/Immotech/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

#### Configuration SSL avec Let's Encrypt
```bash
# Installer Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtenir le certificat SSL
sudo certbot --nginx -d votre-domaine.com

# Renouvellement automatique
sudo crontab -e
# Ajouter : 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔧 Configuration de Production

### Variables d'Environnement Recommandées

```env
# Base de données
MONGODB_URI=mongodb://username:password@host:port/database
DATABASE_NAME=immotech

# Sécurité
SECRET_KEY=votre_cle_secrete_tres_securisee_et_longue
FLASK_ENV=production
DEBUG=False

# Serveur
HOST=0.0.0.0
PORT=5000

# Uploads
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=static/uploads

# Logs
LOG_LEVEL=INFO
LOG_FILE=/var/log/immotech/app.log
```

### Sécurité

1. **Changer la clé secrète**
```python
import secrets
print(secrets.token_hex(32))
```

2. **Configurer le pare-feu**
```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

3. **Sécuriser MongoDB**
```javascript
// Créer un utilisateur avec des permissions limitées
use immotech
db.createUser({
  user: "immotech_user",
  pwd: "mot_de_passe_securise",
  roles: ["readWrite"]
})
```

### Monitoring et Logs

#### Configuration des Logs
```python
import logging
from logging.handlers import RotatingFileHandler

# Configuration des logs
if not app.debug:
    file_handler = RotatingFileHandler('logs/immotech.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Immotech startup')
```

#### Monitoring avec Prometheus
```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
```

## 📊 Sauvegarde et Maintenance

### Sauvegarde de la Base de Données
```bash
# Sauvegarde MongoDB
mongodump --uri="mongodb://username:password@host:port/database" --out=/backup/$(date +%Y%m%d)

# Restauration
mongorestore --uri="mongodb://username:password@host:port/database" /backup/20240115/
```

### Script de Sauvegarde Automatique
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/immotech"
MONGODB_URI="mongodb://username:password@host:port/database"

# Créer le dossier de sauvegarde
mkdir -p $BACKUP_DIR

# Sauvegarder MongoDB
mongodump --uri="$MONGODB_URI" --out="$BACKUP_DIR/mongodb_$DATE"

# Sauvegarder les uploads
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" Immotech/static/uploads/

# Nettoyer les anciennes sauvegardes (garder 7 jours)
find $BACKUP_DIR -name "mongodb_*" -mtime +7 -delete
find $BACKUP_DIR -name "uploads_*" -mtime +7 -delete

echo "Sauvegarde terminée: $DATE"
```

### Mise à Jour de l'Application
```bash
# Arrêter le service
sudo systemctl stop immotech

# Sauvegarder
./backup.sh

# Mettre à jour le code
git pull origin main

# Mettre à jour les dépendances
source venv/bin/activate
pip install -r requirements.txt

# Redémarrer le service
sudo systemctl start immotech
sudo systemctl status immotech
```

## 🚨 Dépannage

### Problèmes Courants

1. **L'application ne démarre pas**
```bash
# Vérifier les logs
sudo journalctl -u immotech -f

# Vérifier les permissions
sudo chown -R www-data:www-data /path/to/immotech
```

2. **Erreur de connexion MongoDB**
```bash
# Tester la connexion
mongo "mongodb://username:password@host:port/database"

# Vérifier le service MongoDB
sudo systemctl status mongodb
```

3. **Problèmes de permissions**
```bash
# Corriger les permissions
sudo chmod -R 755 /path/to/immotech
sudo chown -R www-data:www-data /path/to/immotech
```

## 📞 Support

Pour toute question ou problème de déploiement :
- Ouvrez une issue sur GitHub
- Consultez la documentation
- Contactez l'équipe de maintenance

---

**Note**: Ce guide est destiné à la production. Pour le développement, utilisez le déploiement local. 