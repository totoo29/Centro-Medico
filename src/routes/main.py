from flask import Blueprint, render_template
from src.models import Cliente, Turno, Profesional, Servicio
from datetime import datetime, date

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página principal con dashboard"""
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
    
    return render_template('dashboard.html',
                         total_clientes=total_clientes,
                         total_profesionales=total_profesionales,
                         total_servicios=total_servicios,
                         turnos_hoy=turnos_hoy,
                         proximos_turnos=proximos_turnos)

@main_bp.route('/dashboard')
def dashboard():
    """Redirigir al dashboard principal"""
    return index()