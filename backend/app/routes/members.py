from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Region, Quartier, Utilisateur
import json
import os
import math
from werkzeug.utils import secure_filename

members_bp = Blueprint('members', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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
    genre = request.args.get('genre')
    age_min = request.args.get('age_min', type=int)
    age_max = request.args.get('age_max', type=int)
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 9, type=int)
    user_lat = request.args.get('lat', type=float)
    user_lon = request.args.get('lon', type=float)
    
    query = Utilisateur.query.filter_by(actif=True)
    
    if region_id:
        query = query.filter_by(region_id=region_id)
    
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
    
    # First try to get profiles with same genre
    query = Utilisateur.query.filter_by(actif=True)
    
    if user_genre:
        query = query.filter_by(genre=user_genre)
    
    # Order by nombre_visites (most visited first)
    query = query.order_by(Utilisateur.nombre_visites.desc())
    
    profils = query.limit(limit * 2).all()  # Get more to filter by distance
    
    # If no profiles found with same genre, get all active profiles
    if not profils and user_genre:
        query = Utilisateur.query.filter_by(actif=True)
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
        profils_with_distance.append(profil_dict)
    
    # Sort by distance if available, otherwise by visits
    if user_lat and user_lon:
        profils_with_distance.sort(key=lambda x: (x['distance'] is None, x['distance'] or float('inf')))
    
    # Return limited results
    return jsonify({'profils': profils_with_distance[:limit]}), 200

@members_bp.route('/profil/<int:user_id>', methods=['GET'])
def get_profil(user_id):
    user_lat = request.args.get('lat', type=float)
    user_lon = request.args.get('lon', type=float)
    
    user = Utilisateur.query.get_or_404(user_id)
    profil_dict = user.to_dict()
    
    # Calculate distance if user location is provided
    distance = None
    if user_lat and user_lon and user.latitude and user.longitude:
        distance = calculate_distance(user_lat, user_lon, user.latitude, user.longitude)
    
    profil_dict['distance'] = distance
    
    return jsonify({'profil': profil_dict}), 200

@members_bp.route('/profil/<int:user_id>/visite', methods=['POST'])
def increment_visite(user_id):
    user = Utilisateur.query.get_or_404(user_id)
    user.nombre_visites = (user.nombre_visites or 0) + 1
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
