import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-rencontres-cm-2026'
    
    # Support pour MySQL ou SQLite
    #Pour MySQL: mysql+pymysql://user:password@localhost/db_name
    # Pour SQLite: sqlite:///rencontres_cm.db
    #$#SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///rencontres_cm.db'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:softtech@localhost/rencontres_cm'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_HTTPONLY = True
