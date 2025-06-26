from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from src.models import Categoria
from src.services.categoria_service import CategoriaService
from src.database import db

categorias_bp = Blueprint('categorias', __name__)

@categorias_bp.route('/')
@login_required
def listar():
    """Listar todas las categorías"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)
    
    categorias = CategoriaService.get_paginated_categorias(page, per_page, search)
    
    return render_template('categorias/listar.html', 
                         categorias=categorias, 
                         search=search)

@categorias_bp.route('/nueva')
@login_required
def nueva():
    """Formulario para crear nueva categoría"""
    return render_template('categorias/formulario.html')

@categorias_bp.route('/crear', methods=['POST'])
@login_required
def crear():
    """Crear nueva categoría"""
    try:
        data = request.get_json() if request.is_json else request.form
        categoria = CategoriaService.crear_categoria(data)
        
        if request.is_json:
            return jsonify({'success': True, 'categoria': categoria.to_dict()})
        
        flash('Categoría creada exitosamente', 'success')
        return redirect(url_for('categorias.listar'))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al crear categoría: {str(e)}', 'error')
        return redirect(url_for('categorias.nueva'))

@categorias_bp.route('/<int:id>')
@login_required
def detalle(id):
    """Ver detalle de una categoría"""
    categoria = CategoriaService.get_categoria_by_id(id)
    if not categoria:
        flash('Categoría no encontrada', 'error')
        return redirect(url_for('categorias.listar'))
    
    return render_template('categorias/detalle.html', categoria=categoria)

@categorias_bp.route('/<int:id>/editar')
@login_required
def editar(id):
    """Formulario para editar categoría"""
    categoria = CategoriaService.get_categoria_by_id(id)
    if not categoria:
        flash('Categoría no encontrada', 'error')
        return redirect(url_for('categorias.listar'))
    
    return render_template('categorias/formulario.html', categoria=categoria)

@categorias_bp.route('/<int:id>/actualizar', methods=['POST', 'PUT'])
@login_required
def actualizar(id):
    """Actualizar categoría existente"""
    try:
        data = request.get_json() if request.is_json else request.form
        categoria = CategoriaService.actualizar_categoria(id, data)
        
        if not categoria:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Categoría no encontrada'}), 404
            flash('Categoría no encontrada', 'error')
            return redirect(url_for('categorias.listar'))
        
        if request.is_json:
            return jsonify({'success': True, 'categoria': categoria.to_dict()})
        
        flash('Categoría actualizada exitosamente', 'success')
        return redirect(url_for('categorias.detalle', id=id))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al actualizar categoría: {str(e)}', 'error')
        return redirect(url_for('categorias.editar', id=id))

@categorias_bp.route('/<int:id>/eliminar', methods=['POST', 'DELETE'])
@login_required
def eliminar(id):
    """Eliminar categoría"""
    try:
        success = CategoriaService.eliminar_categoria(id)
        
        if not success:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Categoría no encontrada'}), 404
            flash('Categoría no encontrada', 'error')
            return redirect(url_for('categorias.listar'))
        
        if request.is_json:
            return jsonify({'success': True})
        
        flash('Categoría eliminada exitosamente', 'success')
        return redirect(url_for('categorias.listar'))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al eliminar categoría: {str(e)}', 'error')
        return redirect(url_for('categorias.listar'))

@categorias_bp.route('/api/todas')
@login_required
def api_todas():
    """API para obtener todas las categorías activas"""
    categorias = CategoriaService.get_all_categorias()
    return jsonify([categoria.to_dict() for categoria in categorias])