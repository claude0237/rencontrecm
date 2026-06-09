from flask import Blueprint, request, jsonify, current_app, session
from app import db
from app.models import Region, Quartier, Utilisateur, Appel, WhatsAppClick, WhatsAppSetting, SubscriptionPack, UserSubscription, SubscriptionUpgradeRequest
import json
import os
import math
import re
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

members_bp = Blueprint('members', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def mask_phone_numbers(text):
    """Mask phone numbers in text"""
    if not text:
        return text
    # Mask phone numbers (Cameroon format: +237, 6XX, etc.)
    pattern = r'(\+?237)?[0-9\s\-\(\)]{8,15}'
    masked = re.sub(pattern, '***', text)
    return masked

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers using Haversine formula"""
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return None
    
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    distance = R * c
    return round(distance, 2)

@members_bp.route('/regions', methods=['GET'])
def get_regions():
    regions = Region.query.all()
    return jsonify({'regions': [r.to_dict() for r in regions]}), 200

@members_bp.route('/quartiers/<int:region_id>', methods=['GET'])
def get_quartiers(region_id):
    quartiers = Quartier.query.filter_by(region_id=region_id).all()
    return jsonify({'quartiers': [q.to_dict() for q in quartiers]}), 200

@members_bp.route('/quartiers', methods=['GET'])
def get_all_quartiers():
    quartiers = Quartier.query.all()
    return jsonify({'quartiers': [q.to_dict() for q in quartiers]}), 200

@members_bp.route('/profils', methods=['GET'])
def get_profils():
    region_id = request.args.get('region_id')
    quartier_id = request.args.get('quartier_id')
    genre = request.args.get('genre')
    age_min = request.args.get('age_min', type=int)
    age_max = request.args.get('age_max', type=int)
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 9, type=int)
    user_lat = request.args.get('lat', type=float)
    user_lon = request.args.get('lon', type=float)
    exclude_user_id = request.args.get('exclude_user_id', type=int)
    
    # Get current user subscription if authenticated
    current_user_id = session.get('user_id')
    current_subscription = None
    if current_user_id:
        subscription = UserSubscription.query.filter_by(
            user_id=current_user_id,
            statut='actif'
        ).first()
        if subscription:
            subscription.check_and_handle_expiration()
            if subscription.is_active():
                current_subscription = subscription
    
    query = Utilisateur.query.filter_by(actif=True)
    
    # Exclude specified user if provided
    if exclude_user_id:
        query = query.filter(Utilisateur.id != exclude_user_id)
    
    if region_id:
        query = query.filter_by(region_id=region_id)
    
    if quartier_id:
        query = query.filter_by(quartier_id=quartier_id)
    
    if genre:
        query = query.filter_by(genre=genre)
    
    if age_min:
        query = query.filter(Utilisateur.age >= age_min)
    
    if age_max:
        query = query.filter(Utilisateur.age <= age_max)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    profils = query.offset((page - 1) * limit).limit(limit).all()
    
    # Calculate distances and prepare response
    profils_with_distance = []
    for profil in profils:
        distance = None
        if user_lat and user_lon and profil.latitude and profil.longitude:
            distance = calculate_distance(user_lat, user_lon, profil.latitude, profil.longitude)
        
        profil_dict = profil.to_dict()
        profil_dict['distance'] = distance
        
        # Mask phone numbers in name and description
        profil_dict['nom'] = mask_phone_numbers(profil_dict['nom'])
        profil_dict['description'] = mask_phone_numbers(profil_dict['description'])
        
        # Mask contact info based on profile's subscription pack
        # Get the profile's subscription to check if they allow contact visibility
        profil_subscription = UserSubscription.query.filter_by(
            user_id=profil.id,
            statut='actif'
        ).first()
        
        if profil_subscription:
            profil_subscription.check_and_handle_expiration()
            # Check if profile's pack allows WhatsApp contact visibility
            # First discovery period gives full benefits regardless of pack quotas
            if not profil_subscription.premiere_periode_decouverte and profil_subscription.pack.contacts_whatsapp_par_jour == 0:
                profil_dict['contact_whatsapp'] = None
                profil_dict['whatsapp_masked'] = True
            # Check if profile's pack allows direct call visibility
            # First discovery period gives full benefits regardless of pack quotas
            if not profil_subscription.premiere_periode_decouverte and profil_subscription.pack.appels_directs_par_jour == 0:
                profil_dict['contact_direct'] = None
                profil_dict['call_masked'] = True
        else:
            # No active subscription = no contact visibility
            profil_dict['contact_whatsapp'] = None
            profil_dict['whatsapp_masked'] = True
            profil_dict['contact_direct'] = None
            profil_dict['call_masked'] = True
        
        profils_with_distance.append(profil_dict)
    
    return jsonify({
        'profils': profils_with_distance,
        'total': total,
        'page': page,
        'limit': limit,
        'total_pages': (total + limit - 1) // limit
    }), 200

@members_bp.route('/profils/recommandes', methods=['GET'])
def get_profils_recommandes():
    from flask import session
    
    user_lat = request.args.get('lat', type=float)
    user_lon = request.args.get('lon', type=float)
    user_genre = request.args.get('genre')
    limit = request.args.get('limit', 10, type=int)
    exclude_user_id = request.args.get('exclude_user_id', type=int)
    
    # Get current user subscription if authenticated
    current_user_id = session.get('user_id')
    current_subscription = None
    if current_user_id:
        subscription = UserSubscription.query.filter_by(
            user_id=current_user_id,
            statut='actif'
        ).first()
        if subscription:
            subscription.check_and_handle_expiration()
            if subscription.is_active():
                current_subscription = subscription
    
    # First try to get profiles with same genre
    query = Utilisateur.query.filter_by(actif=True)
    
    # Exclude specified user if provided
    if exclude_user_id:
        query = query.filter(Utilisateur.id != exclude_user_id)
    
    if user_genre:
        query = query.filter_by(genre=user_genre)
    
    # Order by nombre_visites (most visited first)
    query = query.order_by(Utilisateur.nombre_visites.desc())
    
    profils = query.limit(limit * 2).all()  # Get more to filter by distance
    
    # If no profiles found with same genre, get all active profiles
    if not profils and user_genre:
        query = Utilisateur.query.filter_by(actif=True)
        # Exclude specified user if provided
        if exclude_user_id:
            query = query.filter(Utilisateur.id != exclude_user_id)
        query = query.order_by(Utilisateur.nombre_visites.desc())
        profils = query.limit(limit * 2).all()
    
    # Calculate distances and filter
    profils_with_distance = []
    for profil in profils:
        distance = None
        if user_lat and user_lon and profil.latitude and profil.longitude:
            distance = calculate_distance(user_lat, user_lon, profil.latitude, profil.longitude)
        
        profil_dict = profil.to_dict()
        profil_dict['distance'] = distance
        
        # Mask phone numbers in name and description
        profil_dict['nom'] = mask_phone_numbers(profil_dict['nom'])
        profil_dict['description'] = mask_phone_numbers(profil_dict['description'])
        
        # Mask contact info based on profile's subscription pack
        # Get the profile's subscription to check if they allow contact visibility
        profil_subscription = UserSubscription.query.filter_by(
            user_id=profil.id,
            statut='actif'
        ).first()
        
        if profil_subscription:
            profil_subscription.check_and_handle_expiration()
            # Check if profile's pack allows WhatsApp contact visibility
            # First discovery period gives full benefits regardless of pack quotas
            if not profil_subscription.premiere_periode_decouverte and profil_subscription.pack.contacts_whatsapp_par_jour == 0:
                profil_dict['contact_whatsapp'] = None
                profil_dict['whatsapp_masked'] = True
            # Check if profile's pack allows direct call visibility
            # First discovery period gives full benefits regardless of pack quotas
            if not profil_subscription.premiere_periode_decouverte and profil_subscription.pack.appels_directs_par_jour == 0:
                profil_dict['contact_direct'] = None
                profil_dict['call_masked'] = True
        else:
            # No active subscription = no contact visibility
            profil_dict['contact_whatsapp'] = None
            profil_dict['whatsapp_masked'] = True
            profil_dict['contact_direct'] = None
            profil_dict['call_masked'] = True
        
        profils_with_distance.append(profil_dict)
    
    # Sort by distance if available, otherwise by visits
    if user_lat and user_lon:
        profils_with_distance.sort(key=lambda x: (x['distance'] is None, x['distance'] or float('inf')))
    
    # Return limited results
    return jsonify({'profils': profils_with_distance[:limit]}), 200

@members_bp.route('/profil/<int:user_id>', methods=['GET'])
def get_profil(user_id):
    from flask import session
    
    user_lat = request.args.get('lat', type=float)
    user_lon = request.args.get('lon', type=float)
    
    user = Utilisateur.query.get_or_404(user_id)
    profil_dict = user.to_dict()
    
    # Get current user subscription if authenticated
    current_user_id = session.get('user_id')
    current_subscription = None
    is_own_profile = current_user_id == user_id
    
    if current_user_id:
        subscription = UserSubscription.query.filter_by(
            user_id=current_user_id,
            statut='actif'
        ).first()
        if subscription:
            subscription.check_and_handle_expiration()
            if subscription.is_active():
                current_subscription = subscription
    
    # Add subscription info to profile
    if is_own_profile and current_subscription:
        profil_dict['subscription'] = current_subscription.to_dict()
    
    # Calculate distance if user location is provided
    distance = None
    if user_lat and user_lon and user.latitude and user.longitude:
        distance = calculate_distance(user_lat, user_lon, user.latitude, user.longitude)
    
    profil_dict['distance'] = distance
    
    # Mask phone numbers in name and description
    profil_dict['nom'] = mask_phone_numbers(profil_dict['nom'])
    profil_dict['description'] = mask_phone_numbers(profil_dict['description'])
    
    # Mask contact info based on profile's subscription pack (unless it's own profile)
    if not is_own_profile:
        # Get the profile's subscription to check if they allow contact visibility
        profil_subscription = UserSubscription.query.filter_by(
            user_id=user_id,
            statut='actif'
        ).first()
        
        if profil_subscription:
            profil_subscription.check_and_handle_expiration()
            # Check if profile's pack allows WhatsApp contact visibility
            # First discovery period gives full benefits regardless of pack quotas
            if not profil_subscription.premiere_periode_decouverte and profil_subscription.pack.contacts_whatsapp_par_jour == 0:
                profil_dict['contact_whatsapp'] = None
                profil_dict['whatsapp_masked'] = True
            # Check if profile's pack allows direct call visibility
            # First discovery period gives full benefits regardless of pack quotas
            if not profil_subscription.premiere_periode_decouverte and profil_subscription.pack.appels_directs_par_jour == 0:
                profil_dict['contact_direct'] = None
                profil_dict['call_masked'] = True
        else:
            # No active subscription = no contact visibility
            profil_dict['contact_whatsapp'] = None
            profil_dict['whatsapp_masked'] = True
            profil_dict['contact_direct'] = None
            profil_dict['call_masked'] = True
    
    return jsonify({'profil': profil_dict}), 200

@members_bp.route('/profil/<int:user_id>/visite', methods=['POST'])
def increment_visite(user_id):
    from flask import session
    
    user = Utilisateur.query.get_or_404(user_id)
    user.nombre_visites = (user.nombre_visites or 0) + 1
    
    # Track profile view in subscription if authenticated
    current_user_id = session.get('user_id')
    if current_user_id and current_user_id != user_id:
        subscription = UserSubscription.query.filter_by(
            user_id=current_user_id,
            statut='actif'
        ).first()
        if subscription:
            subscription.check_and_handle_expiration()
            if subscription.is_active():
                subscription.reset_daily_quotas()
                if subscription.can_view_profile():
                    subscription.increment_profile_view()
                else:
                    return jsonify({
                        'error': 'Quota de consultations de profils atteint pour aujourd\'hui',
                        'quota_used': subscription.profils_consultes_aujourdhui,
                        'quota_limit': subscription.pack.profils_consultables_par_jour
                    }), 403
    
    db.session.commit()
    return jsonify({'message': 'Visite enregistrée', 'nombre_visites': user.nombre_visites}), 200

@members_bp.route('/profil', methods=['PUT'])
def update_profil():
    from flask import session
    
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    user = Utilisateur.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    data = request.get_json()
    
    if 'nom' in data:
        user.nom = data['nom']
    if 'age' in data:
        user.age = data['age']
    if 'genre' in data:
        user.genre = data['genre']
    if 'description' in data:
        user.description = data['description']
    if 'photo_url' in data:
        user.photo_url = data['photo_url']
    if 'contact_whatsapp' in data:
        user.contact_whatsapp = data['contact_whatsapp']
    if 'contact_direct' in data:
        user.contact_direct = data['contact_direct']
    if 'email' in data:
        if Utilisateur.query.filter_by(email=data['email']).first() and data['email'] != user.email:
            return jsonify({'error': 'Email déjà utilisé'}), 400
        user.email = data['email']
    if 'password' in data:
        user.set_password(data['password'])
    if 'photos' in data:
        user.photos = json.dumps(data['photos'])
    if 'photo_principale' in data:
        user.photo_principale = data['photo_principale']
    
    db.session.commit()
    
    return jsonify({'message': 'Profil mis à jour', 'user': user.to_dict()}), 200

@members_bp.route('/upload-photo', methods=['POST'])
def upload_photo():
    from flask import session, current_app
    
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    if 'photo' not in request.files:
        return jsonify({'error': 'Aucun fichier'}), 400
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Type de fichier non autorisé'}), 400
    
    # Create upload directory if it doesn't exist
    upload_folder = os.path.join(current_app.root_path, '..', '..', 'frontend', 'static', 'uploads')
    upload_folder = os.path.abspath(upload_folder)
    os.makedirs(upload_folder, exist_ok=True)
    
    filename = secure_filename(f"{session['user_id']}_{file.filename}")
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    
    # Return the URL to access the file
    photo_url = f"/static/uploads/{filename}"
    
    print(f"Photo uploaded to: {filepath}")
    print(f"Photo URL: {photo_url}")
    
    return jsonify({'photo_url': photo_url}), 200

@members_bp.route('/upload-photo-public', methods=['POST'])
def upload_photo_public():
    from flask import current_app
    import time
    
    if 'photo' not in request.files:
        return jsonify({'error': 'Aucun fichier'}), 400
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Type de fichier non autorisé'}), 400
    
    # Create upload directory if it doesn't exist
    upload_folder = os.path.join(current_app.root_path, '..', '..', 'frontend', 'static', 'uploads')
    upload_folder = os.path.abspath(upload_folder)
    os.makedirs(upload_folder, exist_ok=True)
    
    # Use timestamp to avoid conflicts for unauthenticated users
    timestamp = int(time.time())
    filename = secure_filename(f"temp_{timestamp}_{file.filename}")
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    
    # Return the URL to access the file
    photo_url = f"/static/uploads/{filename}"
    
    print(f"Photo uploaded to: {filepath}")
    print(f"Photo URL: {photo_url}")
    
    return jsonify({'photo_url': photo_url}), 200

@members_bp.route('/profil/<int:appele_id>/appeler', methods=['POST'])
def track_appel(appele_id):
    """Track call initiation when user clicks call button"""
    from flask import session
    
    appelant_id = session.get('user_id') if 'user_id' in session else None
    
    # Check if called user exists and is active
    appele = Utilisateur.query.get(appele_id)
    
    if not appele:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    if not appele.actif:
        return jsonify({'error': 'Ce compte est désactivé'}), 403
    
    # Check subscription restrictions for authenticated users
    if appelant_id:
        subscription = UserSubscription.query.filter_by(
            user_id=appelant_id,
            statut='actif'
        ).first()
        
        if subscription:
            subscription.reset_daily_quotas()
            if not subscription.can_call_direct():
                return jsonify({
                    'error': 'Quota d\'appels directs atteint pour aujourd\'hui',
                    'quota_used': subscription.appels_directs_aujourdhui,
                    'quota_limit': subscription.pack.appels_directs_par_jour
                }), 403
            subscription.increment_direct_call()
    
    # Create call record (appelant_id can be NULL for anonymous visitors)
    appel = Appel(
        appelant_id=appelant_id,
        appele_id=appele_id
    )
    db.session.add(appel)
    db.session.commit()
    
    return jsonify({
        'message': 'Appel enregistré',
        'appel': appel.to_dict(),
        'appele_phone': appele.contact_direct
    }), 200

@members_bp.route('/profil/<int:cible_id>/whatsapp', methods=['POST'])
def track_whatsapp_click(cible_id):
    """Track WhatsApp click when user clicks WhatsApp button"""
    from flask import session
    
    cliquant_id = session.get('user_id') if 'user_id' in session else None
    
    # Check if target user exists and is active
    cible = Utilisateur.query.get(cible_id)
    
    if not cible:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    if not cible.actif:
        return jsonify({'error': 'Ce compte est désactivé'}), 403
    
    if not cible.contact_whatsapp:
        return jsonify({'error': 'Cet utilisateur n\'a pas de WhatsApp'}), 400
    
    if not cible.whatsapp_enabled:
        return jsonify({'error': 'Le contact WhatsApp est désactivé pour cet utilisateur'}), 403
    
    # Check subscription restrictions for authenticated users
    if cliquant_id:
        subscription = UserSubscription.query.filter_by(
            user_id=cliquant_id,
            statut='actif'
        ).first()
        
        if subscription:
            subscription.reset_daily_quotas()
            if not subscription.can_view_whatsapp():
                return jsonify({
                    'error': 'Quota de contacts WhatsApp atteint pour aujourd\'hui',
                    'quota_used': subscription.contacts_whatsapp_aujourdhui,
                    'quota_limit': subscription.pack.contacts_whatsapp_par_jour
                }), 403
            subscription.increment_whatsapp_view()
    
    # Get default WhatsApp message
    setting = WhatsAppSetting.query.first()
    default_message = setting.default_message if setting else 'Bonjour {nom}, je vous contacte depuis RencontreCm.'
    
    # Replace {nom} with the target user's name
    message = default_message.replace('{nom}', cible.nom)
    
    # Create WhatsApp click record (cliquant_id can be NULL for anonymous visitors)
    whatsapp_click = WhatsAppClick(
        cliquant_id=cliquant_id,
        cible_id=cible_id
    )
    db.session.add(whatsapp_click)
    db.session.commit()
    
    # Format WhatsApp URL
    whatsapp_number = cible.contact_whatsapp.replace('+', '').replace(' ', '')
    whatsapp_url = f"https://wa.me/{whatsapp_number}?text={message}"
    
    return jsonify({
        'message': 'Clic WhatsApp enregistré',
        'whatsapp_click': whatsapp_click.to_dict(),
        'whatsapp_url': whatsapp_url
    }), 200

# Subscription Management for Users
@members_bp.route('/subscription-packs', methods=['GET'])
def get_available_subscription_packs():
    """Get all available subscription packs for users"""
    packs = SubscriptionPack.query.filter_by(actif=True).order_by(SubscriptionPack.prix).all()
    return jsonify({'packs': [pack.to_dict() for pack in packs]}), 200

@members_bp.route('/my-subscription', methods=['GET'])
def get_my_subscription():
    """Get current user's subscription"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    from sqlalchemy.orm import joinedload
    subscription = UserSubscription.query.options(
        joinedload(UserSubscription.pack)
    ).filter_by(
        user_id=session['user_id'],
        statut='actif'
    ).first()
    
    if subscription:
        # Check and handle expiration
        subscription.check_and_handle_expiration()
        # Check if still active after expiration check
        if subscription.statut != 'actif':
            return jsonify({'subscription': None}), 200
        # Reset daily quotas if needed
        subscription.reset_daily_quotas()
        return jsonify({'subscription': subscription.to_dict()}), 200
    return jsonify({'subscription': None}), 200

@members_bp.route('/subscription/purchase', methods=['POST'])
def purchase_subscription():
    """Purchase or upgrade a subscription"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    data = request.get_json()
    
    if not data or 'pack_id' not in data:
        return jsonify({'error': 'pack_id requis'}), 400
    
    pack = SubscriptionPack.query.get_or_404(data['pack_id'])
    
    if not pack.actif:
        return jsonify({'error': 'Ce pack n\'est pas disponible'}), 400
    
    # Check if user already has an active subscription
    existing = UserSubscription.query.filter_by(
        user_id=session['user_id'],
        statut='actif'
    ).first()
    
    if existing:
        # Upgrade: cancel existing and create new
        existing.statut = 'annule'
        db.session.commit()
    
    date_fin = datetime.utcnow() + timedelta(days=pack.duree_jours)
    
    subscription = UserSubscription(
        user_id=session['user_id'],
        pack_id=data['pack_id'],
        date_debut=datetime.utcnow(),
        date_fin=date_fin,
        methode_paiement=data.get('methode_paiement', 'pending'),
        reference_paiement=data.get('reference_paiement')
    )
    
    db.session.add(subscription)
    db.session.commit()
    
    return jsonify({'message': 'Abonnement créé avec succès', 'subscription': subscription.to_dict()}), 201

# Subscription Upgrade Request endpoints
@members_bp.route('/subscription/upgrade-request', methods=['POST'])
def create_upgrade_request():
    """Create a subscription upgrade request"""
    print("Upgrade request endpoint called")
    if 'user_id' not in session:
        print("User not authenticated")
        return jsonify({'error': 'Non authentifié'}), 401
    
    data = request.get_json()
    print(f"Request data: {data}")
    
    if not data or 'pack_id' not in data:
        print("Pack ID missing")
        return jsonify({'error': 'Pack ID requis'}), 400
    
    pack = SubscriptionPack.query.get_or_404(data['pack_id'])
    
    if not pack.actif:
        return jsonify({'error': 'Ce pack n\'est pas disponible'}), 400
    
    # Check if user already has a pending request
    existing_request = SubscriptionUpgradeRequest.query.filter_by(
        user_id=session['user_id'],
        statut='en_attente'
    ).first()
    
    if existing_request:
        print(f"User {session['user_id']} already has a pending request")
        return jsonify({'error': 'Vous avez déjà une demande en attente'}), 400
    
    upgrade_request = SubscriptionUpgradeRequest(
        user_id=session['user_id'],
        pack_id=data['pack_id'],
        methode_paiement=data.get('methode_paiement', 'manuel'),
        reference_paiement=data.get('reference_paiement'),
        message=data.get('message')
    )
    
    db.session.add(upgrade_request)
    db.session.commit()
    
    print(f"Upgrade request created: {upgrade_request.id}")
    return jsonify({'message': 'Demande d\'upgrade créée', 'request': upgrade_request.to_dict()}), 201

@members_bp.route('/subscription/upgrade-requests', methods=['GET'])
def get_my_upgrade_requests():
    """Get current user's upgrade requests"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    requests = SubscriptionUpgradeRequest.query.filter_by(
        user_id=session['user_id']
    ).order_by(SubscriptionUpgradeRequest.created_at.desc()).all()
    
    return jsonify({'requests': [r.to_dict() for r in requests]}), 200

