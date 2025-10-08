# src/database.py - Configuración de la base de datos
# Importar la instancia única de SQLAlchemy desde config_db
from src.config_db import db, migrate

def init_db(app):
    """Inicializar la base de datos con la aplicación Flask"""
    # La configuración ya está hecha en config_db.py
    # Solo necesitamos inicializar las extensiones
    from src.config_db import configure_db
    configure_db(app)
    
    with app.app_context():
        # Crear todas las tablas solo si no existen
        db.create_all()

def get_db():
    """Obtener la instancia de la base de datos"""
    return db

__all__ = ['db', 'migrate', 'init_db', 'get_db']
