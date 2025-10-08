from flask import make_response
from src.models import Autorizacion, Cliente, ObraSocial, PlanObraSocial, Servicio, Profesional
from src.database import db
import pandas as pd
from io import BytesIO
from datetime import datetime, date, timedelta
import uuid

class AutorizacionService:
    
    @staticmethod
    def get_all_autorizaciones():
        """Obtener todas las autorizaciones activas"""
        return Autorizacion.query.filter_by(activo=True).order_by(Autorizacion.fecha_solicitud.desc()).all()
    
    @staticmethod
    def get_autorizacion_by_id(id):
        """Obtener autorización por ID"""
        return Autorizacion.query.filter_by(id=id, activo=True).first()
    
    @staticmethod
    def get_autorizacion_by_numero(numero_autorizacion):
        """Obtener autorización por número"""
        return Autorizacion.query.filter_by(
            numero_autorizacion=numero_autorizacion, activo=True
        ).first()
    
    @staticmethod
    def get_autorizaciones_by_cliente(cliente_id):
        """Obtener autorizaciones por cliente"""
        return Autorizacion.query.filter_by(
            cliente_id=cliente_id, activo=True
        ).order_by(Autorizacion.fecha_solicitud.desc()).all()
    
    @staticmethod
    def get_autorizaciones_by_obra_social(obra_social_id):
        """Obtener autorizaciones por obra social"""
        return Autorizacion.query.filter_by(
            obra_social_id=obra_social_id, activo=True
        ).order_by(Autorizacion.fecha_solicitud.desc()).all()
    
    @staticmethod
    def get_paginated_autorizaciones(page=1, per_page=10, search='', estado=None, obra_social_id=None):
        """Obtener autorizaciones con paginación y búsqueda"""
        query = Autorizacion.query.filter_by(activo=True)
        
        if search:
            query = query.filter(
                db.or_(
                    Autorizacion.numero_autorizacion.contains(search),
                    Cliente.nombre.contains(search),
                    Cliente.apellido.contains(search)
                )
            ).join(Cliente)
        
        if estado:
            query = query.filter(Autorizacion.estado == estado)
        
        if obra_social_id:
            query = query.filter(Autorizacion.obra_social_id == obra_social_id)
        
        return query.order_by(Autorizacion.fecha_solicitud.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def crear_autorizacion(data):
        """Crear nueva autorización"""
        # Validaciones
        if not data.get('cliente_id') or not data.get('obra_social_id'):
            raise ValueError('Cliente y obra social son obligatorios')
        
        # Verificar que el cliente existe
        cliente = Cliente.query.filter_by(id=data['cliente_id'], activo=True).first()
        if not cliente:
            raise ValueError('El cliente especificado no existe')
        
        # Verificar que la obra social existe
        obra_social = ObraSocial.query.filter_by(id=data['obra_social_id'], activo=True).first()
        if not obra_social:
            raise ValueError('La obra social especificada no existe')
        
        # Generar número de autorización único
        numero_autorizacion = AutorizacionService._generar_numero_autorizacion()
        
        # Crear autorización
        autorizacion = Autorizacion(
            numero_autorizacion=numero_autorizacion,
            cliente_id=int(data['cliente_id']),
            obra_social_id=int(data['obra_social_id']),
            plan_id=int(data['plan_id']) if data.get('plan_id') else None,
            servicio_id=int(data['servicio_id']) if data.get('servicio_id') else None,
            profesional_id=int(data['profesional_id']) if data.get('profesional_id') else None,
            fecha_turno=datetime.strptime(data['fecha_turno'], '%Y-%m-%d').date() if data.get('fecha_turno') else None,
            porcentaje_cobertura=data.get('porcentaje_cobertura'),
            copago=data.get('copago'),
            coseguro=data.get('coseguro'),
            limite_autorizacion=data.get('limite_autorizacion'),
            cantidad_autorizada=int(data.get('cantidad_autorizada', 1)),
            observaciones=data.get('observaciones', '').strip() or None,
            usuario_solicitante=data.get('usuario_solicitante')
        )
        
        # Si se especifica un plan, usar sus valores por defecto
        if autorizacion.plan_id:
            plan = PlanObraSocial.query.filter_by(id=autorizacion.plan_id, activo=True).first()
            if plan:
                if autorizacion.porcentaje_cobertura is None:
                    autorizacion.porcentaje_cobertura = plan.porcentaje_cobertura
                if autorizacion.copago is None:
                    autorizacion.copago = plan.copago
                if autorizacion.coseguro is None:
                    autorizacion.coseguro = plan.coseguro
                if autorizacion.limite_autorizacion is None:
                    autorizacion.limite_autorizacion = plan.limite_por_consulta
        
        db.session.add(autorizacion)
        db.session.commit()
        
        return autorizacion
    
    @staticmethod
    def actualizar_autorizacion(id, data):
        """Actualizar autorización existente"""
        autorizacion = AutorizacionService.get_autorizacion_by_id(id)
        if not autorizacion:
            return None
        
        # Solo se pueden actualizar ciertos campos
        campos_editables = [
            'estado', 'motivo_rechazo', 'fecha_autorizacion', 
            'fecha_vencimiento', 'observaciones', 'usuario_autorizador'
        ]
        
        for campo in campos_editables:
            if campo in data:
                if campo == 'fecha_autorizacion' and data[campo]:
                    autorizacion.fecha_autorizacion = datetime.strptime(data[campo], '%Y-%m-%d %H:%M:%S')
                elif campo == 'fecha_vencimiento' and data[campo]:
                    autorizacion.fecha_vencimiento = datetime.strptime(data[campo], '%Y-%m-%d %H:%M:%S')
                else:
                    setattr(autorizacion, campo, data[campo])
        
        db.session.commit()
        return autorizacion
    
    @staticmethod
    def aprobar_autorizacion(id, usuario_autorizador, fecha_vencimiento=None):
        """Aprobar una autorización"""
        autorizacion = AutorizacionService.get_autorizacion_by_id(id)
        if not autorizacion:
            return None
        
        if autorizacion.estado != 'pendiente':
            raise ValueError('Solo se pueden aprobar autorizaciones pendientes')
        
        autorizacion.estado = 'aprobada'
        autorizacion.fecha_autorizacion = datetime.utcnow()
        autorizacion.usuario_autorizador = usuario_autorizador
        
        # Establecer fecha de vencimiento
        if fecha_vencimiento:
            autorizacion.fecha_vencimiento = datetime.strptime(fecha_vencimiento, '%Y-%m-%d')
        else:
            # Por defecto, vence en 30 días
            autorizacion.fecha_vencimiento = datetime.utcnow() + timedelta(days=30)
        
        db.session.commit()
        return autorizacion
    
    @staticmethod
    def rechazar_autorizacion(id, motivo_rechazo, usuario_autorizador):
        """Rechazar una autorización"""
        autorizacion = AutorizacionService.get_autorizacion_by_id(id)
        if not autorizacion:
            return None
        
        if autorizacion.estado != 'pendiente':
            raise ValueError('Solo se pueden rechazar autorizaciones pendientes')
        
        autorizacion.estado = 'rechazada'
        autorizacion.motivo_rechazo = motivo_rechazo
        autorizacion.fecha_autorizacion = datetime.utcnow()
        autorizacion.usuario_autorizador = usuario_autorizador
        
        db.session.commit()
        return autorizacion
    
    @staticmethod
    def eliminar_autorizacion(id):
        """Eliminar (desactivar) autorización"""
        autorizacion = AutorizacionService.get_autorizacion_by_id(id)
        if not autorizacion:
            return False
        
        autorizacion.activo = False
        db.session.commit()
        return True
    
    @staticmethod
    def get_estadisticas_autorizaciones():
        """Obtener estadísticas generales de autorizaciones"""
        total_autorizaciones = Autorizacion.query.filter_by(activo=True).count()
        
        # Contar por estado
        por_estado = db.session.query(
            Autorizacion.estado,
            db.func.count(Autorizacion.id)
        ).filter_by(activo=True).group_by(Autorizacion.estado).all()
        
        # Contar por obra social
        por_obra_social = db.session.query(
            ObraSocial.nombre,
            db.func.count(Autorizacion.id)
        ).join(Autorizacion).filter(
            Autorizacion.activo == True
        ).group_by(ObraSocial.nombre).all()
        
        estadisticas = {
            'total_autorizaciones': total_autorizaciones,
            'por_estado': dict(por_estado),
            'por_obra_social': dict(por_obra_social)
        }
        
        return estadisticas
    
    @staticmethod
    def exportar_excel(search='', estado=None, obra_social_id=None):
        """Exportar autorizaciones a Excel"""
        query = Autorizacion.query.filter_by(activo=True)
        
        if search:
            query = query.filter(
                db.or_(
                    Autorizacion.numero_autorizacion.contains(search),
                    Cliente.nombre.contains(search),
                    Cliente.apellido.contains(search)
                )
            ).join(Cliente)
        
        if estado:
            query = query.filter(Autorizacion.estado == estado)
        
        if obra_social_id:
            query = query.filter(Autorizacion.obra_social_id == obra_social_id)
        
        autorizaciones = query.join(Cliente).join(ObraSocial).order_by(
            Autorizacion.fecha_solicitud.desc()
        ).all()
        
        # Crear DataFrame
        data = []
        for auth in autorizaciones:
            data.append({
                'Número': auth.numero_autorizacion,
                'Cliente': auth.cliente.nombre_completo,
                'Obra Social': auth.obra_social.nombre,
                'Plan': auth.plan.nombre if auth.plan else 'Sin plan',
                'Estado': auth.estado_display,
                'Fecha Solicitud': auth.fecha_solicitud.strftime('%Y-%m-%d %H:%M:%S'),
                'Fecha Autorización': auth.fecha_autorizacion.strftime('%Y-%m-%d %H:%M:%S') if auth.fecha_autorizacion else '',
                'Fecha Vencimiento': auth.fecha_vencimiento.strftime('%Y-%m-%d') if auth.fecha_vencimiento else '',
                'Cobertura': f'{auth.porcentaje_cobertura:.0f}%' if auth.porcentaje_cobertura else 'Sin especificar',
                'Copago': f'${auth.copago:.2f}' if auth.copago else 'Sin copago',
                'Coseguro': f'{auth.coseguro:.0f}%' if auth.coseguro else 'Sin coseguro',
                'Cantidad': auth.cantidad_autorizada,
                'Días Restantes': auth.dias_restantes if auth.dias_restantes is not None else 'N/A'
            })
        
        df = pd.DataFrame(data)
        
        # Crear archivo Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Autorizaciones', index=False)
        
        output.seek(0)
        
        response = make_response(output.read())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = 'attachment; filename=autorizaciones.xlsx'
        
        return response
    
    @staticmethod
    def _generar_numero_autorizacion():
        """Generar número de autorización único"""
        while True:
            # Formato: AUTH-YYYYMMDD-XXXX
            fecha = datetime.now().strftime('%Y%m%d')
            random_part = str(uuid.uuid4())[:4].upper()
            numero = f"AUTH-{fecha}-{random_part}"
            
            # Verificar que no exista
            if not Autorizacion.query.filter_by(numero_autorizacion=numero).first():
                return numero
    
    @staticmethod
    def validar_datos_autorizacion(data):
        """Validar datos de autorización de forma centralizada"""
        errores = []
        
        # Validar campos obligatorios
        if not data.get('cliente_id'):
            errores.append('El cliente es obligatorio')
        
        if not data.get('obra_social_id'):
            errores.append('La obra social es obligatoria')
        
        # Verificar que el cliente existe
        if data.get('cliente_id'):
            cliente = Cliente.query.filter_by(id=data['cliente_id'], activo=True).first()
            if not cliente:
                errores.append('El cliente especificado no existe')
        
        # Verificar que la obra social existe
        if data.get('obra_social_id'):
            obra_social = ObraSocial.query.filter_by(id=data['obra_social_id'], activo=True).first()
            if not obra_social:
                errores.append('La obra social especificada no existe')
        
        # Verificar que el plan existe si se especifica
        if data.get('plan_id'):
            plan = PlanObraSocial.query.filter_by(id=data['plan_id'], activo=True).first()
            if not plan:
                errores.append('El plan especificado no existe')
        
        # Verificar que el servicio existe si se especifica
        if data.get('servicio_id'):
            servicio = Servicio.query.filter_by(id=data['servicio_id'], activo=True).first()
            if not servicio:
                errores.append('El servicio especificado no existe')
        
        # Verificar que el profesional existe si se especifica
        if data.get('profesional_id'):
            profesional = Profesional.query.filter_by(id=data['profesional_id'], activo=True).first()
            if not profesional:
                errores.append('El profesional especificado no existe')
        
        return errores
