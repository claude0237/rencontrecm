from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
cors = CORS()

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder='../../frontend/templates',
                static_folder='../../frontend/static')
    app.config.from_object(config_class)
    
    db.init_app(app)
    cors.init_app(app)
    
    from app.routes.auth import auth_bp
    from app.routes.members import members_bp
    from app.routes.admin import admin_bp
    from app.routes.ads import ads_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(members_bp, url_prefix='/api/v1')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(ads_bp, url_prefix='/api/v1/ads')
    
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('main/index.html')
    
    @app.route('/login')
    def login():
        from flask import render_template
        return render_template('auth/login.html')
    
    @app.route('/register')
    def register():
        from flask import render_template
        return render_template('auth/register.html')
    
    @app.route('/forgot-password')
    def forgot_password():
        from flask import render_template
        return render_template('auth/forgot_password.html')
    
    @app.route('/verify-code')
    def verify_code():
        from flask import render_template
        return render_template('auth/verify_code.html')
    
    @app.route('/reset-password')
    def reset_password():
        from flask import render_template
        return render_template('auth/reset_password.html')
    
    @app.route('/profil/<int:user_id>')
    def profil(user_id):
        from flask import render_template
        return render_template('main/profil.html')
    
    @app.route('/profil')
    def profil_current():
        from flask import render_template, session
        if 'user_id' not in session:
            return render_template('auth/login.html')
        return render_template('main/profil.html')
    
    @app.route('/mes-pubs')
    def mes_pubs():
        from flask import render_template, session, redirect
        if 'user_id' not in session:
            return redirect('/login')
        return render_template('main/mes_pubs.html')
    
    @app.route('/creer-pub')
    def creer_pub():
        from flask import render_template, session, redirect
        if 'user_id' not in session:
            return redirect('/login')
        return render_template('main/creer_pub.html')
    
    @app.route('/modifier-pub/<int:ad_id>')
    def modifier_pub(ad_id):
        from flask import render_template, session, redirect
        if 'user_id' not in session:
            return redirect('/login')
        return render_template('main/modifier_pub.html')
    
    @app.route('/admin/dashboard')
    def admin_dashboard():
        from flask import render_template, session, redirect
        if 'user_id' not in session:
            return redirect('/login')
        from app.models import Utilisateur
        user = Utilisateur.query.get(session['user_id'])
        if not user or not user.est_admin:
            return redirect('/')
        return render_template('admin/dashboard.html')
    
    @app.route('/admin/utilisateurs')
    def admin_utilisateurs():
        from flask import render_template, session, redirect
        if 'user_id' not in session:
            return redirect('/login')
        from app.models import Utilisateur
        user = Utilisateur.query.get(session['user_id'])
        if not user or not user.est_admin:
            return redirect('/')
        return render_template('admin/utilisateurs.html')
    
    @app.route('/admin/geographie')
    def admin_geographie():
        from flask import render_template, session, redirect
        if 'user_id' not in session:
            return redirect('/login')
        from app.models import Utilisateur
        user = Utilisateur.query.get(session['user_id'])
        if not user or not user.est_admin:
            return redirect('/')
        return render_template('admin/geographie.html')
    
    @app.route('/admin/alertes')
    def admin_alertes():
        from flask import render_template, session, redirect
        if 'user_id' not in session:
            return redirect('/login')
        from app.models import Utilisateur
        user = Utilisateur.query.get(session['user_id'])
        if not user or not user.est_admin:
            return redirect('/')
        return render_template('admin/alertes.html')
    
    @app.route('/admin/publicites')
    def admin_publicites():
        from flask import render_template, session, redirect
        if 'user_id' not in session:
            return redirect('/login')
        from app.models import Utilisateur
        user = Utilisateur.query.get(session['user_id'])
        if not user or not user.est_admin:
            return redirect('/')
        return render_template('admin/publicites.html')
    
    @app.route('/admin/packs')
    def admin_packs():
        from flask import render_template, session, redirect
        if 'user_id' not in session:
            return redirect('/login')
        from app.models import Utilisateur
        user = Utilisateur.query.get(session['user_id'])
        if not user or not user.est_admin:
            return redirect('/')
        return render_template('admin/packs.html')
    
    @app.route('/admin/subscription-packs')
    def admin_subscription_packs():
        from flask import render_template, session, redirect
        if 'user_id' not in session:
            return redirect('/login')
        from app.models import Utilisateur
        user = Utilisateur.query.get(session['user_id'])
        if not user or not user.est_admin:
            return redirect('/')
        return render_template('admin/subscription_packs.html')
    
    @app.route('/admin/user-subscriptions')
    def admin_user_subscriptions():
        from flask import render_template, session, redirect
        if 'user_id' not in session:
            return redirect('/login')
        from app.models import Utilisateur
        user = Utilisateur.query.get(session['user_id'])
        if not user or not user.est_admin:
            return redirect('/')
        return render_template('admin/user_subscriptions.html')

    @app.route('/admin/upgrade-requests')
    def admin_upgrade_requests():
        from flask import render_template, session, redirect
        if 'user_id' not in session:
            return redirect('/login')
        from app.models import Utilisateur
        user = Utilisateur.query.get(session['user_id'])
        if not user or not user.est_admin:
            return redirect('/')
        return render_template('admin/upgrade_requests.html')
    
    @app.route('/pub/<int:ad_id>')
    def pub_details(ad_id):
        from flask import render_template
        return render_template('main/pub_details.html')
    
    @app.route('/abonnements')
    def abonnements():
        from flask import render_template, session, redirect
        if 'user_id' not in session:
            return redirect('/login')
        return render_template('members/abonnements.html')
    
    @app.route('/logout')
    def logout():
        from flask import session, redirect
        from app.models import Utilisateur
        from app import db
        
        user_id = session.get('user_id')
        if user_id:
            user = Utilisateur.query.get(user_id)
            if user:
                user.en_ligne = False
                db.session.commit()
        
        session.pop('user_id', None)
        session.pop('is_admin', None)
        return redirect('/')
    
    return app
