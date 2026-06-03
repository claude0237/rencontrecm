from app import create_app, db
from app.models import Utilisateur

app = create_app()

with app.app_context():
    admin = Utilisateur.query.filter_by(email='admin@rencontres.cm').first()
    if admin:
        print(f"Admin account found:")
        print(f"Email: {admin.email}")
        print(f"Nom: {admin.nom}")
        print(f"Actif: {admin.actif}")
        print(f"Est admin: {admin.est_admin}")
        print(f"Password hash: {admin.password_hash}")
        
        # Test password verification
        test_password = 'Cm2026!Admin'
        if admin.check_password(test_password):
            print("Password verification: SUCCESS")
        else:
            print("Password verification: FAILED")
    else:
        print("Admin account NOT found in database")
