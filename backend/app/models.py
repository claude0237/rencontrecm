from datetime import datetime
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
    contact_direct = db.Column(db.String(50), nullable=False, unique=True)  # Numéro de téléphone principal
    actif = db.Column(db.Boolean, default=True)
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
            'contact_direct': self.contact_direct,
            'actif': self.actif,
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
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used = db.Column(db.Boolean, default=False)
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        return not self.used and not self.is_expired() and self.attempts < 3
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'telephone': self.telephone,
            'expires_at': self.expires_at.isoformat(),
            'attempts': self.attempts,
            'is_valid': self.is_valid()
        }
