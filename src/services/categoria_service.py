from src.models import Categoria
from src.database import db
from src.utils.validators import validar_nombre, validar_longitud_texto

class CategoriaService:
    
    @staticmethod
    def get_all_categorias():
        """Obtener todas las categorías activas"""
        return Categoria.query.filter_by(activo=True).order_by(Categoria.nombre).all()
    
    @staticmethod
    def get_categoria_by_id(id):
        """Obtener categoría por ID"""
        return Categoria.query.filter_by(id=id, activo=True).first()
    
    @staticmethod
    def get_paginated_categorias(page=1, per_page=10, search=''):
        """Obtener categorías con paginación y búsqueda"""
        query = Categoria.query.filter_by(activo=True)
        
        if search:
            query = query.filter(
                db.or_(
                    Categoria.nombre.contains(search),
                    Categoria.descripcion.contains(search)
                )
            )
        
        return query.order_by(Categoria.nombre).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def crear_categoria(data):
        """Crear nueva categoría"""
        # Validaciones
        if not data.get('nombre'):
            raise ValueError('El nombre es obligatorio')
        
        if not validar_nombre(data['nombre']):
            raise ValueError('Nombre no válido')
        
        if data.get('descripcion') and not validar_longitud_texto(data['descripcion'], 0, 500):
            raise ValueError('La descripción es demasiado larga')
        
        # Verificar nombre único
        categoria_existente = Categoria.query.filter_by(
            nombre=data['nombre'].strip(), activo=True
        ).first()
        if categoria_existente:
            raise ValueError('Ya existe una categoría con este nombre')
        
        # Validar color hexadecimal
        color = data.get('color', '#007bff')
        if not color.startswith('#') or len(color) != 7:
            color = '#007bff'
        
        # Crear categoría
        categoria = Categoria(
            nombre=data['nombre'].strip(),
            descripcion=data.get('descripcion', '').strip() or None,
            color=color
        )
        
        db.session.add(categoria)
        db.session.commit()
        
        return categoria
    
    @staticmethod
    def actualizar_categoria(id, data):
        """Actualizar categoría existente"""
        categoria = CategoriaService.get_categoria_by_id(id)
        if not categoria:
            return None
        
        # Validaciones
        if 'nombre' in data and data['nombre']:
            if not validar_nombre(data['nombre']):
                raise ValueError('Nombre no válido')
            
            # Verificar nombre único (excepto la categoría actual)
            categoria_existente = Categoria.query.filter(
                Categoria.nombre == data['nombre'].strip(),
                Categoria.activo == True,
                Categoria.id != id
            ).first()
            if categoria_existente:
                raise ValueError('Ya existe una categoría con este nombre')
        
        if data.get('descripcion') and not validar_longitud_texto(data['descripcion'], 0, 500):
            raise ValueError('La descripción es demasiado larga')
        
        # Actualizar campos
        if 'nombre' in data and data['nombre']:
            categoria.nombre = data['nombre'].strip()
        
        if 'descripcion' in data:
            categoria.descripcion = data['descripcion'].strip() or None
        
        if 'color' in data:
            color = data['color']
            if color and color.startswith('#') and len(color) == 7:
                categoria.color = color
        
        db.session.commit()
        return categoria
    
    @staticmethod
    def eliminar_categoria(id):
        """Eliminar (desactivar) categoría"""
        categoria = CategoriaService.get_categoria_by_id(id)
        if not categoria:
            return False
        
        # Verificar si tiene servicios asociados
        if categoria.servicios:
            raise ValueError('No se puede eliminar una categoría que tiene servicios asociados')
        
        categoria.activo = False
        db.session.commit()
        return True
    
    @staticmethod
    def get_categoria_con_servicios(id):
        """Obtener categoría con sus servicios"""
        categoria = CategoriaService.get_categoria_by_id(id)
        if not categoria:
            return None
        
        return {
            'categoria': categoria.to_dict(),
            'servicios': [servicio.to_dict() for servicio in categoria.servicios if servicio.activo]
        }