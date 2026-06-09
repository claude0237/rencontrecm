from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Advertisement, AdPack, Utilisateur
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from flask import session

ads_bp = Blueprint('ads', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ads_bp.route('/packs', methods=['GET'])
def get_ad_packs():
    """Get all active ad packs"""
    packs = AdPack.query.filter_by(actif=True).all()
    return jsonify({
        'packs': [pack.to_dict() for pack in packs]
    }), 200

@ads_bp.route('/mes-pubs', methods=['GET'])
def get_my_advertisements():
    """Get current user's advertisements"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    user_id = session['user_id']
    ads = Advertisement.query.filter_by(utilisateur_id=user_id).order_by(Advertisement.date_creation.desc()).all()
    
    return jsonify({
        'advertisements': [ad.to_dict() for ad in ads]
    }), 200

@ads_bp.route('/pubs', methods=['GET'])
def get_active_advertisements():
    """Get all active advertisements for homepage"""
    from datetime import datetime
    
    now = datetime.utcnow()
    ads = Advertisement.query.filter(
        Advertisement.statut == 'validee',
        Advertisement.date_debut_validite <= now,
        Advertisement.date_fin_validite >= now
    ).order_by(Advertisement.date_creation.desc()).all()
    
    return jsonify({
        'advertisements': [ad.to_dict() for ad in ads]
    }), 200

@ads_bp.route('/pub/<int:ad_id>', methods=['GET'])
def get_advertisement(ad_id):
    """Get a single advertisement by ID"""
    ad = Advertisement.query.get(ad_id)
    if not ad:
        return jsonify({'error': 'Publicité non trouvée'}), 404
    
    return jsonify({
        'advertisement': ad.to_dict()
    }), 200

@ads_bp.route('/pub', methods=['POST'])
def create_advertisement():
    """Create a new advertisement"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    data = request.get_json()
    
    if not data or 'titre' not in data or 'description' not in data:
        return jsonify({'error': 'Titre et description requis'}), 400
    
    user_id = session['user_id']
    
    # Create advertisement
    ad = Advertisement(
        utilisateur_id=user_id,
        titre=data['titre'],
        description=data['description'],
        image_url=data.get('image_url'),
        numero_contact=data.get('numero_contact'),
        whatsapp=data.get('whatsapp'),
        duree_jours=data.get('duree_jours', 7),
        statut='brouillon',
        pack_id=data.get('pack_id')
    )
    
    db.session.add(ad)
    db.session.commit()
    
    return jsonify({
        'message': 'Publicité créée avec succès',
        'advertisement': ad.to_dict()
    }), 201

@ads_bp.route('/pub/image', methods=['POST'])
def upload_ad_image_temp():
    """Upload image for advertisement (temporary, before ad creation)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    if 'image' not in request.files:
        return jsonify({'error': 'Aucune image fournie'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Format de fichier non autorisé. Formats acceptés: png, jpg, jpeg, gif, webp'}), 400
    
    # Save image temporarily
    filename = secure_filename(f"temp_{session['user_id']}_{file.filename}")
    # Use absolute path to frontend static folder
    upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), '../../frontend/static/uploads/ads')
    os.makedirs(upload_folder, exist_ok=True)
    
    file_path = os.path.join(upload_folder, filename)
    try:
        file.save(file_path)
        print(f"Image saved to: {file_path}")
    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({'error': f'Erreur lors de la sauvegarde de l\'image: {str(e)}'}), 500
    
    image_url = f"/static/uploads/ads/{filename}"
    print(f"Image URL: {image_url}")
    
    return jsonify({
        'message': 'Image téléchargée avec succès',
        'image_url': image_url
    }), 200

@ads_bp.route('/pub/<int:ad_id>/image', methods=['POST'])
def upload_ad_image(ad_id):
    """Upload image for advertisement"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    if 'image' not in request.files:
        return jsonify({'error': 'Aucune image fournie'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Format de fichier non autorisé. Formats acceptés: png, jpg, jpeg, gif, webp'}), 400
    
    # Get advertisement
    ad = Advertisement.query.get(ad_id)
    if not ad:
        return jsonify({'error': 'Publicité non trouvée'}), 404
    
    if ad.utilisateur_id != session['user_id']:
        return jsonify({'error': 'Non autorisé'}), 403
    
    # Save image
    filename = secure_filename(f"ad_{ad_id}_{file.filename}")
    # Use absolute path to frontend static folder
    upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), '../../frontend/static/uploads/ads')
    os.makedirs(upload_folder, exist_ok=True)
    
    file_path = os.path.join(upload_folder, filename)
    try:
        file.save(file_path)
    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({'error': f'Erreur lors de la sauvegarde de l\'image: {str(e)}'}), 500
    
    # Update advertisement
    ad.image_url = f"/static/uploads/ads/{filename}"
    db.session.commit()
    
    return jsonify({
        'message': 'Image téléchargée avec succès',
        'image_url': ad.image_url
    }), 200

@ads_bp.route('/pub/<int:ad_id>', methods=['PUT'])
def update_advertisement(ad_id):
    """Update an advertisement"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    data = request.get_json()
    
    ad = Advertisement.query.get(ad_id)
    if not ad:
        return jsonify({'error': 'Publicité non trouvée'}), 404
    
    if ad.utilisateur_id != session['user_id']:
        return jsonify({'error': 'Non autorisé'}), 403
    
    # Only allow updates if status is brouillon or en_attente
    if ad.statut not in ['brouillon', 'en_attente']:
        return jsonify({'error': 'Impossible de modifier une publicité validée'}), 400
    
    # Update fields
    if 'titre' in data:
        ad.titre = data['titre']
    if 'description' in data:
        ad.description = data['description']
    if 'image_url' in data:
        ad.image_url = data['image_url']
    if 'numero_contact' in data:
        ad.numero_contact = data['numero_contact']
    if 'whatsapp' in data:
        ad.whatsapp = data['whatsapp']
    if 'duree_jours' in data:
        ad.duree_jours = data['duree_jours']
    if 'pack_id' in data:
        ad.pack_id = data['pack_id']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Publicité mise à jour avec succès',
        'advertisement': ad.to_dict()
    }), 200

@ads_bp.route('/pub/<int:ad_id>', methods=['DELETE'])
def delete_advertisement(ad_id):
    """Delete an advertisement"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    ad = Advertisement.query.get(ad_id)
    if not ad:
        return jsonify({'error': 'Publicité non trouvée'}), 404
    
    if ad.utilisateur_id != session['user_id']:
        return jsonify({'error': 'Non autorisé'}), 403
    
    # Only allow deletion if status is brouillon or en_attente
    if ad.statut not in ['brouillon', 'en_attente']:
        return jsonify({'error': 'Impossible de supprimer une publicité validée'}), 400
    
    db.session.delete(ad)
    db.session.commit()
    
    return jsonify({'message': 'Publicité supprimée avec succès'}), 200

@ads_bp.route('/pub/<int:ad_id>/soumettre', methods=['POST'])
def submit_advertisement(ad_id):
    """Submit advertisement for validation"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    ad = Advertisement.query.get(ad_id)
    if not ad:
        return jsonify({'error': 'Publicité non trouvée'}), 404
    
    if ad.utilisateur_id != session['user_id']:
        return jsonify({'error': 'Non autorisé'}), 403
    
    if ad.statut != 'brouillon':
        return jsonify({'error': 'Cette publicité a déjà été soumise'}), 400
    
    if not ad.pack_id:
        return jsonify({'error': 'Veuillez sélectionner un pack avant de soumettre'}), 400
    
    ad.statut = 'en_attente'
    db.session.commit()
    
    # Create admin notification
    from app.models import AdminNotification
    notification = AdminNotification(
        type='nouvelle_publicite',
        titre='Nouvelle publicité soumise',
        message=f'Une nouvelle publicité "{ad.titre}" a été soumise par {ad.utilisateur.nom} pour validation.',
        advertisement_id=ad.id,
        utilisateur_id=ad.utilisateur_id
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({
        'message': 'Publicité soumise pour validation',
        'advertisement': ad.to_dict()
    }), 200

@ads_bp.route('/pub/<int:ad_id>/renouveler', methods=['POST'])
def renew_advertisement(ad_id):
    """Renew an expired advertisement"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    data = request.get_json()
    
    ad = Advertisement.query.get(ad_id)
    if not ad:
        return jsonify({'error': 'Publicité non trouvée'}), 404
    
    if ad.utilisateur_id != session['user_id']:
        return jsonify({'error': 'Non autorisé'}), 403
    
    if ad.statut != 'expiree':
        return jsonify({'error': 'Seules les publicités expirées peuvent être renouvelées'}), 400
    
    # Update dates
    duree = ad.duree_jours
    ad.date_debut_validite = datetime.utcnow()
    ad.date_fin_validite = datetime.utcnow() + timedelta(days=duree)
    ad.statut = 'en_attente'
    ad.paiement_effectue = False
    
    db.session.commit()
    
    return jsonify({
        'message': 'Publicité renouvelée avec succès',
        'advertisement': ad.to_dict()
    }), 200

@ads_bp.route('/pub/<int:ad_id>/payer', methods=['POST'])
def pay_for_advertisement(ad_id):
    """Pay for a validated advertisement"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    data = request.get_json()
    
    ad = Advertisement.query.get(ad_id)
    if not ad:
        return jsonify({'error': 'Publicité non trouvée'}), 404
    
    if ad.utilisateur_id != session['user_id']:
        return jsonify({'error': 'Non autorisé'}), 403
    
    if ad.statut != 'validee_en_attente_paiement':
        return jsonify({'error': 'Cette publicité n\'est pas en attente de paiement'}), 400
    
    methode_paiement = data.get('methode_paiement')
    
    if methode_paiement == 'mobile_money':
        # Mobile Money - set status to awaiting admin validation
        if not data.get('reference_paiement'):
            return jsonify({'error': 'Numéro de paiement requis pour Mobile Money'}), 400
        
        ad.statut = 'en_attente_paiement_manuel'
        ad.methode_paiement = 'mobile_money'
        ad.reference_paiement = data.get('reference_paiement')
        
        # Create admin notification for mobile money payment validation
        try:
            from app.models import AdminNotification
            notification = AdminNotification(
                type='paiement_manuel',
                titre='Paiement Mobile Money à valider',
                message=f'Paiement Mobile Money pour publicité "{ad.titre}" par {ad.utilisateur.nom if ad.utilisateur else "Utilisateur inconnu"}. Numéro: {ad.reference_paiement}. Montant: {ad.pack.prix if ad.pack else 0} FCFA.',
                advertisement_id=ad.id,
                utilisateur_id=ad.utilisateur_id
            )
            db.session.add(notification)
        except Exception as e:
            print(f"Error creating notification: {e}")
        
        db.session.commit()
        
        return jsonify({
            'message': 'Paiement Mobile Money enregistré. L\'administrateur validera votre paiement.',
            'advertisement': ad.to_dict()
        }), 200
        
    elif methode_paiement == 'manuel_admin':
        # Manual admin payment - set status to awaiting admin validation
        ad.statut = 'en_attente_paiement_manuel'
        ad.methode_paiement = 'manuel_admin'
        ad.reference_paiement = data.get('reference_paiement', '')
        
        # Create admin notification for manual payment validation
        try:
            from app.models import AdminNotification
            reference_info = f" Référence: {ad.reference_paiement}" if ad.reference_paiement else ""
            notification = AdminNotification(
                type='paiement_manuel',
                titre='Paiement manuel à valider',
                message=f'Paiement manuel pour publicité "{ad.titre}" par {ad.utilisateur.nom if ad.utilisateur else "Utilisateur inconnu"}.{reference_info} Montant: {ad.pack.prix if ad.pack else 0} FCFA.',
                advertisement_id=ad.id,
                utilisateur_id=ad.utilisateur_id
            )
            db.session.add(notification)
        except Exception as e:
            print(f"Error creating notification: {e}")
            # Continue without notification if there's an error
        
        db.session.commit()
        
        return jsonify({
            'message': 'Demande de paiement manuel enregistrée. L\'administrateur validera votre paiement.',
            'advertisement': ad.to_dict()
        }), 200
        
    elif methode_paiement == 'carte_bancaire':
        # Credit card - placeholder for payment gateway integration
        # For now, treat as manual validation
        ad.statut = 'en_attente_paiement_manuel'
        ad.methode_paiement = 'carte_bancaire'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Intégration carte bancaire à venir. Pour l\'instant, paiement en attente de validation.',
            'advertisement': ad.to_dict()
        }), 200
        
    else:
        return jsonify({'error': 'Mode de paiement non reconnu'}), 400
