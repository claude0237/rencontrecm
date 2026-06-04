from datetime import datetime, timedelta
import json
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class Region(db.Model):
    __tablename__ = 'regions'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, unique=True)
    quartiers = db.relationship('Quartier', backref='region', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom
        }

class Quartier(db.Model):
    __tablename__ = 'quartiers'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'region_id': self.region_id
        }

class Utilisateur(db.Model):
    __tablename__ = 'utilisateurs'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(20), nullable=False)  # 'homme' ou 'femme'
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False)
    quartier_id = db.Column(db.Integer, db.ForeignKey('quartiers.id'), nullable=False)
    description = db.Column(db.Text)
    photo_url = db.Column(db.String(255))
    photos = db.Column(db.Text)  # JSON array of photo URLs
    photo_principale = db.Column(db.Integer, default=0)  # Index of the main photo in photos array
    contact_whatsapp = db.Column(db.String(50))
    whatsapp_enabled = db.Column(db.Boolean, default=True)  # Enable/disable WhatsApp contact
    contact_direct = db.Column(db.String(50), nullable=False, unique=True)  # Numéro de téléphone principal
    actif = db.Column(db.Boolean, default=True)
    disabled_reason = db.Column(db.String(100), nullable=True)  # Raison de désactivation
    disabled_at = db.Column(db.DateTime, nullable=True)  # Date de désactivation
    est_admin = db.Column(db.Boolean, default=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    derniere_connexion = db.Column(db.DateTime)
    en_ligne = db.Column(db.Boolean, default=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    equipement = db.Column(db.String(255))
    nombre_visites = db.Column(db.Integer, default=0)
    
    region = db.relationship('Region', lazy=True)
    quartier = db.relationship('Quartier', backref='utilisateurs', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        photos_list = []
        if self.photos:
            try:
                photos_list = json.loads(self.photos)
            except:
                photos_list = []
        
        return {
            'id': self.id,
            'email': self.email,
            'nom': self.nom,
            'age': self.age,
            'genre': self.genre,
            'region_id': self.region_id,
            'region_nom': self.region.nom if self.region else None,
            'quartier_id': self.quartier_id,
            'quartier_nom': self.quartier.nom if self.quartier else None,
            'description': self.description,
            'photo_url': self.photo_url,
            'photos': photos_list,
            'photo_principale': self.photo_principale,
            'contact_whatsapp': self.contact_whatsapp,
            'whatsapp_enabled': self.whatsapp_enabled,
            'contact_direct': self.contact_direct,
            'actif': self.actif,
            'disabled_reason': self.disabled_reason,
            'disabled_at': self.disabled_at.isoformat() if self.disabled_at else None,
            'est_admin': self.est_admin,
            'derniere_connexion': self.derniere_connexion.isoformat() if self.derniere_connexion else None,
            'en_ligne': 'Oui' if self.en_ligne else 'Non',
            'latitude': self.latitude,
            'longitude': self.longitude,
            'equipement': self.equipement,
            'nombre_visites': self.nombre_visites
        }

class AlerteGlobale(db.Model):
    __tablename__ = 'alertes_globales'
    
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'active': self.active,
            'date_creation': self.date_creation.isoformat()
        }

class PasswordReset(db.Model):
    __tablename__ = 'password_resets'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    telephone = db.Column(db.String(20), nullable=True)
    code = db.Column(db.String(6), nullable=False)
    attempts = db.Column(db.Integer, default=0)
    wave_count = db.Column(db.Integer, default=0)  # Number of failed reset waves
    last_attempt_at = db.Column(db.DateTime, nullable=True)  # Last failed attempt time
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used = db.Column(db.Boolean, default=False)
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        return not self.used and not self.is_expired() and self.attempts < 3
    
    def is_in_cooldown(self):
        """Check if user is in 30-minute cooldown after failed attempts"""
        if not self.last_attempt_at or self.wave_count == 0:
            return False
        cooldown_end = self.last_attempt_at + timedelta(minutes=30)
        return datetime.utcnow() < cooldown_end
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'telephone': self.telephone,
            'expires_at': self.expires_at.isoformat(),
            'attempts': self.attempts,
            'wave_count': self.wave_count,
            'is_valid': self.is_valid(),
            'is_in_cooldown': self.is_in_cooldown()
        }

class Appel(db.Model):
    __tablename__ = 'appels'
    
    id = db.Column(db.Integer, primary_key=True)
    appelant_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=True)
    appele_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    appelant = db.relationship('Utilisateur', foreign_keys=[appelant_id], lazy=True)
    appele = db.relationship('Utilisateur', foreign_keys=[appele_id], lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'appelant_id': self.appelant_id,
            'appele_id': self.appele_id,
            'created_at': self.created_at.isoformat()
        }

class WhatsAppClick(db.Model):
    __tablename__ = 'whatsapp_clicks'
    
    id = db.Column(db.Integer, primary_key=True)
    cliquant_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=True)
    cible_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    cliquant = db.relationship('Utilisateur', foreign_keys=[cliquant_id], lazy=True)
    cible = db.relationship('Utilisateur', foreign_keys=[cible_id], lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliquant_id': self.cliquant_id,
            'cible_id': self.cible_id,
            'created_at': self.created_at.isoformat()
        }

class WhatsAppSetting(db.Model):
    __tablename__ = 'whatsapp_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    default_message = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'default_message': self.default_message,
            'updated_at': self.updated_at.isoformat()
        }

class AdPack(db.Model):
    __tablename__ = 'ad_packs'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    prix = db.Column(db.Float, nullable=False)
    duree_jours = db.Column(db.Integer, nullable=False)
    actif = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'description': self.description,
            'prix': self.prix,
            'duree_jours': self.duree_jours,
            'actif': self.actif,
            'created_at': self.created_at.isoformat()
        }

class Advertisement(db.Model):
    __tablename__ = 'advertisements'
    
    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    numero_contact = db.Column(db.String(50))
    whatsapp = db.Column(db.String(50))
    duree_jours = db.Column(db.Integer, nullable=False)
    statut = db.Column(db.String(20), default='brouillon')  # brouillon, en_attente, validee, rejetee, suspendue, expiree
    pack_id = db.Column(db.Integer, db.ForeignKey('ad_packs.id'))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_debut_validite = db.Column(db.DateTime)
    date_fin_validite = db.Column(db.DateTime)
    paiement_effectue = db.Column(db.Boolean, default=False)
    
    utilisateur = db.relationship('Utilisateur', backref='advertisements', lazy=True)
    pack = db.relationship('AdPack', backref='advertisements', lazy=True)
    validation_history = db.relationship('AdValidationHistory', backref='advertisement', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'utilisateur_id': self.utilisateur_id,
            'titre': self.titre,
            'description': self.description,
            'image_url': self.image_url,
            'numero_contact': self.numero_contact,
            'whatsapp': self.whatsapp,
            'duree_jours': self.duree_jours,
            'statut': self.statut,
            'pack_id': self.pack_id,
            'pack_nom': self.pack.nom if self.pack else None,
            'pack_prix': self.pack.prix if self.pack else None,
            'date_creation': self.date_creation.isoformat(),
            'date_debut_validite': self.date_debut_validite.isoformat() if self.date_debut_validite else None,
            'date_fin_validite': self.date_fin_validite.isoformat() if self.date_fin_validite else None,
            'paiement_effectue': self.paiement_effectue
        }

class AdValidationHistory(db.Model):
    __tablename__ = 'ad_validation_history'
    
    id = db.Column(db.Integer, primary_key=True)
    advertisement_id = db.Column(db.Integer, db.ForeignKey('advertisements.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # validee, rejetee, suspendue
    motif_rejet = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    admin = db.relationship('Utilisateur', backref='ad_validations', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'advertisement_id': self.advertisement_id,
            'admin_id': self.admin_id,
            'admin_nom': self.admin.nom if self.admin else None,
            'action': self.action,
            'motif_rejet': self.motif_rejet,
            'created_at': self.created_at.isoformat()
        }

class AdminNotification(db.Model):
    __tablename__ = 'admin_notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # nouvelle_publicite, paiement_publicitaire, autre
    titre = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    advertisement_id = db.Column(db.Integer, db.ForeignKey('advertisements.id'))
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))
    lue = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    advertisement = db.relationship('Advertisement', backref='notifications', lazy=True)
    utilisateur = db.relationship('Utilisateur', backref='notifications', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'titre': self.titre,
            'message': self.message,
            'advertisement_id': self.advertisement_id,
            'utilisateur_id': self.utilisateur_id,
            'utilisateur_nom': self.utilisateur.nom if self.utilisateur else None,
            'lue': self.lue,
            'created_at': self.created_at.isoformat()
        }
