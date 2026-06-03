from flask import Blueprint, request, session, jsonify
from datetime import datetime
from app import db
from app.models import Utilisateur
import json

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['email', 'password', 'nom', 'age', 'genre', 'region_id', 'quartier_id']):
        return jsonify({'error': 'Données incomplètes'}), 400
    
    if Utilisateur.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email déjà utilisé'}), 400
    
    user = Utilisateur(
        email=data['email'],
        nom=data['nom'],
        age=data['age'],
        genre=data['genre'],
        region_id=data['region_id'],
        quartier_id=data['quartier_id'],
        description=data.get('description', ''),
        contact_whatsapp=data.get('contact_whatsapp', ''),
        contact_direct=data.get('contact_direct', ''),
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
