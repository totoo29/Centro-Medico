from datetime import datetime
from src.database import db

class Autorizacion(db.Model):
    __tablename__ = 'autorizaciones'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    numero_autorizacion = db.Column(db.String(100), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    obra_social_id = db.Column(db.Integer, db.ForeignKey('obras_sociales.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('planes_obra_social.id'), nullable=True)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=True)
    profesional_id = db.Column(db.Integer, db.ForeignKey('profesionales.id'), nullable=True)
    
    # Fechas importantes
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_autorizacion = db.Column(db.DateTime, nullable=True)
    fecha_vencimiento = db.Column(db.DateTime, nullable=True)
    fecha_turno = db.Column(db.Date, nullable=True)
    
    # Estado de la autorización
    estado = db.Column(db.String(50), default='pendiente')  # pendiente, aprobada, rechazada, vencida
    motivo_rechazo = db.Column(db.Text, nullable=True)
    
    # Información de cobertura
    porcentaje_cobertura = db.Column(db.Float, nullable=True)
    copago = db.Column(db.Float, nullable=True)
    coseguro = db.Column(db.Float, nullable=True)
    
    # Límites específicos de esta autorización
    limite_autorizacion = db.Column(db.Float, nullable=True)
    cantidad_autorizada = db.Column(db.Integer, default=1)  # Cantidad de consultas/procedimientos
    
    # Información adicional
    observaciones = db.Column(db.Text, nullable=True)
    usuario_solicitante = db.Column(db.String(100), nullable=True)
    usuario_autorizador = db.Column(db.String(100), nullable=True)
    
    # Estado y auditoría
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones (usando back_populates para evitar conflictos)
    cliente = db.relationship('Cliente', foreign_keys=[cliente_id], back_populates='autorizaciones', lazy=True)
    obra_social = db.relationship('ObraSocial', foreign_keys=[obra_social_id], lazy=True)
    plan = db.relationship('PlanObraSocial', foreign_keys=[plan_id], lazy=True)
    servicio = db.relationship('Servicio', foreign_keys=[servicio_id], lazy=True)
    profesional = db.relationship('Profesional', foreign_keys=[profesional_id], lazy=True)
    
    def __repr__(self):
        return f'<Autorizacion {self.numero_autorizacion} - {self.cliente.nombre_completo if self.cliente else "Sin cliente"}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_autorizacion': self.numero_autorizacion,
            'cliente_id': self.cliente_id,
            'cliente_nombre': self.cliente.nombre_completo if self.cliente else None,
            'obra_social_id': self.obra_social_id,
            'obra_social_nombre': self.obra_social.nombre if self.obra_social else None,
            'plan_id': self.plan_id,
            'plan_nombre': self.plan.nombre if self.plan else None,
            'servicio_id': self.servicio_id,
            'servicio_nombre': self.servicio.nombre if self.servicio else None,
            'profesional_id': self.profesional_id,
            'profesional_nombre': self.profesional.nombre_completo if self.profesional else None,
            'fecha_solicitud': self.fecha_solicitud.isoformat() if self.fecha_solicitud else None,
            'fecha_autorizacion': self.fecha_autorizacion.isoformat() if self.fecha_autorizacion else None,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'fecha_turno': self.fecha_turno.isoformat() if self.fecha_turno else None,
            'estado': self.estado,
            'motivo_rechazo': self.motivo_rechazo,
            'porcentaje_cobertura': self.porcentaje_cobertura,
            'copago': self.copago,
            'coseguro': self.coseguro,
            'limite_autorizacion': self.limite_autorizacion,
            'cantidad_autorizada': self.cantidad_autorizada,
            'observaciones': self.observaciones,
            'usuario_solicitante': self.usuario_solicitante,
            'usuario_autorizador': self.usuario_autorizador,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_modificacion': self.fecha_modificacion.isoformat() if self.fecha_modificacion else None
        }
    
    @property
    def estado_display(self):
        """Retorna el estado en formato legible"""
        estados = {
            'pendiente': 'Pendiente',
            'aprobada': 'Aprobada',
            'rechazada': 'Rechazada',
            'vencida': 'Vencida'
        }
        return estados.get(self.estado, self.estado)
    
    @property
    def dias_restantes(self):
        """Calcula los días restantes hasta el vencimiento"""
        if not self.fecha_vencimiento:
            return None
        
        from datetime import date
        hoy = date.today()
        if isinstance(self.fecha_vencimiento, datetime):
            fecha_venc = self.fecha_vencimiento.date()
        else:
            fecha_venc = self.fecha_vencimiento
        
        dias = (fecha_venc - hoy).days
        return dias
    
    @property
    def esta_vencida(self):
        """Verifica si la autorización está vencida"""
        if not self.fecha_vencimiento:
            return False
        
        from datetime import date
        hoy = date.today()
        if isinstance(self.fecha_vencimiento, datetime):
            fecha_venc = self.fecha_vencimiento.date()
        else:
            fecha_venc = self.fecha_vencimiento
        
        return fecha_venc < hoy
    
    @property
    def puede_usar(self):
        """Verifica si la autorización puede ser utilizada"""
        return (self.estado == 'aprobada' and 
                not self.esta_vencida and 
                self.activo and
                self.cantidad_autorizada > 0)
    
    def usar_autorizacion(self):
        """Marca el uso de una autorización"""
        if self.cantidad_autorizada > 0:
            self.cantidad_autorizada -= 1
            if self.cantidad_autorizada == 0:
                self.estado = 'vencida'
            db.session.commit()
            return True
        return False
