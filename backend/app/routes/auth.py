from flask import Blueprint, request, session, jsonify
from datetime import datetime, timedelta
from app import db
from app.models import Utilisateur, PasswordReset
from app.services.notification_service import NotificationService
import json
import random
import string

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validation des champs obligatoires
    required_fields = ['email', 'password', 'nom', 'age', 'genre', 'contact_direct', 'region_id', 'quartier_id']
    if not data or not all(k in data for k in required_fields):
        return jsonify({'error': 'Veuillez compléter votre profil. Tous les champs marqués d\'un * sont obligatoires.'}), 400
    
    # Validation du téléphone (contact_direct)
    contact_direct = data.get('contact_direct', '').strip()
    if not contact_direct:
        return jsonify({'error': 'Numéro de téléphone obligatoire'}), 400
    
    # Format Cameroun: +237XXXXXXXXX ou format national (9 chiffres commençant par 6)
    import re
    cameroon_pattern = re.compile(r'^(\+237)?[6][0-9]{8}$')
    if not cameroon_pattern.match(contact_direct.replace(' ', '')):
        return jsonify({'error': 'Format de téléphone invalide. Utilisez +237XXXXXXXXX ou XXXXXXXXX (9 chiffres commençant par 6)'}), 400
    
    # Validation des photos (minimum 1 photo requise)
    if not data.get('photos') or len(data.get('photos', [])) == 0:
        return jsonify({'error': 'Au moins une photo est requise'}), 400
    
    if Utilisateur.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email déjà utilisé'}), 400
    
    if Utilisateur.query.filter_by(contact_direct=contact_direct).first():
        return jsonify({'error': 'Numéro de téléphone déjà utilisé'}), 400
    
    user = Utilisateur(
        email=data['email'],
        nom=data['nom'],
        age=data['age'],
        genre=data['genre'],
        contact_direct=contact_direct,
        region_id=data['region_id'],
        quartier_id=data['quartier_id'],
        description=data.get('description', ''),
        contact_whatsapp=data.get('contact_whatsapp', ''),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        equipement=data.get('equipement', '')
    )
    
    # Handle photos
    if data.get('photos') and len(data['photos']) > 0:
        user.photos = json.dumps(data['photos'])
    
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    session['user_id'] = user.id
    session['is_admin'] = user.est_admin
    
    return jsonify({'message': 'Inscription réussie', 'user': user.to_dict()}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['email', 'password']):
            return jsonify({'error': 'Email et mot de passe requis'}), 400
        
        user = Utilisateur.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        
        if not user.actif:
            return jsonify({'error': 'Compte désactivé'}), 403
        
        # Update derniere_connexion, en_ligne, geolocation, and equipment
        user.derniere_connexion = datetime.utcnow()
        user.en_ligne = True
        if data.get('latitude') is not None:
            user.latitude = data['latitude']
        if data.get('longitude') is not None:
            user.longitude = data['longitude']
        if data.get('equipement'):
            user.equipement = data['equipement']
        db.session.commit()
        
        session['user_id'] = user.id
        session['is_admin'] = user.est_admin
        
        return jsonify({'message': 'Connexion réussie', 'user': user.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        user_id = session.get('user_id')
        if user_id:
            user = Utilisateur.query.get(user_id)
            if user:
                user.en_ligne = False
                db.session.commit()
        
        session.pop('user_id', None)
        session.pop('is_admin', None)
        return jsonify({'message': 'Déconnexion réussie'}), 200
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    user = Utilisateur.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    return jsonify({'user': user.to_dict()}), 200

# Password Reset Endpoints
@auth_bp.route('/password-reset/request', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    
    if not data or ('email' not in data and 'contact_direct' not in data):
        return jsonify({'error': 'Email ou téléphone requis'}), 400
    
    identifier = data.get('email') or data.get('contact_direct')
    
    # Find user by email or phone
    user = None
    if '@' in identifier:
        user = Utilisateur.query.filter_by(email=identifier).first()
    else:
        user = Utilisateur.query.filter_by(contact_direct=identifier).first()
    
    if not user:
        # Don't reveal if user exists for security
        return jsonify({'message': 'Si le compte existe, un code de réinitialisation a été envoyé'}), 200
    
    # Generate 6-digit code
    code = ''.join(random.choices(string.digits, k=6))
    
    # Create password reset record
    # Invalidate previous unused codes for this user
    PasswordReset.query.filter_by(email=user.email, used=False).update({'used': True})
    
    reset = PasswordReset(
        email=user.email,
        telephone=user.contact_direct,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=15)
    )
    
    db.session.add(reset)
    db.session.commit()
    
    # Send code via email or SMS
    # Try email first, if configured
    email_sent = NotificationService.send_password_reset_code(user, code, method='email')
    
    # If email not sent or SMS is preferred, try SMS
    if not email_sent:
        sms_sent = NotificationService.send_password_reset_code(user, code, method='sms')
        if not sms_sent:
            # Fallback to console if neither works
            print(f"Password reset code for {user.email}: {code}")
    
    return jsonify({'message': 'Si le compte existe, un code de réinitialisation a été envoyé'}), 200

@auth_bp.route('/password-reset/verify', methods=['POST'])
def verify_reset_code():
    data = request.get_json()
    
    if not data or 'code' not in data or ('email' not in data and 'contact_direct' not in data):
        return jsonify({'error': 'Code et identifiant requis'}), 400
    
    identifier = data.get('email') or data.get('contact_direct')
    code = data['code']
    
    # Find user
    user = None
    if '@' in identifier:
        user = Utilisateur.query.filter_by(email=identifier).first()
    else:
        user = Utilisateur.query.filter_by(contact_direct=identifier).first()
    
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    # Find valid reset code
    reset = PasswordReset.query.filter_by(
        email=user.email,
        code=code,
        used=False
    ).order_by(PasswordReset.created_at.desc()).first()
    
    if not reset:
        return jsonify({'error': 'Code invalide'}), 400
    
    if reset.is_expired():
        return jsonify({'error': 'Code expiré'}), 400
    
    if reset.attempts >= 3:
        return jsonify({'error': 'Trop de tentatives. Veuillez demander un nouveau code.'}), 400
    
    # Increment attempts
    reset.attempts += 1
    db.session.commit()
    
    if reset.code == code:
        return jsonify({'message': 'Code validé avec succès', 'email': user.email}), 200
    else:
        return jsonify({'error': 'Code incorrect'}), 400

@auth_bp.route('/password-reset/reset', methods=['POST'])
def reset_password():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['email', 'code', 'new_password']):
        return jsonify({'error': 'Email, code et nouveau mot de passe requis'}), 400
    
    email = data['email']
    code = data['code']
    new_password = data['new_password']
    
    # Find user
    user = Utilisateur.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    # Find valid reset code
    reset = PasswordReset.query.filter_by(
        email=email,
        code=code,
        used=False
    ).order_by(PasswordReset.created_at.desc()).first()
    
    if not reset or not reset.is_valid():
        return jsonify({'error': 'Code invalide ou expiré'}), 400
    
    # Reset password
    user.set_password(new_password)
    
    # Mark code as used
    reset.used = True
    
    db.session.commit()
    
    # Send confirmation email
    NotificationService.send_password_reset_confirmation(user)
    
    return jsonify({'message': 'Mot de passe réinitialisé avec succès'}), 200
