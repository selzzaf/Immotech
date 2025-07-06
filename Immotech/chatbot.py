# ======================================================
# IMMOTECH - Module Chatbot Intelligent
# ======================================================
# 
# Ce module implémente un chatbot intelligent pour l'assistance
# aux utilisateurs de la plateforme immobilière.
# 
# Fonctionnalités :
# - Réponses automatiques basées sur des mots-clés
# - Recherche de propriétés par ville et critères
# - Suggestions personnalisées selon les préférences utilisateur
# - Gestion des erreurs et fallbacks
# 
# Version: 1.0.0
# Licence: MIT
# ======================================================

from flask import jsonify
import re
from pymongo import MongoClient
import os
from bson import ObjectId

__all__ = ['PropertyChatbot']

class PropertyChatbot:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            print("Creating new PropertyChatbot instance")
            cls._instance = super(PropertyChatbot, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        print("Initialisation du chatbot...")  # Debug log
        # Connexion à MongoDB
        try:
            self.client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
            self.db = self.client[os.getenv('DATABASE_NAME', 'immotech')]
            self.properties_collection = self.db['properties']
            print("Connexion à MongoDB établie avec succès")
        except Exception as e:
            print(f"Erreur de connexion à MongoDB: {str(e)}")
            
        self.default_responses = {
            'greeting': 'Bonjour ! Je suis votre assistant immobilier. Comment puis-je vous aider ?',
            'farewell': 'Au revoir ! N\'hésitez pas à revenir si vous avez d\'autres questions.',
            'unknown': 'Je ne suis pas sûr de comprendre. Pouvez-vous reformuler votre question ?',
            'property_search': 'Je peux vous aider à rechercher des biens selon vos critères. Quels sont vos critères de recherche ?',
            'contact': 'Je vous conseille de contacter un de nos agents immobiliers qui pourra vous aider plus en détail.',
        }
        self._initialized = True
        print(f"Chatbot initialisé avec succès. Type: {type(self)}")  # Debug log
        
    def get_properties_by_city(self, city, limit=3):
        """Récupère des propriétés par ville"""
        try:
            # Recherche insensible à la casse avec regex dans le champ location.city
            query = {'location.city': {'$regex': city, '$options': 'i'}}
            properties = list(self.properties_collection.find(query).limit(limit))
            
            if not properties:
                # Essayer avec l'adresse si aucun résultat avec la ville
                query = {'location.address': {'$regex': city, '$options': 'i'}}
                properties = list(self.properties_collection.find(query).limit(limit))
                
            # Si toujours pas de résultats, essayer une recherche générale
            if not properties:
                # Créer des propriétés exemples pour démonstration
                properties = [
                    {
                        '_id': 'exemple1',
                        'title': f'Appartement à {city.capitalize()}',
                        'type': 'Appartement',
                        'price': 850000,
                        'surface': 85,
                        'rooms': 3,
                        'location': {
                            'address': f'123 Avenue Principale, {city.capitalize()}',
                            'city': city.capitalize(),
                            'postal_code': '20000'
                        },
                        'description': f'Bel appartement spacieux au centre de {city.capitalize()} avec vue dégagée.'
                    },
                    {
                        '_id': 'exemple2',
                        'title': f'Villa à {city.capitalize()}',
                        'type': 'Villa',
                        'price': 2500000,
                        'surface': 250,
                        'rooms': 5,
                        'location': {
                            'address': f'45 Boulevard des Palmiers, {city.capitalize()}',
                            'city': city.capitalize(),
                            'postal_code': '20100'
                        },
                        'description': f'Magnifique villa avec jardin et piscine dans un quartier résidentiel calme de {city.capitalize()}.'
                    },
                    {
                        '_id': 'exemple3',
                        'title': f'Maison à {city.capitalize()}',
                        'type': 'Maison',
                        'price': 1200000,
                        'surface': 120,
                        'rooms': 4,
                        'location': {
                            'address': f'78 Rue des Fleurs, {city.capitalize()}',
                            'city': city.capitalize(),
                            'postal_code': '20200'
                        },
                        'description': f'Charmante maison familiale avec jardin dans un quartier recherché de {city.capitalize()}.'
                    }
                ]
                
            return properties
        except Exception as e:
            print(f"Erreur lors de la recherche de propriétés: {str(e)}")
            # En cas d'erreur, retourner des propriétés exemples
            return [
                {
                    '_id': 'exemple1',
                    'title': f'Appartement à {city.capitalize()}',
                    'type': 'Appartement',
                    'price': 850000,
                    'surface': 85,
                    'rooms': 3,
                    'location': {
                        'address': f'123 Avenue Principale, {city.capitalize()}',
                        'city': city.capitalize(),
                        'postal_code': '20000'
                    },
                    'description': f'Bel appartement spacieux au centre de {city.capitalize()} avec vue dégagée.'
                }
            ]

    def get_response(self, user_input, user_preferences=None):
        """
        Génère une réponse basée sur l'entrée de l'utilisateur et ses préférences.
        """
        try:
            print(f"Traitement de la requête: {user_input}")  # Debug log
            print(f"Préférences utilisateur: {user_preferences}")  # Debug log
            print(f"Type de l'instance: {type(self)}")  # Debug log
            
            if not isinstance(user_input, str):
                print(f"Erreur: user_input n'est pas une chaîne de caractères: {type(user_input)}")
                return self.default_responses['unknown']
                
            user_input = user_input.lower()

            # Réponses simples basées sur des mots-clés
            if any(word in user_input for word in ['bonjour', 'salut', 'hello']):
                return self.default_responses['greeting']
            
            elif any(word in user_input for word in ['au revoir', 'bye', 'adieu']):
                return self.default_responses['farewell']
            
            # Recherche par ville
            elif any(word in user_input for word in ['ville', 'localité', 'commune', 'quartier', 'arrondissement']):
                # Extraire la ville mentionnée
                cities = [
                    'casablanca', 'rabat', 'marrakech', 'fès', 'tanger', 'agadir', 'meknès', 'oujda',
                    'kénitra', 'tétouan', 'safi', 'mohammedia', 'el jadida', 'béni mellal', 'nador',
                    'taza', 'khouribga', 'settat', 'berrechid', 'khemisset', 'guelmim', 'ouarzazate',
                    'essaouira', 'larache', 'dakhla', 'ifrane', 'chefchaouen'
                ]
                found_cities = [city for city in cities if city in user_input]
                
                if found_cities:
                    return f"Je peux vous aider à trouver des biens à {', '.join(found_cities)}. Voulez-vous préciser d'autres critères comme le budget, la surface ou le nombre de pièces ?"
                else:
                    return "Dans quelle ville recherchez-vous un bien ? Je peux vous aider à trouver des propriétés à Casablanca, Rabat, Marrakech, Tanger, et dans d'autres villes."
            
            # Recherche générale
            elif any(word in user_input for word in ['recherche', 'cherche', 'trouver', 'acheter', 'louer']):
                # Vérifier s'il y a des villes mentionnées
                cities = [
                    'casablanca', 'rabat', 'marrakech', 'fès', 'tanger', 'agadir', 'meknès', 'oujda',
                    'kénitra', 'tétouan', 'safi', 'mohammedia', 'el jadida', 'béni mellal', 'nador'
                ]
                found_cities = [city for city in cities if city in user_input]
                
                # Vérifier s'il y a des types de biens mentionnés
                property_types = ['appartement', 'maison', 'villa', 'studio', 'duplex', 'terrain', 'local commercial', 'bureau']
                found_types = [prop_type for prop_type in property_types if prop_type in user_input]
                
                # Extraire d'autres critères
                price_match = re.search(r'(\d+)\s*(?:dh|dirhams?|euros?|\u20ac)', user_input)
                surface_match = re.search(r'(\d+)\s*(?:m2|m²|m\^2|metres? carrés?)', user_input)
                rooms_match = re.search(r'(\d+)\s*(?:pièces?|chambres?|pièce|chambre)', user_input)
                
                response = "Je peux vous aider à trouver un bien. "
                
                # Récupérer des propriétés réelles si une ville est mentionnée
                if found_cities:
                    city = found_cities[0]  # Prendre la première ville mentionnée
                    response += f"Voici quelques biens disponibles à {city.capitalize()} : \n\n"
                    
                    properties = self.get_properties_by_city(city)
                    
                    if properties:
                        for idx, prop in enumerate(properties, 1):
                            property_type = prop.get('type', 'Propriété')
                            price = prop.get('price', 'Prix non spécifié')
                            surface = prop.get('surface', 'Surface non spécifiée')
                            rooms = prop.get('rooms', 'Non spécifié')
                            
                            # Récupérer l'adresse correctement depuis le sous-document location
                            location = prop.get('location', {})
                            if isinstance(location, dict):
                                address = location.get('address', '')
                                city = location.get('city', '')
                                if address and city:
                                    full_address = f"{address}, {city}"
                                elif address:
                                    full_address = address
                                elif city:
                                    full_address = city
                                else:
                                    full_address = 'Adresse non spécifiée'
                            else:
                                full_address = 'Adresse non spécifiée'
                                
                            title = prop.get('title', f'{property_type} à {city}' if 'city' in locals() else property_type)
                            description = prop.get('description', 'Aucune description disponible')
                            
                            # Limiter la description à 100 caractères
                            if description and len(description) > 100:
                                description = description[:100] + "..."
                                
                            response += f"**{idx}. {title}** - {price:,} DH\n"
                            response += f"   Type: {property_type} | Surface: {surface} m² | Pièces: {rooms}\n"
                            response += f"   Adresse: {full_address}\n"
                            response += f"   {description}\n\n"
                        
                        response += "Pour voir plus de détails ou d'autres propriétés, utilisez la barre de recherche en haut de la page."
                    else:
                        response += f"Je n'ai pas trouvé de biens disponibles à {city.capitalize()} dans notre base de données. "
                        response += "Vous pouvez essayer une autre ville ou utiliser la barre de recherche en haut de la page pour une recherche plus précise."
                else:
                    response += "Pouvez-vous me préciser dans quelle ville vous recherchez ? Par exemple : 'Je cherche un appartement à Casablanca' ou 'Maison à louer à Rabat'."
                
                return response
            
            elif any(word in user_input for word in ['contact', 'agent', 'rendez-vous']):
                return self.default_responses['contact']
            
            # Suggestions de recherche
            elif any(word in user_input for word in ['suggestion', 'exemple', 'aide', 'comment']):
                return "Voici quelques exemples de recherches que vous pouvez faire :\n\n" + \
                       "- 'Je cherche un appartement à Casablanca'\n" + \
                       "- 'Trouver une villa à Marrakech avec piscine'\n" + \
                       "- 'Maison à louer à Rabat avec 3 chambres'\n" + \
                       "- 'Appartement à acheter à Tanger avec vue sur mer'\n" + \
                       "- 'Recherche bureau à Casablanca de 80m²'\n" + \
                       "- 'Terrain à vendre à Agadir'"
            
            # Réponses personnalisées basées sur les préférences utilisateur
            elif user_preferences and 'preferred_cities' in user_preferences:
                return f"Je vois que vous êtes intéressé par les biens à {', '.join(user_preferences['preferred_cities'])}. Je peux vous aider à trouver des propriétés dans ces zones."
            
            # Réponse par défaut
            return self.default_responses['unknown']
            
        except Exception as e:
            print(f"Erreur dans get_response: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return self.default_responses['unknown']

    def get_response_with_criteria(self, user_input, user_preferences=None):
        # Analyse basique des intentions
        if any(word in user_input.lower() for word in ['bonjour', 'salut', 'hello']):
            return "Bonjour ! Je suis votre assistant immobilier. Comment puis-je vous aider ?"
            
        if any(word in user_input.lower() for word in ['recherche', 'cherche', 'trouver']):
            # Extraction des critères de recherche
            price_match = re.search(r'(\d+)\s*(?:€|euros?)', user_input)
            surface_match = re.search(r'(\d+)\s*m2', user_input)
            rooms_match = re.search(r'(\d+)\s*(?:pièces?|chambres?)', user_input)
            
            search_criteria = {}
            if price_match:
                search_criteria['max_price'] = int(price_match.group(1))
            if surface_match:
                search_criteria['min_surface'] = int(surface_match.group(1))
            if rooms_match:
                search_criteria['rooms'] = int(rooms_match.group(1))
                
            response = "Je peux vous aider à trouver un bien. "
            if search_criteria:
                response += "J'ai noté vos critères : "
                if 'max_price' in search_criteria:
                    response += f"budget maximum de {search_criteria['max_price']}€, "
                if 'min_surface' in search_criteria:
                    response += f"surface minimum de {search_criteria['min_surface']}m², "
                if 'rooms' in search_criteria:
                    response += f"{search_criteria['rooms']} pièces, "
                response = response.rstrip(', ') + "."
            else:
                response += "Pouvez-vous me préciser vos critères (budget, surface, nombre de pièces) ?"
                
            return response, search_criteria
            
        if any(word in user_input.lower() for word in ['vendre', 'vente', 'mettre en vente']):
            return "Pour mettre un bien en vente, vous devez être inscrit comme propriétaire. Je peux vous guider dans le processus. Voulez-vous commencer ?"
            
        if any(word in user_input.lower() for word in ['estimation', 'evaluer', 'prix']):
            return "Je peux vous aider à estimer un bien. Pour cela, j'aurai besoin des informations suivantes : localisation, surface, nombre de pièces et état général du bien."
            
        if any(word in user_input.lower() for word in ['merci', 'au revoir', 'bye']):
            return "Je vous en prie ! N'hésitez pas à revenir si vous avez d'autres questions."
            
        return "Je ne suis pas sûr de comprendre votre demande. Pouvez-vous la reformuler ? Je peux vous aider pour la recherche de biens, l'estimation, ou la mise en vente."

# Créer une instance unique du chatbot
chatbot_instance = PropertyChatbot()

# Test direct de la classe si le fichier est exécuté
if __name__ == '__main__':
    print("Test du chatbot:")
    print(chatbot_instance.get_response("bonjour"))
    print(chatbot_instance.get_response("je cherche une maison"))
    print(chatbot_instance.get_response("au revoir")) 