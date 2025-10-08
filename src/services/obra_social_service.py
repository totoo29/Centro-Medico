from flask import make_response
from src.models import ObraSocial, PlanObraSocial, Cliente
from src.database import db
from src.utils.validators import validar_email, validar_telefono
from src.utils.exports import generar_excel, generar_csv
import pandas as pd
from io import BytesIO
from datetime import datetime, date

class ObraSocialService:
    
    @staticmethod
    def get_all_obras_sociales():
        """Obtener todas las obras sociales activas"""
        return ObraSocial.query.filter_by(activo=True).order_by(ObraSocial.nombre).all()
    
    @staticmethod
    def get_obra_social_by_id(id):
        """Obtener obra social por ID"""
        return ObraSocial.query.filter_by(id=id, activo=True).first()
    
    @staticmethod
    def get_obra_social_by_codigo(codigo):
        """Obtener obra social por código"""
        return ObraSocial.query.filter_by(codigo=codigo, activo=True).first()
    
    @staticmethod
    def get_paginated_obras_sociales(page=1, per_page=10, search='', tipo=None):
        """Obtener obras sociales con paginación y búsqueda"""
        query = ObraSocial.query.filter_by(activo=True)
        
        if search:
            query = query.filter(
                db.or_(
                    ObraSocial.nombre.contains(search),
                    ObraSocial.codigo.contains(search),
                    ObraSocial.cuit.contains(search)
                )
            )
        
        if tipo:
            query = query.filter(ObraSocial.tipo == tipo)
        
        return query.order_by(ObraSocial.nombre).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def buscar_obras_sociales(query, limit=10):
        """Buscar obras sociales para autocompletado"""
        if not query:
            return []
        
        return ObraSocial.query.filter(
            ObraSocial.activo == True,
            db.or_(
                ObraSocial.nombre.contains(query),
                ObraSocial.codigo.contains(query)
            )
        ).limit(limit).all()
    
    @staticmethod
    def crear_obra_social(data):
        """Crear nueva obra social"""
        # Validaciones
        if not data.get('nombre') or not data.get('codigo'):
            raise ValueError('Nombre y código son obligatorios')
        
        if data.get('email') and not validar_email(data['email']):
            raise ValueError('Email no válido')
        
        if data.get('telefono') and not validar_telefono(data['telefono']):
            raise ValueError('Teléfono no válido')
        
        # Verificar código único
        obra_existente = ObraSocial.query.filter_by(
            codigo=data['codigo'], activo=True
        ).first()
        if obra_existente:
            raise ValueError('Ya existe una obra social con este código')
        
        # Crear obra social
        obra_social = ObraSocial(
            nombre=data['nombre'].strip(),
            codigo=data['codigo'].strip().upper(),
            tipo=data.get('tipo', 'obra_social'),
            cuit=data.get('cuit', '').strip() or None,
            direccion=data.get('direccion', '').strip() or None,
            telefono=data.get('telefono', '').strip() or None,
            email=data.get('email', '').strip() or None,
            contacto_nombre=data.get('contacto_nombre', '').strip() or None,
            contacto_telefono=data.get('contacto_telefono', '').strip() or None,
            contacto_email=data.get('contacto_email', '').strip() or None,
            porcentaje_cobertura=float(data.get('porcentaje_cobertura', 0)),
            requiere_autorizacion=data.get('requiere_autorizacion', False),
            dias_autorizacion=int(data.get('dias_autorizacion', 0)),
            notas=data.get('notas', '').strip() or None
        )
        
        db.session.add(obra_social)
        db.session.commit()
        
        return obra_social
    
    @staticmethod
    def actualizar_obra_social(id, data):
        """Actualizar obra social existente"""
        obra_social = ObraSocialService.get_obra_social_by_id(id)
        if not obra_social:
            return None
        
        # Validaciones
        if data.get('email') and not validar_email(data['email']):
            raise ValueError('Email no válido')
        
        if data.get('telefono') and not validar_telefono(data['telefono']):
            raise ValueError('Teléfono no válido')
        
        # Verificar código único (excepto la obra social actual)
        if data.get('codigo') and data['codigo'] != obra_social.codigo:
            obra_existente = ObraSocial.query.filter(
                ObraSocial.codigo == data['codigo'],
                ObraSocial.activo == True,
                ObraSocial.id != id
            ).first()
            if obra_existente:
                raise ValueError('Ya existe una obra social con este código')
        
        # Actualizar campos
        if 'nombre' in data:
            obra_social.nombre = data['nombre'].strip()
        if 'codigo' in data:
            obra_social.codigo = data['codigo'].strip().upper()
        if 'tipo' in data:
            obra_social.tipo = data['tipo']
        if 'cuit' in data:
            obra_social.cuit = data['cuit'].strip() or None
        if 'direccion' in data:
            obra_social.direccion = data['direccion'].strip() or None
        if 'telefono' in data:
            obra_social.telefono = data['telefono'].strip() or None
        if 'email' in data:
            obra_social.email = data['email'].strip() or None
        if 'contacto_nombre' in data:
            obra_social.contacto_nombre = data['contacto_nombre'].strip() or None
        if 'contacto_telefono' in data:
            obra_social.contacto_telefono = data['contacto_telefono'].strip() or None
        if 'contacto_email' in data:
            obra_social.contacto_email = data['contacto_email'].strip() or None
        if 'porcentaje_cobertura' in data:
            obra_social.porcentaje_cobertura = float(data['porcentaje_cobertura'])
        if 'requiere_autorizacion' in data:
            obra_social.requiere_autorizacion = data['requiere_autorizacion']
        if 'dias_autorizacion' in data:
            obra_social.dias_autorizacion = int(data['dias_autorizacion'])
        if 'notas' in data:
            obra_social.notas = data['notas'].strip() or None
        
        db.session.commit()
        return obra_social
    
    @staticmethod
    def eliminar_obra_social(id):
        """Eliminar (desactivar) obra social"""
        obra_social = ObraSocialService.get_obra_social_by_id(id)
        if not obra_social:
            return False
        
        # Verificar que no tenga clientes asociados
        clientes_asociados = Cliente.query.filter_by(
            obra_social_id=id, activo=True
        ).count()
        
        if clientes_asociados > 0:
            raise ValueError(f'No se puede eliminar la obra social porque tiene {clientes_asociados} cliente(s) asociado(s)')
        
        obra_social.activo = False
        db.session.commit()
        return True
    
    @staticmethod
    def get_estadisticas_obras_sociales():
        """Obtener estadísticas generales de obras sociales"""
        total_obras = ObraSocial.query.filter_by(activo=True).count()
        obras_con_autorizacion = ObraSocial.query.filter(
            ObraSocial.activo == True,
            ObraSocial.requiere_autorizacion == True
        ).count()
        
        # Contar por tipo
        tipos = db.session.query(
            ObraSocial.tipo,
            db.func.count(ObraSocial.id)
        ).filter_by(activo=True).group_by(ObraSocial.tipo).all()
        
        estadisticas = {
            'total_obras': total_obras,
            'con_autorizacion': obras_con_autorizacion,
            'por_tipo': dict(tipos)
        }
        
        return estadisticas
    
    @staticmethod
    def exportar_excel(search='', tipo=None):
        """Exportar obras sociales a Excel"""
        query = ObraSocial.query.filter_by(activo=True)
        
        if search:
            query = query.filter(
                db.or_(
                    ObraSocial.nombre.contains(search),
                    ObraSocial.codigo.contains(search),
                    ObraSocial.cuit.contains(search)
                )
            )
        
        if tipo:
            query = query.filter(ObraSocial.tipo == tipo)
        
        obras = query.order_by(ObraSocial.nombre).all()
        
        # Crear DataFrame
        data = []
        for obra in obras:
            data.append({
                'ID': obra.id,
                'Nombre': obra.nombre,
                'Código': obra.codigo,
                'Tipo': obra.tipo_display,
                'CUIT': obra.cuit or '',
                'Dirección': obra.direccion or '',
                'Teléfono': obra.telefono or '',
                'Email': obra.email or '',
                'Contacto': obra.contacto_nombre or '',
                'Cobertura': obra.cobertura_display,
                'Requiere Autorización': 'Sí' if obra.requiere_autorizacion else 'No',
                'Días Autorización': obra.dias_autorizacion,
                'Fecha Creación': obra.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        df = pd.DataFrame(data)
        
        # Crear archivo Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Obras Sociales', index=False)
        
        output.seek(0)
        
        response = make_response(output.read())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = 'attachment; filename=obras_sociales.xlsx'
        
        return response
    
    @staticmethod
    def exportar_csv(search='', tipo=None):
        """Exportar obras sociales a CSV"""
        query = ObraSocial.query.filter_by(activo=True)
        
        if search:
            query = query.filter(
                db.or_(
                    ObraSocial.nombre.contains(search),
                    ObraSocial.codigo.contains(search),
                    ObraSocial.cuit.contains(search)
                )
            )
        
        if tipo:
            query = query.filter(ObraSocial.tipo == tipo)
        
        obras = query.order_by(ObraSocial.nombre).all()
        
        # Crear CSV
        output = BytesIO()
        data = []
        
        for obra in obras:
            data.append({
                'ID': obra.id,
                'Nombre': obra.nombre,
                'Código': obra.codigo,
                'Tipo': obra.tipo_display,
                'CUIT': obra.cuit or '',
                'Dirección': obra.direccion or '',
                'Teléfono': obra.telefono or '',
                'Email': obra.email or '',
                'Contacto': obra.contacto_nombre or '',
                'Cobertura': obra.cobertura_display,
                'Requiere Autorización': 'Sí' if obra.requiere_autorizacion else 'No',
                'Días Autorización': obra.dias_autorizacion,
                'Fecha Creación': obra.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        df = pd.DataFrame(data)
        df.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)
        
        response = make_response(output.read())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=obras_sociales.csv'
        
        return response
    
    @staticmethod
    def validar_datos_obra_social(data, obra_social_id=None):
        """Validar datos de obra social de forma centralizada"""
        errores = []
        
        # Validar campos obligatorios
        if not data.get('nombre', '').strip():
            errores.append('El nombre es obligatorio')
        
        if not data.get('codigo', '').strip():
            errores.append('El código es obligatorio')
        
        # Validar email si se proporciona
        if data.get('email') and not validar_email(data['email']):
            errores.append('El formato del email no es válido')
        
        # Validar teléfono si se proporciona
        if data.get('telefono') and not validar_telefono(data['telefono']):
            errores.append('El formato del teléfono no es válido')
        
        # Verificar unicidad del código
        if data.get('codigo'):
            query = ObraSocial.query.filter_by(codigo=data['codigo'].strip().upper(), activo=True)
            if obra_social_id:
                query = query.filter(ObraSocial.id != obra_social_id)
            
            if query.first():
                errores.append('Ya existe una obra social con este código')
        
        return errores
