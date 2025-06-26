# src/auth.py - Configuración de Flask-Login
from flask_login import LoginManager
from src.models.usuario import Usuario

login_manager = LoginManager()

def init_auth(app):
    """Inicializar sistema de autenticación"""
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Cargar usuario por ID"""
    # Importación diferida para evitar dependencias circulares
    try:
        from src.models.usuario import Usuario
        return Usuario.query.get(int(user_id))
    except:
        return None

# src/app.py - Actualización para incluir autenticación
from flask import Flask, render_template, redirect, url_for
from flask_login import login_required, current_user
from src.database import init_db
from src.routes import register_blueprints
from src.auth import init_auth
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
    
    # Inicializar autenticación
    init_auth(app)
    
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

# (El código de registro de blueprints ha sido movido a src/routes/__init__.py para evitar errores de importación y dependencias circulares)

# Actualización de src/routes/main.py
from flask import Blueprint, render_template
from flask_login import login_required
from src.models import Cliente, Turno, Profesional, Servicio
from datetime import datetime, date

main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard')
@login_required  # Agregar decorador de login requerido
def index():
    """Página principal con dashboard"""
    # Estadísticas básicas
    total_clientes = Cliente.query.filter_by(activo=True).count()
    total_profesionales = Profesional.query.filter_by(activo=True).count()
    total_servicios = Servicio.query.filter_by(activo=True).count()
    
    # Turnos de hoy
    hoy = date.today()
    turnos_hoy = Turno.query.filter_by(fecha=hoy).count()
    
    # Próximos turnos (próximos 5)
    proximos_turnos = Turno.query.filter(
        Turno.fecha >= hoy,
        Turno.estado.in_(['pendiente', 'confirmado'])
    ).order_by(Turno.fecha, Turno.hora).limit(5).all()
    
    return render_template('dashboard.html',
                         total_clientes=total_clientes,
                         total_profesionales=total_profesionales,
                         total_servicios=total_servicios,
                         turnos_hoy=turnos_hoy,
                         proximos_turnos=proximos_turnos)