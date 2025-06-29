from flask import Flask, render_template, redirect, url_for
from flask_login import current_user
from src.database import init_db
from src.routes import register_blueprints
from src.auth import init_auth
from config import Config
from datetime import datetime, date

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
    
    # Inicializar autenticación
    init_auth(app)
    
    # SOLUCIÓN: Hacer current_user disponible globalmente en plantillas
    @app.context_processor
    def inject_user():
        """Inyectar current_user y fecha actual en todas las plantillas"""
        from flask_login import current_user
        return dict(
            current_user=current_user,
            today=date.today(),
            now=datetime.now()
        )
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Registrar filtros de plantillas
    register_template_filters(app)
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    # Ruta raíz redirige al login
    @app.route('/')
    def root():
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        return redirect(url_for('auth.login'))
    
    return app

def register_template_filters(app):
    """Registrar filtros personalizados para las plantillas"""
    try:
        from src.utils.helpers import (
            formatear_telefono, formatear_precio, formatear_fecha, 
            formatear_hora, capitalizar_nombre, formatear_fecha_personalizada,
            fecha_hoy_iso, es_fecha_pasada, dias_hasta_fecha
        )
        
        # Filtros básicos
        app.jinja_env.filters['telefono'] = formatear_telefono
        app.jinja_env.filters['precio'] = formatear_precio
        app.jinja_env.filters['fecha'] = formatear_fecha
        app.jinja_env.filters['hora'] = formatear_hora
        app.jinja_env.filters['capitalizar'] = capitalizar_nombre
        
        # NUEVO: Filtros de fecha mejorados
        app.jinja_env.filters['date'] = formatear_fecha_personalizada
        app.jinja_env.filters['fecha_personalizada'] = formatear_fecha_personalizada
        app.jinja_env.filters['es_pasada'] = es_fecha_pasada
        app.jinja_env.filters['dias_hasta'] = dias_hasta_fecha
        
        # Funciones globales para plantillas
        app.jinja_env.globals['fecha_hoy_iso'] = fecha_hoy_iso
        app.jinja_env.globals['date_today'] = lambda: date.today().isoformat()
        
        # CORRECCIÓN ESPECÍFICA PARA EL CALENDARIO
        @app.template_filter('strftime')
        def strftime_filter(fecha, formato='%Y-%m-%d'):
            """Filtro strftime para fechas"""
            if not fecha:
                return ''
            
            if isinstance(fecha, str):
                try:
                    fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
                except ValueError:
                    return fecha
            
            if hasattr(fecha, 'strftime'):
                return fecha.strftime(formato)
            
            return str(fecha)
        
        print("✅ Filtros de plantillas registrados correctamente")
        
    except ImportError as e:
        print(f"⚠️ Error importando filtros: {e}")
        # Definir filtros básicos como fallback
        
        @app.template_filter('telefono')
        def telefono_filter(s):
            return s or ''
        
        @app.template_filter('precio')
        def precio_filter(s):
            return f'${s:.2f}' if s else '$0.00'
        
        @app.template_filter('date')
        def date_filter(fecha_obj, formato='%Y-%m-%d'):
            """Filtro de fecha con fallback mejorado"""
            if not fecha_obj:
                return ''
            
            if isinstance(fecha_obj, str):
                if fecha_obj == 'now':
                    return datetime.now().strftime(formato)
                elif fecha_obj == 'today':
                    return date.today().strftime(formato)
                return fecha_obj
            
            if isinstance(fecha_obj, (datetime, date)):
                return fecha_obj.strftime(formato)
            
            return str(fecha_obj)
        
        @app.template_filter('strftime')
        def strftime_filter(fecha, formato='%Y-%m-%d'):
            """Filtro strftime de fallback"""
            return date_filter(fecha, formato)
        
        # Función global para fecha de hoy
        app.jinja_env.globals['date_today'] = lambda: date.today().isoformat()
        
        print("⚠️ Usando filtros básicos de fallback")

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