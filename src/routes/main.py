from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import date

main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard')
@login_required
def index():
    """Página principal con dashboard"""
    try:
        from src.models import Cliente, Turno, Profesional, Servicio
        
        # Estadísticas básicas
        total_clientes = Cliente.query.filter_by(activo=True).count()
        total_profesionales = Profesional.query.filter_by(activo=True).count()
        total_servicios = Servicio.query.filter_by(activo=True).count()
        
        # Turnos de hoy
        hoy = date.today()
        turnos_hoy = Turno.query.filter_by(fecha=hoy).count()
        
        # Próximos turnos (próximos 5)
        proximos_turnos = Turno.query.filter(
            Turno.fecha >= hoy,
            Turno.estado.in_(['pendiente', 'confirmado'])
        ).order_by(Turno.fecha, Turno.hora).limit(5).all()
        
    except Exception as e:
        print(f"Error cargando datos del dashboard: {e}")
        # Valores por defecto si hay error
        total_clientes = 0
        total_profesionales = 0
        total_servicios = 0
        turnos_hoy = 0
        proximos_turnos = []
    
    return render_template('dashboard.html',
                         total_clientes=total_clientes,
                         total_profesionales=total_profesionales,
                         total_servicios=total_servicios,
                         turnos_hoy=turnos_hoy,
                         proximos_turnos=proximos_turnos,
                         usuario=current_user)