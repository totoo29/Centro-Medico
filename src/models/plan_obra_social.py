from datetime import datetime
from src.database import db

class PlanObraSocial(db.Model):
    __tablename__ = 'planes_obra_social'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    codigo = db.Column(db.String(50), nullable=False)
    obra_social_id = db.Column(db.Integer, db.ForeignKey('obras_sociales.id'), nullable=False)
    
    # Información de cobertura del plan
    porcentaje_cobertura = db.Column(db.Float, nullable=False, default=0.0)
    copago = db.Column(db.Float, default=0.0)  # Monto del copago
    coseguro = db.Column(db.Float, default=0.0)  # Porcentaje de coseguro
    
    # Límites del plan
    limite_anual = db.Column(db.Float, nullable=True)  # Límite anual de cobertura
    limite_por_consulta = db.Column(db.Float, nullable=True)  # Límite por consulta
    
    # Restricciones
    requiere_autorizacion = db.Column(db.Boolean, default=False)
    dias_autorizacion = db.Column(db.Integer, default=0)
    especialidades_cubiertas = db.Column(db.Text, nullable=True)  # JSON de especialidades
    
    # Estado y auditoría
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notas = db.Column(db.Text, nullable=True)
    
    # Relaciones
    obra_social = db.relationship('ObraSocial', foreign_keys=[obra_social_id], back_populates='planes', lazy=True)
    clientes = db.relationship('Cliente', foreign_keys='Cliente.plan_id', back_populates='plan', lazy=True)
    
    def __repr__(self):
        return f'<PlanObraSocial {self.nombre} - {self.obra_social.nombre}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'codigo': self.codigo,
            'obra_social_id': self.obra_social_id,
            'obra_social_nombre': self.obra_social.nombre if self.obra_social else None,
            'porcentaje_cobertura': self.porcentaje_cobertura,
            'copago': self.copago,
            'coseguro': self.coseguro,
            'limite_anual': self.limite_anual,
            'limite_por_consulta': self.limite_por_consulta,
            'requiere_autorizacion': self.requiere_autorizacion,
            'dias_autorizacion': self.dias_autorizacion,
            'especialidades_cubiertas': self.especialidades_cubiertas,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_modificacion': self.fecha_modificacion.isoformat() if self.fecha_modificacion else None,
            'notas': self.notas
        }
    
    @property
    def cobertura_display(self):
        """Retorna el porcentaje de cobertura en formato legible"""
        if self.porcentaje_cobertura == 0:
            return 'Sin cobertura'
        return f'{self.porcentaje_cobertura:.0f}%'
    
    @property
    def copago_display(self):
        """Retorna el copago en formato legible"""
        if self.copago == 0:
            return 'Sin copago'
        return f'${self.copago:.2f}'
    
    @property
    def coseguro_display(self):
        """Retorna el coseguro en formato legible"""
        if self.coseguro == 0:
            return 'Sin coseguro'
        return f'{self.coseguro:.0f}%'
    
    def calcular_costo_paciente(self, costo_total):
        """Calcula el costo que debe pagar el paciente"""
        if self.porcentaje_cobertura == 0:
            return costo_total
        
        costo_cubierto = costo_total * (self.porcentaje_cobertura / 100)
        costo_paciente = costo_total - costo_cubierto
        
        # Aplicar copago
        if self.copago > 0:
            costo_paciente += self.copago
        
        # Aplicar coseguro
        if self.coseguro > 0:
            coseguro_monto = costo_cubierto * (self.coseguro / 100)
            costo_paciente += coseguro_monto
        
        return max(0, costo_paciente)
    
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
