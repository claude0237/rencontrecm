import click
from flask.cli import with_appcontext
from app import create_app, db
from app.models import Region, Quartier, Utilisateur

app = create_app()

@app.cli.command()
@with_appcontext
def init_db():
    """Initialize the database with tables and seed data."""
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
    
    click.echo('Database initialized successfully!')

@app.cli.command()
@with_appcontext
def drop_db():
    """Drop all database tables."""
    db.drop_all()
    click.echo('Database dropped!')

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'init-db':
        with app.app_context():
            init_db()
    elif len(sys.argv) > 1 and sys.argv[1] == 'drop-db':
        with app.app_context():
            drop_db()
    else:
        app.run(debug=False, host='0.0.0.0')
