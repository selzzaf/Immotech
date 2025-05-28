from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from bson import ObjectId
import os

class TransactionManager:
    def __init__(self, db):
        self.db = db
        self.contracts_dir = os.path.join('static', 'contracts')
        os.makedirs(self.contracts_dir, exist_ok=True)

    def create_transaction(self, property_id, buyer_id, seller_id, transaction_type, amount):
        transaction = {
            'property_id': ObjectId(property_id),
            'buyer_id': ObjectId(buyer_id),
            'seller_id': ObjectId(seller_id),
            'type': transaction_type,
            'amount': float(amount),
            'status': 'pending',
            'created_at': datetime.utcnow(),
            'payment_status': 'pending',
            'booking_status': 'pending' if transaction_type == 'rental' else None,
            'contract_path': None
        }
        
        result = self.db.transactions.insert_one(transaction)
        return str(result.inserted_id)

    def process_payment(self, transaction_id, payment_details):
        # Simuler le traitement du paiement 
        success = True  
        
        if success:
            self.db.transactions.update_one(
                {'_id': ObjectId(transaction_id)},
                {'$set': {
                    'payment_status': 'completed',
                    'payment_details': payment_details,
                    'payment_date': datetime.utcnow()
                }}
            )
            
            # Générer le contrat après le paiement réussi
            self.generate_contract(transaction_id)
            return True
        return False

    def process_booking(self, transaction_id, booking_details):
        # Mettre à jour le statut de réservation
        self.db.transactions.update_one(
            {'_id': ObjectId(transaction_id)},
            {'$set': {
                'booking_status': 'confirmed',
                'booking_details': booking_details,
                'booking_date': datetime.utcnow()
            }}
        )
        return True

    def generate_contract(self, transaction_id):
        # Récupérer les informations de la transaction
        transaction = self.db.transactions.find_one({'_id': ObjectId(transaction_id)})
        if not transaction:
            return None

        # Récupérer les informations associées
        property_data = self.db.properties.find_one({'_id': transaction['property_id']})
        buyer_data = self.db.users.find_one({'_id': transaction['buyer_id']})
        seller_data = self.db.users.find_one({'_id': transaction['seller_id']})

        # Créer le nom du fichier
        filename = f"contract_{transaction_id}.pdf"
        filepath = os.path.join(self.contracts_dir, filename)

        # Créer le document PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        elements.append(Paragraph("Contrat de " + 
            ("Location" if transaction['type'] == 'rental' else "Vente"), title_style))
        elements.append(Spacer(1, 20))

        # Informations de la transaction
        elements.append(Paragraph("ENTRE LES SOUSSIGNÉS", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Informations du vendeur
        elements.append(Paragraph(f"Le vendeur : {seller_data['first_name']} {seller_data['last_name']}", styles['Normal']))
        elements.append(Paragraph(f"Email : {seller_data['email']}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Informations de l'acheteur
        elements.append(Paragraph(f"L'acheteur : {buyer_data['first_name']} {buyer_data['last_name']}", styles['Normal']))
        elements.append(Paragraph(f"Email : {buyer_data['email']}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Informations du bien
        elements.append(Paragraph("BIEN IMMOBILIER", styles['Heading2']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Adresse : {property_data['location']['address']}", styles['Normal']))
        elements.append(Paragraph(f"Ville : {property_data['location']['city']}", styles['Normal']))
        elements.append(Paragraph(f"Code postal : {property_data['location']['postal_code']}", styles['Normal']))
        elements.append(Paragraph(f"Surface : {property_data['surface']} m²", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Conditions financières
        elements.append(Paragraph("CONDITIONS FINANCIÈRES", styles['Heading2']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Montant : {transaction['amount']} €", styles['Normal']))
        elements.append(Paragraph(f"Type de transaction : {transaction['type']}", styles['Normal']))
        elements.append(Paragraph(f"Date de transaction : {transaction['created_at'].strftime('%d/%m/%Y')}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Signatures
        elements.append(Paragraph("SIGNATURES", styles['Heading2']))
        elements.append(Spacer(1, 30))
        
        # Tableau pour les signatures
        signature_data = [
            ['Le vendeur', 'L\'acheteur'],
            ['Date: _____________', 'Date: _____________'],
            ['Signature:', 'Signature:'],
            ['________________', '________________']
        ]
        signature_table = Table(signature_data, colWidths=[250, 250])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
        ]))
        elements.append(signature_table)

        # Générer le PDF
        doc.build(elements)

        # Mettre à jour le chemin du contrat dans la base de données
        self.db.transactions.update_one(
            {'_id': ObjectId(transaction_id)},
            {'$set': {'contract_path': filename}}
        )

        return filename

    def get_contract_path(self, transaction_id):
        transaction = self.db.transactions.find_one({'_id': ObjectId(transaction_id)})
        if transaction and transaction.get('contract_path'):
            return os.path.join(self.contracts_dir, transaction['contract_path'])
        return None

    def update_transaction_status(self, transaction_id, status):
        self.db.transactions.update_one(
            {'_id': ObjectId(transaction_id)},
            {'$set': {'status': status}}
        )
        
    def get_transaction_history(self, user_id):
        return list(self.db.transactions.find({
            '$or': [
                {'buyer_id': ObjectId(user_id)},
                {'seller_id': ObjectId(user_id)}
            ]
        }).sort('created_at', -1)) 