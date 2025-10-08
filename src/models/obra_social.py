from datetime import datetime
from src.database import db

class ObraSocial(db.Model):
    __tablename__ = 'obras_sociales'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # 'obra_social', 'prepaga', 'particular'
    cuit = db.Column(db.String(20), nullable=True)
    direccion = db.Column(db.String(300), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    contacto_nombre = db.Column(db.String(100), nullable=True)
    contacto_telefono = db.Column(db.String(20), nullable=True)
    contacto_email = db.Column(db.String(120), nullable=True)
    
    # Información de cobertura
    porcentaje_cobertura = db.Column(db.Float, default=0.0)  # Porcentaje de cobertura por defecto
    requiere_autorizacion = db.Column(db.Boolean, default=False)
    dias_autorizacion = db.Column(db.Integer, default=0)  # Días de anticipación para autorización
    
    # Estado y auditoría
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notas = db.Column(db.Text, nullable=True)
    
    # Relaciones (usando back_populates para evitar conflictos)
    clientes = db.relationship('Cliente', foreign_keys='Cliente.obra_social_id', back_populates='obra_social', lazy=True)
    planes = db.relationship('PlanObraSocial', back_populates='obra_social', lazy=True)
    
    def __repr__(self):
        return f'<ObraSocial {self.nombre} ({self.codigo})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'codigo': self.codigo,
            'tipo': self.tipo,
            'cuit': self.cuit,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'email': self.email,
            'contacto_nombre': self.contacto_nombre,
            'contacto_telefono': self.contacto_telefono,
            'contacto_email': self.contacto_email,
            'porcentaje_cobertura': self.porcentaje_cobertura,
            'requiere_autorizacion': self.requiere_autorizacion,
            'dias_autorizacion': self.dias_autorizacion,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_modificacion': self.fecha_modificacion.isoformat() if self.fecha_modificacion else None,
            'notas': self.notas
        }
    
    @property
    def tipo_display(self):
        """Retorna el tipo de obra social en formato legible"""
        tipos = {
            'obra_social': 'Obra Social',
            'prepaga': 'Prepaga',
            'particular': 'Particular'
        }
        return tipos.get(self.tipo, self.tipo)
    
    @property
    def cobertura_display(self):
        """Retorna el porcentaje de cobertura en formato legible"""
        if self.porcentaje_cobertura == 0:
            return 'Sin cobertura'
        return f'{self.porcentaje_cobertura:.0f}%'
    
    def requiere_autorizacion_para_fecha(self, fecha_turno):
        """Verifica si requiere autorización para una fecha específica"""
        if not self.requiere_autorizacion:
            return False
        
        from datetime import date
        if isinstance(fecha_turno, str):
            try:
                fecha_turno = datetime.strptime(fecha_turno, '%Y-%m-%d').date()
            except ValueError:
                return False
        
        if isinstance(fecha_turno, datetime):
            fecha_turno = fecha_turno.date()
        
        dias_hasta_turno = (fecha_turno - date.today()).days
        return dias_hasta_turno < self.dias_autorizacion
