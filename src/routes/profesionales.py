from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from src.models import Profesional
from src.services.profesional_service import ProfesionalService
from src.database import db

profesionales_bp = Blueprint('profesionales', __name__)

@profesionales_bp.route('/')
@login_required
def listar():
    """Listar todos los profesionales"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)
    
    profesionales = ProfesionalService.get_paginated_profesionales(page, per_page, search)
    
    return render_template('profesionales/listar.html', 
                         profesionales=profesionales, 
                         search=search)

@profesionales_bp.route('/nuevo')
@login_required
def nuevo():
    """Formulario para crear nuevo profesional"""
    return render_template('profesionales/formulario.html')

@profesionales_bp.route('/crear', methods=['POST'])
@login_required
def crear():
    """Crear nuevo profesional"""
    try:
        data = request.get_json() if request.is_json else request.form
        profesional = ProfesionalService.crear_profesional(data)
        
        if request.is_json:
            return jsonify({'success': True, 'profesional': profesional.to_dict()})
        
        flash('Profesional creado exitosamente', 'success')
        return redirect(url_for('profesionales.listar'))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al crear profesional: {str(e)}', 'error')
        return redirect(url_for('profesionales.nuevo'))

@profesionales_bp.route('/<int:id>')
@login_required
def detalle(id):
    """Ver detalle de un profesional"""
    profesional = ProfesionalService.get_profesional_by_id(id)
    if not profesional:
        flash('Profesional no encontrado', 'error')
        return redirect(url_for('profesionales.listar'))
    
    return render_template('profesionales/detalle.html', profesional=profesional)

@profesionales_bp.route('/<int:id>/editar')
@login_required
def editar(id):
    """Formulario para editar profesional"""
    profesional = ProfesionalService.get_profesional_by_id(id)
    if not profesional:
        flash('Profesional no encontrado', 'error')
        return redirect(url_for('profesionales.listar'))
    
    return render_template('profesionales/formulario.html', profesional=profesional)

@profesionales_bp.route('/<int:id>/actualizar', methods=['POST', 'PUT'])
@login_required
def actualizar(id):
    """Actualizar profesional existente"""
    try:
        data = request.get_json() if request.is_json else request.form
        profesional = ProfesionalService.actualizar_profesional(id, data)
        
        if not profesional:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Profesional no encontrado'}), 404
            flash('Profesional no encontrado', 'error')
            return redirect(url_for('profesionales.listar'))
        
        if request.is_json:
            return jsonify({'success': True, 'profesional': profesional.to_dict()})
        
        flash('Profesional actualizado exitosamente', 'success')
        return redirect(url_for('profesionales.detalle', id=id))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al actualizar profesional: {str(e)}', 'error')
        return redirect(url_for('profesionales.editar', id=id))

@profesionales_bp.route('/<int:id>/eliminar', methods=['POST', 'DELETE'])
@login_required
def eliminar(id):
    """Eliminar profesional"""
    try:
        success = ProfesionalService.eliminar_profesional(id)
        
        if not success:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Profesional no encontrado'}), 404
            flash('Profesional no encontrado', 'error')
            return redirect(url_for('profesionales.listar'))
        
        if request.is_json:
            return jsonify({'success': True})
        
        flash('Profesional eliminado exitosamente', 'success')
        return redirect(url_for('profesionales.listar'))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al eliminar profesional: {str(e)}', 'error')
        return redirect(url_for('profesionales.listar'))

@profesionales_bp.route('/buscar')
@login_required
def buscar():
    """API para buscar profesionales"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)
    
    profesionales = ProfesionalService.buscar_profesionales(query, limit)
    
    return jsonify([profesional.to_dict() for profesional in profesionales])

@profesionales_bp.route('/api/todos')
@login_required
def api_todos():
    """API para obtener todos los profesionales activos"""
    profesionales = ProfesionalService.get_all_profesionales()
    return jsonify([profesional.to_dict() for profesional in profesionales])

@profesionales_bp.route('/<int:id>/horarios')
@login_required
def horarios(id):
    """Ver y gestionar horarios de un profesional"""
    profesional = ProfesionalService.get_profesional_by_id(id)
    if not profesional:
        flash('Profesional no encontrado', 'error')
        return redirect(url_for('profesionales.listar'))
    
    # Por ahora usamos horarios por defecto
    # En el futuro esto vendría de la base de datos
    horarios_default = {
        'lunes': {'activo': True, 'inicio': '09:00', 'fin': '17:00'},
        'martes': {'activo': True, 'inicio': '09:00', 'fin': '17:00'},
        'miercoles': {'activo': True, 'inicio': '09:00', 'fin': '17:00'},
        'jueves': {'activo': True, 'inicio': '09:00', 'fin': '17:00'},
        'viernes': {'activo': True, 'inicio': '09:00', 'fin': '17:00'},
        'sabado': {'activo': False, 'inicio': '09:00', 'fin': '13:00'},
        'domingo': {'activo': False, 'inicio': '09:00', 'fin': '13:00'}
    }
    
    return render_template('profesionales/horarios.html', 
                         profesional=profesional,
                         horarios=horarios_default)

@profesionales_bp.route('/<int:id>/horarios/actualizar', methods=['POST'])
@login_required
def actualizar_horarios(id):
    """Actualizar horarios de un profesional"""
    profesional = ProfesionalService.get_profesional_by_id(id)
    if not profesional:
        flash('Profesional no encontrado', 'error')
        return redirect(url_for('profesionales.listar'))
    
    try:
        # Por ahora solo mostramos un mensaje
        # En el futuro aquí se guardarían los horarios en la base de datos
        flash('Horarios actualizados correctamente (funcionalidad en desarrollo)', 'success')
        return redirect(url_for('profesionales.horarios', id=id))
        
    except Exception as e:
        flash(f'Error al actualizar horarios: {str(e)}', 'error')
        return redirect(url_for('profesionales.horarios', id=id))