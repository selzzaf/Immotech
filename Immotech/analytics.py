# ======================================================
# IMMOTECH - Module d'Analyses et Statistiques
# ======================================================
# 
# Ce module gère toutes les analyses et statistiques de la plateforme
# immobilière, incluant les rapports de marché, les tendances de prix,
# et les analyses d'activité utilisateur.
# 
# Fonctionnalités :
# - Analyse des tendances de prix
# - Rapports de marché détaillés
# - Statistiques d'activité utilisateur
# - Génération de graphiques et visualisations
# - Calculs de métriques immobilières
# 
# Version: 1.0.0
# Licence: MIT
# ======================================================

from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import numpy as np
from bson import ObjectId
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsManager:
    def __init__(self, db):
        self.db = db
        
    def get_price_trends(self, city=None, property_type=None, period_days=365):
        start_date = datetime.utcnow() - timedelta(days=period_days)
        
        # Construction de la requête
        match_query = {
            'created_at': {'$gte': start_date}
        }
        if city:
            match_query['location.city'] = city
        if property_type:
            match_query['type'] = property_type
            
        # Agrégation des données
        pipeline = [
            {'$match': match_query},
            {'$group': {
                '_id': {
                    'year': {'$year': '$created_at'},
                    'month': {'$month': '$created_at'}
                },
                'avg_price': {'$avg': '$price'},
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id.year': 1, '_id.month': 1}}
        ]
        
        results = list(self.db.properties.aggregate(pipeline))
        
        # Conversion en DataFrame pour analyse
        df = pd.DataFrame(results)
        if df.empty:
            return None, None
            
        # Création du graphique
        plt.figure(figsize=(10, 6))
        plt.plot(range(len(df)), df['avg_price'], marker='o')
        plt.title('Évolution des prix moyens')
        plt.xlabel('Période')
        plt.ylabel('Prix moyen (€)')
        
        # Sauvegarde du graphique en base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        graphic = base64.b64encode(image_png).decode('utf-8')
        
        return df.to_dict('records'), graphic
        
    def get_market_analysis(self, city=None):
        # Analyse du marché par type de bien
        pipeline = [
            {'$group': {
                '_id': '$type',
                'count': {'$sum': 1},
                'avg_price': {'$avg': '$price'},
                'avg_surface': {'$avg': '$surface'},
                'price_per_m2': {'$avg': {'$divide': ['$price', '$surface']}}
            }},
            {'$sort': {'count': -1}}
        ]
        
        if city:
            pipeline.insert(0, {'$match': {'location.city': city}})
            
        market_analysis = list(self.db.properties.aggregate(pipeline))
        
        # Création de visualisations
        if market_analysis:
            df = pd.DataFrame(market_analysis)
            
            # Graphique de répartition des types de biens
            plt.figure(figsize=(10, 6))
            plt.pie(df['count'], labels=df['_id'], autopct='%1.1f%%')
            plt.title('Répartition des types de biens')
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            pie_chart = base64.b64encode(image_png).decode('utf-8')
            
            # Graphique des prix moyens par type
            plt.figure(figsize=(10, 6))
            plt.bar(df['_id'], df['avg_price'])
            plt.title('Prix moyen par type de bien')
            plt.xticks(rotation=45)
            plt.ylabel('Prix moyen (€)')
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            bar_chart = base64.b64encode(image_png).decode('utf-8')
            
            return market_analysis, pie_chart, bar_chart
        
        return None, None, None
        
    def get_user_activity_report(self, user_id):
        """
        Génère un rapport d'activité pour un utilisateur spécifique.
        """
        try:
            user_id_obj = ObjectId(user_id)
            
            # Récupérer les propriétés de l'utilisateur
            properties = list(self.db.properties.find({
                'created_by': user_id
            }).sort('created_at', -1))

            # Récupérer les transactions de l'utilisateur (achat et vente)
            transactions = list(self.db.transactions.find({
                '$or': [
                    {'buyer_id': user_id_obj},
                    {'seller_id': user_id_obj}
                ]
            }).sort('created_at', -1))

            # Enrichir les transactions avec les détails des propriétés
            for transaction in transactions:
                property_data = self.db.properties.find_one({'_id': transaction['property_id']})
                if property_data:
                    transaction['property'] = property_data

            return {
                'properties': properties,
                'total_properties': len(properties),
                'transactions': transactions,
                'total_transactions': len(transactions),
                'stats': {
                    'properties_value': sum(float(p.get('price', 0)) for p in properties),
                    'transactions_value': sum(float(t.get('amount', 0)) for t in transactions),
                    'active_listings': sum(1 for p in properties if p.get('status') == 'available')
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport d'activité: {str(e)}")
            return None
        
    def generate_market_report(self, city='', property_type='', transaction_type=''):
        try:
            # Construire le filtre de requête
            query = {}
            if city:
                query['location.city'] = {'$regex': city, '$options': 'i'}
            if property_type:
                query['type'] = property_type
            if transaction_type:
                query['transaction_type'] = transaction_type

            # Récupérer les propriétés correspondantes
            properties = list(self.db.properties.find(query))
            
            if not properties:
                return None

            # Calculer les statistiques
            total_properties = len(properties)
            available_properties = len([p for p in properties if p.get('status') == 'available'])
            
            prices = [float(p.get('price', 0)) for p in properties]
            average_price = sum(prices) / len(prices) if prices else 0
            
            surfaces = [float(p.get('surface', 0)) for p in properties]
            total_surface = sum(surfaces)
            price_per_sqm = average_price / (total_surface / len(properties)) if total_surface > 0 else 0
            
            # Calculer le temps moyen sur le marché
            now = datetime.utcnow()
            time_on_market = []
            for p in properties:
                if p.get('created_at'):
                    if isinstance(p['created_at'], str):
                        try:
                            created_at = datetime.strptime(p['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                        except ValueError:
                            created_at = datetime.strptime(p['created_at'], '%Y-%m-%d %H:%M:%S')
                    else:
                        created_at = p['created_at']
                    time_on_market.append((now - created_at).days)
            
            average_time_on_market = sum(time_on_market) / len(time_on_market) if time_on_market else 0
            
            # Calculer le taux de négociation
            sold_properties = [p for p in properties if p.get('status') == 'sold']
            if sold_properties:
                original_prices = [float(p.get('original_price', p.get('price', 0))) for p in sold_properties]
                final_prices = [float(p.get('price', 0)) for p in sold_properties]
                negotiation_rate = (sum(original_prices) - sum(final_prices)) / sum(original_prices) if sum(original_prices) > 0 else 0
            else:
                negotiation_rate = 0
            
            # Historique des prix sur les 6 derniers mois
            six_months_ago = now - timedelta(days=180)
            price_history = list(self.db.properties.aggregate([
                {
                    '$match': {
                        **query,
                        'created_at': {'$gte': six_months_ago}
                    }
                },
                {
                    '$group': {
                        '_id': {
                            'year': {'$year': '$created_at'},
                            'month': {'$month': '$created_at'}
                        },
                        'average_price': {'$avg': '$price'}
                    }
                },
                {'$sort': {'_id.year': 1, '_id.month': 1}}
            ]))
            
            # Distribution des surfaces
            surface_ranges = [
                {'min': 0, 'max': 50},
                {'min': 50, 'max': 100},
                {'min': 100, 'max': 150},
                {'min': 150, 'max': 200},
                {'min': 200, 'max': float('inf')}
            ]
            
            surface_distribution = {
                f"{r['min']}-{r['max']}": len([
                    p for p in properties
                    if float(r['min']) <= float(p.get('surface', 0)) < float(r['max'])
                ])
                for r in surface_ranges
            }
            
            # Formater les tendances de prix
            price_trend = []
            for h in price_history:
                try:
                    price_trend.append({
                        'period': f"{h['_id']['month']}/{h['_id']['year']}",
                        'price': round(float(h['average_price']), 2)
                    })
                except (KeyError, TypeError, ValueError) as e:
                    logger.error(f"Erreur lors du formatage des prix: {str(e)}")
                    continue
            
            return {
                'total_properties': total_properties,
                'available_properties': available_properties,
                'average_price': round(average_price, 2),
                'price_per_sqm': round(price_per_sqm, 2),
                'average_time_on_market': round(average_time_on_market, 1),
                'negotiation_rate': round(negotiation_rate * 100, 1),
                'price_trend': price_trend,
                'surface_distribution': surface_distribution,
                'transaction_type': transaction_type,
                'property_type': property_type,
                'city': city
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
            return None

    def get_price_history(self, query):
        """
        Récupère l'historique des prix sur les 12 derniers mois
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=365)
            query['created_at'] = {'$gte': start_date}
            
            pipeline = [
                {'$match': query},
                {'$group': {
                    '_id': {
                        'year': {'$year': '$created_at'},
                        'month': {'$month': '$created_at'}
                    },
                    'average_price': {'$avg': '$price'}
                }},
                {'$sort': {'_id.year': 1, '_id.month': 1}}
            ]
            
            results = list(self.db.properties.aggregate(pipeline))
            logger.info(f"Retrieved price history data: {len(results)} data points")
            
            # Formater les données pour Chart.js
            labels = []
            prices = []
            
            for result in results:
                month_year = f"{result['_id']['month']}/{result['_id']['year']}"
                labels.append(month_year)
                prices.append(round(float(result['average_price']), 2))
                
            return {
                'labels': labels,
                'prices': prices
            }
            
        except Exception as e:
            logger.error(f"Error getting price history: {str(e)}")
            return {'labels': [], 'prices': []}

    def get_surface_distribution(self, surfaces):
        """
        Calcule la distribution des surfaces pour le graphique
        """
        try:
            if not surfaces:
                logger.warning("No surface data available")
                return {'labels': [], 'data': []}
                
            # Créer des tranches de surface
            bins = [0, 50, 100, 150, 200, 250, 300, float('inf')]
            labels = ['0-50m²', '50-100m²', '100-150m²', '150-200m²', '200-250m²', '250-300m²', '300m² et +']
            
            # Compter le nombre de propriétés dans chaque tranche
            hist, _ = np.histogram(surfaces, bins=bins)
            data = hist.tolist()
            
            logger.info(f"Calculated surface distribution with {len(data)} bins")
            return {
                'labels': labels,
                'data': data
            }
            
        except Exception as e:
            logger.error(f"Error calculating surface distribution: {str(e)}")
            return {'labels': [], 'data': []} 