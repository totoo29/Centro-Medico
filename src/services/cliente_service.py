from flask import make_response
from src.models import Cliente
from src.database import db
from src.utils.validators import validar_email, validar_telefono
from src.utils.exports import generar_excel, generar_csv
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
            email=data.get('email', '').strip() or None
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
            data.append({
                'ID': cliente.id,
                'Nombre': cliente.nombre,
                'Apellido': cliente.apellido,
                'Teléfono': cliente.telefono or '',
                'Email': cliente.email or '',
                'Fecha Creación': cliente.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        df = pd.DataFrame(data)
        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)
        
        response = make_response(output.read())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=clientes.csv'
        
        return response
    
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
    
    @staticmethod
    def exportar_csv(search=''):
        """Exportar clientes a CSV"""
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
        output = BytesIO()
        data = []
        
        for cliente in clientes:
            data.append({
                'ID': cliente.id,
                'Nombre': cliente.nombre,
                'Apellido': cliente.apellido,
                'Teléfono': cliente.telefono or '',
                'Email': cliente.email or '',
                'Fecha Creación': cliente.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
            })