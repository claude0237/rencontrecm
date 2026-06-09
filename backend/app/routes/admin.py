from flask import Blueprint, request, jsonify
from app import db
from app.models import AlerteGlobale, Utilisateur, Region, Quartier, Appel, WhatsAppClick, WhatsAppSetting, Advertisement, AdPack, AdValidationHistory, AdminNotification, SubscriptionPack, UserSubscription, SubscriptionUpgradeRequest
from app.utils import admin_required
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/alerte', methods=['POST'])
@admin_required
def create_alerte():
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': 'Message requis'}), 400
    
    alerte = AlerteGlobale(
        message=data['message'],
        active=data.get('active', True)
    )
    
    db.session.add(alerte)
    db.session.commit()
    
    return jsonify({'message': 'Alerte créée', 'alerte': alerte.to_dict()}), 201

@admin_bp.route('/alerte/<int:alerte_id>', methods=['PUT'])
@admin_required
def update_alerte(alerte_id):
    alerte = AlerteGlobale.query.get_or_404(alerte_id)
    data = request.get_json()
    
    if 'message' in data:
        alerte.message = data['message']
    if 'active' in data:
        alerte.active = data['active']
    
    db.session.commit()
    
    return jsonify({'message': 'Alerte mise à jour', 'alerte': alerte.to_dict()}), 200

@admin_bp.route('/alerte/<int:alerte_id>', methods=['DELETE'])
@admin_required
def delete_alerte(alerte_id):
    alerte = AlerteGlobale.query.get_or_404(alerte_id)
    db.session.delete(alerte)
    db.session.commit()
    
    return jsonify({'message': 'Alerte supprimée'}), 200

@admin_bp.route('/alertes', methods=['GET'])
def get_alertes():
    alertes = AlerteGlobale.query.order_by(AlerteGlobale.date_creation.desc()).all()
    return jsonify({'alertes': [a.to_dict() for a in alertes]}), 200

@admin_bp.route('/alerte-active', methods=['GET'])
def get_active_alerte():
    try:
        alerte = AlerteGlobale.query.filter_by(active=True).first()
        if alerte:
            return jsonify({'alerte': alerte.to_dict()}), 200
        return jsonify({'alerte': None}), 200
    except Exception as e:
        return jsonify({'alerte': None}), 200

@admin_bp.route('/utilisateurs', methods=['GET'])
def get_all_utilisateurs():
    search = request.args.get('search', '')
    query = Utilisateur.query
    
    if search:
        query = query.filter(
            (Utilisateur.email.ilike(f'%{search}%')) |
            (Utilisateur.nom.ilike(f'%{search}%'))
        )
    
    utilisateurs = query.all()
    return jsonify({'utilisateurs': [u.to_dict() for u in utilisateurs]}), 200

@admin_bp.route('/utilisateur/<int:user_id>/actif', methods=['PUT'])
@admin_required
def toggle_user_actif(user_id):
    user = Utilisateur.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'actif' in data:
        user.actif = data['actif']
        db.session.commit()
    
    return jsonify({'message': 'Statut utilisateur mis à jour', 'user': user.to_dict()}), 200

@admin_bp.route('/utilisateur/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = Utilisateur.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'Utilisateur supprimé'}), 200

@admin_bp.route('/utilisateur/<int:user_id>/admin', methods=['PUT'])
@admin_required
def toggle_user_admin(user_id):
    user = Utilisateur.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'est_admin' in data:
        user.est_admin = data['est_admin']
        db.session.commit()
    
    return jsonify({'message': 'Statut admin mis à jour', 'user': user.to_dict()}), 200

@admin_bp.route('/utilisateur/<int:user_id>/whatsapp', methods=['PUT'])
@admin_required
def toggle_user_whatsapp(user_id):
    user = Utilisateur.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'whatsapp_enabled' in data:
        user.whatsapp_enabled = data['whatsapp_enabled']
    db.session.commit()
    
    return jsonify({'message': 'Statut WhatsApp mis à jour', 'user': user.to_dict()}), 200

# Region CRUD
@admin_bp.route('/regions', methods=['POST'])
@admin_required
def create_region():
    data = request.get_json()
    
    if not data or 'nom' not in data:
        return jsonify({'error': 'Nom requis'}), 400
    
    if Region.query.filter_by(nom=data['nom']).first():
        return jsonify({'error': 'Région existe déjà'}), 400
    
    region = Region(nom=data['nom'])
    db.session.add(region)
    db.session.commit()
    
    return jsonify({'message': 'Région créée', 'region': region.to_dict()}), 201

@admin_bp.route('/region/<int:region_id>', methods=['PUT'])
@admin_required
def update_region(region_id):
    region = Region.query.get_or_404(region_id)
    data = request.get_json()
    
    if 'nom' in data:
        region.nom = data['nom']
        db.session.commit()
    
    return jsonify({'message': 'Région mise à jour', 'region': region.to_dict()}), 200

@admin_bp.route('/region/<int:region_id>', methods=['DELETE'])
@admin_required
def delete_region(region_id):
    region = Region.query.get_or_404(region_id)
    
    # Check if users are linked to this region
    if Utilisateur.query.filter_by(region_id=region_id).first():
        return jsonify({'error': 'Des utilisateurs sont liés à cette région'}), 400
    
    db.session.delete(region)
    db.session.commit()
    
    return jsonify({'message': 'Région supprimée'}), 200

# Quartier CRUD
@admin_bp.route('/quartiers', methods=['POST'])
@admin_required
def create_quartier():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['nom', 'region_id']):
        return jsonify({'error': 'Nom et region_id requis'}), 400
    
    region = Region.query.get_or_404(data['region_id'])
    
    quartier = Quartier(nom=data['nom'], region_id=data['region_id'])
    db.session.add(quartier)
    db.session.commit()
    
    return jsonify({'message': 'Commune créée', 'quartier': quartier.to_dict()}), 201

@admin_bp.route('/quartier/<int:quartier_id>', methods=['PUT'])
@admin_required
def update_quartier(quartier_id):
    quartier = Quartier.query.get_or_404(quartier_id)
    data = request.get_json()
    
    if 'nom' in data:
        quartier.nom = data['nom']
    if 'region_id' in data:
        quartier.region_id = data['region_id']
    
    db.session.commit()
    
    return jsonify({'message': 'Commune mise à jour', 'quartier': quartier.to_dict()}), 200

@admin_bp.route('/quartier/<int:quartier_id>', methods=['DELETE'])
@admin_required
def delete_quartier(quartier_id):
    quartier = Quartier.query.get_or_404(quartier_id)
    
    # Check if users are linked to this quartier
    if Utilisateur.query.filter_by(quartier_id=quartier_id).first():
        return jsonify({'error': 'Des utilisateurs sont liés à cette commune'}), 400
    
    db.session.delete(quartier)
    db.session.commit()
    
    return jsonify({'message': 'Commune supprimée'}), 200

# Statistics
@admin_bp.route('/statistiques', methods=['GET'])
def get_statistiques():
    total_users = Utilisateur.query.count()
    hommes = Utilisateur.query.filter_by(genre='homme').count()
    femmes = Utilisateur.query.filter_by(genre='femme').count()
    actifs = Utilisateur.query.filter_by(actif=True).count()
    inactifs = Utilisateur.query.filter_by(actif=False).count()
    
    # Most active region
    region_counts = db.session.query(
        Region.nom,
        db.func.count(Utilisateur.id).label('count')
    ).join(Utilisateur).group_by(Region.id).order_by(db.desc('count')).first()
    
    most_active_region = region_counts[0] if region_counts else None
    
    return jsonify({
        'total_users': total_users,
        'hommes': hommes,
        'femmes': femmes,
        'actifs': actifs,
        'inactifs': inactifs,
        'most_active_region': most_active_region
    }), 200

# Call statistics
@admin_bp.route('/statistiques/appels', methods=['GET'])
def get_call_statistics():
    total_calls = Appel.query.count()
    
    return jsonify({
        'total_calls': total_calls
    }), 200

@admin_bp.route('/statistiques/appels/details', methods=['GET'])
def get_call_statistics_details():
    """Get detailed call statistics by user"""
    from sqlalchemy import func
    
    # Get call statistics grouped by caller
    caller_stats = db.session.query(
        Appel.appelant_id,
        Utilisateur.nom,
        Utilisateur.email,
        func.count(Appel.id).label('total_calls'),
        func.count(func.distinct(Appel.appele_id)).label('unique_called')
    ).join(Utilisateur, Appel.appelant_id == Utilisateur.id)\
     .group_by(Appel.appelant_id, Utilisateur.nom, Utilisateur.email)\
     .order_by(func.count(Appel.id).desc())\
     .all()
    
    # Get call statistics grouped by called user
    called_stats = db.session.query(
        Appel.appele_id,
        Utilisateur.nom,
        Utilisateur.email,
        func.count(Appel.id).label('total_received')
    ).join(Utilisateur, Appel.appele_id == Utilisateur.id)\
     .group_by(Appel.appele_id, Utilisateur.nom, Utilisateur.email)\
     .order_by(func.count(Appel.id).desc())\
     .all()
    
    return jsonify({
        'caller_stats': [
            {
                'user_id': stat.appelant_id,
                'nom': stat.nom,
                'email': stat.email,
                'total_calls': stat.total_calls,
                'unique_called': stat.unique_called
            }
            for stat in caller_stats
        ],
        'called_stats': [
            {
                'user_id': stat.appele_id,
                'nom': stat.nom,
                'email': stat.email,
                'total_received': stat.total_received
            }
            for stat in called_stats
        ]
    }), 200

# Profile view statistics
@admin_bp.route('/statistiques/visites', methods=['GET'])
def get_visit_statistics():
    """Get profile view statistics"""
    total_visits = db.session.query(db.func.sum(Utilisateur.nombre_visites)).scalar() or 0
    
    return jsonify({
        'total_visits': total_visits
    }), 200

@admin_bp.route('/statistiques/visites/details', methods=['GET'])
def get_visit_statistics_details():
    """Get detailed profile view statistics by user"""
    visit_stats = Utilisateur.query\
        .filter(Utilisateur.nombre_visites > 0)\
        .order_by(Utilisateur.nombre_visites.desc())\
        .all()
    
    return jsonify({
        'visit_stats': [
            {
                'user_id': user.id,
                'nom': user.nom,
                'email': user.email,
                'nombre_visites': user.nombre_visites,
                'region_nom': user.region.nom if user.region else None
            }
            for user in visit_stats
        ]
    }), 200

# WhatsApp statistics
@admin_bp.route('/statistiques/whatsapp', methods=['GET'])
def get_whatsapp_statistics():
    total_clicks = WhatsAppClick.query.count()
    
    return jsonify({
        'total_clicks': total_clicks
    }), 200

@admin_bp.route('/statistiques/whatsapp/details', methods=['GET'])
def get_whatsapp_statistics_details():
    """Get detailed WhatsApp click statistics by user"""
    from sqlalchemy import func
    
    # Get click statistics grouped by clicker
    clicker_stats = db.session.query(
        WhatsAppClick.cliquant_id,
        Utilisateur.nom,
        Utilisateur.email,
        func.count(WhatsAppClick.id).label('total_clicks'),
        func.count(func.distinct(WhatsAppClick.cible_id)).label('unique_clicked')
    ).join(Utilisateur, WhatsAppClick.cliquant_id == Utilisateur.id)\
     .group_by(WhatsAppClick.cliquant_id, Utilisateur.nom, Utilisateur.email)\
     .order_by(func.count(WhatsAppClick.id).desc())\
     .all()
    
    # Get click statistics grouped by target user
    target_stats = db.session.query(
        WhatsAppClick.cible_id,
        Utilisateur.nom,
        Utilisateur.email,
        func.count(WhatsAppClick.id).label('total_received')
    ).join(Utilisateur, WhatsAppClick.cible_id == Utilisateur.id)\
     .group_by(WhatsAppClick.cible_id, Utilisateur.nom, Utilisateur.email)\
     .order_by(func.count(WhatsAppClick.id).desc())\
     .all()
    
    return jsonify({
        'clicker_stats': [
            {
                'user_id': stat.cliquant_id,
                'nom': stat.nom,
                'email': stat.email,
                'total_clicks': stat.total_clicks,
                'unique_clicked': stat.unique_clicked
            }
            for stat in clicker_stats
        ],
        'target_stats': [
            {
                'user_id': stat.cible_id,
                'nom': stat.nom,
                'email': stat.email,
                'total_received': stat.total_received
            }
            for stat in target_stats
        ]
    }), 200

# WhatsApp settings
@admin_bp.route('/whatsapp-setting', methods=['GET'])
def get_whatsapp_setting():
    setting = WhatsAppSetting.query.first()
    if not setting:
        # Create default setting if none exists
        setting = WhatsAppSetting(
            default_message='Bonjour {nom}, je vous contacte depuis RencontreCm. Votre profil a retenu mon attention.'
        )
        db.session.add(setting)
        db.session.commit()
    
    return jsonify({'setting': setting.to_dict()}), 200

@admin_bp.route('/whatsapp-setting', methods=['PUT'])
@admin_required
def update_whatsapp_setting():
    data = request.get_json()
    
    if not data or 'default_message' not in data:
        return jsonify({'error': 'Message requis'}), 400
    
    setting = WhatsAppSetting.query.first()
    if not setting:
        setting = WhatsAppSetting(default_message=data['default_message'])
        db.session.add(setting)
    else:
        setting.default_message = data['default_message']
    
    db.session.commit()
    
    return jsonify({'message': 'Message WhatsApp mis à jour', 'setting': setting.to_dict()}), 200

# Advertisement management
@admin_bp.route('/publicites', methods=['GET'])
@admin_required
def get_all_advertisements():
    """Get all advertisements for admin management"""
    ads = Advertisement.query.order_by(Advertisement.date_creation.desc()).all()
    
    return jsonify({
        'advertisements': [
            {
                **ad.to_dict(),
                'annonceur_nom': ad.utilisateur.nom if ad.utilisateur else None,
                'annonceur_email': ad.utilisateur.email if ad.utilisateur else None,
                'annonceur_telephone': ad.utilisateur.contact_direct if ad.utilisateur else None
            }
            for ad in ads
        ]
    }), 200

@admin_bp.route('/publicites/en-attente', methods=['GET'])
@admin_required
def get_pending_advertisements():
    """Get all pending advertisements"""
    ads = Advertisement.query.filter_by(statut='en_attente').order_by(Advertisement.date_creation.desc()).all()
    
    return jsonify({
        'advertisements': [
            {
                **ad.to_dict(),
                'annonceur_nom': ad.utilisateur.nom if ad.utilisateur else None,
                'annonceur_email': ad.utilisateur.email if ad.utilisateur else None,
                'annonceur_telephone': ad.utilisateur.contact_direct if ad.utilisateur else None
            }
            for ad in ads
        ]
    }), 200

@admin_bp.route('/publicite/<int:ad_id>/valider', methods=['POST'])
@admin_required
def validate_advertisement(ad_id):
    """Validate an advertisement"""
    ad = Advertisement.query.get_or_404(ad_id)
    
    if ad.statut != 'en_attente':
        return jsonify({'error': 'Cette publicité n\'est pas en attente'}), 400
    
    # Set validation dates
    ad.statut = 'validee'
    ad.date_debut_validite = datetime.utcnow()
    ad.date_fin_validite = datetime.utcnow() + timedelta(days=ad.duree_jours)
    
    # Log validation
    from flask import session
    history = AdValidationHistory(
        advertisement_id=ad.id,
        admin_id=session['user_id'],
        action='validee'
    )
    db.session.add(history)
    
    db.session.commit()
    
    return jsonify({'message': 'Publicité validée', 'advertisement': ad.to_dict()}), 200

@admin_bp.route('/publicite/<int:ad_id>/rejeter', methods=['POST'])
@admin_required
def reject_advertisement(ad_id):
    """Reject an advertisement with reason"""
    data = request.get_json()
    
    if not data or 'motif' not in data:
        return jsonify({'error': 'Motif de rejet requis'}), 400
    
    ad = Advertisement.query.get_or_404(ad_id)
    
    if ad.statut != 'en_attente':
        return jsonify({'error': 'Cette publicité n\'est pas en attente'}), 400
    
    # Update status
    ad.statut = 'rejetee'
    
    # Log rejection
    from flask import session
    history = AdValidationHistory(
        advertisement_id=ad.id,
        admin_id=session['user_id'],
        action='rejetee',
        motif_rejet=data['motif']
    )
    db.session.add(history)
    
    db.session.commit()
    
    return jsonify({'message': 'Publicité rejetée', 'advertisement': ad.to_dict()}), 200

@admin_bp.route('/publicite/<int:ad_id>/suspendre', methods=['POST'])
@admin_required
def suspend_advertisement(ad_id):
    """Suspend an advertisement"""
    ad = Advertisement.query.get_or_404(ad_id)
    
    if ad.statut != 'validee':
        return jsonify({'error': 'Seules les publicités validées peuvent être suspendues'}), 400
    
    # Update status
    ad.statut = 'suspendue'
    
    # Log suspension
    from flask import session
    history = AdValidationHistory(
        advertisement_id=ad.id,
        admin_id=session['user_id'],
        action='suspendue'
    )
    db.session.add(history)
    
    db.session.commit()
    
    return jsonify({'message': 'Publicité suspendue', 'advertisement': ad.to_dict()}), 200

@admin_bp.route('/publicite/<int:ad_id>/reactiver', methods=['POST'])
@admin_required
def reactivate_advertisement(ad_id):
    """Reactivate a suspended advertisement"""
    ad = Advertisement.query.get_or_404(ad_id)
    
    if ad.statut != 'suspendue':
        return jsonify({'error': 'Seules les publicités suspendues peuvent être réactivées'}), 400
    
    # Update status
    ad.statut = 'validee'
    
    # Update end date
    ad.date_fin_validite = datetime.utcnow() + timedelta(days=ad.duree_jours)
    
    # Log reactivation
    from flask import session
    history = AdValidationHistory(
        advertisement_id=ad.id,
        admin_id=session['user_id'],
        action='validee'
    )
    db.session.add(history)
    
    db.session.commit()
    
    return jsonify({'message': 'Publicité réactivée', 'advertisement': ad.to_dict()}), 200

@admin_bp.route('/publicite/<int:ad_id>/supprimer', methods=['DELETE'])
@admin_required
def delete_advertisement(ad_id):
    """Delete a suspended or rejected advertisement"""
    ad = Advertisement.query.get_or_404(ad_id)
    
    if ad.statut not in ['suspendue', 'rejetee']:
        return jsonify({'error': 'Seules les publicités suspendues ou rejetées peuvent être supprimées'}), 400
    
    # Delete image file if exists
    if ad.image_url:
        try:
            import os
            image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '../../frontend', ad.image_url.lstrip('/'))
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            print(f"Error deleting image file: {e}")
    
    # Delete advertisement
    db.session.delete(ad)
    db.session.commit()
    
    return jsonify({'message': 'Publicité supprimée'}), 200


@admin_bp.route('/publicite/<int:ad_id>/historique', methods=['GET'])
@admin_required
def get_ad_history(ad_id):
    """Get validation history for an advertisement"""
    ad = Advertisement.query.get_or_404(ad_id)
    history = AdValidationHistory.query.filter_by(advertisement_id=ad_id).order_by(AdValidationHistory.created_at.desc()).all()
    
    return jsonify({
        'history': [h.to_dict() for h in history]
    }), 200

# Ad pack management
@admin_bp.route('/packs', methods=['GET'])
@admin_required
def get_ad_packs():
    """Get all ad packs"""
    packs = AdPack.query.all()
    
    return jsonify({
        'packs': [pack.to_dict() for pack in packs]
    }), 200

@admin_bp.route('/pack', methods=['POST'])
@admin_required
def create_ad_pack():
    """Create a new ad pack"""
    data = request.get_json()
    
    if not data or 'nom' not in data or 'prix' not in data or 'duree_jours' not in data:
        return jsonify({'error': 'Nom, prix et durée requis'}), 400
    
    pack = AdPack(
        nom=data['nom'],
        description=data.get('description'),
        prix=data['prix'],
        duree_jours=data['duree_jours'],
        actif=data.get('actif', True)
    )
    
    db.session.add(pack)
    db.session.commit()
    
    return jsonify({'message': 'Pack créé', 'pack': pack.to_dict()}), 201

@admin_bp.route('/pack/<int:pack_id>', methods=['PUT'])
@admin_required
def update_ad_pack(pack_id):
    """Update an ad pack"""
    pack = AdPack.query.get_or_404(pack_id)
    data = request.get_json()
    
    if 'nom' in data:
        pack.nom = data['nom']
    if 'description' in data:
        pack.description = data['description']
    if 'prix' in data:
        pack.prix = data['prix']
    if 'duree_jours' in data:
        pack.duree_jours = data['duree_jours']
    if 'actif' in data:
        pack.actif = data['actif']
    
    db.session.commit()
    
    return jsonify({'message': 'Pack mis à jour', 'pack': pack.to_dict()}), 200

@admin_bp.route('/pack/<int:pack_id>', methods=['DELETE'])
@admin_required
def delete_ad_pack(pack_id):
    """Delete an ad pack"""
    pack = AdPack.query.get_or_404(pack_id)
    db.session.delete(pack)
    db.session.commit()
    
    return jsonify({'message': 'Pack supprimé'}), 200

# Admin notifications
@admin_bp.route('/notifications', methods=['GET'])
@admin_required
def get_notifications():
    """Get all admin notifications"""
    notifications = AdminNotification.query.order_by(AdminNotification.created_at.desc()).limit(50).all()
    unread_count = AdminNotification.query.filter_by(lue=False).count()
    
    return jsonify({
        'notifications': [n.to_dict() for n in notifications],
        'unread_count': unread_count
    }), 200

@admin_bp.route('/notification/<int:notification_id>/lire', methods=['POST'])
@admin_required
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    notification = AdminNotification.query.get_or_404(notification_id)
    notification.lue = True
    db.session.commit()
    
    return jsonify({'message': 'Notification marquée comme lue'}), 200

@admin_bp.route('/notifications/lire-toutes', methods=['POST'])
@admin_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    AdminNotification.query.update({'lue': True})
    db.session.commit()
    
    return jsonify({'message': 'Toutes les notifications marquées comme lues'}), 200

@admin_bp.route('/notification/<int:notification_id>', methods=['DELETE'])
@admin_required
def delete_notification(notification_id):
    """Delete a notification"""
    notification = AdminNotification.query.get_or_404(notification_id)
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({'message': 'Notification supprimée'}), 200

# Subscription Packs Management
@admin_bp.route('/subscription-packs', methods=['GET'])
@admin_required
def get_subscription_packs():
    """Get all subscription packs"""
    packs = SubscriptionPack.query.order_by(SubscriptionPack.prix).all()
    return jsonify({'packs': [pack.to_dict() for pack in packs]}), 200

@admin_bp.route('/subscription-pack', methods=['POST'])
@admin_required
def create_subscription_pack():
    """Create a new subscription pack"""
    data = request.get_json()
    
    if not data or 'nom' not in data or 'niveau' not in data:
        return jsonify({'error': 'Nom et niveau requis'}), 400
    
    pack = SubscriptionPack(
        nom=data['nom'],
        niveau=data['niveau'],
        prix=data.get('prix', 0),
        duree_jours=data.get('duree_jours', 30),
        profils_consultables_par_jour=data.get('profils_consultables_par_jour', 5),
        contacts_whatsapp_par_jour=data.get('contacts_whatsapp_par_jour', 0),
        appels_directs_par_jour=data.get('appels_directs_par_jour', 0),
        mise_en_avant_pourcentage=data.get('mise_en_avant_pourcentage', 0),
        badge=data.get('badge'),
        actif=data.get('actif', True),
        description=data.get('description')
    )
    
    db.session.add(pack)
    db.session.commit()
    
    return jsonify({'message': 'Pack créé', 'pack': pack.to_dict()}), 201

@admin_bp.route('/subscription-pack/<int:pack_id>', methods=['PUT'])
@admin_required
def update_subscription_pack(pack_id):
    """Update a subscription pack"""
    pack = SubscriptionPack.query.get_or_404(pack_id)
    data = request.get_json()
    
    if 'nom' in data:
        pack.nom = data['nom']
    if 'niveau' in data:
        pack.niveau = data['niveau']
    if 'prix' in data:
        pack.prix = data['prix']
    if 'duree_jours' in data:
        pack.duree_jours = data['duree_jours']
    if 'profils_consultables_par_jour' in data:
        pack.profils_consultables_par_jour = data['profils_consultables_par_jour']
    if 'contacts_whatsapp_par_jour' in data:
        pack.contacts_whatsapp_par_jour = data['contacts_whatsapp_par_jour']
    if 'appels_directs_par_jour' in data:
        pack.appels_directs_par_jour = data['appels_directs_par_jour']
    if 'mise_en_avant_pourcentage' in data:
        pack.mise_en_avant_pourcentage = data['mise_en_avant_pourcentage']
    if 'badge' in data:
        pack.badge = data['badge']
    if 'actif' in data:
        pack.actif = data['actif']
    if 'description' in data:
        pack.description = data['description']
    
    db.session.commit()
    
    return jsonify({'message': 'Pack mis à jour', 'pack': pack.to_dict()}), 200

@admin_bp.route('/subscription-pack/<int:pack_id>', methods=['DELETE'])
@admin_required
def delete_subscription_pack(pack_id):
    """Delete a subscription pack"""
    pack = SubscriptionPack.query.get_or_404(pack_id)
    db.session.delete(pack)
    db.session.commit()
    
    return jsonify({'message': 'Pack supprimé'}), 200

# User Subscription Management
@admin_bp.route('/user-subscriptions', methods=['GET'])
@admin_required
def get_user_subscriptions():
    """Get all user subscriptions"""
    subscriptions = UserSubscription.query.order_by(UserSubscription.created_at.desc()).all()
    return jsonify({'subscriptions': [sub.to_dict() for sub in subscriptions]}), 200

@admin_bp.route('/user-subscription', methods=['POST'])
@admin_required
def create_user_subscription():
    """Create a user subscription (manual assignment by admin)"""
    data = request.get_json()
    
    if not data or 'user_id' not in data or 'pack_id' not in data:
        return jsonify({'error': 'user_id et pack_id requis'}), 400
    
    user = Utilisateur.query.get_or_404(data['user_id'])
    pack = SubscriptionPack.query.get_or_404(data['pack_id'])
    
    # Check if user already has an active subscription
    existing = UserSubscription.query.filter_by(
        user_id=data['user_id'],
        statut='actif'
    ).first()
    
    if existing:
        return jsonify({'error': 'Cet utilisateur a déjà un abonnement actif'}), 400
    
    date_fin = datetime.utcnow() + timedelta(days=pack.duree_jours)
    
    subscription = UserSubscription(
        user_id=data['user_id'],
        pack_id=data['pack_id'],
        date_debut=datetime.utcnow(),
        date_fin=date_fin,
        methode_paiement=data.get('methode_paiement', 'manuel'),
        reference_paiement=data.get('reference_paiement')
    )
    
    db.session.add(subscription)
    db.session.commit()
    
    return jsonify({'message': 'Abonnement créé', 'subscription': subscription.to_dict()}), 201

@admin_bp.route('/user-subscription/<int:subscription_id>', methods=['PUT'])
@admin_required
def update_user_subscription(subscription_id):
    """Update a user subscription"""
    subscription = UserSubscription.query.get_or_404(subscription_id)
    data = request.get_json()
    
    if 'statut' in data:
        subscription.statut = data['statut']
    if 'pack_id' in data:
        pack = SubscriptionPack.query.get_or_404(data['pack_id'])
        subscription.pack_id = data['pack_id']
        # Recalculate end date based on new pack duration
        if subscription.statut == 'actif':
            subscription.date_fin = subscription.date_debut + timedelta(days=pack.duree_jours)
    if 'date_fin' in data:
        subscription.date_fin = datetime.fromisoformat(data['date_fin'])
    
    db.session.commit()
    
    return jsonify({'message': 'Abonnement mis à jour', 'subscription': subscription.to_dict()}), 200

@admin_bp.route('/user-subscription/<int:subscription_id>', methods=['DELETE'])
@admin_required
def delete_user_subscription(subscription_id):
    """Delete a user subscription"""
    subscription = UserSubscription.query.get_or_404(subscription_id)
    db.session.delete(subscription)
    db.session.commit()
    
    return jsonify({'message': 'Abonnement supprimé'}), 200

@admin_bp.route('/user/<int:user_id>/subscription', methods=['GET'])
@admin_required
def get_user_subscription(user_id):
    """Get current subscription for a specific user"""
    subscription = UserSubscription.query.filter_by(
        user_id=user_id,
        statut='actif'
    ).first()
    
    if subscription:
        return jsonify({'subscription': subscription.to_dict()}), 200
    return jsonify({'subscription': None}), 200

# Subscription Upgrade Request Management
@admin_bp.route('/upgrade-requests', methods=['GET'])
@admin_required
def get_upgrade_requests():
    """Get all upgrade requests"""
    statut = request.args.get('statut')
    query = SubscriptionUpgradeRequest.query
    
    if statut:
        query = query.filter_by(statut=statut)
    
    requests = query.order_by(SubscriptionUpgradeRequest.created_at.desc()).all()
    return jsonify({'requests': [r.to_dict() for r in requests]}), 200

@admin_bp.route('/upgrade-request/<int:request_id>/approve', methods=['POST'])
@admin_required
def approve_upgrade_request(request_id):
    """Approve an upgrade request"""
    upgrade_request = SubscriptionUpgradeRequest.query.get_or_404(request_id)
    
    if upgrade_request.statut != 'en_attente':
        return jsonify({'error': 'Cette demande a déjà été traitée'}), 400
    
    # Cancel existing active subscription
    existing = UserSubscription.query.filter_by(
        user_id=upgrade_request.user_id,
        statut='actif'
    ).first()
    
    if existing:
        existing.statut = 'annule'
    
    # Create new subscription
    pack = SubscriptionPack.query.get(upgrade_request.pack_id)
    date_fin = datetime.utcnow() + timedelta(days=pack.duree_jours)
    
    subscription = UserSubscription(
        user_id=upgrade_request.user_id,
        pack_id=upgrade_request.pack_id,
        date_debut=datetime.utcnow(),
        date_fin=date_fin,
        methode_paiement=upgrade_request.methode_paiement,
        reference_paiement=upgrade_request.reference_paiement
    )
    
    # Update request status
    upgrade_request.statut = 'approuve'
    upgrade_request.processed_at = datetime.utcnow()
    upgrade_request.processed_by = session.get('user_id')
    
    db.session.add(subscription)
    db.session.commit()
    
    return jsonify({'message': 'Demande approuvée', 'subscription': subscription.to_dict()}), 200

@admin_bp.route('/upgrade-request/<int:request_id>/reject', methods=['POST'])
@admin_required
def reject_upgrade_request(request_id):
    """Reject an upgrade request"""
    upgrade_request = SubscriptionUpgradeRequest.query.get_or_404(request_id)
    
    if upgrade_request.statut != 'en_attente':
        return jsonify({'error': 'Cette demande a déjà été traitée'}), 400
    
    data = request.get_json()
    upgrade_request.statut = 'refuse'
    upgrade_request.admin_notes = data.get('admin_notes') if data else None
    upgrade_request.processed_at = datetime.utcnow()
    upgrade_request.processed_by = session.get('user_id')
    
    db.session.commit()
    
    return jsonify({'message': 'Demande refusée'}), 200

