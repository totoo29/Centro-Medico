from flask import Flask, render_template
from src.database import init_db
from src.routes import register_blueprints
from config import Config

def create_app(config=None):
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configuración
    if config:
        app.config.update(config)
    else:
        app.config.from_object(Config)
    
    # Inicializar base de datos
    init_db(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Registrar filtros de plantillas
    register_template_filters(app)
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    return app

def register_template_filters(app):
    """Registrar filtros personalizados para las plantillas"""
    try:
        from src.utils.helpers import (
            formatear_telefono, formatear_precio, formatear_fecha, 
            formatear_hora, capitalizar_nombre
        )
        
        app.jinja_env.filters['telefono'] = formatear_telefono
        app.jinja_env.filters['precio'] = formatear_precio
        app.jinja_env.filters['fecha'] = formatear_fecha
        app.jinja_env.filters['hora'] = formatear_hora
        app.jinja_env.filters['capitalizar'] = capitalizar_nombre
        print("✅ Filtros de plantillas registrados")
    except ImportError as e:
        print(f"⚠️ Error importando filtros: {e}")

def register_error_handlers(app):
    """Registrar manejadores de errores"""
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from src.database import db
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    
    print("✅ Manejadores de errores registrados")

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)