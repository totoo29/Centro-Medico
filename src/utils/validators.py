import re
from datetime import datetime, date

def validar_email(email):
    """Validar formato de email"""
    if not email:
        return False
    
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, email.strip()))

def validar_telefono(telefono):
    """Validar formato de teléfono"""
    if not telefono:
        return False
    
    # Remover espacios y caracteres especiales
    telefono_limpio = re.sub(r'[^\d+]', '', telefono.strip())
    
    # Validar longitud y formato básico
    if len(telefono_limpio) < 8 or len(telefono_limpio) > 15:
        return False
    
    # Debe empezar con dígito o +
    return telefono_limpio[0].isdigit() or telefono_limpio[0] == '+'

def validar_precio(precio):
    """Validar que el precio sea un número válido"""
    try:
        precio_float = float(precio)
        return precio_float >= 0
    except (ValueError, TypeError):
        return False

def validar_fecha(fecha_str):
    """Validar formato de fecha (YYYY-MM-DD)"""
    try:
        datetime.strptime(fecha_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validar_hora(hora_str):
    """Validar formato de hora (HH:MM)"""
    try:
        datetime.strptime(hora_str, '%H:%M')
        return True
    except ValueError:
        return False

def validar_duracion(duracion):
    """Validar duración en minutos"""
    try:
        duracion_int = int(duracion)
        return 1 <= duracion_int <= 480  # Entre 1 minuto y 8 horas
    except (ValueError, TypeError):
        return False

def validar_estado_turno(estado):
    """Validar estado de turno"""
    estados_validos = ['pendiente', 'confirmado', 'completado', 'cancelado']
    return estado in estados_validos

def validar_nombre(nombre):
    """Validar que el nombre no esté vacío y tenga formato válido"""
    if not nombre or not nombre.strip():
        return False
    
    # Solo letras, espacios, tildes y algunos caracteres especiales
    patron = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-\'\.]+$'
    return bool(re.match(patron, nombre.strip())) and len(nombre.strip()) <= 100

def validar_longitud_texto(texto, min_length=0, max_length=255):
    """Validar longitud de texto"""
    if not texto:
        return min_length == 0
    
    return min_length <= len(texto.strip()) <= max_length