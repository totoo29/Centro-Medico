from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from src.models import Turno, Cliente, Profesional, Servicio
from src.services.turno_service import TurnoService
from src.services.cliente_service import ClienteService
from src.services.profesional_service import ProfesionalService
from src.services.servicio_service import ServicioService
from datetime import date, datetime, timedelta
from src.database import db
import calendar
# Importaciones de servicios con manejo de errores
try:
    from src.services.turno_service import TurnoService
except ImportError:
    TurnoService = None
    print("⚠️ TurnoService no disponible")

try:
    from src.services.cliente_service import ClienteService
except ImportError:
    ClienteService = None
    print("⚠️ ClienteService no disponible")

try:
    from src.services.profesional_service import ProfesionalService
except ImportError:
    ProfesionalService = None
    print("⚠️ ProfesionalService no disponible")

try:
    from src.services.servicio_service import ServicioService
except ImportError:
    ServicioService = None
    print("⚠️ ServicioService no disponible")

turnos_bp = Blueprint('turnos', __name__)

# Función helper para obtener servicios con fallback
def get_service_data(service_class, method_name, *args, **kwargs):
    """Obtener datos de un servicio con fallback si no está disponible"""
    if service_class is None:
        return []
    
    try:
        method = getattr(service_class, method_name)
        return method(*args, **kwargs)
    except Exception as e:
        print(f"Error en {service_class.__name__}.{method_name}: {e}")
        return []

# Función helper para manejar errores de servicios
def handle_service_error(service_name, error, default_redirect='turnos.listar'):
    """Manejar errores de servicios de forma consistente"""
    error_msg = f'Error en {service_name}: {str(error)}'
    flash(error_msg, 'error')
    print(error_msg)
    return redirect(url_for(default_redirect))

# ===== FUNCIONES AUXILIARES PARA EL CALENDARIO =====

def generar_datos_calendario(vista, fecha_base, turnos_por_fecha):
    """Generar estructura de datos para el calendario"""
    calendario_data = {
        'vista': vista,
        'titulo': '',
        'fechas': [],
        'semanas': [],
        'horarios': list(range(8, 20))  # 8:00 a 19:00
    }
    
    if vista == 'dia':
        calendario_data['titulo'] = fecha_base.strftime('%A, %d de %B de %Y')
        calendario_data['fechas'] = [fecha_base]
        
    elif vista == 'semana':
        # Encontrar el lunes de la semana
        dias_desde_lunes = fecha_base.weekday()
        lunes = fecha_base - timedelta(days=dias_desde_lunes)
        
        calendario_data['titulo'] = f"Semana del {lunes.strftime('%d/%m')} al {(lunes + timedelta(days=6)).strftime('%d/%m/%Y')}"
        calendario_data['fechas'] = [lunes + timedelta(days=i) for i in range(7)]
        
    else:  # mes
        calendario_data['titulo'] = fecha_base.strftime('%B %Y')
        
        # Generar todas las semanas del mes
        primer_dia = fecha_base.replace(day=1)
        
        # Calcular último día del mes
        if primer_dia.month == 12:
            ultimo_dia = primer_dia.replace(year=primer_dia.year + 1, month=1) - timedelta(days=1)
        else:
            ultimo_dia = primer_dia.replace(month=primer_dia.month + 1) - timedelta(days=1)
        
        # Encontrar el primer lunes antes o igual al primer día del mes
        dias_desde_lunes = primer_dia.weekday()
        inicio_calendario = primer_dia - timedelta(days=dias_desde_lunes)
        
        # Generar semanas
        fecha_actual = inicio_calendario
        while fecha_actual <= ultimo_dia or len(calendario_data['semanas']) == 0:
            semana = []
            for i in range(7):
                dia_actual = fecha_actual + timedelta(days=i)
                semana.append({
                    'fecha': dia_actual,
                    'es_mes_actual': dia_actual.month == fecha_base.month,
                    'turnos': turnos_por_fecha.get(dia_actual.isoformat(), [])
                })
            calendario_data['semanas'].append(semana)
            fecha_actual += timedelta(days=7)
            
            # Límite de seguridad - máximo 6 semanas
            if len(calendario_data['semanas']) >= 6:
                break
    
    return calendario_data

def calcular_estadisticas_calendario(turnos, vista):
    """Calcular estadísticas para el período del calendario"""
    if not turnos:
        return {
            'total_turnos': 0,
            'pendientes': 0,
            'confirmados': 0,
            'completados': 0,
            'cancelados': 0,
            'ingresos_total': 0
        }
    
    estadisticas = {
        'total_turnos': len(turnos),
        'pendientes': sum(1 for t in turnos if t.estado == 'pendiente'),
        'confirmados': sum(1 for t in turnos if t.estado == 'confirmado'),
        'completados': sum(1 for t in turnos if t.estado == 'completado'),
        'cancelados': sum(1 for t in turnos if t.estado == 'cancelado'),
        'ingresos_total': sum(
            float(t.precio_final or t.servicio.precio or 0) 
            for t in turnos if t.estado == 'completado'
        )
    }
    
    return estadisticas

def organizar_turnos_por_fecha(turnos):
    """Organizar turnos por fecha"""
    turnos_por_fecha = {}
    for turno in turnos:
        fecha_str = turno.fecha.isoformat()
        if fecha_str not in turnos_por_fecha:
            turnos_por_fecha[fecha_str] = []
        turnos_por_fecha[fecha_str].append({
            'id': turno.id,
            'hora': turno.hora.strftime('%H:%M'),
            'cliente': turno.cliente.nombre_completo,
            'profesional': turno.profesional.nombre_completo,
            'servicio': turno.servicio.nombre,
            'estado': turno.estado,
            'duracion': turno.servicio.duracion,
            'precio': float(turno.precio_final or turno.servicio.precio or 0)
        })
    return turnos_por_fecha

def get_color_by_estado(estado):
    """Obtener color por estado del turno"""
    colores = {
        'pendiente': '#ffc107',
        'confirmado': '#17a2b8',
        'completado': '#28a745',
        'cancelado': '#dc3545'
    }
    return colores.get(estado, '#6c757d')

turnos_bp = Blueprint('turnos', __name__)

@turnos_bp.route('/')
@login_required
def listar():
    """Listar todos los turnos con filtros"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 15, type=int)
    fecha_desde = request.args.get('fecha_desde', type=str)
    fecha_hasta = request.args.get('fecha_hasta', type=str)
    estado = request.args.get('estado', type=str)
    profesional_id = request.args.get('profesional_id', type=int)
    
    try:
        turnos = TurnoService.get_paginated_turnos(
            page=page,
            per_page=per_page,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            estado=estado,
            profesional_id=profesional_id
        )
        
        profesionales = ProfesionalService.get_all_profesionales()
        estados = ['pendiente', 'confirmado', 'completado', 'cancelado']
        
        return render_template('turnos/listar.html', 
                             turnos=turnos,
                             profesionales=profesionales,
                             estados=estados,
                             filtros={
                                 'fecha_desde': fecha_desde,
                                 'fecha_hasta': fecha_hasta,
                                 'estado': estado,
                                 'profesional_id': profesional_id
                             })
    except Exception as e:
        flash(f'Error al cargar turnos: {str(e)}', 'error')
        return render_template('turnos/listar.html', turnos=None, profesionales=[], estados=[])

@turnos_bp.route('/calendario')
@login_required
def calendario():
    """Vista de calendario de turnos completamente rediseñada"""
    # Obtener parámetros de la URL
    fecha_param = request.args.get('fecha', date.today().isoformat())
    profesional_id = request.args.get('profesional_id', type=int)
    vista = request.args.get('vista', 'semana')  # dia, semana, mes
    
    try:
        # Validar y parsear fecha
        try:
            fecha_base = datetime.strptime(fecha_param, '%Y-%m-%d').date()
        except ValueError:
            fecha_base = date.today()
        
        # Calcular fechas según la vista
        if vista == 'dia':
            fecha_inicio = fecha_base
            fecha_fin = fecha_base
        elif vista == 'semana':
            # Encontrar el lunes de la semana
            dias_desde_lunes = fecha_base.weekday()
            fecha_inicio = fecha_base - timedelta(days=dias_desde_lunes)
            fecha_fin = fecha_inicio + timedelta(days=6)
        else:  # mes
            fecha_inicio = fecha_base.replace(day=1)
            siguiente_mes = fecha_inicio.replace(month=fecha_inicio.month + 1) if fecha_inicio.month < 12 else fecha_inicio.replace(year=fecha_inicio.year + 1, month=1)
            fecha_fin = siguiente_mes - timedelta(days=1)
        
        # Obtener turnos en el rango de fechas
        turnos_query = Turno.query.filter(
            Turno.fecha >= fecha_inicio,
            Turno.fecha <= fecha_fin
        )
        
        # Filtrar por profesional si se especifica
        if profesional_id:
            turnos_query = turnos_query.filter(Turno.profesional_id == profesional_id)
        
        # Obtener turnos ordenados
        turnos = turnos_query.order_by(Turno.fecha, Turno.hora).all()
        
        # Organizar turnos por fecha para facilitar el renderizado
        turnos_por_fecha = {}
        for turno in turnos:
            fecha_str = turno.fecha.isoformat()
            if fecha_str not in turnos_por_fecha:
                turnos_por_fecha[fecha_str] = []
            turnos_por_fecha[fecha_str].append({
                'id': turno.id,
                'hora': turno.hora.strftime('%H:%M'),
                'cliente': turno.cliente.nombre_completo,
                'profesional': turno.profesional.nombre_completo,
                'servicio': turno.servicio.nombre,
                'estado': turno.estado,
                'duracion': turno.servicio.duracion,
                'precio': float(turno.precio_final or turno.servicio.precio or 0)
            })
        
        # Obtener lista de profesionales para el filtro
        profesionales = ProfesionalService.get_all_profesionales()
        
        # Generar datos del calendario según la vista
        calendario_data = generar_datos_calendario(vista, fecha_base, turnos_por_fecha)
        
        # Calcular estadísticas del período
        estadisticas = calcular_estadisticas_calendario(turnos, vista)
        
        return render_template('turnos/calendario.html',
                             vista=vista,
                             fecha_base=fecha_base,
                             fecha_inicio=fecha_inicio,
                             fecha_fin=fecha_fin,
                             turnos_por_fecha=turnos_por_fecha,
                             profesionales=profesionales,
                             profesional_id=profesional_id,
                             calendario_data=calendario_data,
                             estadisticas=estadisticas)
                             
    except Exception as e:
        flash(f'Error al cargar calendario: {str(e)}', 'error')
        return render_template('turnos/calendario.html', 
                             vista='semana', 
                             fecha_base=date.today(),
                             turnos_por_fecha={},
                             profesionales=[],
                             calendario_data={},
                             estadisticas={})

def generar_datos_calendario(vista, fecha_base, turnos_por_fecha):
    """Generar estructura de datos para el calendario"""
    calendario_data = {
        'vista': vista,
        'titulo': '',
        'fechas': [],
        'semanas': [],
        'horarios': list(range(8, 20))  # 8:00 a 19:00
    }
    
    if vista == 'dia':
        calendario_data['titulo'] = fecha_base.strftime('%A, %d de %B de %Y')
        calendario_data['fechas'] = [fecha_base]
        
    elif vista == 'semana':
        # Encontrar el lunes de la semana
        dias_desde_lunes = fecha_base.weekday()
        lunes = fecha_base - timedelta(days=dias_desde_lunes)
        
        calendario_data['titulo'] = f"Semana del {lunes.strftime('%d/%m')} al {(lunes + timedelta(days=6)).strftime('%d/%m/%Y')}"
        calendario_data['fechas'] = [lunes + timedelta(days=i) for i in range(7)]
        
    else:  # mes
        calendario_data['titulo'] = fecha_base.strftime('%B %Y')
        
        # Generar todas las semanas del mes
        primer_dia = fecha_base.replace(day=1)
        ultimo_dia = (primer_dia.replace(month=primer_dia.month + 1) if primer_dia.month < 12 
                     else primer_dia.replace(year=primer_dia.year + 1, month=1)) - timedelta(days=1)
        
        # Encontrar el primer lunes antes o igual al primer día del mes
        dias_desde_lunes = primer_dia.weekday()
        inicio_calendario = primer_dia - timedelta(days=dias_desde_lunes)
        
        # Generar semanas
        fecha_actual = inicio_calendario
        while fecha_actual <= ultimo_dia:
            semana = []
            for i in range(7):
                dia_actual = fecha_actual + timedelta(days=i)
                semana.append({
                    'fecha': dia_actual,
                    'es_mes_actual': dia_actual.month == fecha_base.month,
                    'turnos': turnos_por_fecha.get(dia_actual.isoformat(), [])
                })
            calendario_data['semanas'].append(semana)
            fecha_actual += timedelta(days=7)
            
            # Evitar bucle infinito
            if fecha_actual > ultimo_dia + timedelta(days=7):
                break
    
    return calendario_data

def calcular_estadisticas_calendario(turnos, vista):
    """Calcular estadísticas para el período del calendario"""
    if not turnos:
        return {
            'total_turnos': 0,
            'pendientes': 0,
            'confirmados': 0,
            'completados': 0,
            'cancelados': 0,
            'ingresos_total': 0
        }
    
    estadisticas = {
        'total_turnos': len(turnos),
        'pendientes': sum(1 for t in turnos if t.estado == 'pendiente'),
        'confirmados': sum(1 for t in turnos if t.estado == 'confirmado'),
        'completados': sum(1 for t in turnos if t.estado == 'completado'),
        'cancelados': sum(1 for t in turnos if t.estado == 'cancelado'),
        'ingresos_total': sum(
            float(t.precio_final or t.servicio.precio or 0) 
            for t in turnos if t.estado == 'completado'
        )
    }
    
    return estadisticas

@turnos_bp.route('/nuevo')
@login_required
def nuevo():
    """Formulario para crear nuevo turno"""
    try:
        clientes = ClienteService.get_all_clientes()
        profesionales = ProfesionalService.get_all_profesionales()
        servicios = ServicioService.get_all_servicios()
        
        return render_template('turnos/formulario.html',
                             clientes=clientes,
                             profesionales=profesionales,
                             servicios=servicios)
    except Exception as e:
        flash(f'Error al cargar formulario: {str(e)}', 'error')
        return redirect(url_for('turnos.listar'))

@turnos_bp.route('/crear', methods=['POST'])
@login_required
def crear():
    """Crear nuevo turno"""
    try:
        data = request.get_json() if request.is_json else request.form
        turno = TurnoService.crear_turno(data)
        
        if request.is_json:
            return jsonify({'success': True, 'turno': turno.to_dict()})
        
        flash('Turno creado exitosamente', 'success')
        return redirect(url_for('turnos.listar'))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al crear turno: {str(e)}', 'error')
        return redirect(url_for('turnos.nuevo'))

@turnos_bp.route('/<int:id>')
@login_required
def detalle(id):
    """Ver detalle de un turno"""
    try:
        turno = TurnoService.get_turno_by_id(id)
        if not turno:
            flash('Turno no encontrado', 'error')
            return redirect(url_for('turnos.listar'))
        
        return render_template('turnos/detalle.html', turno=turno)
    except Exception as e:
        flash(f'Error al cargar turno: {str(e)}', 'error')
        return redirect(url_for('turnos.listar'))

@turnos_bp.route('/<int:id>/editar')
@login_required
def editar(id):
    """Formulario para editar turno"""
    try:
        turno = TurnoService.get_turno_by_id(id)
        if not turno:
            flash('Turno no encontrado', 'error')
            return redirect(url_for('turnos.listar'))
        
        clientes = ClienteService.get_all_clientes()
        profesionales = ProfesionalService.get_all_profesionales()
        servicios = ServicioService.get_all_servicios()
        
        return render_template('turnos/formulario.html',
                             turno=turno,
                             clientes=clientes,
                             profesionales=profesionales,
                             servicios=servicios)
    except Exception as e:
        flash(f'Error al cargar turno: {str(e)}', 'error')
        return redirect(url_for('turnos.listar'))

@turnos_bp.route('/<int:id>/actualizar', methods=['POST', 'PUT'])
@login_required
def actualizar(id):
    """Actualizar turno existente"""
    try:
        data = request.get_json() if request.is_json else request.form
        turno = TurnoService.actualizar_turno(id, data)
        
        if not turno:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Turno no encontrado'}), 404
            flash('Turno no encontrado', 'error')
            return redirect(url_for('turnos.listar'))
        
        if request.is_json:
            return jsonify({'success': True, 'turno': turno.to_dict()})
        
        flash('Turno actualizado exitosamente', 'success')
        return redirect(url_for('turnos.detalle', id=id))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al actualizar turno: {str(e)}', 'error')
        return redirect(url_for('turnos.editar', id=id))

@turnos_bp.route('/<int:id>/cambiar-estado', methods=['POST'])
@login_required
def cambiar_estado(id):
    """Cambiar estado de un turno"""
    try:
        data = request.get_json() if request.is_json else request.form
        nuevo_estado = data.get('estado')
        
        turno = TurnoService.cambiar_estado_turno(id, nuevo_estado)
        
        if not turno:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Turno no encontrado'}), 404
            flash('Turno no encontrado', 'error')
            return redirect(url_for('turnos.listar'))
        
        if request.is_json:
            return jsonify({'success': True, 'turno': turno.to_dict()})
        
        flash(f'Turno marcado como {nuevo_estado}', 'success')
        return redirect(url_for('turnos.detalle', id=id))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al cambiar estado: {str(e)}', 'error')
        return redirect(url_for('turnos.detalle', id=id))

@turnos_bp.route('/<int:id>/cancelar', methods=['POST'])
@login_required
def cancelar(id):
    """Cancelar un turno"""
    try:
        data = request.get_json() if request.is_json else request.form
        motivo = data.get('motivo', '')
        turno = TurnoService.cancelar_turno(id, motivo)
        
        if not turno:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Turno no encontrado'}), 404
            flash('Turno no encontrado', 'error')
            return redirect(url_for('turnos.listar'))
        
        if request.is_json:
            return jsonify({'success': True, 'turno': turno.to_dict()})
        
        flash('Turno cancelado exitosamente', 'success')
        return redirect(url_for('turnos.listar'))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al cancelar turno: {str(e)}', 'error')
        return redirect(url_for('turnos.detalle', id=id))

@turnos_bp.route('/horarios-disponibles')
@login_required
def horarios_disponibles():
    """API para obtener horarios disponibles - CORREGIDA"""
    fecha = request.args.get('fecha')
    profesional_id = request.args.get('profesional_id', type=int)
    servicio_id = request.args.get('servicio_id', type=int)
    
    if not fecha or not profesional_id:
        return jsonify({'error': 'Fecha y profesional son requeridos'}), 400
    
    try:
        # Validar formato de fecha
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        # No permitir fechas pasadas
        if fecha_obj < date.today():
            return jsonify({'horarios': []})
        
        # Obtener duración del servicio
        duracion = 60  # Por defecto 60 minutos
        if servicio_id:
            servicio = Servicio.query.get(servicio_id)
            if servicio:
                duracion = servicio.duracion
        
        # Verificar si el profesional existe
        profesional = Profesional.query.get(profesional_id)
        if not profesional:
            return jsonify({'error': 'Profesional no encontrado'}), 404
        
        # Horario de trabajo (esto podría venir de configuración del profesional)
        horarios_base = []
        hora_inicio = 8  # 8:00 AM
        hora_fin = 19    # 7:00 PM
        intervalo = 30   # Intervalos de 30 minutos
        
        # Generar horarios base
        hora_actual = hora_inicio * 60  # Convertir a minutos
        hora_limite = hora_fin * 60
        
        while hora_actual < hora_limite:
            horas = hora_actual // 60
            minutos = hora_actual % 60
            horario = f"{horas:02d}:{minutos:02d}"
            horarios_base.append(horario)
            hora_actual += intervalo
        
        # Obtener turnos ocupados para esa fecha y profesional
        turnos_ocupados = Turno.query.filter(
            Turno.profesional_id == profesional_id,
            Turno.fecha == fecha_obj,
            Turno.estado.in_(['pendiente', 'confirmado'])
        ).all()
        
        # Filtrar horarios ocupados considerando la duración
        horarios_disponibles = []
        
        for horario in horarios_base:
            hora_partes = horario.split(':')
            hora_inicio_minutos = int(hora_partes[0]) * 60 + int(hora_partes[1])
            hora_fin_minutos = hora_inicio_minutos + duracion
            
            # Verificar si hay conflicto con algún turno existente
            conflicto = False
            
            for turno in turnos_ocupados:
                turno_inicio_minutos = turno.hora.hour * 60 + turno.hora.minute
                turno_fin_minutos = turno_inicio_minutos + turno.servicio.duracion
                
                # Verificar solapamiento
                if (hora_inicio_minutos < turno_fin_minutos and 
                    hora_fin_minutos > turno_inicio_minutos):
                    conflicto = True
                    break
            
            if not conflicto:
                horarios_disponibles.append(horario)
        
        return jsonify({'horarios': horarios_disponibles})
        
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido'}), 400
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@turnos_bp.route('/resumen-dia')
@login_required
def resumen_dia():
    """API para obtener resumen del día"""
    fecha = request.args.get('fecha', date.today().isoformat())
    profesional_id = request.args.get('profesional_id', type=int)
    
    try:
        resumen = TurnoService.get_resumen_dia(fecha, profesional_id)
        return jsonify(resumen)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@turnos_bp.route('/proximos')
@login_required
def proximos():
    """API para obtener próximos turnos"""
    limite = request.args.get('limite', 5, type=int)
    profesional_id = request.args.get('profesional_id', type=int)
    
    try:
        turnos = TurnoService.get_proximos_turnos(limite, profesional_id)
        return jsonify([turno.to_dict() for turno in turnos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@turnos_bp.route('/reporte')
@login_required
def reporte():
    """Generar reporte de turnos"""
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    formato = request.args.get('formato', 'excel')
    
    try:
        if formato == 'excel':
            return TurnoService.exportar_excel(fecha_desde, fecha_hasta)
        elif formato == 'pdf':
            return TurnoService.exportar_pdf(fecha_desde, fecha_hasta)
        else:
            return TurnoService.exportar_csv(fecha_desde, fecha_hasta)
    except Exception as e:
        flash(f'Error al generar reporte: {str(e)}', 'error')
        return redirect(url_for('turnos.listar'))

# ===== NUEVAS RUTAS PARA MEJORAR EL CALENDARIO =====

@turnos_bp.route('/api/turnos-calendario')
@login_required
def api_turnos_calendario():
    """API para obtener turnos del calendario en formato JSON"""
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    profesional_id = request.args.get('profesional_id', type=int)
    
    try:
        # Validar fechas
        if not fecha_inicio or not fecha_fin:
            return jsonify({'error': 'Se requieren fecha_inicio y fecha_fin'}), 400
        
        fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        # Construir query
        query = Turno.query.filter(
            Turno.fecha >= fecha_inicio_obj,
            Turno.fecha <= fecha_fin_obj
        )
        
        if profesional_id:
            query = query.filter(Turno.profesional_id == profesional_id)
        
        turnos = query.order_by(Turno.fecha, Turno.hora).all()
        
        # Formatear respuesta
        turnos_data = []
        for turno in turnos:
            turnos_data.append({
                'id': turno.id,
                'fecha': turno.fecha.isoformat(),
                'hora': turno.hora.strftime('%H:%M'),
                'cliente': turno.cliente.nombre_completo,
                'profesional': turno.profesional.nombre_completo,
                'servicio': turno.servicio.nombre,
                'estado': turno.estado,
                'duracion': turno.servicio.duracion,
                'precio': float(turno.precio_final or turno.servicio.precio or 0),
                'color': get_color_by_estado(turno.estado)
            })
        
        return jsonify({'turnos': turnos_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_color_by_estado(estado):
    """Obtener color por estado del turno"""
    colores = {
        'pendiente': '#ffc107',
        'confirmado': '#17a2b8',
        'completado': '#28a745',
        'cancelado': '#dc3545'
    }
    return colores.get(estado, '#6c757d')

@turnos_bp.route('/crear-rapido', methods=['POST'])
@login_required
def crear_rapido():
    """Crear turno rápido desde el calendario"""
    try:
        data = request.get_json()
        
        # Validaciones básicas
        required_fields = ['fecha', 'hora', 'profesional_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} es requerido'}), 400
        
        # Si no hay cliente o servicio, redirigir al formulario completo
        if not data.get('cliente_id') or not data.get('servicio_id'):
            url_formulario = url_for('turnos.nuevo', 
                                   fecha=data.get('fecha'),
                                   hora=data.get('hora'),
                                   profesional_id=data.get('profesional_id'))
            return jsonify({
                'success': False, 
                'redirect': url_formulario,
                'message': 'Redirigiendo al formulario completo'
            })
        
        # Crear turno con todos los datos
        turno = TurnoService.crear_turno(data)
        
        return jsonify({
            'success': True, 
            'turno': turno.to_dict(),
            'message': 'Turno creado exitosamente'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400