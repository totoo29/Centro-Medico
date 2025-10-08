# src/models_init.py - Inicialización segura de modelos
from src.config_db import db

def init_models():
    """Inicializar todos los modelos de forma segura"""
    try:
        # Importar modelos individuales
        from .models.cliente import Cliente
        from .models.obra_social import ObraSocial
        from .models.plan_obra_social import PlanObraSocial
        from .models.profesional import Profesional
        from .models.servicio import Servicio
        from .models.turno import Turno
        from .models.autorizacion import Autorizacion
        from .models.categoria import Categoria
        from .models.usuario import Usuario
        
        print("✅ Modelos importados correctamente")
        return True
        
    except ImportError as e:
        print(f"⚠️  Error de importación de modelos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado al importar modelos: {e}")
        return False

def get_model_classes():
    """Obtener todas las clases de modelo"""
    try:
        from .models.cliente import Cliente
        from .models.obra_social import ObraSocial
        from .models.plan_obra_social import PlanObraSocial
        from .models.profesional import Profesional
        from .models.servicio import Servicio
        from .models.turno import Turno
        from .models.autorizacion import Autorizacion
        from .models.categoria import Categoria
        from .models.usuario import Usuario
        
        return {
            'Cliente': Cliente,
            'ObraSocial': ObraSocial,
            'PlanObraSocial': PlanObraSocial,
            'Profesional': Profesional,
            'Servicio': Servicio,
            'Turno': Turno,
            'Autorizacion': Autorizacion,
            'Categoria': Categoria,
            'Usuario': Usuario
        }
        
    except Exception as e:
        print(f"❌ Error al obtener clases de modelo: {e}")
        return {}

__all__ = ['init_models', 'get_model_classes']
