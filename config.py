import os
from datetime import timedelta

class Config:
    """Configuración base para la aplicación Flask"""
    
    # Configuración básica de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuración de base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///consultorio.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Cambiar a True para ver las consultas SQL en desarrollo
    
    # Configuración de paginación
    POSTS_PER_PAGE = 10
    CLIENTES_PER_PAGE = 10
    TURNOS_PER_PAGE = 15
    
    # Configuración de archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo para uploads
    
    # Configuración de correo (para futuras implementaciones)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configuración de zona horaria
    TIMEZONE = 'America/Argentina/Buenos_Aires'
    
    # Configuración de sesiones
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # Configuración del sistema
    SYSTEM_NAME = 'Sistema de Gestión - Consultorio Médico'
    SYSTEM_VERSION = '1.2.1'
    SYSTEM_AUTHOR = 'Marcelo Diaz'
    
    # Horarios de trabajo por defecto
    HORARIO_INICIO = '08:00'
    HORARIO_FIN = '18:00'
    INTERVALO_TURNOS = 30  # minutos
    
    # Configuración de backup
    BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
    
    @staticmethod
    def init_app(app):
        """Inicialización adicional de la aplicación"""
        pass

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Mostrar consultas SQL en desarrollo

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    # SQLite para producción
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///consultorio.db'

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}