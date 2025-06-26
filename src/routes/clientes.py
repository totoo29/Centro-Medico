from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required

# Crear el blueprint
clientes_bp = Blueprint('clientes', __name__)

# Importaciones que pueden fallar, las manejamos con try/except
try:
    from src.models import Cliente
except ImportError:
    Cliente = None
    print("⚠️ No se pudo importar el modelo Cliente")

try:
    from src.services.cliente_service import ClienteService
except ImportError:
    ClienteService = None
    print("⚠️ No se pudo importar ClienteService")

try:
    from src.database import db
except ImportError:
    db = None
    print("⚠️ No se pudo importar db")

@clientes_bp.route('/')
@login_required
def listar():
    """Listar todos los clientes con paginación y búsqueda"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '', type=str)
        
        if ClienteService:
            clientes = ClienteService.get_paginated_clientes(page, per_page, search)
        else:
            # Fallback si el servicio no está disponible
            from flask import abort
            abort(500)
        
        return render_template('clientes/listar.html', 
                             clientes=clientes, 
                             search=search)
    except Exception as e:
        flash(f'Error al cargar clientes: {str(e)}', 'error')
        return render_template('clientes/listar.html', clientes=None, search='')

@clientes_bp.route('/nuevo')
@login_required
def nuevo():
    """Formulario para crear nuevo cliente"""
    return render_template('clientes/formulario.html')

@clientes_bp.route('/crear', methods=['POST'])
@login_required
def crear():
    """Crear nuevo cliente"""
    try:
        data = request.get_json() if request.is_json else request.form
        
        if ClienteService:
            cliente = ClienteService.crear_cliente(data)
        else:
            raise Exception("Servicio no disponible")
        
        if request.is_json:
            return jsonify({'success': True, 'cliente': cliente.to_dict()})
        
        flash('Cliente creado exitosamente', 'success')
        return redirect(url_for('clientes.listar'))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al crear cliente: {str(e)}', 'error')
        return redirect(url_for('clientes.nuevo'))

@clientes_bp.route('/<int:id>')
@login_required
def detalle(id):
    """Ver detalle de un cliente"""
    try:
        if ClienteService:
            cliente = ClienteService.get_cliente_by_id(id)
        else:
            cliente = None
            
        if not cliente:
            flash('Cliente no encontrado', 'error')
            return redirect(url_for('clientes.listar'))
        
        return render_template('clientes/detalle.html', cliente=cliente)
    except Exception as e:
        flash(f'Error al cargar cliente: {str(e)}', 'error')
        return redirect(url_for('clientes.listar'))

@clientes_bp.route('/<int:id>/editar')
@login_required
def editar(id):
    """Formulario para editar cliente"""
    try:
        if ClienteService:
            cliente = ClienteService.get_cliente_by_id(id)
        else:
            cliente = None
            
        if not cliente:
            flash('Cliente no encontrado', 'error')
            return redirect(url_for('clientes.listar'))
        
        return render_template('clientes/formulario.html', cliente=cliente)
    except Exception as e:
        flash(f'Error al cargar cliente: {str(e)}', 'error')
        return redirect(url_for('clientes.listar'))

@clientes_bp.route('/<int:id>/actualizar', methods=['POST', 'PUT'])
@login_required
def actualizar(id):
    """Actualizar cliente existente"""
    try:
        data = request.get_json() if request.is_json else request.form
        
        if ClienteService:
            cliente = ClienteService.actualizar_cliente(id, data)
        else:
            cliente = None
        
        if not cliente:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404
            flash('Cliente no encontrado', 'error')
            return redirect(url_for('clientes.listar'))
        
        if request.is_json:
            return jsonify({'success': True, 'cliente': cliente.to_dict()})
        
        flash('Cliente actualizado exitosamente', 'success')
        return redirect(url_for('clientes.detalle', id=id))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al actualizar cliente: {str(e)}', 'error')
        return redirect(url_for('clientes.editar', id=id))

@clientes_bp.route('/<int:id>/eliminar', methods=['POST', 'DELETE'])
@login_required
def eliminar(id):
    """Eliminar (desactivar) cliente"""
    try:
        if ClienteService:
            success = ClienteService.eliminar_cliente(id)
        else:
            success = False
        
        if not success:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404
            flash('Cliente no encontrado', 'error')
            return redirect(url_for('clientes.listar'))
        
        if request.is_json:
            return jsonify({'success': True})
        
        flash('Cliente eliminado exitosamente', 'success')
        return redirect(url_for('clientes.listar'))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error al eliminar cliente: {str(e)}', 'error')
        return redirect(url_for('clientes.listar'))

@clientes_bp.route('/buscar')
@login_required
def buscar():
    """API para buscar clientes (AJAX)"""
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 10, type=int)
        
        if ClienteService:
            clientes = ClienteService.buscar_clientes(query, limit)
            return jsonify([cliente.to_dict() for cliente in clientes])
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clientes_bp.route('/exportar')
@login_required
def exportar():
    """Exportar clientes a Excel/CSV"""
    try:
        formato = request.args.get('formato', 'excel')
        search = request.args.get('search', '')
        
        if not ClienteService:
            flash('Servicio no disponible', 'error')
            return redirect(url_for('clientes.listar'))
        
        if formato == 'excel':
            return ClienteService.exportar_excel(search)
        else:
            return ClienteService.exportar_csv(search)
            
    except Exception as e:
        flash(f'Error al exportar: {str(e)}', 'error')
        return redirect(url_for('clientes.listar'))

# Ruta de prueba para verificar que el blueprint funciona
@clientes_bp.route('/test')
def test():
    """Ruta de prueba"""
    return jsonify({
        'status': 'ok',
        'blueprint': 'clientes',
        'message': 'Blueprint clientes funcionando correctamente'
    })

def register_blueprints(app):
    """Registrar todos los blueprints en la aplicación Flask"""
    
    # Registrar blueprint main
    try:
        from .main import main_bp
        app.register_blueprint(main_bp)
        print("✅ Blueprint 'main' registrado correctamente")
    except ImportError as e:
        print(f"⚠️ Error al registrar blueprint 'main': {e}")
    except Exception as e:
        print(f"❌ Error inesperado con blueprint 'main': {e}")
    
    # Registrar blueprint clientes
    try:
        from routes.clientes import clientes_bp
        app.register_blueprint(clientes_bp, url_prefix='/clientes')
        print("✅ Blueprint 'clientes' registrado correctamente")
    except ImportError as e:
        print(f"⚠️ Error al registrar blueprint 'clientes': {e}")
    except Exception as e:
        print(f"❌ Error inesperado con blueprint 'clientes': {e}")
    
    # Registrar blueprint categorias
    try:
        from .categorias import categorias_bp
        app.register_blueprint(categorias_bp, url_prefix='/categorias')
        print("✅ Blueprint 'categorias' registrado correctamente")
    except ImportError as e:
        print(f"⚠️ Error al registrar blueprint 'categorias': {e}")
    except Exception as e:
        print(f"❌ Error inesperado con blueprint 'categorias': {e}")
    
    # Registrar blueprint profesionales
    try:
        from .profesionales import profesionales_bp
        app.register_blueprint(profesionales_bp, url_prefix='/profesionales')
        print("✅ Blueprint 'profesionales' registrado correctamente")
    except ImportError as e:
        print(f"⚠️ Error al registrar blueprint 'profesionales': {e}")
    except Exception as e:
        print(f"❌ Error inesperado con blueprint 'profesionales': {e}")
    
    # Registrar blueprint servicios
    try:
        from .servicios import servicios_bp
        app.register_blueprint(servicios_bp, url_prefix='/servicios')
        print("✅ Blueprint 'servicios' registrado correctamente")
    except ImportError as e:
        print(f"⚠️ Error al registrar blueprint 'servicios': {e}")
    except Exception as e:
        print(f"❌ Error inesperado con blueprint 'servicios': {e}")
    
    # Registrar blueprint turnos
    try:
        from .turnos import turnos_bp
        app.register_blueprint(turnos_bp, url_prefix='/turnos')
        print("✅ Blueprint 'turnos' registrado correctamente")
    except ImportError as e:
        print(f"⚠️ Error al registrar blueprint 'turnos': {e}")
    except Exception as e:
        print(f"❌ Error inesperado con blueprint 'turnos': {e}")
    
    print("🎯 Registro de blueprints completado")