from app import create_app, db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    try:
        # Check if column already exists
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('user_subscription')]
        
        if 'premiere_periode_decouverte' not in columns:
            db.session.execute(db.text('ALTER TABLE user_subscription ADD COLUMN premiere_periode_decouverte BOOLEAN DEFAULT FALSE'))
            db.session.commit()
            print('Column premiere_periode_decouverte added successfully')
        else:
            print('Column premiere_periode_decouverte already exists')
    except Exception as e:
        print(f'Error adding column: {e}')
        db.session.rollback()
