# src/config_db.py - Configuración específica para evitar conflictos de SQLAlchemy
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Configuración global para evitar conflictos de tablas
SQLALCHEMY_CONFIG = {
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_ENGINE_OPTIONS': {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'check_same_thread': False
        }
    }
}

# Crear instancia única de SQLAlchemy con configuración específica
db = SQLAlchemy(
    engine_options={
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
)
migrate = Migrate()

def configure_db(app):
    """Configurar la base de datos con la aplicación Flask"""
    # Aplicar configuración específica
    for key, value in SQLALCHEMY_CONFIG.items():
        app.config.setdefault(key, value)
    
    # Configuración adicional para evitar conflictos
    app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///instance/consultorio.db')
    app.config.setdefault('SQLALCHEMY_BINDS', {})
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    
    return db, migrate

def init_db_tables(app):
    """Inicializar las tablas de la base de datos"""
    with app.app_context():
        try:
            # Importar modelos antes de crear tablas
            from .models.cliente import Cliente
            from .models.obra_social import ObraSocial
            from .models.plan_obra_social import PlanObraSocial
            
            db.create_all()
            print("✅ Tablas de base de datos creadas/verificadas correctamente")
        except Exception as e:
            print(f"⚠️  Advertencia al crear tablas: {e}")
            # Continuar aunque haya advertencias

def get_db():
    """Obtener la instancia de la base de datos"""
    return db

__all__ = ['db', 'migrate', 'configure_db', 'init_db_tables', 'get_db']
