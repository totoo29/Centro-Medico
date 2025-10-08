from flask import make_response
from src.models import PlanObraSocial, ObraSocial, Cliente
from src.database import db
import pandas as pd
from io import BytesIO
from datetime import datetime, date

class PlanObraSocialService:
    
    @staticmethod
    def get_all_planes():
        """Obtener todos los planes activos"""
        return PlanObraSocial.query.filter_by(activo=True).order_by(PlanObraSocial.nombre).all()
    
    @staticmethod
    def get_plan_by_id(id):
        """Obtener plan por ID"""
        return PlanObraSocial.query.filter_by(id=id, activo=True).first()
    
    @staticmethod
    def get_planes_by_obra_social(obra_social_id):
        """Obtener planes por obra social"""
        return PlanObraSocial.query.filter_by(
            obra_social_id=obra_social_id, activo=True
        ).order_by(PlanObraSocial.nombre).all()
    
    @staticmethod
    def get_paginated_planes(page=1, per_page=10, search='', obra_social_id=None):
        """Obtener planes con paginación y búsqueda"""
        query = PlanObraSocial.query.filter_by(activo=True)
        
        if search:
            query = query.filter(
                db.or_(
                    PlanObraSocial.nombre.contains(search),
                    PlanObraSocial.codigo.contains(search)
                )
            )
        
        if obra_social_id:
            query = query.filter(PlanObraSocial.obra_social_id == obra_social_id)
        
        return query.order_by(PlanObraSocial.nombre).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def buscar_planes(query, obra_social_id=None, limit=10):
        """Buscar planes para autocompletado"""
        if not query:
            return []
        
        query_filter = PlanObraSocial.query.filter(
            PlanObraSocial.activo == True
        )
        
        if obra_social_id:
            query_filter = query_filter.filter(PlanObraSocial.obra_social_id == obra_social_id)
        
        return query_filter.filter(
            db.or_(
                PlanObraSocial.nombre.contains(query),
                PlanObraSocial.codigo.contains(query)
            )
        ).limit(limit).all()
    
    @staticmethod
    def crear_plan(data):
        """Crear nuevo plan"""
        # Validaciones
        if not data.get('nombre') or not data.get('codigo') or not data.get('obra_social_id'):
            raise ValueError('Nombre, código y obra social son obligatorios')
        
        # Verificar que la obra social existe
        obra_social = ObraSocial.query.filter_by(
            id=data['obra_social_id'], activo=True
        ).first()
        if not obra_social:
            raise ValueError('La obra social especificada no existe')
        
        # Verificar código único dentro de la misma obra social
        plan_existente = PlanObraSocial.query.filter_by(
            codigo=data['codigo'],
            obra_social_id=data['obra_social_id'],
            activo=True
        ).first()
        if plan_existente:
            raise ValueError('Ya existe un plan con este código en la misma obra social')
        
        # Crear plan
        plan = PlanObraSocial(
            nombre=data['nombre'].strip(),
            codigo=data['codigo'].strip().upper(),
            obra_social_id=int(data['obra_social_id']),
            porcentaje_cobertura=float(data.get('porcentaje_cobertura', 0)),
            copago=float(data.get('copago', 0)),
            coseguro=float(data.get('coseguro', 0)),
            limite_anual=float(data.get('limite_anual', 0)) if data.get('limite_anual') else None,
            limite_por_consulta=float(data.get('limite_por_consulta', 0)) if data.get('limite_por_consulta') else None,
            requiere_autorizacion='requiere_autorizacion' in data,
            dias_autorizacion=int(data.get('dias_autorizacion', 0)),
            especialidades_cubiertas=data.get('especialidades_cubiertas', '').strip() or None,
            notas=data.get('notas', '').strip() or None
        )
        
        db.session.add(plan)
        db.session.commit()
        
        return plan
    
    @staticmethod
    def actualizar_plan(id, data):
        """Actualizar plan existente"""
        plan = PlanObraSocialService.get_plan_by_id(id)
        if not plan:
            return None
        
        # Verificar código único dentro de la misma obra social (excepto el plan actual)
        if data.get('codigo') and data['codigo'] != plan.codigo:
            plan_existente = PlanObraSocial.query.filter(
                PlanObraSocial.codigo == data['codigo'],
                PlanObraSocial.obra_social_id == plan.obra_social_id,
                PlanObraSocial.activo == True,
                PlanObraSocial.id != id
            ).first()
            if plan_existente:
                raise ValueError('Ya existe un plan con este código en la misma obra social')
        
        # Actualizar campos
        if 'nombre' in data:
            plan.nombre = data['nombre'].strip()
        if 'codigo' in data:
            plan.codigo = data['codigo'].strip().upper()
        if 'porcentaje_cobertura' in data:
            plan.porcentaje_cobertura = float(data['porcentaje_cobertura'])
        if 'copago' in data:
            plan.copago = float(data['copago'])
        if 'coseguro' in data:
            plan.coseguro = float(data['coseguro'])
        if 'limite_anual' in data:
            plan.limite_anual = float(data['limite_anual']) if data['limite_anual'] else None
        if 'limite_por_consulta' in data:
            plan.limite_por_consulta = float(data['limite_por_consulta']) if data['limite_por_consulta'] else None
        # Manejar el checkbox de requiere_autorizacion
        plan.requiere_autorizacion = 'requiere_autorizacion' in data
        if 'dias_autorizacion' in data:
            plan.dias_autorizacion = int(data['dias_autorizacion'])
        if 'especialidades_cubiertas' in data:
            plan.especialidades_cubiertas = data['especialidades_cubiertas'].strip() or None
        if 'notas' in data:
            plan.notas = data['notas'].strip() or None
        
        db.session.commit()
        return plan
    
    @staticmethod
    def eliminar_plan(id):
        """Eliminar (desactivar) plan"""
        plan = PlanObraSocialService.get_plan_by_id(id)
        if not plan:
            return False
        
        # Verificar que no tenga clientes asociados
        clientes_asociados = Cliente.query.filter_by(
            plan_id=id, activo=True
        ).count()
        
        if clientes_asociados > 0:
            raise ValueError(f'No se puede eliminar el plan porque tiene {clientes_asociados} cliente(s) asociado(s)')
        
        plan.activo = False
        db.session.commit()
        return True
    
    @staticmethod
    def get_estadisticas_planes():
        """Obtener estadísticas generales de planes"""
        total_planes = PlanObraSocial.query.filter_by(activo=True).count()
        planes_con_autorizacion = PlanObraSocial.query.filter(
            PlanObraSocial.activo == True,
            PlanObraSocial.requiere_autorizacion == True
        ).count()
        
        # Contar por obra social
        por_obra_social = db.session.query(
            ObraSocial.nombre,
            db.func.count(PlanObraSocial.id)
        ).join(PlanObraSocial).filter(
            PlanObraSocial.activo == True
        ).group_by(ObraSocial.nombre).all()
        
        estadisticas = {
            'total_planes': total_planes,
            'con_autorizacion': planes_con_autorizacion,
            'por_obra_social': dict(por_obra_social)
        }
        
        return estadisticas
    
    @staticmethod
    def exportar_excel(search='', obra_social_id=None):
        """Exportar planes a Excel"""
        query = PlanObraSocial.query.filter_by(activo=True)
        
        if search:
            query = query.filter(
                db.or_(
                    PlanObraSocial.nombre.contains(search),
                    PlanObraSocial.codigo.contains(search)
                )
            )
        
        if obra_social_id:
            query = query.filter(PlanObraSocial.obra_social_id == obra_social_id)
        
        planes = query.join(ObraSocial).order_by(PlanObraSocial.nombre).all()
        
        # Crear DataFrame
        data = []
        for plan in planes:
            data.append({
                'ID': plan.id,
                'Nombre': plan.nombre,
                'Código': plan.codigo,
                'Obra Social': plan.obra_social.nombre,
                'Cobertura': plan.cobertura_display,
                'Copago': plan.copago_display,
                'Coseguro': plan.coseguro_display,
                'Límite Anual': f'${plan.limite_anual:.2f}' if plan.limite_anual else 'Sin límite',
                'Límite por Consulta': f'${plan.limite_por_consulta:.2f}' if plan.limite_por_consulta else 'Sin límite',
                'Requiere Autorización': 'Sí' if plan.requiere_autorizacion else 'No',
                'Días Autorización': plan.dias_autorizacion,
                'Fecha Creación': plan.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        df = pd.DataFrame(data)
        
        # Crear archivo Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Planes Obra Social', index=False)
        
        output.seek(0)
        
        response = make_response(output.read())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = 'attachment; filename=planes_obra_social.xlsx'
        
        return response
    
    @staticmethod
    def exportar_csv(search='', obra_social_id=None):
        """Exportar planes a CSV"""
        query = PlanObraSocial.query.filter_by(activo=True)
        
        if search:
            query = query.filter(
                db.or_(
                    PlanObraSocial.nombre.contains(search),
                    PlanObraSocial.codigo.contains(search)
                )
            )
        
        if obra_social_id:
            query = query.filter(PlanObraSocial.obra_social_id == obra_social_id)
        
        planes = query.join(ObraSocial).order_by(PlanObraSocial.nombre).all()
        
        # Crear CSV
        output = BytesIO()
        data = []
        
        for plan in planes:
            data.append({
                'ID': plan.id,
                'Nombre': plan.nombre,
                'Código': plan.codigo,
                'Obra Social': plan.obra_social.nombre,
                'Cobertura': plan.cobertura_display,
                'Copago': plan.copago_display,
                'Coseguro': plan.coseguro_display,
                'Límite Anual': f'${plan.limite_anual:.2f}' if plan.limite_anual else 'Sin límite',
                'Límite por Consulta': f'${plan.limite_por_consulta:.2f}' if plan.limite_por_consulta else 'Sin límite',
                'Requiere Autorización': 'Sí' if plan.requiere_autorizacion else 'No',
                'Días Autorización': plan.dias_autorizacion,
                'Fecha Creación': plan.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        df = pd.DataFrame(data)
        df.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)
        
        response = make_response(output.read())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=planes_obra_social.csv'
        
        return response
    
    @staticmethod
    def validar_datos_plan(data, plan_id=None):
        """Validar datos de plan de forma centralizada"""
        errores = []
        
        # Validar campos obligatorios
        if not data.get('nombre', '').strip():
            errores.append('El nombre es obligatorio')
        
        if not data.get('codigo', '').strip():
            errores.append('El código es obligatorio')
        
        if not data.get('obra_social_id'):
            errores.append('La obra social es obligatoria')
        
        # Verificar que la obra social existe
        if data.get('obra_social_id'):
            obra_social = ObraSocial.query.filter_by(
                id=data['obra_social_id'], activo=True
            ).first()
            if not obra_social:
                errores.append('La obra social especificada no existe')
        
        # Verificar unicidad del código dentro de la misma obra social
        if data.get('codigo') and data.get('obra_social_id'):
            query = PlanObraSocial.query.filter_by(
                codigo=data['codigo'].strip().upper(),
                obra_social_id=data['obra_social_id'],
                activo=True
            )
            if plan_id:
                query = query.filter(PlanObraSocial.id != plan_id)
            
            if query.first():
                errores.append('Ya existe un plan con este código en la misma obra social')
        
        return errores
