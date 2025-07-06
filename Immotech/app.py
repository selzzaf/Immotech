from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
# ======================================================
# IMMOTECH - Plateforme de gestion immobilière
# ======================================================
# 
# Ce fichier est le point d'entrée principal de l'application Flask.
# Il contient :
# - Configuration de l'application Flask
# - Connexion à la base de données MongoDB
# - Définition de toutes les routes de l'application
# - Gestion de l'authentification et des autorisations
# - Système de messagerie et notifications
# - Gestion des biens immobiliers et transactions
# 
# Version: 1.0.0
# Licence: MIT
# ======================================================

# ======== Importations des bibliothèques standards ========
import os
import sys
import bcrypt
import logging
import traceback
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

# ======== Importations des bibliothèques externes ========
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
from waitress import serve

# Ajout du répertoire courant au chemin Python pour permettre les importations relatives
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ======== Importations des modules internes ========
# Instance du chatbot pour l'assistance aux utilisateurs
from chatbot import chatbot_instance
# Gestionnaire des transactions immobilières
from transactions import TransactionManager
# Gestionnaire des analyses et statistiques
from analytics import AnalyticsManager

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

# ======== Configuration de l'application Flask ========
# Création de l'instance de l'application Flask
app = Flask(__name__)

# Configuration de la clé secrète pour les sessions et les tokens CSRF
# Utilise la variable d'environnement SECRET_KEY ou une valeur par défaut si non définie
app.secret_key = os.getenv('SECRET_KEY', 'votre_clé_secrète_ici')

# Configuration des paramètres de sécurité et de performance de l'application
app.config.update(
    # Désactivation du mode débogage en production
    DEBUG=False,
    # Désactivation du rechargement automatique des templates pour améliorer les performances
    TEMPLATES_AUTO_RELOAD=False,
    # Sécurisation des cookies de session (uniquement transmis via HTTPS)
    SESSION_COOKIE_SECURE=True,
    # Protection contre les attaques XSS en empêchant l'accès aux cookies via JavaScript
    SESSION_COOKIE_HTTPONLY=True,
    # Protection contre les attaques CSRF en limitant l'envoi des cookies aux requêtes du même site
    SESSION_COOKIE_SAMESITE='Lax',
    # Schéma d'URL préféré pour la génération des URLs
    PREFERRED_URL_SCHEME='http'
)

# ======== Configuration du système d'upload de fichiers ========
# Définition du dossier de stockage des fichiers uploadés
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')

# Extensions de fichiers autorisées pour les uploads (images uniquement)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Fonction de validation des extensions de fichiers
def allowed_file(filename):
    """Vérifie si un fichier a une extension autorisée
    
    Args:
        filename (str): Nom du fichier à vérifier
        
    Returns:
        bool: True si l'extension est autorisée, False sinon
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Création du dossier d'uploads s'il n'existe pas encore
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ======== Configuration de la connexion MongoDB ========
# Établissement de la connexion au serveur MongoDB
# Utilise l'URI de connexion depuis les variables d'environnement ou une valeur par défaut
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))

# Sélection de la base de données à utiliser
db = client[os.getenv('DATABASE_NAME', 'immotech')]

# Collections
users_collection = db['users']
properties_collection = db['properties']
transactions_collection = db['transactions']
documents_collection = db['documents']
messages_collection = db['messages']  # Nouvelle collection pour les messages
notifications_collection = db['notifications']

# Routes
@app.route('/contact/send', methods=['POST'])
@login_required
def contact_agent():
    try:
        recipient_id = request.form.get('recipient_id')
        subject = request.form.get('subject')
        content = request.form.get('content')
        property_id = request.form.get('property_id')

        if not recipient_id or not subject or not content:
            flash('Veuillez remplir tous les champs requis', 'error')
            return redirect(request.referrer or url_for('home'))

        # Vérifier que le destinataire existe
        recipient = users_collection.find_one({'_id': ObjectId(recipient_id)})
        if not recipient:
            flash('Destinataire non trouvé', 'error')
            return redirect(request.referrer or url_for('home'))

        # Créer le message
        message_data = {
            'property_id': ObjectId(property_id) if property_id else None,
            'sender_id': ObjectId(current_user.id),
            'recipient_id': ObjectId(recipient_id),
            'subject': subject,
            'content': content,
            'created_at': datetime.utcnow(),
            'read': False
        }

        # Enregistrer le message
        result = messages_collection.insert_one(message_data)
        
        if result.inserted_id:
            flash('Message envoyé avec succès', 'success')
        else:
            flash('Erreur lors de l\'envoi du message', 'error')

        return redirect(request.referrer or url_for('home'))

    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du message: {str(e)}")
        flash('Une erreur est survenue lors de l\'envoi du message', 'error')
        return redirect(request.referrer or url_for('home'))

# Configuration pour les uploads
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Créer le dossier uploads s'il n'existe pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
db = client[os.getenv('DATABASE_NAME', 'immotech')]

# Initialize managers
transaction_manager = TransactionManager(db)
app.analytics_manager = AnalyticsManager(db)  
analytics_manager = app.analytics_manager  

# Verify managers
logger = logging.getLogger(__name__)
logger.info("Initializing managers...")
properties_collection = db['properties']

# Collection des transactions (ventes, locations)
transactions_collection = db['transactions']

# Collection des documents associés aux propriétés et transactions
documents_collection = db['documents']

# Collection des messages entre utilisateurs
messages_collection = db['messages']

# Collection des notifications système pour les utilisateurs
notifications_collection = db['notifications']

# ======== Configuration des rôles utilisateurs ========
# Définition des rôles disponibles dans l'application
# - client: utilisateur cherchant à acheter/louer un bien
# - agent: agent immobilier gérant les propriétés et les clients
# - admin: administrateur de la plateforme avec accès complet
# - owner: propriétaire d'un bien immobilier
ROLE_ADMIN = 'admin'
ROLE_AGENT = 'agent'
ROLE_CLIENT = 'client'
ROLE_OWNER = 'owner'

# ======== Configuration de Flask-Login ========
# Initialisation du gestionnaire d'authentification
login_manager = LoginManager()

# Association du gestionnaire d'authentification à l'application Flask
login_manager.init_app(app)

# Définition de la route de redirection en cas de tentative d'accès à une page protégée
login_manager.login_view = 'login'

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# ======== Modèle d'utilisateur pour Flask-Login ========
class User(UserMixin):
    """Classe représentant un utilisateur de l'application.
    
    Hérite de UserMixin de Flask-Login pour fournir les méthodes requises par Flask-Login.
    Encapsule les données utilisateur stockées dans MongoDB et fournit des méthodes
    utilitaires pour vérifier les rôles et permissions.
    
    Attributes:
        user_data (dict): Données brutes de l'utilisateur depuis MongoDB
        id (str): Identifiant unique de l'utilisateur (converti en string depuis ObjectId)
        email (str): Adresse email de l'utilisateur
        username (str): Nom d'utilisateur
        role (str): Rôle de l'utilisateur (client, agent, admin, propriétaire)
        first_name (str): Prénom de l'utilisateur
        last_name (str): Nom de famille de l'utilisateur
        phone (str): Numéro de téléphone
        created_at (datetime): Date de création du compte
        preferences (dict): Préférences utilisateur (recherches sauvegardées, etc.)
    """
    def __init__(self, user_data):
        """Initialise un nouvel objet utilisateur à partir des données MongoDB.
        
        Args:
            user_data (dict): Dictionnaire contenant les données utilisateur depuis MongoDB
        """
        self.user_data = user_data
        self.id = str(user_data['_id'])
        self.email = user_data['email']
        self.username = user_data['username']
        self.role = user_data.get('role', ROLE_CLIENT)  # Par défaut, rôle client
        self.first_name = user_data.get('first_name', '')
        self.last_name = user_data.get('last_name', '')
        self.phone = user_data.get('phone', '')
        self.created_at = user_data.get('created_at', datetime.utcnow())
        self.preferences = user_data.get('preferences', {})
        
    def is_admin(self):
        """Vérifie si l'utilisateur a le rôle d'administrateur.
        
        Returns:
            bool: True si l'utilisateur est administrateur, False sinon
        """
        return self.role == ROLE_ADMIN
        
    def is_agent(self):
        """Vérifie si l'utilisateur a le rôle d'agent immobilier.
        
        Returns:
            bool: True si l'utilisateur est agent immobilier, False sinon
        """
        return self.role == ROLE_AGENT
        
    def is_owner(self):
        """Vérifie si l'utilisateur a le rôle de propriétaire.
        
        Returns:
            bool: True si l'utilisateur est propriétaire, False sinon
        """
        return self.role == ROLE_OWNER

    def is_client(self):
        """Vérifie si l'utilisateur a le rôle de client.
        
        Returns:
            bool: True si l'utilisateur est client, False sinon
        """
        return self.role == ROLE_CLIENT

    def get_id(self):
        """Retourne l'identifiant unique de l'utilisateur sous forme de chaîne.
        
        Cette méthode est requise par Flask-Login.
        
        Returns:
            str: L'identifiant unique de l'utilisateur
        """
        return str(self.id)

# ======== Fonction de chargement d'utilisateur pour Flask-Login ========
@login_manager.user_loader
def load_user(user_id):
    """Charge un utilisateur depuis la base de données par son ID.
    
    Cette fonction est utilisée par Flask-Login pour charger l'utilisateur
    à partir de l'ID stocké dans la session.
    
    Args:
        user_id (str): L'identifiant unique de l'utilisateur à charger
        
    Returns:
        User: L'objet utilisateur si trouvé, None sinon
    """
    try:
        user_data = users_collection.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User(user_data)
        return None
    except Exception as e:
        logger.error(f"Erreur lors du chargement de l'utilisateur {user_id}: {str(e)}")
        return None

# ======== Routes principales de l'application ========
@app.route('/')
def home():
    """Route de la page d'accueil de l'application.
    
    Affiche la page d'accueil avec une sélection de propriétés disponibles
    et des informations spécifiques à l'utilisateur connecté.
    
    Returns:
        str: Le template HTML rendu avec les données nécessaires
    """
    try:
        # Récupérer les propriétés disponibles (limité à 6 pour la page d'accueil)
        # Utiliser une requête avec limite pour éviter le chargement excessif et optimiser les performances
        properties = list(properties_collection.find({
            'status': {'$in': ['available', None]}  # Uniquement les propriétés disponibles
        }).limit(6))  # Limiter à 6 propriétés pour la page d'accueil
        
        # Préparer les données des propriétés pour l'affichage
        for prop in properties:
            # Convertir les ObjectId en str pour la sérialisation JSON
            prop['_id'] = str(prop['_id'])
            
            # S'assurer que tous les champs requis existent avec des valeurs par défaut
            # Cela évite les erreurs dans le template si certains champs sont manquants
            prop.setdefault('title', 'Sans titre')
            prop.setdefault('description', '')
            prop.setdefault('price', 0)
            prop.setdefault('surface', 0)
            prop.setdefault('rooms', 0)
            prop.setdefault('location', {'city': 'Non spécifiée'})
        
        # Compteur de messages non lus pour l'utilisateur connecté
        unread_messages_count = 0
        if current_user.is_authenticated:
            # Compter les messages non lus adressés à l'utilisateur courant
            unread_messages_count = messages_collection.count_documents({
                'recipient_id': ObjectId(current_user.id),
                'read': False
            })
        
        # Rendre le template avec les données préparées
        return render_template('home.html',
                            properties=properties,  # Liste des propriétés à afficher
                            unread_messages_count=unread_messages_count)  # Nombre de messages non lus
                            
    except Exception as e:
        # Journalisation détaillée des erreurs pour faciliter le débogage
        logger.error(f"Erreur dans la route home: {str(e)}")
        logger.error(f"Type d'erreur: {type(e)}")
        logger.error(traceback.format_exc())
        
        # Afficher un message d'erreur à l'utilisateur
        flash('Une erreur est survenue lors du chargement de la page d\'accueil', 'error')
        
        # Retourner une page d'accueil vide en cas d'erreur
        return render_template('home.html', properties=[], unread_messages_count=0)
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        # En cas d'erreur, retourner une liste vide
        return render_template('home.html',
                            properties=[],
                            unread_messages_count=0)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_data = users_collection.find_one({'email': email})
        
        if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['password']):
            user = User(user_data)
            login_user(user)
            flash('Connexion réussie!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        else:
            flash('Email ou mot de passe incorrect', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', ROLE_CLIENT)
        
        # Vérification si l'email existe déjà
        if users_collection.find_one({'email': email}):
            flash('Cet email est déjà utilisé', 'error')
            return redirect(url_for('register'))
        
        # Hashage du mot de passe
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Création de l'utilisateur
        user_data = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'role': role,
            'created_at': datetime.utcnow(),
            'preferences': {}
        }
        
        result = users_collection.insert_one(user_data)
        
        if result.inserted_id:
            # Création de l'objet User et connexion automatique
            user = User(user_data)
            login_user(user)
            flash('Inscription réussie et connexion automatique!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Erreur lors de l\'inscription', 'error')
            
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def user_profile():
    # Récupérer les informations de l'utilisateur
    user_data = users_collection.find_one({'_id': ObjectId(current_user.id)})
    
    # Récupérer les biens de l'utilisateur s'il est propriétaire
    properties = []
    if current_user.is_owner():
        properties = list(properties_collection.find({'created_by': ObjectId(current_user.id)}))
    
    # Récupérer les visites de l'utilisateur
    visits = []
    if current_user.is_owner():
        # Pour les propriétaires : visites de leurs biens
        property_ids = [prop['_id'] for prop in properties]
        visits = list(db.visits.find({'property_id': {'$in': property_ids}}))
    else:
        # Pour les clients : leurs visites
        visits = list(db.visits.find({'client_id': ObjectId(current_user.id)}))
    
    # Récupérer les messages non lus
    unread_messages = list(messages_collection.find({
        'recipient_id': ObjectId(current_user.id),
        'read': False
    }).sort('created_at', -1))
    
    return render_template('profile.html',
                         user=user_data,
                         properties=properties,
                         visits=visits,
                         unread_messages=unread_messages)

@app.route('/property/add', methods=['GET', 'POST'])
@login_required
def add_property():
    if not (current_user.is_owner() or current_user.is_agent()):
        flash('Accès non autorisé')
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        property_data = {
            'title': request.form['title'],
            'description': request.form['description'],
            'type': request.form['type'],
            'price': float(request.form['price']),
            'surface': float(request.form['surface']),
            'rooms': int(request.form['rooms']),
            'location': {
                'address': request.form['address'],
                'city': request.form['city'],
                'postal_code': request.form['postal_code'],
                'coordinates': [float(request.form['longitude']), float(request.form['latitude'])]
            },
            'features': request.form.getlist('features'),
            'status': request.form['status'],
            'created_by': current_user.id,
            'created_at': datetime.utcnow(),
            'images': []  # À implémenter avec le stockage des images
        }
        properties_collection.insert_one(property_data)
        flash('Bien immobilier ajouté avec succès')
        return redirect(url_for('home'))
    return render_template('property/add.html')

@app.route('/property/<property_id>')
def view_property(property_id):
    try:
        logger.info(f"Tentative d'accès au bien {property_id}")
        
        # Vérifier si l'ID est un ObjectId valide
        if not ObjectId.is_valid(property_id):
            logger.error(f"ID invalide : {property_id}")
            flash('ID de bien immobilier invalide', 'error')
            return redirect(url_for('home'))
        
        # Récupérer le bien
        property_data = properties_collection.find_one({'_id': ObjectId(property_id)})
        
        if not property_data:
            logger.error(f"Bien non trouvé avec l'ID : {property_id}")
            flash('Bien immobilier non trouvé', 'error')
            return redirect(url_for('home'))

        # S'assurer que toutes les clés nécessaires existent
        property_data.setdefault('title', 'Sans titre')
        property_data.setdefault('description', '')
        property_data.setdefault('price', 0)
        property_data.setdefault('surface', 0)
        property_data.setdefault('rooms', 0)
        property_data.setdefault('type', '')
        property_data.setdefault('features', [])
        property_data.setdefault('location', {
            'address': '',
            'city': 'Non spécifiée',
            'postal_code': ''
        })
        property_data.setdefault('images', [])
        
        # Convertir les ObjectId en str 
        property_data['_id'] = str(property_data['_id'])
        if 'created_by' in property_data:
            property_data['created_by'] = str(property_data['created_by'])
        if 'agent_id' in property_data:
            property_data['agent_id'] = str(property_data['agent_id'])

        # Récupérer l'agent assigné si existe
        agent_data = None
        if 'agent_id' in property_data:
            agent = users_collection.find_one({'_id': ObjectId(property_data['agent_id'])})
            if agent:
                agent_data = {
                    'id': str(agent['_id']),
                    'username': agent.get('username', 'Agent inconnu'),
                    'email': agent.get('email', ''),
                    'phone': agent.get('phone', '')
                }

        # Déterminer le rôle de l'utilisateur
        user_role = None
        if current_user.is_authenticated:
            if current_user.is_admin():
                user_role = 'admin'
            elif current_user.is_agent():
                user_role = 'agent'
            elif current_user.is_owner() and 'created_by' in property_data and str(current_user.id) == property_data['created_by']:
                user_role = 'owner'
            else:
                user_role = 'client'

        # Ajouter la date actuelle pour le formulaire de visite
        now = datetime.utcnow()

        return render_template('property/view.html',
                            property=property_data,
                            agent=agent_data,
                            user_role=user_role,
                            now=now)
                            
    except Exception as e:
        logger.error(f"Erreur lors de l'accès au bien {property_id}")
        logger.error(f"Type d'erreur : {type(e)}")
        logger.error(f"Message d'erreur : {str(e)}")
        logger.error(f"Traceback complet :\n{traceback.format_exc()}")
        flash('Une erreur est survenue lors de l\'accès au bien immobilier', 'error')
        return redirect(url_for('home'))

@app.route('/property/<property_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_property(property_id):
    property_data = properties_collection.find_one({'_id': ObjectId(property_id)})
    if not property_data:
        flash('Bien immobilier non trouvé', 'error')
        return redirect(url_for('home'))
        
    # Vérifier si l'utilisateur est le propriétaire ou un admin
    if not (current_user.id == str(property_data['created_by']) or current_user.is_admin()):
        flash('Vous n\'êtes pas autorisé à modifier ce bien', 'error')
        return redirect(url_for('view_property', property_id=property_id))
        
    if request.method == 'POST':
        # Récupérer les données du formulaire
        updated_data = {
            'title': request.form['title'],
            'description': request.form['description'],
            'type': request.form['type'],
            'price': float(request.form['price']),
            'surface': float(request.form['surface']),
            'rooms': int(request.form['rooms']),
            'location': {
                'address': request.form['address'],
                'city': request.form['city'],
                'postal_code': request.form['postal_code'],
                'coordinates': [float(request.form['longitude']), float(request.form['latitude'])]
            },
            'features': request.form.getlist('features'),
            'status': request.form['status'],
            'updated_at': datetime.utcnow()
        }
        
        # Gérer les images
        if 'delete_images' in request.form:
            # Convertir les indices en entiers
            delete_indices = [int(idx) for idx in request.form.getlist('delete_images')]
            # Filtrer les images à conserver
            current_images = property_data.get('images', [])
            updated_images = [img for idx, img in enumerate(current_images) if idx not in delete_indices]
        else:
            updated_images = property_data.get('images', [])
            
        # Ajouter les nouvelles images
        new_images = request.files.getlist('new_images')
        for image in new_images:
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join('static', 'uploads', filename)
                image.save(os.path.join(app.root_path, image_path))
                updated_images.append(url_for('static', filename=f'uploads/{filename}'))
                
        updated_data['images'] = updated_images
        
        # Mettre à jour dans la base de données
        result = properties_collection.update_one(
            {'_id': ObjectId(property_id)},
            {'$set': updated_data}
        )
        
        if result.modified_count > 0:
            flash('Bien immobilier mis à jour avec succès', 'success')
        else:
            flash('Aucune modification n\'a été effectuée', 'info')
            
        return redirect(url_for('view_property', property_id=property_id))
        
    return render_template('property/edit.html', property=property_data)

@app.route('/property/search')
def search_properties():
    query = {}
    
    # Filtres de recherche
    if 'type' in request.args:
        query['type'] = request.args['type']
    if 'city' in request.args:
        query['location.city'] = {'$regex': request.args['city'], '$options': 'i'}
    if 'min_price' in request.args:
        query['price'] = {'$gte': float(request.args['min_price'])}
    if 'max_price' in request.args and 'price' in query:
        query['price']['$lte'] = float(request.args['max_price'])
    elif 'max_price' in request.args:
        query['price'] = {'$lte': float(request.args['max_price'])}
    if 'min_surface' in request.args:
        query['surface'] = {'$gte': float(request.args['min_surface'])}
    if 'max_surface' in request.args and 'surface' in query:
        query['surface']['$lte'] = float(request.args['max_surface'])
    elif 'max_surface' in request.args:
        query['surface'] = {'$lte': float(request.args['max_surface'])}
    if 'rooms' in request.args:
        query['rooms'] = int(request.args['rooms'])
        
    properties = properties_collection.find(query)
    return render_template('property/search.html', properties=properties, filters=request.args)

@app.route('/property/<property_id>/delete', methods=['POST'])
@login_required
def delete_property(property_id):
    property_data = properties_collection.find_one({'_id': ObjectId(property_id)})
    if not property_data:
        return jsonify({'success': False, 'message': 'Bien immobilier non trouvé'})
        
    if not (current_user.is_admin() or current_user.id == str(property_data['created_by'])):
        return jsonify({'success': False, 'message': 'Accès non autorisé'})
        
    properties_collection.delete_one({'_id': ObjectId(property_id)})
    return jsonify({'success': True, 'message': 'Bien immobilier supprimé avec succès'})

@app.route('/chatbot')
@login_required
def chatbot():
    try:
        return render_template('chatbot.html')
    except Exception as e:
        print(f"Erreur dans chatbot: {str(e)}")
        flash('Une erreur est survenue lors du chargement de l\'assistant', 'error')
        return redirect(url_for('home'))

@app.route('/chatbot/query', methods=['POST'])
@login_required
def chatbot_query():
    try:
        user_input = request.json.get('message')
        if not user_input:
            return jsonify({'response': 'Je n\'ai pas compris votre message. Pouvez-vous réessayer ?'})
            
        # Debug: Afficher l'entrée utilisateur
        print(f"Message reçu: {user_input}")
            
        # Récupérer les préférences de l'utilisateur
        user_data = users_collection.find_one({'_id': ObjectId(current_user.id)})
        user_preferences = user_data.get('preferences', {}) if user_data else {}
        
        # Debug: Afficher les préférences utilisateur
        print(f"Préférences utilisateur: {user_preferences}")
        
        # Obtenir la réponse du chatbot
        try:
            print(f"Chatbot instance type: {type(chatbot_instance)}")  # Debug log
            response = chatbot_instance.get_response(user_input, user_preferences)
            print(f"Réponse du chatbot: {response}")
            
            return jsonify({'response': response})
            
        except Exception as chatbot_error:
            print(f"Erreur dans le chatbot: {str(chatbot_error)}")
            print(f"Type d'erreur: {type(chatbot_error)}")
            import traceback
            print(f"Traceback complet: {traceback.format_exc()}")
            raise chatbot_error
        
    except Exception as e:
        print(f"Erreur dans chatbot_query: {str(e)}")
        print(f"Type d'erreur: {type(e)}")
        import traceback
        print(f"Traceback complet: {traceback.format_exc()}")
        return jsonify({
            'response': 'Je suis désolé, j\'ai rencontré une erreur. Pouvez-vous reformuler votre question ?'
        })

@app.route('/transaction/create', methods=['POST'])
@login_required
def create_transaction():
    property_id = request.form.get('property_id')
    seller_id = request.form.get('seller_id')
    transaction_type = request.form.get('type')
    amount = float(request.form.get('amount'))
    
    transaction_id = transaction_manager.create_transaction(
        property_id=property_id,
        buyer_id=current_user.id,
        seller_id=seller_id,
        transaction_type=transaction_type,
        amount=amount
    )
    
    return redirect(url_for('process_payment', transaction_id=transaction_id))

@app.route('/transaction/payment/<transaction_id>', methods=['GET', 'POST'])
@login_required
def process_payment(transaction_id):
    if request.method == 'POST':
        # Simuler le traitement du paiement
        payment_details = {
            'card_number': request.form.get('card_number')[-4:],  # Stocker uniquement les 4 derniers chiffres
            'payment_method': request.form.get('payment_method'),
            'amount': request.form.get('amount')
        }
        
        if transaction_manager.process_payment(transaction_id, payment_details):
            flash('Paiement effectué avec succès', 'success')
            return redirect(url_for('view_transaction', transaction_id=transaction_id))
        else:
            flash('Erreur lors du paiement', 'error')
            
    transaction = db.transactions.find_one({'_id': ObjectId(transaction_id)})
    return render_template('transaction/payment.html', transaction=transaction)

@app.route('/transaction/booking/<transaction_id>', methods=['GET', 'POST'])
@login_required
def process_booking(transaction_id):
    if request.method == 'POST':
        booking_details = {
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date'),
            'notes': request.form.get('notes')
        }
        
        if transaction_manager.process_booking(transaction_id, booking_details):
            flash('Réservation confirmée', 'success')
            return redirect(url_for('view_transaction', transaction_id=transaction_id))
        else:
            flash('Erreur lors de la réservation', 'error')
            
    transaction = db.transactions.find_one({'_id': ObjectId(transaction_id)})
    return render_template('transaction/booking.html', transaction=transaction)

@app.route('/transaction/<transaction_id>')
@login_required
def view_transaction(transaction_id):
    transaction = transactions_collection.find_one({'_id': ObjectId(transaction_id)})
    if not transaction:
        flash('Transaction non trouvée')
        return redirect(url_for('home'))
        
    if not (current_user.is_admin() or 
            current_user.id in [str(transaction['buyer_id']), str(transaction['seller_id'])]):
        flash('Accès non autorisé')
        return redirect(url_for('home'))
        
    property_data = properties_collection.find_one({'_id': transaction['property_id']})
    buyer_data = users_collection.find_one({'_id': transaction['buyer_id']})
    seller_data = users_collection.find_one({'_id': transaction['seller_id']})
    
    return render_template('transaction/view.html',
                         transaction=transaction,
                         property=property_data,
                         buyer=buyer_data,
                         seller=seller_data)

@app.route('/transaction/<transaction_id>/contract')
@login_required
def download_contract(transaction_id):
    contract_path = transaction_manager.get_contract_path(transaction_id)
    if contract_path and os.path.exists(contract_path):
        return send_file(
            contract_path,
            as_attachment=True,
            download_name=f"contract_{transaction_id}.pdf"
        )
    flash('Contrat non disponible', 'error')
    return redirect(url_for('view_transaction', transaction_id=transaction_id))

@app.route('/analytics/market')
@login_required
def market_analytics():
    try:
        logger.info("=== Début de market_analytics ===")
        
        # Log user information
        logger.info(f"User ID: {current_user.id}")
        logger.info(f"User Role: {current_user.role}")
        
        if not (current_user.is_admin() or current_user.is_agent() or current_user.is_owner()):
            logger.warning(f"Accès refusé pour l'utilisateur {current_user.id} : rôle {current_user.role}")
            flash('Accès non autorisé', 'error')
            return redirect(url_for('home'))
        
        try:
            # Check if analytics_manager is properly initialized
            logger.info("Vérification de analytics_manager...")
            if not hasattr(app, 'analytics_manager'):
                logger.error("analytics_manager n'est pas initialisé")
                raise RuntimeError("analytics_manager n'est pas initialisé")
            
            # Generate report with detailed logging
            logger.info("Génération du rapport...")
            report = analytics_manager.generate_market_report()  # Sans paramètres pour l'analyse générale
            logger.info(f"Statut du rapport: {'Généré' if report else 'Aucune donnée'}")
            
            if report is None:
                logger.info("Aucune donnée disponible")
                flash('Aucune donnée disponible', 'info')
                return render_template('analytics/market.html', report=None)
            
            # Verify report structure
            required_fields = [
                'total_properties', 'available_properties', 'average_price',
                'price_per_sqm', 'average_time_on_market', 'negotiation_rate',
                'price_trend', 'surface_distribution'
            ]
            
            logger.info("Vérification des champs du rapport...")
            missing_fields = [field for field in required_fields if field not in report]
            
            if missing_fields:
                logger.error(f"Champs manquants dans le rapport: {missing_fields}")
                logger.error(f"Contenu du rapport: {report}")
                flash('Erreur lors de la génération du rapport : données incomplètes', 'error')
                return render_template('analytics/market.html', report=None)
            
            # Log successful report generation
            logger.info("Rapport généré avec succès, rendu du template...")
            return render_template('analytics/market.html', report=report)
            
        except Exception as report_error:
            logger.error("Erreur lors de la génération du rapport")
            logger.error(f"Type d'erreur: {type(report_error)}")
            logger.error(f"Message d'erreur: {str(report_error)}")
            logger.error(f"Traceback complet:\n{traceback.format_exc()}")
            flash('Une erreur est survenue lors de la génération du rapport', 'error')
            return render_template('analytics/market.html', report=None)
            
    except Exception as e:
        logger.error("Erreur générale dans market_analytics")
        logger.error(f"Type d'erreur: {type(e)}")
        logger.error(f"Message d'erreur: {str(e)}")
        logger.error(f"Traceback complet:\n{traceback.format_exc()}")
        flash('Une erreur est survenue lors de l\'accès aux analyses', 'error')
        return redirect(url_for('home'))

@app.route('/analytics/user')
@login_required
def user_analytics():
    try:
        # S'assurer que les collections nécessaires existent
        collections = db.list_collection_names()
        required_collections = ['properties', 'transactions', 'messages']
        
        for collection in required_collections:
            if collection not in collections:
                db.create_collection(collection)
        
        # Récupérer le rapport d'activité
        report = analytics_manager.get_user_activity_report(current_user.id)
        
        return render_template('analytics/user.html', report=report)
    except Exception as e:
        print(f"Erreur dans user_analytics: {str(e)}")
        flash('Une erreur est survenue lors du chargement du tableau de bord', 'error')
        return redirect(url_for('home'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin():
        flash('Accès non autorisé', 'error')
        return redirect(url_for('home'))

    # Compter les totaux
    total_users = users_collection.count_documents({})
    total_properties = properties_collection.count_documents({})
    total_transactions = transactions_collection.count_documents({})

    # Récupérer les listes limitées pour l'affichage
    users = list(users_collection.find().limit(10))
    properties = list(properties_collection.find().sort('created_at', -1).limit(10))
    transactions = list(transactions_collection.find().sort('created_at', -1).limit(10))

    return render_template('admin/dashboard.html',
                         users=users,
                         properties=properties,
                         transactions=transactions,
                         total_users=total_users,
                         total_properties=total_properties,
                         total_transactions=total_transactions)

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin():
        flash('Accès non autorisé')
        return redirect(url_for('home'))
        
    users = users_collection.find()
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/<user_id>/role', methods=['POST'])
@login_required
def update_user_role(user_id):
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'Accès non autorisé'})
        
    new_role = request.form.get('role')
    if new_role not in [ROLE_ADMIN, ROLE_AGENT, ROLE_CLIENT, ROLE_OWNER]:
        return jsonify({'success': False, 'message': 'Rôle invalide'})
        
    users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'role': new_role}}
    )
    
    return jsonify({'success': True})

@app.route('/admin/user/<user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'Accès non autorisé'})
    
    # Vérifier que l'utilisateur existe
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'success': False, 'message': 'Utilisateur non trouvé'})
    
    # Ne pas permettre la suppression de son propre compte
    if user_id == current_user.id:
        return jsonify({'success': False, 'message': 'Vous ne pouvez pas supprimer votre propre compte'})
    
    # Supprimer l'utilisateur
    result = users_collection.delete_one({'_id': ObjectId(user_id)})
    
    if result.deleted_count > 0:
        return jsonify({'success': True, 'message': 'Utilisateur supprimé avec succès'})
    else:
        return jsonify({'success': False, 'message': 'Erreur lors de la suppression de l\'utilisateur'})

@app.route('/message/send', methods=['POST'])
@login_required
def send_message():
    try:
        # Récupérer les données du formulaire
        property_id = request.form.get('property_id')
        recipient_id = request.form.get('recipient_id')
        subject = request.form.get('subject')
        content = request.form.get('content')
        visit_requested = request.form.get('request_visit') == 'on'
        visit_date = request.form.get('visit_date')

        # Vérifier les données requises
        if not all([property_id, subject, content]):
            return jsonify({
                'success': False,
                'message': 'Veuillez remplir tous les champs requis'
            })

        # Récupérer les informations du bien
        property_data = properties_collection.find_one({'_id': ObjectId(property_id)})
        if not property_data:
            return jsonify({
                'success': False,
                'message': 'Bien non trouvé'
            })

        # Déterminer le destinataire
        if recipient_id:
            # Si un destinataire est spécifié (cas du message direct à l'agent ou au propriétaire)
            final_recipient_id = ObjectId(recipient_id)
        else:
            # Utiliser l'agent assigné au bien, sinon le propriétaire
            if property_data.get('agent_id'):
                final_recipient_id = property_data['agent_id']
            else:
                final_recipient_id = property_data['created_by']

        if not final_recipient_id:
            return jsonify({
                'success': False,
                'message': 'Destinataire non trouvé'
            })

        # Créer le message
        message_data = {
            'property_id': ObjectId(property_id),
            'sender_id': ObjectId(current_user.id),
            'recipient_id': final_recipient_id,
            'subject': subject,
            'content': content,
            'created_at': datetime.utcnow(),
            'read': False,
            'visit_requested': visit_requested
        }

        if visit_requested and visit_date:
            message_data['visit_date'] = visit_date

        # Enregistrer le message
        result = messages_collection.insert_one(message_data)
        
        if result.inserted_id:
            # Créer une notification
            notification_message = "Nouvelle demande de visite" if visit_requested else "Nouveau message"
            create_notification(
                user_id=str(final_recipient_id),
                message=f"{notification_message} de {current_user.username} : {subject}",
                notification_type='new_message',
                link=url_for('view_messages')
            )

            # Si c'est une demande de visite, créer l'entrée dans la collection des visites
            if visit_requested and visit_date:
                visit_data = {
                    'property_id': ObjectId(property_id),
                    'client_id': ObjectId(current_user.id),
                    'agent_id': property_data.get('agent_id'),
                    'requested_date': datetime.strptime(visit_date, '%Y-%m-%dT%H:%M'),
                    'status': 'pending',
                    'message_id': result.inserted_id,
                    'created_at': datetime.utcnow()
                }
                db.visits.insert_one(visit_data)
            
            return jsonify({
                'success': True,
                'message': 'Message envoyé avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erreur lors de l\'envoi du message'
            })
            
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du message: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': 'Une erreur est survenue lors de l\'envoi du message'
        })

@app.route('/messages')
@login_required
def view_messages():
    try:
        logger.info(f"Début de view_messages pour l'utilisateur {current_user.id}")
        
        # Récupérer les messages reçus et envoyés
        try:
            received_messages = list(messages_collection.find({
                'recipient_id': ObjectId(current_user.id)
            }).sort('created_at', -1))
            logger.info(f"Messages reçus récupérés: {len(received_messages)}")
            
            sent_messages = list(messages_collection.find({
                'sender_id': ObjectId(current_user.id)
            }).sort('created_at', -1))
            logger.info(f"Messages envoyés récupérés: {len(sent_messages)}")
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des messages: {str(e)}")
            raise
        
        # Récupérer les IDs des utilisateurs impliqués
        user_ids = set()
        property_ids = set()
        
        # Traiter les messages reçus
        for message in received_messages:
            try:
                message['_id'] = str(message['_id'])
                if 'sender_id' in message:
                    message['sender_id'] = str(message['sender_id'])
                    user_ids.add(message['sender_id'])
                if 'recipient_id' in message:
                    message['recipient_id'] = str(message['recipient_id'])
                    user_ids.add(message['recipient_id'])
                if 'property_id' in message:
                    message['property_id'] = str(message['property_id'])
                    property_ids.add(message['property_id'])
            except Exception as e:
                logger.error(f"Erreur lors du traitement d'un message reçu: {str(e)}")
                logger.error(f"Message problématique: {message}")
                continue
        
        # Traiter les messages envoyés
        for message in sent_messages:
            try:
                message['_id'] = str(message['_id'])
                if 'sender_id' in message:
                    message['sender_id'] = str(message['sender_id'])
                    user_ids.add(message['sender_id'])
                if 'recipient_id' in message:
                    message['recipient_id'] = str(message['recipient_id'])
                    user_ids.add(message['recipient_id'])
                if 'property_id' in message:
                    message['property_id'] = str(message['property_id'])
                    property_ids.add(message['property_id'])
            except Exception as e:
                logger.error(f"Erreur lors du traitement d'un message envoyé: {str(e)}")
                logger.error(f"Message problématique: {message}")
                continue
        
        logger.info(f"Nombre d'utilisateurs à récupérer: {len(user_ids)}")
        logger.info(f"Nombre de propriétés à récupérer: {len(property_ids)}")
        
        # Récupérer les informations des utilisateurs
        users = {}
        try:
            user_list = users_collection.find({'_id': {'$in': [ObjectId(uid) for uid in user_ids]}})
            for user in user_list:
                users[str(user['_id'])] = {
                    'username': user.get('username', 'Utilisateur inconnu'),
                    'email': user.get('email', ''),
                    'role': user.get('role', 'client')
                }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des utilisateurs: {str(e)}")
            raise
        
        # Ajouter les utilisateurs manquants
        for user_id in user_ids:
            if user_id not in users:
                users[user_id] = {
                    'username': 'Utilisateur supprimé',
                    'email': '',
                    'role': 'unknown'
                }
        
        # Récupérer les informations des propriétés
        properties = {}
        if property_ids:
            try:
                property_list = properties_collection.find({'_id': {'$in': [ObjectId(pid) for pid in property_ids]}})
                for prop in property_list:
                    properties[str(prop['_id'])] = {
                        'title': prop.get('title', 'Bien sans titre'),
                        'type': prop.get('type', ''),
                        'location': prop.get('location', {})
                    }
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des propriétés: {str(e)}")
                raise
            
            # Ajouter les propriétés manquantes
            for pid in property_ids:
                if pid not in properties:
                    properties[pid] = {
                        'title': 'Bien immobilier supprimé',
                        'type': '',
                        'location': {}
                    }
        
        logger.info("Rendu du template messages.html")
        return render_template('messages.html',
                             received_messages=received_messages,
                             sent_messages=sent_messages,
                             users=users,
                             properties=properties)
                             
    except Exception as e:
        logger.error(f"Erreur dans view_messages: {str(e)}")
        logger.error(f"Type d'erreur: {type(e)}")
        logger.error(f"Traceback complet:\n{traceback.format_exc()}")
        flash('Une erreur est survenue lors du chargement des messages', 'error')
        return redirect(url_for('home'))

@app.route('/message/<message_id>/read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    message = messages_collection.find_one({'_id': ObjectId(message_id)})
    
    if not message or str(message['recipient_id']) != current_user.id:
        return jsonify({'success': False, 'message': 'Message non trouvé'})
        
    messages_collection.update_one(
        {'_id': ObjectId(message_id)},
        {'$set': {'read': True}}
    )
    
    return jsonify({'success': True})

@app.route('/property/<property_id>/validate', methods=['POST'])
@login_required
def validate_property(property_id):
    if not current_user.is_agent():
        return jsonify({'success': False, 'message': 'Accès non autorisé'})
        
    status = request.form.get('status')  # 'approved' ou 'rejected'
    feedback = request.form.get('feedback')
    
    if status not in ['approved', 'rejected']:
        return jsonify({'success': False, 'message': 'Statut invalide'})
    
    update_data = {
        'validation_status': status,
        'validation_feedback': feedback,
        'validated_by': current_user.id,
        'validated_at': datetime.utcnow()
    }
    
    if status == 'approved':
        update_data['status'] = 'available'
    
    result = properties_collection.update_one(
        {'_id': ObjectId(property_id)},
        {'$set': update_data}
    )
    
    if result.modified_count > 0:
        # Envoyer une notification au propriétaire
        property_data = properties_collection.find_one({'_id': ObjectId(property_id)})
        message_data = {
            'property_id': ObjectId(property_id),
            'sender_id': ObjectId(current_user.id),
            'recipient_id': ObjectId(property_data['created_by']),
            'subject': f"Validation de votre bien immobilier - {status}",
            'content': feedback,
            'created_at': datetime.utcnow(),
            'read': False
        }
        messages_collection.insert_one(message_data)
        
        return jsonify({
            'success': True,
            'message': 'Statut de validation mis à jour avec succès'
        })
    
    return jsonify({
        'success': False,
        'message': 'Erreur lors de la mise à jour du statut'
    })

@app.route('/property/<property_id>/suggest-price', methods=['POST'])
@login_required
def suggest_property_price(property_id):
    if not current_user.is_agent():
        return jsonify({'success': False, 'message': 'Accès non autorisé'})
        
    suggested_price = float(request.form.get('suggested_price'))
    justification = request.form.get('justification')
    
    property_data = properties_collection.find_one({'_id': ObjectId(property_id)})
    if not property_data:
        return jsonify({'success': False, 'message': 'Bien non trouvé'})
    
    # Enregistrer la suggestion de prix
    suggestion_data = {
        'agent_id': ObjectId(current_user.id),
        'property_id': ObjectId(property_id),
        'current_price': property_data.get('price'),
        'suggested_price': suggested_price,
        'justification': justification,
        'created_at': datetime.utcnow()
    }
    
    db.price_suggestions.insert_one(suggestion_data)
    
    # Envoyer un message au propriétaire
    message_data = {
        'property_id': ObjectId(property_id),
        'sender_id': ObjectId(current_user.id),
        'recipient_id': ObjectId(property_data['created_by']),
        'subject': "Suggestion de prix pour votre bien",
        'content': f"Prix suggéré : {suggested_price}€\n\nJustification : {justification}",
        'created_at': datetime.utcnow(),
        'read': False
    }
    messages_collection.insert_one(message_data)
    
    return jsonify({
        'success': True,
        'message': 'Suggestion de prix envoyée avec succès'
    })

@app.route('/visits')
@login_required
def manage_visits():
    try:
        # Récupérer le filtre depuis les paramètres de l'URL
        status_filter = request.args.get('filter')
        
        # Construire la requête de base
        base_query = {}
        
        # Ajouter le filtre de statut SEULEMENT si spécifié explicitement
        if status_filter and status_filter in ['pending', 'confirmed', 'cancelled', 'completed']:
            base_query['status'] = status_filter

        # Récupérer les visites en fonction du rôle
        if current_user.is_agent():
            # Pour les agents : voir toutes les visites assignées à eux
            base_query['agent_id'] = ObjectId(current_user.id)
            visits_cursor = db.visits.find(base_query).sort('requested_date', -1)
        elif current_user.is_owner():
            # Pour les propriétaires : voir les visites de leurs biens
            owner_properties = list(properties_collection.find({'created_by': ObjectId(current_user.id)}, {'_id': 1}))
            property_ids = [p['_id'] for p in owner_properties]
            base_query['property_id'] = {'$in': property_ids}
            visits_cursor = db.visits.find(base_query).sort('requested_date', -1)
        else:
            # Pour les clients : voir leurs propres visites
            base_query['client_id'] = ObjectId(current_user.id)
            visits_cursor = db.visits.find(base_query).sort('requested_date', -1)
            visits = list(visits_cursor)
            
            if not visits:
                return render_template('visits.html',
                                    visits=[],
                                    properties={},
                                    current_filter=status_filter)
            
            # Récupérer les IDs des propriétés et des agents
            property_ids = set()
            agent_ids = set()
            
            for visit in visits:
                if 'property_id' in visit and visit['property_id']:
                    property_ids.add(visit['property_id'])
                if 'agent_id' in visit and visit['agent_id']:
                    agent_ids.add(visit['agent_id'])
            
            # Récupérer les informations des propriétés
            properties = {}
            if property_ids:
                properties = {
                    str(prop['_id']): prop 
                    for prop in properties_collection.find({'_id': {'$in': list(property_ids)}})
                }
            
            # Récupérer les informations des agents
            agents = {}
            if agent_ids:
                agents = {
                    str(user['_id']): user 
                    for user in users_collection.find({'_id': {'$in': list(agent_ids)}})
                }
            
            # Formater les visites pour l'affichage
            for visit in visits:
                visit['_id'] = str(visit['_id'])
                if 'property_id' in visit and visit['property_id']:
                    visit['property_id'] = str(visit['property_id'])
                if 'agent_id' in visit and visit['agent_id']:
                    agent_id = str(visit['agent_id'])
                    visit['agent_id'] = agent_id
                    agent = agents.get(agent_id, {})
                    visit['agent_name'] = agent.get('username', 'Agent inconnu')
                
                # S'assurer que le champ date est un objet datetime
                if 'requested_date' in visit and not 'date' in visit:
                    visit['date'] = visit['requested_date']
                elif not 'date' in visit and not 'requested_date' in visit:
                    # Utiliser la date de création comme fallback
                    visit['date'] = visit.get('created_at', datetime.utcnow())
            
            return render_template('visits.html',
                                visits=visits,
                                properties=properties,
                                current_filter=status_filter)

        # Pour les autres rôles (agent et propriétaire)
        visits = list(visits_cursor)
        if not visits:
            return render_template('visits.html',
                                visits=[],
                                properties={},
                                current_filter=status_filter)

        # Récupérer les IDs des propriétés et des utilisateurs
        property_ids = {visit['property_id'] for visit in visits}
        client_ids = {visit['client_id'] for visit in visits if 'client_id' in visit}
        agent_ids = {visit.get('agent_id') for visit in visits if visit.get('agent_id')}

        # Récupérer les informations des propriétés
        properties = {
            str(prop['_id']): prop 
            for prop in properties_collection.find({'_id': {'$in': list(property_ids)}})
        }
        
        # Récupérer les informations des clients
        clients = {
            str(user['_id']): user 
            for user in users_collection.find({'_id': {'$in': list(client_ids)}})
        }
        
        # Récupérer les informations des agents
        agents = {
            str(user['_id']): user 
            for user in users_collection.find({'_id': {'$in': list(agent_ids)}})
        } if agent_ids else {}

        # Formater les visites pour l'affichage
        for visit in visits:
            visit['_id'] = str(visit['_id'])
            if 'property_id' in visit and visit['property_id']:
                visit['property_id'] = str(visit['property_id'])
            
            if 'client_id' in visit:
                visit['client_id'] = str(visit['client_id'])
                client = clients.get(visit['client_id'])
                if client:
                    visit['client_name'] = f"{client.get('first_name', '')} {client.get('last_name', '')} ({client.get('username', '')})"
                else:
                    visit['client_name'] = "Client inconnu"
            
            if 'agent_id' in visit and visit['agent_id']:
                agent_id = str(visit['agent_id'])
                visit['agent_id'] = agent_id
                agent = agents.get(agent_id, {})
                visit['agent_name'] = agent.get('username', 'Agent inconnu')
                
            # S'assurer que le champ date est un objet datetime
            if 'requested_date' in visit and not 'date' in visit:
                visit['date'] = visit['requested_date']
            elif not 'date' in visit and not 'requested_date' in visit:
                # Utiliser la date de création comme fallback
                visit['date'] = visit.get('created_at', datetime.utcnow())
        
        return render_template('visits.html',
                            visits=visits,
                            properties=properties,
                            current_filter=status_filter)
                             
    except Exception as e:
        logger.error(f"Erreur générale dans manage_visits: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        return render_template('visits.html',
                            visits=[],
                            properties={},
                            current_filter=status_filter,
                            error_message="Une erreur est survenue lors du chargement des visites.")

@app.route('/visit/schedule', methods=['POST'])
@login_required
def schedule_visit():
    try:
        # Validation des données requises
        property_id = request.form.get('property_id')
        date_str = request.form.get('formatted_date') or request.form.get('date')  # Essayer d'abord la date formatée
        notes = request.form.get('notes', '')

        if not property_id or not date_str:
            return jsonify({
                'success': False,
                'message': 'Veuillez fournir toutes les informations requises'
            }), 400

        try:
            # Essayer d'abord le format français
            try:
                date = datetime.strptime(date_str, '%d/%m/%Y %H:%M')
            except ValueError:
                # Si ça échoue, essayer le format datetime-local
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    # Si ça échoue encore, essayer un autre format courant
                    date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')

            # Vérifier que la date n'est pas dans le passé
            if date < datetime.now():
                return jsonify({
                    'success': False,
                    'message': 'La date de visite ne peut pas être dans le passé'
                }), 400
        except ValueError as e:
            logger.error(f"Erreur de format de date: {str(e)}")
            logger.error(f"Date reçue: {date_str}")
            return jsonify({
                'success': False,
                'message': 'Format de date invalide'
            }), 400

        # Vérifier que le bien existe
        try:
            property_data = properties_collection.find_one({'_id': ObjectId(property_id)})
        except Exception as e:
            logger.error(f"Erreur avec l'ID du bien: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'ID de bien invalide'
            }), 400

        if not property_data:
            return jsonify({
                'success': False,
                'message': 'Bien non trouvé'
            }), 404

        # Vérifier si un agent est assigné
        agent_id = property_data.get('agent_id')
        if not agent_id:
            # Assigner automatiquement un agent disponible
            agent = users_collection.find_one({'role': 'agent'})
            if agent:
                agent_id = agent['_id']
                # Mettre à jour le bien avec l'agent assigné
                properties_collection.update_one(
                    {'_id': ObjectId(property_id)},
                    {'$set': {'agent_id': agent_id}}
                )
            else:
                return jsonify({
                    'success': False,
                    'message': 'Aucun agent disponible pour le moment'
                }), 400

        # Créer la visite
        visit_data = {
            'property_id': ObjectId(property_id),
            'client_id': ObjectId(current_user.id),
            'agent_id': agent_id,
            'date': date,
            'notes': notes,
            'status': 'pending',
            'created_at': datetime.utcnow()
        }

        result = db.visits.insert_one(visit_data)

        if result.inserted_id:
            # Notifier l'agent et le propriétaire
            recipients = []
            if agent_id:
                recipients.append(agent_id)
            if property_data.get('created_by'):
                recipients.append(property_data['created_by'])

            for recipient_id in recipients:
                try:
                    message_data = {
                        'property_id': ObjectId(property_id),
                        'sender_id': ObjectId(current_user.id),
                        'recipient_id': ObjectId(recipient_id),
                        'subject': "Nouvelle demande de visite",
                        'content': f"Date souhaitée : {date.strftime('%d/%m/%Y %H:%M')}\n\nNotes : {notes}",
                        'created_at': datetime.utcnow(),
                        'read': False
                    }
                    messages_collection.insert_one(message_data)
                except Exception as e:
                    logger.error(f"Erreur lors de l'envoi de la notification: {str(e)}")

            return jsonify({
                'success': True,
                'message': 'Demande de visite enregistrée avec succès'
            })

        return jsonify({
            'success': False,
            'message': 'Erreur lors de l\'enregistrement de la visite'
        }), 500

    except Exception as e:
        logger.error(f"Erreur lors de la programmation de la visite: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': 'Une erreur est survenue lors de la programmation de la visite'
        }), 500

@app.route('/visit/<visit_id>/modify', methods=['POST'])
@login_required
def modify_visit(visit_id):
    if not current_user.is_agent():
        return jsonify({'success': False, 'message': 'Accès non autorisé'})
    
    try:
        new_date = datetime.strptime(request.form['new_date'], '%Y-%m-%dT%H:%M')
        notes = request.form.get('notes', '')
        
        # Mettre à jour la visite
        result = db.visits.update_one(
            {'_id': ObjectId(visit_id)},
            {'$set': {
                'date': new_date,
                'notes': notes,
                'updated_at': datetime.utcnow(),
                'updated_by': current_user.id
            }}
        )
        
        if result.modified_count > 0:
            # Récupérer les informations de la visite
            visit = db.visits.find_one({'_id': ObjectId(visit_id)})
            property_data = properties_collection.find_one({'_id': visit['property_id']})
            
            # Notifier le client
            client_message = {
                'property_id': visit['property_id'],
                'sender_id': ObjectId(current_user.id),
                'recipient_id': visit['client_id'],
                'subject': 'Modification de votre rendez-vous de visite',
                'content': f"Votre rendez-vous pour la visite du bien {property_data['title']} a été modifié.\n\nNouvelle date : {new_date.strftime('%d/%m/%Y à %H:%M')}\n\nNotes : {notes}",
                'created_at': datetime.utcnow(),
                'read': False
            }
            messages_collection.insert_one(client_message)
            
            # Notifier le propriétaire
            owner_message = {
                'property_id': visit['property_id'],
                'sender_id': ObjectId(current_user.id),
                'recipient_id': property_data['created_by'],
                'subject': 'Modification d\'une visite',
                'content': f"Une visite pour votre bien {property_data['title']} a été replanifiée.\n\nNouvelle date : {new_date.strftime('%d/%m/%Y à %H:%M')}",
                'created_at': datetime.utcnow(),
                'read': False
            }
            messages_collection.insert_one(owner_message)
            
            return jsonify({
                'success': True,
                'message': 'Visite modifiée avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Aucune modification effectuée'
            })
            
    except Exception as e:
        logger.error(f"Erreur lors de la modification de la visite: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Une erreur est survenue lors de la modification de la visite'
        })

@app.route('/visit/<visit_id>/status', methods=['POST'])
@login_required
def update_visit_status(visit_id):
    if not current_user.is_agent():
        return jsonify({'success': False, 'message': 'Accès non autorisé'})
    
    try:
        data = request.get_json()
        status = data.get('status')
        
        if status not in ['confirmed', 'cancelled', 'completed']:
            return jsonify({'success': False, 'message': 'Statut invalide'})
        
        # Mettre à jour le statut
        result = db.visits.update_one(
            {'_id': ObjectId(visit_id)},
            {'$set': {
                'status': status,
                'updated_at': datetime.utcnow(),
                'updated_by': current_user.id
            }}
        )
        
        if result.modified_count > 0:
            visit = db.visits.find_one({'_id': ObjectId(visit_id)})
            property_data = properties_collection.find_one({'_id': visit['property_id']})
            
            status_messages = {
                'confirmed': 'confirmée',
                'cancelled': 'annulée',
                'completed': 'terminée'
            }
            
            # Créer une notification pour le client
            create_notification(
                user_id=str(visit['client_id']),
                message=f"Votre visite pour le bien {property_data['title']} a été {status_messages[status]}",
                notification_type=status,
                link=url_for('view_property', property_id=str(property_data['_id']))
            )
            
            # Créer une notification pour le propriétaire
            create_notification(
                user_id=str(property_data['created_by']),
                message=f"Une visite pour votre bien {property_data['title']} a été {status_messages[status]}",
                notification_type=status,
                link=url_for('view_property', property_id=str(property_data['_id']))
            )
            
            return jsonify({
                'success': True,
                'message': f'Statut de la visite mis à jour : {status_messages[status]}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Aucune modification effectuée'
            })
            
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du statut de la visite: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Une erreur est survenue lors de la mise à jour du statut'
        })

# Filtres Jinja pour les statuts de visite
@app.template_filter('status_color')
def status_color(status):
    colors = {
        'pending': 'warning',
        'confirmed': 'success',
        'cancelled': 'danger',
        'completed': 'info'
    }
    return colors.get(status, 'secondary')

@app.template_filter('status_label')
def status_label(status):
    labels = {
        'pending': 'En attente',
        'confirmed': 'Confirmée',
        'cancelled': 'Annulée',
        'completed': 'Terminée'
    }
    return labels.get(status, status)

# Filtre Jinja pour formater les nombres
@app.template_filter('number_format')
def number_format(value, decimals=0):
    if value is None:
        return ''
    try:
        value = float(value)
        format_string = f'{{:,.{decimals}f}}'
        return format_string.format(value).replace(',', ' ')
    except (ValueError, TypeError):
        return value

# Filtre pour formater les dates
@app.template_filter('datetime')
def format_datetime(value):
    """Format a datetime object to a French readable string"""
    if not value:
        return ''
    try:
        if isinstance(value, str):
            value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
        return value.strftime('%d/%m/%Y à %H:%M')
    except (ValueError, TypeError):
        return str(value)

# Ajouter après l'initialisation de l'app mais avant les routes
@app.context_processor
def utility_processor():
    def get_unread_messages_count():
        if not current_user.is_authenticated:
            return 0
        return messages_collection.count_documents({
            'recipient_id': ObjectId(current_user.id),
            'read': False
        })
    
    def get_notifications():
        if current_user.is_authenticated:
            return list(notifications_collection.find({
                'user_id': ObjectId(current_user.id),
                'read': False
            }).sort('created_at', -1).limit(5))
        return []
        
    def get_notifications_count():
        if current_user.is_authenticated:
            return notifications_collection.count_documents({
                'user_id': ObjectId(current_user.id),
                'read': False
            })
        return 0
        
    def get_pending_visits_count():
        if current_user.is_authenticated and current_user.is_agent():
            count = db.visits.count_documents({'status': 'pending', 'agent_id': ObjectId(current_user.id)})
            return count if count > 0 else None
        return None
        
    def get_user_visits_count():
        if current_user.is_authenticated:
            try:
                query = None
                if current_user.is_agent():
                    query = {'agent_id': ObjectId(current_user.id)}
                elif current_user.is_owner():
                    owner_properties = list(properties_collection.find(
                        {'created_by': ObjectId(current_user.id)},
                        {'_id': 1}
                    ))
                    if not owner_properties:
                        return None
                    property_ids = [p['_id'] for p in owner_properties]
                    query = {'property_id': {'$in': property_ids}}
                else:
                    query = {'client_id': ObjectId(current_user.id)}
                
                count = db.visits.count_documents(query) if query else 0
                return count if count > 0 else None
            except Exception as e:
                logger.error(f"Erreur dans get_user_visits_count: {str(e)}")
                return None
        return None
        
    return {
        'notifications': get_notifications(),
        'notifications_count': get_notifications_count(),
        'pending_visits_count': get_pending_visits_count(),
        'user_visits_count': get_user_visits_count(),
        'unread_messages_count': get_unread_messages_count()
    }

def create_notification(user_id, message, notification_type, link=None):
    """Crée une notification"""
    try:
        # Créer la notification dans la base de données
        notification = {
            'user_id': ObjectId(user_id),
            'message': message,
            'type': notification_type,
            'link': link,
            'read': False,
            'created_at': datetime.utcnow()
        }
        result = notifications_collection.insert_one(notification)
        return True if result.inserted_id else False
    except Exception as e:
        logger.error(f"Erreur lors de la création de la notification: {str(e)}")
        return False

@app.route('/notification/mark-read/<notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    try:
        # Vérifier que la notification existe et appartient à l'utilisateur
        notification = notifications_collection.find_one({
            '_id': ObjectId(notification_id),
            'user_id': ObjectId(current_user.id)
        })

        if not notification:
            return jsonify({
                'success': False,
                'message': 'Notification non trouvée'
            })

        # Marquer comme lu
        notifications_collection.update_one(
            {'_id': ObjectId(notification_id)},
            {'$set': {'read': True}}
        )

        return jsonify({
            'success': True,
            'message': 'Notification marquée comme lue'
        })

    except Exception as e:
        logger.error(f"Erreur lors du marquage de la notification: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Une erreur est survenue'
        })

@app.route('/notifications')
@login_required
def view_notifications():
    try:
        notifications = list(notifications_collection.find({
            'user_id': ObjectId(current_user.id)
        }).sort('created_at', -1))

        # Convertir les ObjectId en str
        for notif in notifications:
            notif['_id'] = str(notif['_id'])

        return render_template('notifications.html', notifications=notifications)
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage des notifications: {str(e)}")
        flash('Une erreur est survenue lors du chargement des notifications', 'error')
        return redirect(url_for('home'))

@app.route('/property/<property_id>/create-offer', methods=['GET', 'POST'])
@login_required
def create_property_offer(property_id):
    try:
        # Vérifier que le bien existe et appartient au propriétaire
        property_data = properties_collection.find_one({
            '_id': ObjectId(property_id)
        })
        
        if not property_data:
            flash('Bien non trouvé', 'error')
            return redirect(url_for('home'))

        # Vérifier que l'utilisateur est le propriétaire du bien
        if not current_user.is_owner() or str(property_data['created_by']) != current_user.id:
            flash('Accès non autorisé', 'error')
            return redirect(url_for('view_property', property_id=property_id))
            
        if request.method == 'POST':
            offer_data = {
                'property_id': ObjectId(property_id),
                'owner_id': ObjectId(current_user.id),
                'title': request.form.get('title'),
                'description': request.form.get('description'),
                'original_price': float(property_data.get('price', 0)),
                'offer_price': float(request.form.get('offer_price')),
                'start_date': datetime.strptime(request.form.get('start_date'), '%Y-%m-%d'),
                'end_date': datetime.strptime(request.form.get('end_date'), '%Y-%m-%d'),
                'conditions': request.form.get('conditions'),
                'status': 'active',
                'created_at': datetime.utcnow()
            }
            
            # Vérifier les dates
            if offer_data['end_date'] <= offer_data['start_date']:
                flash('La date de fin doit être postérieure à la date de début', 'error')
                return render_template('property/create_offer.html', property=property_data)
                
            # Vérifier le prix
            if offer_data['offer_price'] >= offer_data['original_price']:
                flash('Le prix de l\'offre doit être inférieur au prix original', 'error')
                return render_template('property/create_offer.html', property=property_data)
            
            # Insérer l'offre
            result = db.property_offers.insert_one(offer_data)
            
            if result.inserted_id:
                # Créer une notification pour les agents
                agents = users_collection.find({'role': 'agent'})
                for agent in agents:
                    create_notification(
                        user_id=str(agent['_id']),
                        message=f"Nouvelle offre sur le bien {property_data['title']}",
                        notification_type='new_offer',
                        link=url_for('view_property', property_id=property_id)
                    )
                
                flash('Offre créée avec succès', 'success')
                return redirect(url_for('view_property', property_id=property_id))
            else:
                flash('Erreur lors de la création de l\'offre', 'error')
                
        return render_template('property/create_offer.html', 
                             property=property_data,
                             now=datetime.utcnow())
        
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'offre: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        flash('Une erreur est survenue lors de la création de l\'offre', 'error')
        return redirect(url_for('view_property', property_id=property_id))

@app.route('/property/<property_id>/offers')
@login_required
def view_property_offers(property_id):
    try:
        property_data = properties_collection.find_one({'_id': ObjectId(property_id)})
        if not property_data:
            flash('Bien non trouvé', 'error')
            return redirect(url_for('home'))
            
        # Récupérer les offres actives pour ce bien
        offers = list(db.property_offers.find({
            'property_id': ObjectId(property_id),
            'status': 'active',
            'end_date': {'$gte': datetime.utcnow()}
        }).sort('created_at', -1))
        
        # Convertir les ObjectId en str
        for offer in offers:
            offer['_id'] = str(offer['_id'])
            offer['property_id'] = str(offer['property_id'])
            offer['owner_id'] = str(offer['owner_id'])
            
        return render_template('property/offers.html',
                             property=property_data,
                             offers=offers)
                             
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage des offres: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        flash('Une erreur est survenue lors du chargement des offres', 'error')
        return redirect(url_for('home'))

@app.route('/property/offer/<offer_id>/cancel', methods=['POST'])
@login_required
def cancel_property_offer(offer_id):
    try:
        # Vérifier que l'offre existe et appartient au propriétaire
        offer = db.property_offers.find_one({
            '_id': ObjectId(offer_id),
            'owner_id': ObjectId(current_user.id)
        })
        
        if not offer:
            return jsonify({
                'success': False,
                'message': 'Offre non trouvée ou accès non autorisé'
            })
            
        # Mettre à jour le statut
        result = db.property_offers.update_one(
            {'_id': ObjectId(offer_id)},
            {'$set': {
                'status': 'cancelled',
                'cancelled_at': datetime.utcnow()
            }}
        )
        
        if result.modified_count > 0:
            return jsonify({
                'success': True,
                'message': 'Offre annulée avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erreur lors de l\'annulation de l\'offre'
            })
            
    except Exception as e:
        logger.error(f"Erreur lors de l'annulation de l'offre: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Une erreur est survenue'
        })

@app.route('/property/<property_id>/assign-agent', methods=['GET', 'POST'])
@login_required
def assign_agent(property_id):
    try:
        # Vérifier que le bien existe et appartient au propriétaire
        property_data = properties_collection.find_one({
            '_id': ObjectId(property_id)
        })
        
        if not property_data:
            flash('Bien non trouvé', 'error')
            return redirect(url_for('home'))

        # Vérifier que l'utilisateur est le propriétaire du bien
        if not current_user.is_owner() or str(property_data['created_by']) != current_user.id:
            flash('Accès non autorisé', 'error')
            return redirect(url_for('view_property', property_id=property_id))

        if request.method == 'POST':
            agent_id = request.form.get('agent_id')
            if not agent_id:
                flash('Veuillez sélectionner un agent', 'error')
                return redirect(url_for('assign_agent', property_id=property_id))

            # Vérifier que l'agent existe et est bien un agent
            agent = users_collection.find_one({
                '_id': ObjectId(agent_id),
                'role': 'agent'
            })

            if not agent:
                flash('Agent non trouvé', 'error')
                return redirect(url_for('assign_agent', property_id=property_id))

            # Mettre à jour le bien avec l'agent assigné
            result = properties_collection.update_one(
                {'_id': ObjectId(property_id)},
                {'$set': {
                    'agent_id': ObjectId(agent_id),
                    'agent_assigned_at': datetime.utcnow()
                }}
            )

            if result.modified_count > 0:
                # Notifier l'agent
                create_notification(
                    user_id=agent_id,
                    message=f"Vous avez été assigné au bien : {property_data['title']}",
                    notification_type='agent_assignment',
                    link=url_for('view_property', property_id=property_id)
                )
                
                # Envoyer un message automatique à l'agent
                message_data = {
                    'property_id': ObjectId(property_id),
                    'sender_id': ObjectId(current_user.id),
                    'recipient_id': ObjectId(agent_id),
                    'subject': f"Assignation au bien : {property_data['title']}",
                    'content': "Vous avez été assigné comme agent pour ce bien. Veuillez prendre en charge sa gestion.",
                    'created_at': datetime.utcnow(),
                    'read': False
                }
                messages_collection.insert_one(message_data)

                flash('Agent assigné avec succès', 'success')
                return redirect(url_for('view_property', property_id=property_id))
            else:
                flash('Erreur lors de l\'assignation de l\'agent', 'error')

        # Récupérer la liste des agents disponibles
        agents = list(users_collection.find({'role': 'agent'}).sort('username', 1))
        return render_template('property/assign_agent.html',
                             property=property_data,
                             agents=agents,
                             current_agent_id=str(property_data.get('agent_id', '')))

    except Exception as e:
        logger.error(f"Erreur lors de l'assignation de l'agent: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        flash('Une erreur est survenue', 'error')
        return redirect(url_for('view_property', property_id=property_id))

@app.route('/message/<message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id):
    try:
        # Vérifier que le message existe et appartient à l'utilisateur (envoyé ou reçu)
        message = messages_collection.find_one({
            '_id': ObjectId(message_id),
            '$or': [
                {'sender_id': ObjectId(current_user.id)},
                {'recipient_id': ObjectId(current_user.id)}
            ]
        })
        
        if not message:
            return jsonify({
                'success': False,
                'message': 'Message non trouvé ou accès non autorisé'
            })
            
        # Supprimer le message
        result = messages_collection.delete_one({'_id': ObjectId(message_id)})
        
        if result.deleted_count > 0:
            return jsonify({
                'success': True,
                'message': 'Message supprimé avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erreur lors de la suppression du message'
            })
            
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du message: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Une erreur est survenue lors de la suppression'
        })

if __name__ == '__main__':
    # Création des dossiers nécessaires
    os.makedirs(os.path.join('static', 'contracts'), exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Démarrage du serveur avec Waitress
    print("Démarrage du serveur sur http://127.0.0.1:5000")
    serve(app, host='127.0.0.1', port=5000, threads=4, _quiet=True) 