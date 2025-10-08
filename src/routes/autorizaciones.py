from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

# Crear el blueprint
autorizaciones_bp = Blueprint('autorizaciones', __name__)

# Importaciones que pueden fallar, las manejamos con try/except
try:
    from src.models import Autorizacion, Cliente, ObraSocial, PlanObraSocial, Servicio, Profesional
except ImportError:
    Autorizacion = None
    Cliente = None
    ObraSocial = None
    PlanObraSocial = None
    Servicio = None
    Profesional = None
    print("⚠️ No se pudo importar los modelos de autorización")

try:
    from src.services.autorizacion_service import AutorizacionService
    from src.services.obra_social_service import ObraSocialService
    from src.services.plan_obra_social_service import PlanObraSocialService
except ImportError:
    AutorizacionService = None
    ObraSocialService = None
    PlanObraSocialService = None
    print("⚠️ No se pudo importar los servicios de autorización")

@autorizaciones_bp.route('/')
@login_required
def listar():
    """Listar todas las autorizaciones con paginación y búsqueda"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '', type=str)
        estado = request.args.get('estado', '', type=str)
        obra_social_id = request.args.get('obra_social_id', '', type=str)
        
        if AutorizacionService:
            autorizaciones = AutorizacionService.get_paginated_autorizaciones(
                page, per_page, search, estado, obra_social_id
            )
        else:
            autorizaciones = None
        
        # Obtener estados disponibles para el filtro
        estados_disponibles = [
            ('pendiente', 'Pendiente'),
            ('aprobada', 'Aprobada'),
            ('rechazada', 'Rechazada'),
            ('vencida', 'Vencida')
        ]
        
        # Obtener obras sociales para el filtro
        if ObraSocialService:
            obras_sociales = ObraSocialService.get_all_obras_sociales()
        else:
            obras_sociales = []
        
        return render_template('autorizaciones/listar.html', 
                             autorizaciones=autorizaciones, 
                             search=search,
                             estado=estado,
                             obra_social_id=obra_social_id,
                             estados_disponibles=estados_disponibles,
                             obras_sociales=obras_sociales,
                             today=datetime.now())
    except Exception as e:
        flash(f'Error al cargar autorizaciones: {str(e)}', 'error')
        return render_template('autorizaciones/listar.html', 
                             autorizaciones=None, 
                             search='', 
                             estado='', 
                             obra_social_id='',
                             estados_disponibles=[],
                             obras_sociales=[],
                             today=datetime.now())

@autorizaciones_bp.route('/nuevo')
@login_required
def nuevo():
    """Formulario para crear nueva autorización"""
    try:
        # Obtener datos necesarios para el formulario
        if ObraSocialService:
            obras_sociales = ObraSocialService.get_all_obras_sociales()
        else:
            obras_sociales = []
        
        if PlanObraSocialService:
            planes = PlanObraSocialService.get_all_planes()
        else:
            planes = []
        
        # Obtener clientes, servicios y profesionales
        try:
            from src.services.cliente_service import ClienteService
            from src.services.servicio_service import ServicioService
            from src.services.profesional_service import ProfesionalService
            clientes = ClienteService.get_all_clientes() if ClienteService else []
            servicios = ServicioService.get_all_servicios() if ServicioService else []
            profesionales = ProfesionalService.get_all_profesionales() if ProfesionalService else []
        except ImportError:
            clientes = []
            servicios = []
            profesionales = []
        
        return render_template('autorizaciones/formulario.html', 
                             obras_sociales=obras_sociales,
                             planes=planes,
                             clientes=clientes,
                             servicios=servicios,
                             profesionales=profesionales)
    except Exception as e:
        flash(f'Error al cargar formulario: {str(e)}', 'error')
        return redirect(url_for('autorizaciones.listar'))

@autorizaciones_bp.route('/crear', methods=['POST'])
@login_required
def crear():
    """Crear nueva autorización"""
    try:
        data = request.get_json() if request.is_json else request.form
        data['usuario_solicitante'] = current_user.username if current_user.is_authenticated else 'Sistema'
        
        if AutorizacionService:
            autorizacion = AutorizacionService.crear_autorizacion(data)
        else:
            raise Exception("Servicio no disponible")
        
        if request.is_json:
            return jsonify({'success': True, 'autorizacion': autorizacion.to_dict()})
        
        flash('Autorización creada exitosamente', 'success')
        return redirect(url_for('autorizaciones.listar'))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al crear autorización: {str(e)}', 'error')
        return redirect(url_for('autorizaciones.nuevo'))

@autorizaciones_bp.route('/<int:id>')
@login_required
def detalle(id):
    """Ver detalle de una autorización"""
    try:
        if AutorizacionService:
            autorizacion = AutorizacionService.get_autorizacion_by_id(id)
        else:
            autorizacion = None
            
        if not autorizacion:
            flash('Autorización no encontrada', 'error')
            return redirect(url_for('autorizaciones.listar'))
        
        return render_template('autorizaciones/detalle.html', autorizacion=autorizacion, today=datetime.now())
    except Exception as e:
        flash(f'Error al cargar autorización: {str(e)}', 'error')
        return redirect(url_for('autorizaciones.listar'))

@autorizaciones_bp.route('/<int:id>/editar')
@login_required
def editar(id):
    """Formulario para editar autorización"""
    try:
        if AutorizacionService:
            autorizacion = AutorizacionService.get_autorizacion_by_id(id)
        else:
            autorizacion = None
            
        if not autorizacion:
            flash('Autorización no encontrada', 'error')
            return redirect(url_for('autorizaciones.listar'))
        
        # Solo se pueden editar autorizaciones pendientes
        if autorizacion.estado != 'pendiente':
            flash('Solo se pueden editar autorizaciones pendientes', 'error')
            return redirect(url_for('autorizaciones.detalle', id=id))
        
        # Obtener datos necesarios para el formulario
        if ObraSocialService:
            obras_sociales = ObraSocialService.get_all_obras_sociales()
        else:
            obras_sociales = []
        
        if PlanObraSocialService:
            planes = PlanObraSocialService.get_all_planes()
        else:
            planes = []
        
        # Obtener clientes, servicios y profesionales
        try:
            from src.services.cliente_service import ClienteService
            from src.services.servicio_service import ServicioService
            from src.services.profesional_service import ProfesionalService
            clientes = ClienteService.get_all_clientes() if ClienteService else []
            servicios = ServicioService.get_all_servicios() if ServicioService else []
            profesionales = ProfesionalService.get_all_profesionales() if ProfesionalService else []
        except ImportError:
            clientes = []
            servicios = []
            profesionales = []
        
        return render_template('autorizaciones/formulario.html', 
                             autorizacion=autorizacion,
                             obras_sociales=obras_sociales,
                             planes=planes,
                             clientes=clientes,
                             servicios=servicios,
                             profesionales=profesionales)
    except Exception as e:
        flash(f'Error al cargar autorización: {str(e)}', 'error')
        return redirect(url_for('autorizaciones.listar'))

@autorizaciones_bp.route('/<int:id>/actualizar', methods=['POST', 'PUT'])
@login_required
def actualizar(id):
    """Actualizar autorización existente"""
    try:
        data = request.get_json() if request.is_json else request.form
        
        if AutorizacionService:
            autorizacion = AutorizacionService.actualizar_autorizacion(id, data)
        else:
            autorizacion = None
        
        if not autorizacion:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Autorización no encontrada'}), 404
            flash('Autorización no encontrada', 'error')
            return redirect(url_for('autorizaciones.listar'))
        
        if request.is_json:
            return jsonify({'success': True, 'autorizacion': autorizacion.to_dict()})
        
        flash('Autorización actualizada exitosamente', 'success')
        return redirect(url_for('autorizaciones.detalle', id=id))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al actualizar autorización: {str(e)}', 'error')
        return redirect(url_for('autorizaciones.editar', id=id))

@autorizaciones_bp.route('/<int:id>/aprobar', methods=['POST'])
@login_required
def aprobar(id):
    """Aprobar una autorización"""
    try:
        data = request.get_json() if request.is_json else request.form
        fecha_vencimiento = data.get('fecha_vencimiento')
        usuario_autorizador = current_user.username if current_user.is_authenticated else 'Sistema'
        
        if AutorizacionService:
            autorizacion = AutorizacionService.aprobar_autorizacion(id, usuario_autorizador, fecha_vencimiento)
        else:
            autorizacion = None
        
        if not autorizacion:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Autorización no encontrada'}), 404
            flash('Autorización no encontrada', 'error')
            return redirect(url_for('autorizaciones.listar'))
        
        if request.is_json:
            return jsonify({'success': True, 'autorizacion': autorizacion.to_dict()})
        
        flash('Autorización aprobada exitosamente', 'success')
        return redirect(url_for('autorizaciones.detalle', id=id))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al aprobar autorización: {str(e)}', 'error')
        return redirect(url_for('autorizaciones.detalle', id=id))

@autorizaciones_bp.route('/<int:id>/rechazar', methods=['POST'])
@login_required
def rechazar(id):
    """Rechazar una autorización"""
    try:
        data = request.get_json() if request.is_json else request.form
        motivo_rechazo = data.get('motivo_rechazo', '')
        usuario_autorizador = current_user.username if current_user.is_authenticated else 'Sistema'
        
        if not motivo_rechazo:
            raise ValueError('El motivo del rechazo es obligatorio')
        
        if AutorizacionService:
            autorizacion = AutorizacionService.rechazar_autorizacion(id, motivo_rechazo, usuario_autorizador)
        else:
            autorizacion = None
        
        if not autorizacion:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Autorización no encontrada'}), 404
            flash('Autorización no encontrada', 'error')
            return redirect(url_for('autorizaciones.listar'))
        
        if request.is_json:
            return jsonify({'success': True, 'autorizacion': autorizacion.to_dict()})
        
        flash('Autorización rechazada exitosamente', 'success')
        return redirect(url_for('autorizaciones.detalle', id=id))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al rechazar autorización: {str(e)}', 'error')
        return redirect(url_for('autorizaciones.detalle', id=id))

@autorizaciones_bp.route('/<int:id>/eliminar', methods=['POST', 'DELETE'])
@login_required
def eliminar(id):
    """Eliminar (desactivar) autorización"""
    try:
        if AutorizacionService:
            success = AutorizacionService.eliminar_autorizacion(id)
        else:
            success = False
        
        if not success:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Autorización no encontrada'}), 404
            flash('Autorización no encontrada', 'error')
            return redirect(url_for('autorizaciones.listar'))
        
        if request.is_json:
            return jsonify({'success': True})
        
        flash('Autorización eliminada exitosamente', 'success')
        return redirect(url_for('autorizaciones.listar'))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al eliminar autorización: {str(e)}', 'error')
        return redirect(url_for('autorizaciones.listar'))

@autorizaciones_bp.route('/exportar/<formato>')
@login_required
def exportar(formato):
    """Exportar autorizaciones a Excel/CSV"""
    try:
        search = request.args.get('search', '')
        estado = request.args.get('estado', '')
        obra_social_id = request.args.get('obra_social_id', '')
        
        if not AutorizacionService:
            flash('Servicio no disponible', 'error')
            return redirect(url_for('autorizaciones.listar'))
        
        if formato == 'excel':
            return AutorizacionService.exportar_excel(search, estado, obra_social_id)
        elif formato == 'csv':
            return AutorizacionService.exportar_csv(search, estado, obra_social_id)
        else:
            flash('Formato de exportación no válido', 'error')
            return redirect(url_for('autorizaciones.listar'))
            
    except Exception as e:
        flash(f'Error al exportar: {str(e)}', 'error')
        return redirect(url_for('autorizaciones.listar'))

# API para obtener planes de una obra social (AJAX)
@autorizaciones_bp.route('/api/planes/<int:obra_social_id>')
@login_required
def api_planes(obra_social_id):
    """API para obtener planes de una obra social específica"""
    try:
        if PlanObraSocialService:
            planes = PlanObraSocialService.get_planes_by_obra_social(obra_social_id)
            return jsonify([plan.to_dict() for plan in planes])
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta de prueba para verificar que el blueprint funciona
@autorizaciones_bp.route('/test')
def test():
    """Ruta de prueba"""
    return jsonify({
        'status': 'ok',
        'blueprint': 'autorizaciones',
        'message': 'Blueprint autorizaciones funcionando correctamente'
    })
