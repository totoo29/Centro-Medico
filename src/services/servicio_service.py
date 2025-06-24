from src.models import Servicio, Categoria
from src.database import db
from src.utils.validators import validar_nombre, validar_precio, validar_duracion, validar_longitud_texto

class ServicioService:
    
    @staticmethod
    def get_all_servicios(categoria_id=None):
        """Obtener todos los servicios activos"""
        query = Servicio.query.filter_by(activo=True)
        
        if categoria_id:
            query = query.filter_by(categoria_id=categoria_id)
        
        return query.order_by(Servicio.nombre).all()
    
    @staticmethod
    def get_servicio_by_id(id):
        """Obtener servicio por ID"""
        return Servicio.query.filter_by(id=id, activo=True).first()
    
    @staticmethod
    def get_paginated_servicios(page=1, per_page=10, search='', categoria_id=None):
        """Obtener servicios con paginación y búsqueda"""
        query = Servicio.query.filter_by(activo=True)
        
        if categoria_id:
            query = query.filter_by(categoria_id=categoria_id)
        
        if search:
            query = query.filter(
                db.or_(
                    Servicio.nombre.contains(search),
                    Servicio.descripcion.contains(search)
                )
            )
        
        return query.order_by(Servicio.nombre).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def buscar_servicios(query, categoria_id=None, limit=10):
        """Buscar servicios para autocompletado"""
        if not query:
            return []
        
        search_query = Servicio.query.filter(
            Servicio.activo == True,
            db.or_(
                Servicio.nombre.contains(query),
                Servicio.descripcion.contains(query)
            )
        )
        
        if categoria_id:
            search_query = search_query.filter_by(categoria_id=categoria_id)
        
        return search_query.limit(limit).all()
    
    @staticmethod
    def crear_servicio(data):
        """Crear nuevo servicio"""
        # Validaciones
        if not data.get('nombre'):
            raise ValueError('El nombre es obligatorio')
        
        if not validar_nombre(data['nombre']):
            raise ValueError('Nombre no válido')
        
        if not data.get('precio') or not validar_precio(data['precio']):
            raise ValueError('Precio no válido')
        
        if not data.get('duracion') or not validar_duracion(data['duracion']):
            raise ValueError('Duración no válida (debe ser entre 1 y 480 minutos)')
        
        if data.get('descripcion') and not validar_longitud_texto(data['descripcion'], 0, 1000):
            raise ValueError('La descripción es demasiado larga')
        
        # Verificar nombre único
        servicio_existente = Servicio.query.filter_by(
            nombre=data['nombre'].strip(), activo=True
        ).first()
        if servicio_existente:
            raise ValueError('Ya existe un servicio con este nombre')
        
        # Verificar que la categoría existe si se proporciona
        categoria_id = data.get('categoria_id')
        if categoria_id:
            categoria = Categoria.query.filter_by(id=categoria_id, activo=True).first()
            if not categoria:
                raise ValueError('La categoría seleccionada no existe')
        
        # Crear servicio
        servicio = Servicio(
            nombre=data['nombre'].strip(),
            descripcion=data.get('descripcion', '').strip() or None,
            precio=float(data['precio']),
            duracion=int(data['duracion']),
            categoria_id=categoria_id if categoria_id else None
        )
        
        db.session.add(servicio)
        db.session.commit()
        
        return servicio
    
    @staticmethod
    def actualizar_servicio(id, data):
        """Actualizar servicio existente"""
        servicio = ServicioService.get_servicio_by_id(id)
        if not servicio:
            return None
        
        # Validaciones
        if 'nombre' in data and data['nombre']:
            if not validar_nombre(data['nombre']):
                raise ValueError('Nombre no válido')
            
            # Verificar nombre único (excepto el servicio actual)
            servicio_existente = Servicio.query.filter(
                Servicio.nombre == data['nombre'].strip(),
                Servicio.activo == True,
                Servicio.id != id
            ).first()
            if servicio_existente:
                raise ValueError('Ya existe un servicio con este nombre')
        
        if 'precio' in data and data['precio'] is not None:
            if not validar_precio(data['precio']):
                raise ValueError('Precio no válido')
        
        if 'duracion' in data and data['duracion'] is not None:
            if not validar_duracion(data['duracion']):
                raise ValueError('Duración no válida (debe ser entre 1 y 480 minutos)')
        
        if data.get('descripcion') and not validar_longitud_texto(data['descripcion'], 0, 1000):
            raise ValueError('La descripción es demasiado larga')
        
        # Verificar categoría si se proporciona
        if 'categoria_id' in data and data['categoria_id']:
            categoria = Categoria.query.filter_by(id=data['categoria_id'], activo=True).first()
            if not categoria:
                raise ValueError('La categoría seleccionada no existe')
        
        # Actualizar campos
        if 'nombre' in data and data['nombre']:
            servicio.nombre = data['nombre'].strip()
        
        if 'descripcion' in data:
            servicio.descripcion = data['descripcion'].strip() or None
        
        if 'precio' in data and data['precio'] is not None:
            servicio.precio = float(data['precio'])
        
        if 'duracion' in data and data['duracion'] is not None:
            servicio.duracion = int(data['duracion'])
        
        if 'categoria_id' in data:
            servicio.categoria_id = data['categoria_id'] if data['categoria_id'] else None
        
        db.session.commit()
        return servicio
    
    @staticmethod
    def eliminar_servicio(id):
        """Eliminar (desactivar) servicio"""
        servicio = ServicioService.get_servicio_by_id(id)
        if not servicio:
            return False
        
        # Verificar si tiene turnos asociados
        from src.models import Turno
        turnos_activos = Turno.query.filter(
            Turno.servicio_id == id,
            Turno.estado.in_(['pendiente', 'confirmado'])
        ).count()
        
        if turnos_activos > 0:
            raise ValueError('No se puede eliminar un servicio que tiene turnos pendientes o confirmados')
        
        servicio.activo = False
        db.session.commit()
        return True
    
    @staticmethod
    def get_servicios_por_categoria():
        """Obtener servicios agrupados por categoría"""
        servicios = Servicio.query.filter_by(activo=True).join(
            Categoria, Servicio.categoria_id == Categoria.id, isouter=True
        ).order_by(Categoria.nombre, Servicio.nombre).all()
        
        servicios_agrupados = {}
        
        for servicio in servicios:
            categoria_nombre = servicio.categoria.nombre if servicio.categoria else 'Sin categoría'
            
            if categoria_nombre not in servicios_agrupados:
                servicios_agrupados[categoria_nombre] = {
                    'categoria': servicio.categoria.to_dict() if servicio.categoria else None,
                    'servicios': []
                }
            
            servicios_agrupados[categoria_nombre]['servicios'].append(servicio.to_dict())
        
        return servicios_agrupados
    
    @staticmethod
    def get_servicios_populares(limite=5):
        """Obtener servicios más solicitados"""
        from src.models import Turno
        from sqlalchemy import func
        
        servicios_populares = db.session.query(
            Servicio,
            func.count(Turno.id).label('cantidad_turnos')
        ).join(
            Turno, Servicio.id == Turno.servicio_id
        ).filter(
            Servicio.activo == True,
            Turno.estado == 'completado'
        ).group_by(
            Servicio.id
        ).order_by(
            func.count(Turno.id).desc()
        ).limit(limite).all()
        
        return [
            {
                'servicio': servicio.to_dict(),
                'cantidad_turnos': cantidad
            }
            for servicio, cantidad in servicios_populares
        ]
    
    @staticmethod
    def calcular_tiempo_total_servicios(servicio_ids):
        """Calcular tiempo total de una lista de servicios"""
        if not servicio_ids:
            return 0
        
        servicios = Servicio.query.filter(
            Servicio.id.in_(servicio_ids),
            Servicio.activo == True
        ).all()
        
        return sum(servicio.duracion for servicio in servicios)
    
    @staticmethod
    def calcular_precio_total_servicios(servicio_ids):
        """Calcular precio total de una lista de servicios"""
        if not servicio_ids:
            return 0
        
        servicios = Servicio.query.filter(
            Servicio.id.in_(servicio_ids),
            Servicio.activo == True
        ).all()
        
        return sum(float(servicio.precio) for servicio in servicios)