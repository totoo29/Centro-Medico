from flask import make_response
from src.models import Cliente
from src.database import db
from src.utils.validators import validar_email, validar_telefono

import pandas as pd
from io import BytesIO

class ClienteService:
    
    @staticmethod
    def get_all_clientes():
        """Obtener todos los clientes activos"""
        return Cliente.query.filter_by(activo=True).order_by(Cliente.apellido, Cliente.nombre).all()
    
    @staticmethod
    def get_cliente_by_id(id):
        """Obtener cliente por ID"""
        return Cliente.query.filter_by(id=id, activo=True).first()
    
    @staticmethod
    def get_paginated_clientes(page=1, per_page=10, search=''):
        """Obtener clientes con paginación y búsqueda"""
        query = Cliente.query.filter_by(activo=True)
        
        if search:
            query = query.filter(
                db.or_(
                    Cliente.nombre.contains(search),
                    Cliente.apellido.contains(search),
                    Cliente.email.contains(search),
                    Cliente.telefono.contains(search)
                )
            )
        
        return query.order_by(Cliente.apellido, Cliente.nombre).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def buscar_clientes(query, limit=10):
        """Buscar clientes para autocompletado"""
        if not query:
            return []
        
        return Cliente.query.filter(
            Cliente.activo == True,
            db.or_(
                Cliente.nombre.contains(query),
                Cliente.apellido.contains(query),
                Cliente.email.contains(query)
            )
        ).limit(limit).all()
    
    @staticmethod
    def crear_cliente(data):
        """Crear nuevo cliente"""
        # Validaciones
        if not data.get('nombre') or not data.get('apellido'):
            raise ValueError('Nombre y apellido son obligatorios')
        
        if data.get('email') and not validar_email(data['email']):
            raise ValueError('Email no válido')
        
        if data.get('telefono') and not validar_telefono(data['telefono']):
            raise ValueError('Teléfono no válido')
        
        # Verificar email único
        if data.get('email'):
            cliente_existente = Cliente.query.filter_by(
                email=data['email'], activo=True
            ).first()
            if cliente_existente:
                raise ValueError('Ya existe un cliente con este email')
        
        # Crear cliente
        cliente = Cliente(
            nombre=data['nombre'].strip(),
            apellido=data['apellido'].strip(),
            telefono=data.get('telefono', '').strip() or None,
            email=data.get('email', '').strip() or None,
            obra_social_id=data.get('obra_social_id') if data.get('obra_social_id') and data.get('obra_social_id') != 'particular' else None,
            plan_id=data.get('plan_id') if data.get('plan_id') else None,
            numero_afiliado=data.get('numero_afiliado', '').strip() or None,
            grupo_familiar=data.get('grupo_familiar', '').strip() or None,
            titular_id=data.get('titular_id') if data.get('titular_id') else None
        )
        
        db.session.add(cliente)
        db.session.commit()
        
        return cliente
    
    @staticmethod
    def actualizar_cliente(id, data):
        """Actualizar cliente existente"""
        cliente = ClienteService.get_cliente_by_id(id)
        if not cliente:
            return None
        
        # Validaciones
        if data.get('email') and not validar_email(data['email']):
            raise ValueError('Email no válido')
        
        if data.get('telefono') and not validar_telefono(data['telefono']):
            raise ValueError('Teléfono no válido')
        
        # Verificar email único (excepto el cliente actual)
        if data.get('email') and data['email'] != cliente.email:
            cliente_existente = Cliente.query.filter(
                Cliente.email == data['email'],
                Cliente.activo == True,
                Cliente.id != id
            ).first()
            if cliente_existente:
                raise ValueError('Ya existe un cliente con este email')
        
        # Actualizar campos
        if 'nombre' in data:
            cliente.nombre = data['nombre'].strip()
        if 'apellido' in data:
            cliente.apellido = data['apellido'].strip()
        if 'telefono' in data:
            cliente.telefono = data['telefono'].strip() or None
        if 'email' in data:
            cliente.email = data['email'].strip() or None
        if 'obra_social_id' in data:
            cliente.obra_social_id = data['obra_social_id'] if data['obra_social_id'] and data['obra_social_id'] != 'particular' else None
        if 'plan_id' in data:
            cliente.plan_id = data['plan_id'] if data['plan_id'] else None
        if 'numero_afiliado' in data:
            cliente.numero_afiliado = data['numero_afiliado'].strip() or None
        if 'grupo_familiar' in data:
            cliente.grupo_familiar = data['grupo_familiar'].strip() or None
        if 'titular_id' in data:
            cliente.titular_id = data['titular_id'] if data['titular_id'] else None
        
        db.session.commit()
        return cliente
    
    @staticmethod
    def eliminar_cliente(id):
        """Eliminar (desactivar) cliente"""
        cliente = ClienteService.get_cliente_by_id(id)
        if not cliente:
            return False
        
        cliente.activo = False
        db.session.commit()
        return True
    
    @staticmethod
    def exportar_excel(search=''):
        """Exportar clientes a Excel"""
        try:
            query = Cliente.query.filter_by(activo=True)
            
            if search:
                query = query.filter(
                    db.or_(
                        Cliente.nombre.contains(search),
                        Cliente.apellido.contains(search),
                        Cliente.email.contains(search),
                        Cliente.telefono.contains(search)
                    )
                )
            
            clientes = query.order_by(Cliente.apellido, Cliente.nombre).all()
            
            # Crear DataFrame
            data = []
            for cliente in clientes:
                try:
                    # Obtener información de obra social y plan de forma segura
                    obra_social_nombre = 'Particular'
                    plan_nombre = ''
                    
                    try:
                        if cliente.obra_social:
                            obra_social_nombre = cliente.obra_social.nombre
                        if cliente.plan:
                            plan_nombre = cliente.plan.nombre
                    except Exception as e:
                        print(f"Error accediendo a relaciones del cliente {cliente.id}: {e}")
                    
                    data.append({
                        'ID': cliente.id,
                        'Nombre': cliente.nombre,
                        'Apellido': cliente.apellido,
                        'Teléfono': cliente.telefono or '',
                        'Email': cliente.email or '',
                        'Obra Social': obra_social_nombre,
                        'Plan': plan_nombre,
                        'Número Afiliado': cliente.numero_afiliado or '',
                        'Grupo Familiar': cliente.grupo_familiar or '',
                        'Fecha Creación': cliente.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if cliente.fecha_creacion else ''
                    })
                except Exception as e:
                    # Si hay un error con un cliente específico, lo saltamos y continuamos
                    print(f"Error procesando cliente {cliente.id}: {e}")
                    continue
            
            if not data:
                # Si no hay datos, crear un Excel vacío con headers
                df = pd.DataFrame(columns=[
                    'ID', 'Nombre', 'Apellido', 'Teléfono', 'Email', 
                    'Obra Social', 'Plan', 'Número Afiliado', 'Grupo Familiar', 'Fecha Creación'
                ])
            else:
                df = pd.DataFrame(data)
            
            # Crear archivo Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Clientes', index=False)
            
            output.seek(0)
            
            response = make_response(output.read())
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = 'attachment; filename=clientes.xlsx'
            
            return response
            
        except Exception as e:
            print(f"Error general en exportar_excel: {e}")
            raise e
    
    @staticmethod
    def get_estadisticas_clientes():
        """Obtener estadísticas generales de clientes"""
        total_clientes = Cliente.query.filter_by(activo=True).count()
        clientes_con_email = Cliente.query.filter(
            Cliente.activo == True,
            Cliente.email.isnot(None),
            Cliente.email != ''
        ).count()
        clientes_con_telefono = Cliente.query.filter(
            Cliente.activo == True,
            Cliente.telefono.isnot(None),
            Cliente.telefono != ''
        ).count()
        
        return {
            'total_clientes': total_clientes,
            'con_email': clientes_con_email,
            'con_telefono': clientes_con_telefono,
            'porcentaje_email': (clientes_con_email / total_clientes * 100) if total_clientes > 0 else 0,
            'porcentaje_telefono': (clientes_con_telefono / total_clientes * 100) if total_clientes > 0 else 0
        }
    
    @staticmethod
    def clientes_recientes(limite=5):
        """Obtener clientes más recientes"""
        return Cliente.query.filter_by(activo=True).order_by(
            Cliente.fecha_creacion.desc()
        ).limit(limite).all()
    
    @staticmethod
    def validar_datos_cliente(data, cliente_id=None):
        """Validar datos de cliente de forma centralizada"""
        errores = []
        
        # Validar campos obligatorios
        if not data.get('nombre', '').strip():
            errores.append('El nombre es obligatorio')
        
        if not data.get('apellido', '').strip():
            errores.append('El apellido es obligatorio')
        
        # Validar email si se proporciona
        if data.get('email'):
            if not validar_email(data['email']):
                errores.append('El formato del email no es válido')
            else:
                # Verificar unicidad del email
                query = Cliente.query.filter_by(email=data['email'], activo=True)
                if cliente_id:
                    query = query.filter(Cliente.id != cliente_id)
                
                if query.first():
                    errores.append('Ya existe un cliente con este email')
        
        # Validar teléfono si se proporciona
        if data.get('telefono') and not validar_telefono(data['telefono']):
            errores.append('El formato del teléfono no es válido')
        
        return errores
    
    @staticmethod
    def exportar_csv(search=''):
        """Exportar clientes a CSV"""
        try:
            query = Cliente.query.filter_by(activo=True)
            
            if search:
                query = query.filter(
                    db.or_(
                        Cliente.nombre.contains(search),
                        Cliente.apellido.contains(search),
                        Cliente.email.contains(search),
                        Cliente.telefono.contains(search)
                    )
                )
            
            clientes = query.order_by(Cliente.apellido, Cliente.nombre).all()
            
            # Crear CSV
            data = []
            
            for cliente in clientes:
                try:
                    # Obtener información de obra social y plan de forma segura
                    obra_social_nombre = 'Particular'
                    plan_nombre = ''
                    
                    try:
                        if cliente.obra_social:
                            obra_social_nombre = cliente.obra_social.nombre
                        if cliente.plan:
                            plan_nombre = cliente.plan.nombre
                    except Exception as e:
                        print(f"Error accediendo a relaciones del cliente {cliente.id}: {e}")
                    
                    data.append({
                        'ID': cliente.id,
                        'Nombre': cliente.nombre,
                        'Apellido': cliente.apellido,
                        'Teléfono': cliente.telefono or '',
                        'Email': cliente.email or '',
                        'Obra Social': obra_social_nombre,
                        'Plan': plan_nombre,
                        'Número Afiliado': cliente.numero_afiliado or '',
                        'Grupo Familiar': cliente.grupo_familiar or '',
                        'Fecha Creación': cliente.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if cliente.fecha_creacion else ''
                    })
                except Exception as e:
                    # Si hay un error con un cliente específico, lo saltamos y continuamos
                    print(f"Error procesando cliente {cliente.id}: {e}")
                    continue
            
            if not data:
                # Si no hay datos, crear un CSV vacío con headers
                df = pd.DataFrame(columns=[
                    'ID', 'Nombre', 'Apellido', 'Teléfono', 'Email', 
                    'Obra Social', 'Plan', 'Número Afiliado', 'Grupo Familiar', 'Fecha Creación'
                ])
            else:
                df = pd.DataFrame(data)
            
            # Crear archivo CSV
            output = BytesIO()
            df.to_csv(output, index=False, encoding='utf-8-sig')  # UTF-8 con BOM para Excel
            output.seek(0)
            
            response = make_response(output.read())
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = 'attachment; filename=clientes.csv'
            
            return response
            
        except Exception as e:
            print(f"Error general en exportar_csv: {e}")
            raise e