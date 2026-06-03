from flask import Blueprint, request, jsonify
from app import db
from app.models import AlerteGlobale, Utilisateur, Region, Quartier, Appel
from app.utils import admin_required

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
