# src/auth.py - Configuración de Flask-Login
from flask_login import LoginManager

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
    try:
        from src.models.usuario import Usuario
        return Usuario.query.get(int(user_id))
    except Exception as e:
        print(f"Error cargando usuario {user_id}: {e}")
        return None