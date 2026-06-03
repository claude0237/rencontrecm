from functools import wraps
from flask import session, jsonify
from app.models import Utilisateur

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Non authentifié'}), 401
        
        user = Utilisateur.query.get(session['user_id'])
        if not user or not user.est_admin:
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        return f(*args, **kwargs)
    return decorated_function
