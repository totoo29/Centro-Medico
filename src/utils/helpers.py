import re
from datetime import datetime, date

def formatear_telefono(telefono):
    """Formatear número de teléfono para visualización"""
    if not telefono:
        return ''
    
    # Remover caracteres no numéricos (excepto +)
    telefono_limpio = re.sub(r'[^\d+]', '', str(telefono))
    
    # Si empieza con código de país
    if telefono_limpio.startswith('+54'):
        # Formato argentino: +54 9 XXX XXX-XXXX
        if len(telefono_limpio) >= 13:
            return f"+54 9 {telefono_limpio[5:8]} {telefono_limpio[8:11]}-{telefono_limpio[11:]}"
        return telefono_limpio
    
    # Formato local argentino
    if len(telefono_limpio) == 10:
        return f"{telefono_limpio[:3]} {telefono_limpio[3:6]}-{telefono_limpio[6:]}"
    elif len(telefono_limpio) == 8:
        return f"{telefono_limpio[:4]}-{telefono_limpio[4:]}"
    
    return telefono

def formatear_precio(precio):
    """Formatear precio para visualización"""
    if precio is None or precio == 0:
        return '$0.00'
    
    try:
        precio_float = float(precio)
        return f'${precio_float:,.2f}'.replace(',', '.')
    except (ValueError, TypeError):
        return '$0.00'

def formatear_fecha(fecha):
    """Formatear fecha para visualización"""
    if not fecha:
        return ''
    
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        except ValueError:
            return fecha
    
    if isinstance(fecha, datetime):
        fecha = fecha.date()
    
    if isinstance(fecha, date):
        # Formato dd/mm/yyyy
        return fecha.strftime('%d/%m/%Y')
    
    return str(fecha)

def formatear_hora(hora):
    """Formatear hora para visualización"""
    if not hora:
        return ''
    
    if isinstance(hora, str):
        try:
            hora = datetime.strptime(hora, '%H:%M').time()
        except ValueError:
            return hora
    
    if hasattr(hora, 'strftime'):
        return hora.strftime('%H:%M')
    
    return str(hora)

def formatear_fecha_hora(fecha_hora):
    """Formatear fecha y hora para visualización"""
    if not fecha_hora:
        return ''
    
    if isinstance(fecha_hora, str):
        try:
            fecha_hora = datetime.fromisoformat(fecha_hora)
        except ValueError:
            return fecha_hora
    
    if isinstance(fecha_hora, datetime):
        return fecha_hora.strftime('%d/%m/%Y %H:%M')
    
    return str(fecha_hora)

def calcular_edad(fecha_nacimiento):
    """Calcular edad a partir de fecha de nacimiento"""
    if not fecha_nacimiento:
        return None
    
    if isinstance(fecha_nacimiento, str):
        try:
            fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
        except ValueError:
            return None
    
    if isinstance(fecha_nacimiento, datetime):
        fecha_nacimiento = fecha_nacimiento.date()
    
    if isinstance(fecha_nacimiento, date):
        hoy = date.today()
        edad = hoy.year - fecha_nacimiento.year
        
        # Ajustar si aún no cumplió años este año
        if hoy.month < fecha_nacimiento.month or \
           (hoy.month == fecha_nacimiento.month and hoy.day < fecha_nacimiento.day):
            edad -= 1
        
        return edad
    
    return None

def generar_codigo_unico(prefijo='', longitud=8):
    """Generar código único para identificadores"""
    import secrets
    import string
    
    caracteres = string.ascii_uppercase + string.digits
    codigo = ''.join(secrets.choice(caracteres) for _ in range(longitud))
    
    return f"{prefijo}{codigo}" if prefijo else codigo

def limpiar_texto(texto):
    """Limpiar y normalizar texto"""
    if not texto:
        return ''
    
    # Convertir a string y limpiar espacios
    texto = str(texto).strip()
    
    # Remover espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto

def capitalizar_nombre(nombre):
    """Capitalizar nombre correctamente"""
    if not nombre:
        return ''
    
    # Limpiar texto primero
    nombre = limpiar_texto(nombre)
    
    # Capitalizar cada palabra
    palabras = nombre.split()
    palabras_capitalizadas = []
    
    for palabra in palabras:
        if palabra.lower() in ['de', 'del', 'la', 'el', 'y', 'e']:
            palabras_capitalizadas.append(palabra.lower())
        else:
            palabras_capitalizadas.append(palabra.capitalize())
    
    return ' '.join(palabras_capitalizadas)

def obtener_iniciales(nombre, apellido):
    """Obtener iniciales de nombre y apellido"""
    iniciales = ''
    
    if nombre:
        iniciales += nombre[0].upper()
    
    if apellido:
        iniciales += apellido[0].upper()
    
    return iniciales

def es_fecha_valida(fecha_str, formato='%Y-%m-%d'):
    """Verificar si una fecha string es válida"""
    try:
        datetime.strptime(fecha_str, formato)
        return True
    except (ValueError, TypeError):
        return False

def convertir_a_slug(texto):
    """Convertir texto a slug (URL-friendly)"""
    if not texto:
        return ''
    
    # Convertir a minúsculas
    slug = texto.lower()
    
    # Reemplazar caracteres especiales
    slug = re.sub(r'[áàäâ]', 'a', slug)
    slug = re.sub(r'[éèëê]', 'e', slug)
    slug = re.sub(r'[íìïî]', 'i', slug)
    slug = re.sub(r'[óòöô]', 'o', slug)
    slug = re.sub(r'[úùüû]', 'u', slug)
    slug = re.sub(r'ñ', 'n', slug)
    
    # Remover caracteres no alfanuméricos
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    
    # Reemplazar espacios y guiones múltiples con un solo guión
    slug = re.sub(r'[\s-]+', '-', slug)
    
    # Remover guiones al inicio y final
    slug = slug.strip('-')
    
    return slug