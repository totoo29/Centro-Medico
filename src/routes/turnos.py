from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from src.models import Turno
from src.services.turno_service import TurnoService
from src.services.cliente_service import ClienteService
from src.services.profesional_service import ProfesionalService
from src.services.servicio_service import ServicioService
from datetime import date, datetime
from src.database import db

turnos_bp = Blueprint('turnos', __name__)

@turnos_bp.route('/')
def listar():
    """Listar todos los turnos"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    fecha_desde = request.args.get('fecha_desde', type=str)
    fecha_hasta = request.args.get('fecha_hasta', type=str)
    estado = request.args.get('estado', type=str)
    profesional_id = request.args.get('profesional_id', type=int)
    
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

@turnos_bp.route('/calendario')
def calendario():
    """Vista de calendario de turnos"""
    fecha = request.args.get('fecha', date.today().isoformat())
    profesional_id = request.args.get('profesional_id', type=int)
    
    turnos = TurnoService.get_turnos_by_fecha(fecha, profesional_id)
    profesionales = ProfesionalService.get_all_profesionales()
    
    return render_template('turnos/calendario.html',
                         turnos=turnos,
                         profesionales=profesionales,
                         fecha=fecha,
                         profesional_id=profesional_id)

@turnos_bp.route('/nuevo')
def nuevo():
    """Formulario para crear nuevo turno"""
    clientes = ClienteService.get_all_clientes()
    profesionales = ProfesionalService.get_all_profesionales()
    servicios = ServicioService.get_all_servicios()
    
    return render_template('turnos/formulario.html',
                         clientes=clientes,
                         profesionales=profesionales,
                         servicios=servicios)

@turnos_bp.route('/crear', methods=['POST'])
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
def detalle(id):
    """Ver detalle de un turno"""
    turno = TurnoService.get_turno_by_id(id)
    if not turno:
        flash('Turno no encontrado', 'error')
        return redirect(url_for('turnos.listar'))
    
    return render_template('turnos/detalle.html', turno=turno)

@turnos_bp.route('/<int:id>/editar')
def editar(id):
    """Formulario para editar turno"""
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

@turnos_bp.route('/<int:id>/actualizar', methods=['POST', 'PUT'])
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
def cancelar(id):
    """Cancelar un turno"""
    try:
        motivo = request.form.get('motivo', '') if not request.is_json else request.get_json().get('motivo', '')
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
def horarios_disponibles():
    """API para obtener horarios disponibles"""
    fecha = request.args.get('fecha')
    profesional_id = request.args.get('profesional_id', type=int)
    servicio_id = request.args.get('servicio_id', type=int)
    
    if not fecha or not profesional_id:
        return jsonify({'error': 'Fecha y profesional son requeridos'}), 400
    
    horarios = TurnoService.get_horarios_disponibles(fecha, profesional_id, servicio_id)
    
    return jsonify({'horarios': horarios})

@turnos_bp.route('/resumen-dia')
def resumen_dia():
    """API para obtener resumen del día"""
    fecha = request.args.get('fecha', date.today().isoformat())
    profesional_id = request.args.get('profesional_id', type=int)
    
    resumen = TurnoService.get_resumen_dia(fecha, profesional_id)
    
    return jsonify(resumen)

@turnos_bp.route('/proximos')
def proximos():
    """API para obtener próximos turnos"""
    limite = request.args.get('limite', 5, type=int)
    profesional_id = request.args.get('profesional_id', type=int)
    
    turnos = TurnoService.get_proximos_turnos(limite, profesional_id)
    
    return jsonify([turno.to_dict() for turno in turnos])

@turnos_bp.route('/reporte')
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