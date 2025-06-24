from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Inicializar la base de datos con la aplicación Flask"""
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        db.create_all()

# Create src directory and required files if they don't exist
if not os.path.exists('src'):
    os.makedirs('src')

with open('src/__init__.py', 'a'):
    pass

with open('src/database.py', 'a'):
    pass

with open('src/models.py', 'a'):
    pass

with open('src/app.py', 'a'):
    pass