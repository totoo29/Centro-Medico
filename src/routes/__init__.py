from .main import main_bp
from .clientes import clientes_bp
from .categorias import categorias_bp
from .profesionales import profesionales_bp
from .servicios import servicios_bp
from .turnos import turnos_bp

def register_blueprints(app):
    """Registrar todos los blueprints en la aplicación Flask"""
    try:
        from .main import main_bp
        app.register_blueprint(main_bp)
        print("✅ Blueprint main registrado")
    except ImportError as e:
        print(f"⚠️ Error importando main: {e}")
    
    try:
        from .clientes import clientes_bp
        app.register_blueprint(clientes_bp, url_prefix='/clientes')
        print("✅ Blueprint clientes registrado")
    except ImportError as e:
        print(f"⚠️ Error importando clientes: {e}")
    
    try:
        from .categorias import categorias_bp
        app.register_blueprint(categorias_bp, url_prefix='/categorias')
        print("✅ Blueprint categorias registrado")
    except ImportError as e:
        print(f"⚠️ Error importando categorias: {e}")
    
    try:
        from .profesionales import profesionales_bp
        app.register_blueprint(profesionales_bp, url_prefix='/profesionales')
        print("✅ Blueprint profesionales registrado")
    except ImportError as e:
        print(f"⚠️ Error importando profesionales: {e}")
    
    try:
        from .servicios import servicios_bp
        app.register_blueprint(servicios_bp, url_prefix='/servicios')
        print("✅ Blueprint servicios registrado")
    except ImportError as e:
        print(f"⚠️ Error importando servicios: {e}")
    
    try:
        from .turnos import turnos_bp
        app.register_blueprint(turnos_bp, url_prefix='/turnos')
        print("✅ Blueprint turnos registrado")
    except ImportError as e:
        print(f"⚠️ Error importando turnos: {e}")

# Importaciones opcionales para compatibilidad
try:
    from .main import main_bp
except ImportError:
    main_bp = None

try:
    from .clientes import clientes_bp
except ImportError:
    clientes_bp = None

try:
    from .categorias import categorias_bp
except ImportError:
    categorias_bp = None

try:
    from .profesionales import profesionales_bp
except ImportError:
    profesionales_bp = None

try:
    from .servicios import servicios_bp
except ImportError:
    servicios_bp = None

try:
    from .turnos import turnos_bp
except ImportError:
    turnos_bp = None