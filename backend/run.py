import click
from flask.cli import with_appcontext
from app import create_app, db
from app.models import Region, Quartier, Utilisateur
import os

def init_db():
    """Initialize the database with tables and seed data."""
    db.create_all()
    
    # Run SQL migrations if they exist
    migration_files = [
        'add_password_resets_table.sql',
        'add_security_fields.sql',
        'add_ad_photos_support.sql'
    ]
    
    for migration_file in migration_files:
        migration_path = os.path.join(os.path.dirname(__file__), migration_file)
        if os.path.exists(migration_path):
            try:
                with open(migration_path, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                    # Split by semicolon and execute each statement
                    statements = [s.strip() for s in sql_content.split(';') if s.strip()]
                    for statement in statements:
                        db.session.execute(statement)
                    db.session.commit()
                    click.echo(f'Migration {migration_file} executed successfully!')
            except Exception as e:
                db.session.rollback()
                click.echo(f'Warning: Migration {migration_file} failed (may already be applied): {e}')
    
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
            contact_direct='691234567',
            est_admin=True,
            actif=True
        )
        admin.set_password('Cm2026!Admin')
        db.session.add(admin)
        db.session.commit()
    
    click.echo('Database initialized successfully!')

def drop_db():
    """Drop all database tables."""
    db.drop_all()
    click.echo('Database dropped!')

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'init-db':
        app = create_app()
        with app.app_context():
            init_db()
        sys.exit(0)
    elif len(sys.argv) > 1 and sys.argv[1] == 'drop-db':
        app = create_app()
        with app.app_context():
            drop_db()
        sys.exit(0)
    else:
        app = create_app()
        
        @app.cli.command()
        @with_appcontext
        def init_db_cli():
            """Initialize the database with tables and seed data."""
            init_db()
        
        @app.cli.command()
        @with_appcontext
        def drop_db_cli():
            """Drop all database tables."""
            drop_db()
        
        app.run(debug=True)
