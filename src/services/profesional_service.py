from src.models import Profesional, Turno
from src.database import db
from src.utils.validators import validar_email, validar_telefono, validar_nombre
from datetime import datetime, date, time, timedelta

class ProfesionalService:
    
    @staticmethod
    def get_all_profesionales():
        """Obtener todos los profesionales activos"""
        return Profesional.query.filter_by(activo=True).order_by(Profesional.apellido, Profesional.nombre).all()
    
    @staticmethod
    def get_profesional_by_id(id):
        """Obtener profesional por ID"""
        return Profesional.query.filter_by(id=id, activo=True).first()
    
    @staticmethod
    def get_paginated_profesionales(page=1, per_page=10, search=''):
        """Obtener profesionales con paginación y búsqueda"""
        query = Profesional.query.filter_by(activo=True)
        
        if search:
            query = query.filter(
                db.or_(
                    Profesional.nombre.contains(search),
                    Profesional.apellido.contains(search),
                    Profesional.especialidad.contains(search),
                    Profesional.email.contains(search),
                    Profesional.telefono.contains(search)
                )
            )
        
        return query.order_by(Profesional.apellido, Profesional.nombre).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def buscar_profesionales(query, limit=10):
        """Buscar profesionales para autocompletado"""
        if not query:
            return []
        
        return Profesional.query.filter(
            Profesional.activo == True,
            db.or_(
                Profesional.nombre.contains(query),
                Profesional.apellido.contains(query),
                Profesional.especialidad.contains(query)
            )
        ).limit(limit).all()
    
    @staticmethod
    def crear_profesional(data):
        """Crear nuevo profesional"""
        # Validaciones
        if not data.get('nombre') or not data.get('apellido'):
            raise ValueError('Nombre y apellido son obligatorios')
        
        if not validar_nombre(data['nombre']) or not validar_nombre(data['apellido']):
            raise ValueError('Nombre o apellido no válidos')
        
        if data.get('email') and not validar_email(data['email']):
            raise ValueError('Email no válido')
        
        if data.get('telefono') and not validar_telefono(data['telefono']):
            raise ValueError('Teléfono no válido')
        
        # Verificar email único
        if data.get('email'):
            profesional_existente = Profesional.query.filter_by(
                email=data['email'], activo=True
            ).first()
            if profesional_existente:
                raise ValueError('Ya existe un profesional con este email')
        
        # Crear profesional
        profesional = Profesional(
            nombre=data['nombre'].strip(),
            apellido=data['apellido'].strip(),
            telefono=data.get('telefono', '').strip() or None,
            email=data.get('email', '').strip() or None,
            especialidad=data.get('especialidad', '').strip() or None
        )
        
        db.session.add(profesional)
        db.session.commit()
        
        return profesional
    
    @staticmethod
    def actualizar_profesional(id, data):
        """Actualizar profesional existente"""
        profesional = ProfesionalService.get_profesional_by_id(id)
        if not profesional:
            return None
        
        # Validaciones
        if data.get('nombre') and not validar_nombre(data['nombre']):
            raise ValueError('Nombre no válido')
        
        if data.get('apellido') and not validar_nombre(data['apellido']):
            raise ValueError('Apellido no válido')
        
        if data.get('email') and not validar_email(data['email']):
            raise ValueError('Email no válido')
        
        if data.get('telefono') and not validar_telefono(data['telefono']):
            raise ValueError('Teléfono no válido')
        
        # Verificar email único (excepto el profesional actual)
        if data.get('email') and data['email'] != profesional.email:
            profesional_existente = Profesional.query.filter(
                Profesional.email == data['email'],
                Profesional.activo == True,
                Profesional.id != id
            ).first()
            if profesional_existente:
                raise ValueError('Ya existe un profesional con este email')
        
        # Actualizar campos
        if 'nombre' in data and data['nombre']:
            profesional.nombre = data['nombre'].strip()
        if 'apellido' in data and data['apellido']:
            profesional.apellido = data['apellido'].strip()
        if 'telefono' in data:
            profesional.telefono = data['telefono'].strip() or None
        if 'email' in data:
            profesional.email = data['email'].strip() or None
        if 'especialidad' in data:
            profesional.especialidad = data['especialidad'].strip() or None
        
        db.session.commit()
        return profesional
    
    @staticmethod
    def eliminar_profesional(id):
        """Eliminar (desactivar) profesional"""
        profesional = ProfesionalService.get_profesional_by_id(id)
        if not profesional:
            return False
        
        # Verificar si tiene turnos pendientes o confirmados
        turnos_activos = Turno.query.filter(
            Turno.profesional_id == id,
            Turno.estado.in_(['pendiente', 'confirmado']),
            Turno.fecha >= date.today()
        ).count()
        
        if turnos_activos > 0:
            raise ValueError('No se puede eliminar un profesional que tiene turnos pendientes o confirmados')
        
        profesional.activo = False
        db.session.commit()
        return True
    
    @staticmethod
    def get_horarios_disponibles(profesional_id, fecha_str, duracion_servicio=60):
        """Obtener horarios disponibles para un profesional en una fecha"""
        if not fecha_str:
            return []
        
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return []
        
        # No permitir fechas pasadas
        if fecha < date.today():
            return []
        
        # Horario de trabajo (esto podría venir de la configuración del profesional)
        hora_inicio = time(9, 0)  # 9:00 AM
        hora_fin = time(18, 0)    # 6:00 PM
        intervalo_minutos = 30    # Intervalos de 30 minutos
        
        # Obtener turnos existentes para esa fecha y profesional
        turnos_ocupados = Turno.query.filter(
            Turno.profesional_id == profesional_id,
            Turno.fecha == fecha,
            Turno.estado.in_(['pendiente', 'confirmado'])
        ).all()
        
        # Generar horarios disponibles
        horarios_disponibles = []
        hora_actual = datetime.combine(fecha, hora_inicio)
        hora_limite = datetime.combine(fecha, hora_fin)
        
        while hora_actual < hora_limite:
            # Verificar si el horario está libre
            horario_libre = True
            
            for turno in turnos_ocupados:
                hora_turno = datetime.combine(fecha, turno.hora)
                # Asumir duración del servicio del turno
                duracion_turno = turno.servicio.duracion if turno.servicio else 60
                hora_fin_turno = hora_turno + timedelta(minutes=duracion_turno)
                
                # Verificar solapamiento
                if (hora_actual < hora_fin_turno and 
                    (hora_actual + timedelta(minutes=duracion_servicio)) > hora_turno):
                    horario_libre = False
                    break
            
            if horario_libre:
                horarios_disponibles.append(hora_actual.time().strftime('%H:%M'))
            
            hora_actual += timedelta(minutes=intervalo_minutos)
        
        return horarios_disponibles
    
    @staticmethod
    def get_turnos_profesional(profesional_id, fecha_desde=None, fecha_hasta=None):
        """Obtener turnos de un profesional en un rango de fechas"""
        query = Turno.query.filter_by(profesional_id=profesional_id)
        
        if fecha_desde:
            try:
                fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                query = query.filter(Turno.fecha >= fecha_desde)
            except ValueError:
                pass
        
        if fecha_hasta:
            try:
                fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                query = query.filter(Turno.fecha <= fecha_hasta)
            except ValueError:
                pass
        
        return query.order_by(Turno.fecha, Turno.hora).all()
    
    @staticmethod
    def get_estadisticas_profesional(profesional_id, mes=None, ano=None):
        """Obtener estadísticas de un profesional"""
        if not mes:
            mes = date.today().month
        if not ano:
            ano = date.today().year
        
        # Filtrar turnos del mes
        turnos = Turno.query.filter(
            Turno.profesional_id == profesional_id,
            db.extract('month', Turno.fecha) == mes,
            db.extract('year', Turno.fecha) == ano
        ).all()
        
        # Calcular estadísticas
        total_turnos = len(turnos)
        turnos_completados = len([t for t in turnos if t.estado == 'completado'])
        turnos_cancelados = len([t for t in turnos if t.estado == 'cancelado'])
        
        ingresos_total = sum([
            float(t.precio_final or t.servicio.precio or 0) 
            for t in turnos if t.estado == 'completado'
        ])
        
        return {
            'total_turnos': total_turnos,
            'turnos_completados': turnos_completados,
            'turnos_cancelados': turnos_cancelados,
            'tasa_completados': (turnos_completados / total_turnos * 100) if total_turnos > 0 else 0,
            'ingresos_total': ingresos_total,
            'promedio_por_turno': (ingresos_total / turnos_completados) if turnos_completados > 0 else 0
        }