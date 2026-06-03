from app import create_app, db
from app.models import Region, Quartier, Utilisateur

app = create_app()

with app.app_context():
    db.create_all()
    
    # Add 10 regions of Cameroon
    regions_data = [
        'Douala', 'Yaoundé', 'Bafoussam', 'Bamenda', 
        'Garoua', 'Maroua', 'Ngaoundéré', 'Buea',
        'Kribi', 'Limbé'
    ]
    
    for nom in regions_data:
        if not Region.query.filter_by(nom=nom).first():
            region = Region(nom=nom)
            db.session.add(region)
    
    db.session.commit()
    
    # Add communes for Douala
    douala = Region.query.filter_by(nom='Douala').first()
    douala_quartiers = [
        'Douala 1er', 'Douala 2e', 'Douala 3e', 'Douala 4e', 'Douala 5e'
    ]
    
    for nom in douala_quartiers:
        if not Quartier.query.filter_by(nom=nom, region_id=douala.id).first():
            quartier = Quartier(nom=nom, region_id=douala.id)
            db.session.add(quartier)
    
    # Add communes for Yaoundé
    yaounde = Region.query.filter_by(nom='Yaoundé').first()
    yaounde_quartiers = [
        'Yaoundé 1er', 'Yaoundé 2e', 'Yaoundé 3e', 'Yaoundé 4e', 'Yaoundé 5e', 'Yaoundé 6e', 'Yaoundé 7e'
    ]
    
    for nom in yaounde_quartiers:
        if not Quartier.query.filter_by(nom=nom, region_id=yaounde.id).first():
            quartier = Quartier(nom=nom, region_id=yaounde.id)
            db.session.add(quartier)
    
    db.session.commit()
    
    # Create admin account
    if not Utilisateur.query.filter_by(email='admin@rencontres.cm').first():
        admin = Utilisateur(
            email='admin@rencontres.cm',
            nom='Administrateur',
            age=30,
            genre='homme',
            region_id=douala.id,
            quartier_id=Quartier.query.filter_by(region_id=douala.id).first().id,
            description='Compte administrateur',
            est_admin=True,
            actif=True
        )
        admin.set_password('Cm2026!Admin')
        db.session.add(admin)
        db.session.commit()
    
    print('Database initialized successfully!')
