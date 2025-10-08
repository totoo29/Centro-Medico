from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user

# Crear el blueprint
obras_sociales_bp = Blueprint('obras_sociales', __name__)

# Importaciones que pueden fallar, las manejamos con try/except
try:
    from src.models import ObraSocial, PlanObraSocial
except ImportError:
    ObraSocial = None
    PlanObraSocial = None
    print("⚠️ No se pudo importar los modelos de obra social")

try:
    from src.services.obra_social_service import ObraSocialService
    from src.services.plan_obra_social_service import PlanObraSocialService
except ImportError:
    ObraSocialService = None
    PlanObraSocialService = None
    print("⚠️ No se pudo importar los servicios de obra social")

@obras_sociales_bp.route('/')
@login_required
def listar():
    """Listar todas las obras sociales con paginación y búsqueda"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '', type=str)
        tipo = request.args.get('tipo', '', type=str)
        
        if ObraSocialService:
            obras_sociales = ObraSocialService.get_paginated_obras_sociales(page, per_page, search, tipo)
        else:
            obras_sociales = None
        
        # Obtener tipos disponibles para el filtro
        tipos_disponibles = [
            ('obra_social', 'Obra Social'),
            ('prepaga', 'Prepaga'),
            ('particular', 'Particular')
        ]
        
        return render_template('obras_sociales/listar.html', 
                             obras_sociales=obras_sociales, 
                             search=search,
                             tipo=tipo,
                             tipos_disponibles=tipos_disponibles)
    except Exception as e:
        flash(f'Error al cargar obras sociales: {str(e)}', 'error')
        return render_template('obras_sociales/listar.html', obras_sociales=None, search='', tipo='')

@obras_sociales_bp.route('/nuevo')
@login_required
def nuevo():
    """Formulario para crear nueva obra social"""
    tipos_disponibles = [
        ('obra_social', 'Obra Social'),
        ('prepaga', 'Prepaga'),
        ('particular', 'Particular')
    ]
    return render_template('obras_sociales/formulario.html', tipos_disponibles=tipos_disponibles)

@obras_sociales_bp.route('/crear', methods=['POST'])
@login_required
def crear():
    """Crear nueva obra social"""
    try:
        data = request.get_json() if request.is_json else request.form
        
        if ObraSocialService:
            obra_social = ObraSocialService.crear_obra_social(data)
        else:
            raise Exception("Servicio no disponible")
        
        if request.is_json:
            return jsonify({'success': True, 'obra_social': obra_social.to_dict()})
        
        flash('Obra social creada exitosamente', 'success')
        return redirect(url_for('obras_sociales.listar'))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al crear obra social: {str(e)}', 'error')
        return redirect(url_for('obras_sociales.nuevo'))

@obras_sociales_bp.route('/<int:id>')
@login_required
def detalle(id):
    """Ver detalle de una obra social"""
    try:
        if ObraSocialService:
            obra_social = ObraSocialService.get_obra_social_by_id(id)
        else:
            obra_social = None
            
        if not obra_social:
            flash('Obra social no encontrada', 'error')
            return redirect(url_for('obras_sociales.listar'))
        
        # Obtener planes asociados
        if PlanObraSocialService:
            planes = PlanObraSocialService.get_planes_by_obra_social(id)
        else:
            planes = []
        
        return render_template('obras_sociales/detalle.html', 
                             obra_social=obra_social, 
                             planes=planes)
    except Exception as e:
        flash(f'Error al cargar obra social: {str(e)}', 'error')
        return redirect(url_for('obras_sociales.listar'))

@obras_sociales_bp.route('/<int:id>/editar')
@login_required
def editar(id):
    """Formulario para editar obra social"""
    try:
        if ObraSocialService:
            obra_social = ObraSocialService.get_obra_social_by_id(id)
        else:
            obra_social = None
            
        if not obra_social:
            flash('Obra social no encontrada', 'error')
            return redirect(url_for('obras_sociales.listar'))
        
        tipos_disponibles = [
            ('obra_social', 'Obra Social'),
            ('prepaga', 'Prepaga'),
            ('particular', 'Particular')
        ]
        
        return render_template('obras_sociales/formulario.html', 
                             obra_social=obra_social,
                             tipos_disponibles=tipos_disponibles)
    except Exception as e:
        flash(f'Error al cargar obra social: {str(e)}', 'error')
        return redirect(url_for('obras_sociales.listar'))

@obras_sociales_bp.route('/<int:id>/actualizar', methods=['POST', 'PUT'])
@login_required
def actualizar(id):
    """Actualizar obra social existente"""
    try:
        data = request.get_json() if request.is_json else request.form
        
        if ObraSocialService:
            obra_social = ObraSocialService.actualizar_obra_social(id, data)
        else:
            obra_social = None
        
        if not obra_social:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Obra social no encontrada'}), 404
            flash('Obra social no encontrada', 'error')
            return redirect(url_for('obras_sociales.listar'))
        
        if request.is_json:
            return jsonify({'success': True, 'obra_social': obra_social.to_dict()})
        
        flash('Obra social actualizada exitosamente', 'success')
        return redirect(url_for('obras_sociales.detalle', id=id))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al actualizar obra social: {str(e)}', 'error')
        return redirect(url_for('obras_sociales.editar', id=id))

@obras_sociales_bp.route('/<int:id>/eliminar', methods=['POST', 'DELETE'])
@login_required
def eliminar(id):
    """Eliminar (desactivar) obra social"""
    try:
        if ObraSocialService:
            success = ObraSocialService.eliminar_obra_social(id)
        else:
            success = False
        
        if not success:
            if request.is_json():
                return jsonify({'success': False, 'error': 'Obra social no encontrada'}), 404
            flash('Obra social no encontrada', 'error')
            return redirect(url_for('obras_sociales.listar'))
        
        if request.is_json():
            return jsonify({'success': True})
        
        flash('Obra social eliminada exitosamente', 'success')
        return redirect(url_for('obras_sociales.listar'))
        
    except Exception as e:
        if request.is_json():
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al eliminar obra social: {str(e)}', 'error')
        return redirect(url_for('obras_sociales.listar'))

@obras_sociales_bp.route('/buscar')
@login_required
def buscar():
    """API para buscar obras sociales (AJAX)"""
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 10, type=int)
        
        if ObraSocialService:
            obras_sociales = ObraSocialService.buscar_obras_sociales(query, limit)
            return jsonify([obra.to_dict() for obra in obras_sociales])
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@obras_sociales_bp.route('/exportar')
@login_required
def exportar():
    """Exportar obras sociales a Excel/CSV"""
    try:
        formato = request.args.get('formato', 'excel')
        search = request.args.get('search', '')
        tipo = request.args.get('tipo', '')
        
        if not ObraSocialService:
            flash('Servicio no disponible', 'error')
            return redirect(url_for('obras_sociales.listar'))
        
        if formato == 'excel':
            return ObraSocialService.exportar_excel(search, tipo)
        else:
            return ObraSocialService.exportar_csv(search, tipo)
            
    except Exception as e:
        flash(f'Error al exportar: {str(e)}', 'error')
        return redirect(url_for('obras_sociales.listar'))

# Rutas para planes de obra social
@obras_sociales_bp.route('/<int:obra_social_id>/planes')
@login_required
def listar_planes(obra_social_id):
    """Listar planes de una obra social específica"""
    try:
        if ObraSocialService:
            obra_social = ObraSocialService.get_obra_social_by_id(obra_social_id)
        else:
            obra_social = None
            
        if not obra_social:
            flash('Obra social no encontrada', 'error')
            return redirect(url_for('obras_sociales.listar'))
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '', type=str)
        
        if PlanObraSocialService:
            planes = PlanObraSocialService.get_paginated_planes(page, per_page, search, obra_social_id)
        else:
            planes = None
        
        return render_template('obras_sociales/planes.html', 
                             obra_social=obra_social,
                             planes=planes,
                             search=search)
    except Exception as e:
        flash(f'Error al cargar planes: {str(e)}', 'error')
        return redirect(url_for('obras_sociales.listar'))

@obras_sociales_bp.route('/<int:obra_social_id>/planes/nuevo')
@login_required
def nuevo_plan(obra_social_id):
    """Formulario para crear nuevo plan"""
    try:
        if ObraSocialService:
            obra_social = ObraSocialService.get_obra_social_by_id(obra_social_id)
        else:
            obra_social = None
            
        if not obra_social:
            flash('Obra social no encontrada', 'error')
            return redirect(url_for('obras_sociales.listar'))
        
        return render_template('obras_sociales/formulario_plan.html', 
                             obra_social=obra_social)
    except Exception as e:
        flash(f'Error al cargar obra social: {str(e)}', 'error')
        return redirect(url_for('obras_sociales.listar'))

@obras_sociales_bp.route('/<int:obra_social_id>/planes/crear', methods=['POST'])
@login_required
def crear_plan(obra_social_id):
    """Crear nuevo plan"""
    try:
        data = request.get_json() if request.is_json else request.form
        data['obra_social_id'] = obra_social_id
        
        if PlanObraSocialService:
            plan = PlanObraSocialService.crear_plan(data)
        else:
            raise Exception("Servicio no disponible")
        
        if request.is_json:
            return jsonify({'success': True, 'plan': plan.to_dict()})
        
        flash('Plan creado exitosamente', 'success')
        return redirect(url_for('obras_sociales.listar_planes', obra_social_id=obra_social_id))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al crear plan: {str(e)}', 'error')
        return redirect(url_for('obras_sociales.nuevo_plan', obra_social_id=obra_social_id))

@obras_sociales_bp.route('/<int:obra_social_id>/planes/<int:plan_id>/editar')
@login_required
def editar_plan(obra_social_id, plan_id):
    """Formulario para editar plan existente"""
    try:
        if ObraSocialService:
            obra_social = ObraSocialService.get_obra_social_by_id(obra_social_id)
        else:
            obra_social = None
            
        if not obra_social:
            flash('Obra social no encontrada', 'error')
            return redirect(url_for('obras_sociales.listar'))
        
        if PlanObraSocialService:
            plan = PlanObraSocialService.get_plan_by_id(plan_id)
        else:
            plan = None
            
        if not plan:
            flash('Plan no encontrado', 'error')
            return redirect(url_for('obras_sociales.listar_planes', obra_social_id=obra_social_id))
        
        # Verificar que el plan pertenezca a la obra social
        if plan.obra_social_id != obra_social_id:
            flash('Plan no pertenece a esta obra social', 'error')
            return redirect(url_for('obras_sociales.listar_planes', obra_social_id=obra_social_id))
        
        return render_template('obras_sociales/formulario_plan.html', 
                             obra_social=obra_social,
                             plan=plan)
    except Exception as e:
        flash(f'Error al cargar plan: {str(e)}', 'error')
        return redirect(url_for('obras_sociales.listar_planes', obra_social_id=obra_social_id))

@obras_sociales_bp.route('/<int:obra_social_id>/planes/<int:plan_id>/actualizar', methods=['POST', 'PUT'])
@login_required
def actualizar_plan(obra_social_id, plan_id):
    """Actualizar plan existente"""
    try:
        data = request.get_json() if request.is_json else request.form
        data['obra_social_id'] = obra_social_id
        
        if PlanObraSocialService:
            plan = PlanObraSocialService.actualizar_plan(plan_id, data)
        else:
            raise Exception("Servicio no disponible")
        
        if not plan:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Plan no encontrado'}), 404
            flash('Plan no encontrado', 'error')
            return redirect(url_for('obras_sociales.listar_planes', obra_social_id=obra_social_id))
        
        if request.is_json:
            return jsonify({'success': True, 'plan': plan.to_dict()})
        
        flash('Plan actualizado exitosamente', 'success')
        return redirect(url_for('obras_sociales.listar_planes', obra_social_id=obra_social_id))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al actualizar plan: {str(e)}', 'error')
        return redirect(url_for('obras_sociales.editar_plan', obra_social_id=obra_social_id, plan_id=plan_id))

@obras_sociales_bp.route('/<int:obra_social_id>/planes/<int:plan_id>/eliminar', methods=['POST', 'DELETE'])
@login_required
def eliminar_plan(obra_social_id, plan_id):
    """Eliminar (desactivar) plan"""
    try:
        if PlanObraSocialService:
            success = PlanObraSocialService.eliminar_plan(plan_id)
        else:
            success = False
        
        if not success:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Plan no encontrado'}), 404
            flash('Plan no encontrado', 'error')
            return redirect(url_for('obras_sociales.listar_planes', obra_social_id=obra_social_id))
        
        if request.is_json:
            return jsonify({'success': True})
        
        flash('Plan eliminado exitosamente', 'success')
        return redirect(url_for('obras_sociales.listar_planes', obra_social_id=obra_social_id))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al eliminar plan: {str(e)}', 'error')
        return redirect(url_for('obras_sociales.listar_planes', obra_social_id=obra_social_id))

# Ruta de prueba para verificar que el blueprint funciona
@obras_sociales_bp.route('/test')
def test():
    """Ruta de prueba"""
    return jsonify({
        'status': 'ok',
        'blueprint': 'obras_sociales',
        'message': 'Blueprint obras_sociales funcionando correctamente'
    })

# Rutas API para el formulario de clientes
@obras_sociales_bp.route('/api/listar')
@login_required
def api_listar():
    """API para listar obras sociales (AJAX)"""
    try:
        if ObraSocialService:
            obras_sociales = ObraSocialService.get_all_obras_sociales()
            return jsonify([obra.to_dict() for obra in obras_sociales if obra.activo])
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@obras_sociales_bp.route('/<int:obra_social_id>/planes/api')
@login_required
def api_planes(obra_social_id):
    """API para obtener planes de una obra social (AJAX)"""
    try:
        if PlanObraSocialService:
            planes = PlanObraSocialService.get_planes_by_obra_social(obra_social_id)
            return jsonify([plan.to_dict() for plan in planes if plan.activo])
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
