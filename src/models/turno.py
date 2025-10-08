from datetime import datetime
from src.database import db

class Turno(db.Model):
    __tablename__ = 'turnos'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, confirmado, completado, cancelado
    observaciones = db.Column(db.Text, nullable=True)
    precio_final = db.Column(db.Numeric(10, 2), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    profesional_id = db.Column(db.Integer, db.ForeignKey('profesionales.id'), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)
    
    def __repr__(self):
        return f'<Turno {self.fecha} {self.hora} - {self.cliente.nombre_completo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'hora': self.hora.strftime('%H:%M') if self.hora else None,
            'estado': self.estado,
            'observaciones': self.observaciones,
            'precio_final': float(self.precio_final) if self.precio_final else None,
            'cliente_id': self.cliente_id,
            'cliente': self.cliente.nombre_completo if self.cliente else None,
            'profesional_id': self.profesional_id,
            'profesional': self.profesional.nombre_completo if self.profesional else None,
            'servicio_id': self.servicio_id,
            'servicio': self.servicio.nombre if self.servicio else None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
    
    @property
    def fecha_hora_completa(self):
        if self.fecha and self.hora:
            return datetime.combine(self.fecha, self.hora)
        return None
    
    @property
    def estado_badge_class(self):
        estados = {
            'pendiente': 'warning',
            'confirmado': 'info',
            'completado': 'success',
            'cancelado': 'danger'
        }
        return estados.get(self.estado, 'secondary')