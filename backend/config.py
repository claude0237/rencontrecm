import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-rencontres-cm-2026'
    
    # Support pour MySQL ou SQLite
    # Pour MySQL: mysql+pymysql://user:password@localhost/db_name
    # Pour SQLite: sqlite:///rencontres_cm.db
    #$#SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///rencontres_cm.db'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:ncd@172.19.14.29/rencontres_cm'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_HTTPONLY = True
    
    # SMTP Configuration for Email
    SMTP_SERVER = os.environ.get('SMTP_SERVER') or 'smtp.gmail.com'
    SMTP_PORT = int(os.environ.get('SMTP_PORT') or 587)
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    SMTP_FROM = os.environ.get('SMTP_FROM') or 'noreply@rencontrescm.com'
    
    # SMS Configuration
    SMS_PROVIDER = os.environ.get('SMS_PROVIDER') or 'none'  # 'twilio', 'africastalking', or 'none'
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER')
    
    # Africa's Talking Configuration
    AFRICASTALKING_USERNAME = os.environ.get('AFRICASTALKING_USERNAME')
    AFRICASTALKING_API_KEY = os.environ.get('AFRICASTALKING_API_KEY')
