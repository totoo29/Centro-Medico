from datetime import datetime
from src.database import db

class Cliente(db.Model):
    __tablename__ = 'clientes'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    # Información de obra social
    obra_social_id = db.Column(db.Integer, db.ForeignKey('obras_sociales.id'), nullable=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('planes_obra_social.id'), nullable=True)
    numero_afiliado = db.Column(db.String(100), nullable=True)
    grupo_familiar = db.Column(db.String(100), nullable=True)
    titular_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)  # Para grupo familiar
    
    # Relaciones
    turnos = db.relationship('Turno', backref='cliente', lazy=True)
    autorizaciones = db.relationship('Autorizacion', back_populates='cliente', lazy=True)
    familiares = db.relationship('Cliente', backref=db.backref('titular', remote_side=[id]))
    
    # Relaciones con obras sociales (usando back_populates para evitar conflictos)
    obra_social = db.relationship('ObraSocial', foreign_keys=[obra_social_id], back_populates='clientes', lazy=True)
    plan = db.relationship('PlanObraSocial', foreign_keys=[plan_id], back_populates='clientes', lazy=True)
    
    def __repr__(self):
        return f'<Cliente {self.nombre} {self.apellido}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'telefono': self.telefono,
            'email': self.email,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'activo': self.activo,
            'obra_social_id': self.obra_social_id,
            'obra_social_nombre': self.obra_social.nombre if self.obra_social else None,
            'plan_id': self.plan_id,
            'plan_nombre': self.plan.nombre if self.plan else None,
            'numero_afiliado': self.numero_afiliado,
            'grupo_familiar': self.grupo_familiar,
            'titular_id': self.titular_id
        }
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"