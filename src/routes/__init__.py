# src/routes/__init__.py
"""
Módulo de rutas para el Sistema de Gestión de Consultorio Médico
Registra todos los blueprints de la aplicación
"""

def register_blueprints(app):
    """Registrar todos los blueprints en la aplicación Flask"""
    
    # ========================================
    # BLUEPRINT DE AUTENTICACIÓN (PRIMERO)
    # ========================================
    try:
        from .auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
        print("✅ Blueprint 'auth' registrado correctamente")
    except ImportError as e:
        print(f"⚠️ Error al registrar blueprint 'auth': {e}")
        print("   Asegúrate de que existe el archivo: src/routes/auth.py")
    except Exception as e:
        print(f"❌ Error inesperado con blueprint 'auth': {e}")
    
    # ========================================
    # BLUEPRINT PRINCIPAL - DASHBOARD
    # ========================================
    try:
        from .main import main_bp
        app.register_blueprint(main_bp)
        print("✅ Blueprint 'main' registrado correctamente")
    except ImportError as e:
        print(f"⚠️ Error al registrar blueprint 'main': {e}")
        print("   Asegúrate de que existe el archivo: src/routes/main.py")
    except Exception as e:
        print(f"❌ Error inesperado con blueprint 'main': {e}")
    
    # ========================================
    # BLUEPRINT DE CLIENTES/PACIENTES
    # ========================================
    try:
        from .clientes import clientes_bp
        app.register_blueprint(clientes_bp, url_prefix='/clientes')
        print("✅ Blueprint 'clientes' registrado correctamente")
    except ImportError as e:
        print(f"⚠️ Error al registrar blueprint 'clientes': {e}")
        print("   Asegúrate de que existe el archivo: src/routes/clientes.py")
    except Exception as e:
        print(f"❌ Error inesperado con blueprint 'clientes': {e}")
    
    # ========================================
    # BLUEPRINT DE CATEGORÍAS
    # ========================================
    try:
        from .categorias import categorias_bp
        app.register_blueprint(categorias_bp, url_prefix='/categorias')
        print("✅ Blueprint 'categorias' registrado correctamente")
    except ImportError as e:
        print(f"⚠️ Error al registrar blueprint 'categorias': {e}")
        print("   Asegúrate de que existe el archivo: src/routes/categorias.py")
    except Exception as e:
        print(f"❌ Error inesperado con blueprint 'categorias': {e}")
    
    # ========================================
    # BLUEPRINT DE PROFESIONALES/MÉDICOS
    # ========================================
    try:
        from .profesionales import profesionales_bp
        app.register_blueprint(profesionales_bp, url_prefix='/profesionales')
        print("✅ Blueprint 'profesionales' registrado correctamente")
    except ImportError as e:
        print(f"⚠️ Error al registrar blueprint 'profesionales': {e}")
        print("   Asegúrate de que existe el archivo: src/routes/profesionales.py")
    except Exception as e:
        print(f"❌ Error inesperado con blueprint 'profesionales': {e}")
    
    # ========================================
    # BLUEPRINT DE SERVICIOS
    # ========================================
    try:
        from .servicios import servicios_bp
        app.register_blueprint(servicios_bp, url_prefix='/servicios')
        print("✅ Blueprint 'servicios' registrado correctamente")
    except ImportError as e:
        print(f"⚠️ Error al registrar blueprint 'servicios': {e}")
        print("   Asegúrate de que existe el archivo: src/routes/servicios.py")
    except Exception as e:
        print(f"❌ Error inesperado con blueprint 'servicios': {e}")
    
    # ========================================
    # BLUEPRINT DE TURNOS
    # ========================================
    try:
        from .turnos import turnos_bp
        app.register_blueprint(turnos_bp, url_prefix='/turnos')
        print("✅ Blueprint 'turnos' registrado correctamente")
    except ImportError as e:
        print(f"⚠️ Error al registrar blueprint 'turnos': {e}")
        print("   Asegúrate de que existe el archivo: src/routes/turnos.py")
    except Exception as e:
        print(f"❌ Error inesperado con blueprint 'turnos': {e}")
    
    # ========================================
    # BLUEPRINT DE OBRAS SOCIALES
    # ========================================
    try:
        from .obras_sociales import obras_sociales_bp
        app.register_blueprint(obras_sociales_bp, url_prefix='/obras-sociales')
        print("✅ Blueprint 'obras_sociales' registrado correctamente")
    except ImportError as e:
        print(f"⚠️ Error al registrar blueprint 'obras_sociales': {e}")
        print("   Asegúrate de que existe el archivo: src/routes/obras_sociales.py")
    except Exception as e:
        print(f"❌ Error inesperado con blueprint 'obras_sociales': {e}")
    
    # ========================================
    # BLUEPRINT DE AUTORIZACIONES
    # ========================================
    try:
        from .autorizaciones import autorizaciones_bp
        app.register_blueprint(autorizaciones_bp, url_prefix='/autorizaciones')
        print("✅ Blueprint 'autorizaciones' registrado correctamente")
    except ImportError as e:
        print(f"⚠️ Error al registrar blueprint 'autorizaciones': {e}")
        print("   Asegúrate de que existe el archivo: src/routes/autorizaciones.py")
    except Exception as e:
        print(f"❌ Error inesperado con blueprint 'autorizaciones': {e}")
    
    print("🎯 Registro de blueprints completado")


# ========================================
# IMPORTACIONES OPCIONALES PARA COMPATIBILIDAD
# ========================================

# Estas importaciones permiten que otros módulos importen directamente
# los blueprints desde este archivo si es necesario

try:
    from .auth import auth_bp
except ImportError:
    auth_bp = None
    print("⚠️ Blueprint 'auth' no disponible para importación directa")

try:
    from .main import main_bp
except ImportError:
    main_bp = None
    print("⚠️ Blueprint 'main' no disponible para importación directa")

try:
    from .clientes import clientes_bp
except ImportError:
    clientes_bp = None
    print("⚠️ Blueprint 'clientes' no disponible para importación directa")

try:
    from .categorias import categorias_bp
except ImportError:
    categorias_bp = None
    print("⚠️ Blueprint 'categorias' no disponible para importación directa")

try:
    from .profesionales import profesionales_bp
except ImportError:
    profesionales_bp = None
    print("⚠️ Blueprint 'profesionales' no disponible para importación directa")

try:
    from .servicios import servicios_bp
except ImportError:
    servicios_bp = None
    print("⚠️ Blueprint 'servicios' no disponible para importación directa")

try:
    from .turnos import turnos_bp
except ImportError:
    turnos_bp = None
    print("⚠️ Blueprint 'turnos' no disponible para importación directa")

# ========================================
# LISTA DE TODOS LOS BLUEPRINTS DISPONIBLES
# ========================================

__all__ = [
    'register_blueprints',
    'auth_bp',
    'main_bp', 
    'clientes_bp',
    'categorias_bp',
    'profesionales_bp',
    'servicios_bp',
    'turnos_bp'
]

# ========================================
# INFORMACIÓN DE DEPURACIÓN
# ========================================

def get_blueprint_info():
    """
    Función de utilidad para obtener información sobre los blueprints registrados
    Útil para debugging
    """
    blueprints_info = {
        'auth': {
            'available': auth_bp is not None,
            'url_prefix': '/auth',
            'description': 'Autenticación y gestión de usuarios'
        },
        'main': {
            'available': main_bp is not None,
            'url_prefix': '/',
            'description': 'Dashboard principal'
        },
        'clientes': {
            'available': clientes_bp is not None,
            'url_prefix': '/clientes',
            'description': 'Gestión de pacientes'
        },
        'categorias': {
            'available': categorias_bp is not None,
            'url_prefix': '/categorias',
            'description': 'Gestión de categorías de servicios'
        },
        'profesionales': {
            'available': profesionales_bp is not None,
            'url_prefix': '/profesionales',
            'description': 'Gestión de médicos y profesionales'
        },
        'servicios': {
            'available': servicios_bp is not None,
            'url_prefix': '/servicios',
            'description': 'Gestión de servicios médicos'
        },
        'turnos': {
            'available': turnos_bp is not None,
            'url_prefix': '/turnos',
            'description': 'Gestión de turnos y citas'
        }
    }
    
    return blueprints_info

def print_blueprint_status():
    """
    Imprime el estado de todos los blueprints
    Útil para debugging durante el desarrollo
    """
    print("\n" + "="*50)
    print("📋 ESTADO DE BLUEPRINTS")
    print("="*50)
    
    info = get_blueprint_info()
    
    for name, data in info.items():
        status = "✅ Disponible" if data['available'] else "❌ No disponible"
        print(f"{name.upper():<15} {status:<15} {data['url_prefix']:<15} {data['description']}")
    
    print("="*50)

# Ejecutar al importar este módulo (solo en modo debug)
if __name__ == '__main__':
    print_blueprint_status()

from flask import Blueprint

clientes_bp = Blueprint('clientes', __name__)

# Puedes agregar tus rutas aquí
@clientes_bp.route('/')
def index():
    return