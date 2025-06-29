from src.models import Turno, Cliente, Profesional, Servicio
from src.database import db
from src.utils.validators import validar_fecha, validar_hora, validar_estado_turno, validar_precio
from src.utils.exports import generar_excel, generar_csv
from datetime import datetime, date, time, timedelta
import pandas as pd

class TurnoService:
    
    @staticmethod
    def get_turnos_by_fecha_range(fecha_inicio, fecha_fin, profesional_id=None):
        """Obtener turnos en un rango de fechas"""
        query = Turno.query.filter(
            Turno.fecha >= fecha_inicio,
            Turno.fecha <= fecha_fin
        )
        
        if profesional_id:
            query = query.filter(Turno.profesional_id == profesional_id)
        
        return query.order_by(Turno.fecha, Turno.hora).all()

    @staticmethod
    def organizar_turnos_por_fecha(turnos):
        """Organizar lista de turnos por fecha"""
        turnos_por_fecha = {}
        
        for turno in turnos:
            fecha_str = turno.fecha.isoformat()
            if fecha_str not in turnos_por_fecha:
                turnos_por_fecha[fecha_str] = []
            
            turnos_por_fecha[fecha_str].append({
                'id': turno.id,
                'hora': turno.hora.strftime('%H:%M'),
                'cliente': turno.cliente.nombre_completo,
                'profesional': turno.profesional.nombre_completo,
                'servicio': turno.servicio.nombre,
                'estado': turno.estado,
                'duracion': turno.servicio.duracion,
                'precio': float(turno.precio_final or turno.servicio.precio or 0)
            })
        
        return turnos_por_fecha

    @staticmethod
    def calcular_estadisticas_periodo(turnos):
        """Calcular estadísticas para un período de turnos"""
        if not turnos:
            return {
                'total_turnos': 0,
                'pendientes': 0,
                'confirmados': 0,
                'completados': 0,
                'cancelados': 0,
                'ingresos_total': 0
            }
        
        estadisticas = {
            'total_turnos': len(turnos),
            'pendientes': sum(1 for t in turnos if t.estado == 'pendiente'),
            'confirmados': sum(1 for t in turnos if t.estado == 'confirmado'),
            'completados': sum(1 for t in turnos if t.estado == 'completado'),
            'cancelados': sum(1 for t in turnos if t.estado == 'cancelado'),
            'ingresos_total': sum(
                float(t.precio_final or t.servicio.precio or 0) 
                for t in turnos if t.estado == 'completado'
            )
        }
        
        return estadisticas

    @staticmethod
    def verificar_disponibilidad_extendida(profesional_id, fecha, hora, duracion, excluir_turno_id=None):
        """Verificación de disponibilidad más robusta"""
        from datetime import datetime, timedelta
        
        # Buscar turnos que se solapen
        query = Turno.query.filter(
            Turno.profesional_id == profesional_id,
            Turno.fecha == fecha,
            Turno.estado.in_(['pendiente', 'confirmado'])
        )
        
        if excluir_turno_id:
            query = query.filter(Turno.id != excluir_turno_id)
        
        turnos_existentes = query.all()
        
        # Convertir hora a datetime para facilitar cálculos
        if isinstance(hora, str):
            hora_obj = datetime.strptime(hora, '%H:%M').time()
        else:
            hora_obj = hora
        
        inicio_nuevo = datetime.combine(fecha, hora_obj)
        fin_nuevo = inicio_nuevo + timedelta(minutes=duracion)
        
        for turno in turnos_existentes:
            inicio_existente = datetime.combine(fecha, turno.hora)
            fin_existente = inicio_existente + timedelta(minutes=turno.servicio.duracion)
            
            # Verificar solapamiento
            if inicio_nuevo < fin_existente and fin_nuevo > inicio_existente:
                return False
        
        return True

    @staticmethod
    def get_horarios_disponibles_mejorado(profesional_id, fecha, servicio_id=None):
        """Obtener horarios disponibles mejorado para el calendario"""
        from datetime import datetime, time, timedelta
        
        if isinstance(fecha, str):
            try:
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            except ValueError:
                return []
        else:
            fecha_obj = fecha
        
        # No permitir fechas pasadas
        if fecha_obj < date.today():
            return []
        
        # Obtener duración del servicio
        duracion = 60  # Por defecto 60 minutos
        if servicio_id:
            servicio = Servicio.query.get(servicio_id)
            if servicio:
                duracion = servicio.duracion
        
        # Verificar que el profesional existe
        profesional = Profesional.query.get(profesional_id)
        if not profesional:
            return []
        
        # Configuración de horarios (esto podría venir de configuración del profesional)
        # Horarios típicos de consultorio médico
        horarios_trabajo = {
            'lunes': {'inicio': time(8, 0), 'fin': time(18, 0)},
            'martes': {'inicio': time(8, 0), 'fin': time(18, 0)},
            'miercoles': {'inicio': time(8, 0), 'fin': time(18, 0)},
            'jueves': {'inicio': time(8, 0), 'fin': time(18, 0)},
            'viernes': {'inicio': time(8, 0), 'fin': time(18, 0)},
            'sabado': {'inicio': time(9, 0), 'fin': time(13, 0)},
            'domingo': None  # No trabaja domingos
        }
        
        dias_semana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        dia_actual = dias_semana[fecha_obj.weekday()]
        
        # Verificar si trabaja ese día
        horario_dia = horarios_trabajo.get(dia_actual)
        if not horario_dia:
            return []
        
        hora_inicio = horario_dia['inicio']
        hora_fin = horario_dia['fin']
        intervalo = 30  # Intervalos de 30 minutos
        
        # Obtener turnos ocupados para esa fecha y profesional
        turnos_ocupados = Turno.query.filter(
            Turno.profesional_id == profesional_id,
            Turno.fecha == fecha_obj,
            Turno.estado.in_(['pendiente', 'confirmado'])
        ).all()
        
        # Generar horarios disponibles
        horarios_disponibles = []
        hora_actual = datetime.combine(fecha_obj, hora_inicio)
        hora_limite = datetime.combine(fecha_obj, hora_fin)
        
        while hora_actual + timedelta(minutes=duracion) <= hora_limite:
            # Verificar si hay conflicto con algún turno existente
            disponible = True
            
            for turno in turnos_ocupados:
                inicio_turno = datetime.combine(fecha_obj, turno.hora)
                fin_turno = inicio_turno + timedelta(minutes=turno.servicio.duracion)
                fin_nuevo_turno = hora_actual + timedelta(minutes=duracion)
                
                # Verificar solapamiento
                if hora_actual < fin_turno and fin_nuevo_turno > inicio_turno:
                    disponible = False
                    break
            
            if disponible:
                horarios_disponibles.append(hora_actual.time().strftime('%H:%M'))
            
            hora_actual += timedelta(minutes=intervalo)
        
        return horarios_disponibles

    @staticmethod
    def crear_turno_validado(data):
        """Crear turno con validaciones extendidas"""
        # Validaciones básicas
        required_fields = ['fecha', 'hora', 'cliente_id', 'profesional_id', 'servicio_id']
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f'{field} es obligatorio')
        
        # Convertir y validar fecha
        try:
            if isinstance(data['fecha'], str):
                fecha_turno = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
            else:
                fecha_turno = data['fecha']
        except ValueError:
            raise ValueError('Formato de fecha inválido (use YYYY-MM-DD)')
        
        # Convertir y validar hora
        try:
            if isinstance(data['hora'], str):
                hora_turno = datetime.strptime(data['hora'], '%H:%M').time()
            else:
                hora_turno = data['hora']
        except ValueError:
            raise ValueError('Formato de hora inválido (use HH:MM)')
        
        # No permitir turnos en el pasado
        fecha_hora_turno = datetime.combine(fecha_turno, hora_turno)
        if fecha_hora_turno < datetime.now():
            raise ValueError('No se pueden crear turnos en el pasado')
        
        # Verificar que existan los registros relacionados
        cliente = Cliente.query.filter_by(id=data['cliente_id'], activo=True).first()
        if not cliente:
            raise ValueError('Cliente no encontrado o inactivo')
        
        profesional = Profesional.query.filter_by(id=data['profesional_id'], activo=True).first()
        if not profesional:
            raise ValueError('Profesional no encontrado o inactivo')
        
        servicio = Servicio.query.filter_by(id=data['servicio_id'], activo=True).first()
        if not servicio:
            raise ValueError('Servicio no encontrado o inactivo')
        
        # Verificar disponibilidad del profesional
        if not TurnoService.verificar_disponibilidad_extendida(
            data['profesional_id'], fecha_turno, hora_turno, servicio.duracion
        ):
            raise ValueError('El profesional no está disponible en ese horario')
        
        # Validar estado
        estado = data.get('estado', 'pendiente')
        estados_validos = ['pendiente', 'confirmado', 'completado', 'cancelado']
        if estado not in estados_validos:
            raise ValueError(f'Estado debe ser uno de: {", ".join(estados_validos)}')
        
        # Validar precio final si se proporciona
        precio_final = data.get('precio_final')
        if precio_final:
            try:
                precio_final = float(precio_final)
                if precio_final < 0:
                    raise ValueError('El precio no puede ser negativo')
            except (ValueError, TypeError):
                raise ValueError('Precio final debe ser un número válido')
        
        # Crear turno
        turno = Turno(
            fecha=fecha_turno,
            hora=hora_turno,
            estado=estado,
            observaciones=data.get('observaciones', '').strip() or None,
            precio_final=precio_final,
            cliente_id=data['cliente_id'],
            profesional_id=data['profesional_id'],
            servicio_id=data['servicio_id']
        )
        
        try:
            db.session.add(turno)
            db.session.commit()
            return turno
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'Error al guardar el turno: {str(e)}')

    @staticmethod
    def get_calendario_data(vista, fecha_base, profesional_id=None):
        """Obtener datos estructurados para el calendario"""
        from datetime import timedelta
        import calendar
        
        if vista == 'dia':
            fecha_inicio = fecha_base
            fecha_fin = fecha_base
            titulo = fecha_base.strftime('%A, %d de %B de %Y')
        elif vista == 'semana':
            # Encontrar el lunes de la semana
            dias_desde_lunes = fecha_base.weekday()
            fecha_inicio = fecha_base - timedelta(days=dias_desde_lunes)
            fecha_fin = fecha_inicio + timedelta(days=6)
            titulo = f"Semana del {fecha_inicio.strftime('%d/%m')} al {fecha_fin.strftime('%d/%m/%Y')}"
        else:  # mes
            fecha_inicio = fecha_base.replace(day=1)
            if fecha_base.month == 12:
                siguiente_mes = fecha_base.replace(year=fecha_base.year + 1, month=1)
            else:
                siguiente_mes = fecha_base.replace(month=fecha_base.month + 1)
            fecha_fin = siguiente_mes - timedelta(days=1)
            titulo = fecha_base.strftime('%B %Y')
        
        # Obtener turnos
        turnos = TurnoService.get_turnos_by_fecha_range(fecha_inicio, fecha_fin, profesional_id)
        turnos_por_fecha = TurnoService.organizar_turnos_por_fecha(turnos)
        estadisticas = TurnoService.calcular_estadisticas_periodo(turnos)
        
        # Generar estructura específica según la vista
        fechas = []
        semanas = []
        
        if vista == 'dia':
            fechas = [fecha_base]
        elif vista == 'semana':
            fechas = [fecha_inicio + timedelta(days=i) for i in range(7)]
        else:  # mes
            # Generar calendario mensual
            primer_dia = fecha_base.replace(day=1)
            ultimo_dia = fecha_fin
            
            # Encontrar el primer día del calendario (lunes anterior o igual)
            dias_desde_lunes = primer_dia.weekday()
            inicio_calendario = primer_dia - timedelta(days=dias_desde_lunes)
            
            fecha_actual = inicio_calendario
            while fecha_actual <= ultimo_dia or len(semanas) == 0:
                semana = []
                for i in range(7):
                    dia_actual = fecha_actual + timedelta(days=i)
                    semana.append({
                        'fecha': dia_actual,
                        'es_mes_actual': dia_actual.month == fecha_base.month,
                        'turnos': turnos_por_fecha.get(dia_actual.isoformat(), [])
                    })
                semanas.append(semana)
                fecha_actual += timedelta(days=7)
                
                # Evitar bucle infinito - máximo 6 semanas
                if len(semanas) >= 6:
                    break
        
        return {
            'vista': vista,
            'titulo': titulo,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'fechas': fechas,
            'semanas': semanas,
            'horarios': list(range(8, 20)),  # 8:00 a 19:00
            'turnos_por_fecha': turnos_por_fecha,
            'estadisticas': estadisticas
        }
    
    @staticmethod
    def get_all_turnos():
        """Obtener todos los turnos"""
        return Turno.query.order_by(Turno.fecha.desc(), Turno.hora.desc()).all()
    
    @staticmethod
    def get_turno_by_id(id):
        """Obtener turno por ID"""
        return Turno.query.get(id)
    
    @staticmethod
    def get_paginated_turnos(page=1, per_page=10, fecha_desde=None, fecha_hasta=None, 
                           estado=None, profesional_id=None):
        """Obtener turnos con paginación y filtros"""
        query = Turno.query
        
        # Filtros
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
        
        if estado:
            query = query.filter(Turno.estado == estado)
        
        if profesional_id:
            query = query.filter(Turno.profesional_id == profesional_id)
        
        return query.order_by(Turno.fecha.desc(), Turno.hora.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def get_turnos_by_fecha(fecha_str, profesional_id=None):
        """Obtener turnos por fecha"""
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return []
        
        query = Turno.query.filter_by(fecha=fecha)
        
        if profesional_id:
            query = query.filter_by(profesional_id=profesional_id)
        
        return query.order_by(Turno.hora).all()
    
    @staticmethod
    def crear_turno(data):
        """Crear nuevo turno"""
        # Validaciones básicas
        required_fields = ['fecha', 'hora', 'cliente_id', 'profesional_id', 'servicio_id']
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f'{field} es obligatorio')
        
        # Validar fecha y hora
        if not validar_fecha(data['fecha']):
            raise ValueError('Fecha no válida')
        
        if not validar_hora(data['hora']):
            raise ValueError('Hora no válida')
        
        fecha_turno = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        hora_turno = datetime.strptime(data['hora'], '%H:%M').time()
        
        # No permitir turnos en el pasado
        fecha_hora_turno = datetime.combine(fecha_turno, hora_turno)
        if fecha_hora_turno < datetime.now():
            raise ValueError('No se pueden crear turnos en el pasado')
        
        # Verificar que existan los registros relacionados
        cliente = Cliente.query.filter_by(id=data['cliente_id'], activo=True).first()
        if not cliente:
            raise ValueError('Cliente no encontrado')
        
        profesional = Profesional.query.filter_by(id=data['profesional_id'], activo=True).first()
        if not profesional:
            raise ValueError('Profesional no encontrado')
        
        servicio = Servicio.query.filter_by(id=data['servicio_id'], activo=True).first()
        if not servicio:
            raise ValueError('Servicio no encontrado')
        
        # Verificar disponibilidad del profesional
        if not TurnoService._verificar_disponibilidad(
            data['profesional_id'], fecha_turno, hora_turno, servicio.duracion
        ):
            raise ValueError('El profesional no está disponible en ese horario')
        
        # Validar estado si se proporciona
        estado = data.get('estado', 'pendiente')
        if not validar_estado_turno(estado):
            raise ValueError('Estado no válido')
        
        # Validar precio final si se proporciona
        precio_final = data.get('precio_final')
        if precio_final and not validar_precio(precio_final):
            raise ValueError('Precio final no válido')
        
        # Crear turno
        turno = Turno(
            fecha=fecha_turno,
            hora=hora_turno,
            estado=estado,
            observaciones=data.get('observaciones', '').strip() or None,
            precio_final=float(precio_final) if precio_final else None,
            cliente_id=data['cliente_id'],
            profesional_id=data['profesional_id'],
            servicio_id=data['servicio_id']
        )
        
        db.session.add(turno)
        db.session.commit()
        
        return turno
    
    @staticmethod
    def actualizar_turno(id, data):
        """Actualizar turno existente"""
        turno = TurnoService.get_turno_by_id(id)
        if not turno:
            return None
        
        # Validaciones de fecha y hora si se actualizan
        if 'fecha' in data and data['fecha']:
            if not validar_fecha(data['fecha']):
                raise ValueError('Fecha no válida')
            
            nueva_fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
            hora_actual = turno.hora
            
            if 'hora' in data and data['hora']:
                if not validar_hora(data['hora']):
                    raise ValueError('Hora no válida')
                hora_actual = datetime.strptime(data['hora'], '%H:%M').time()
            
            # Verificar que no sea en el pasado
            fecha_hora_nueva = datetime.combine(nueva_fecha, hora_actual)
            if fecha_hora_nueva < datetime.now():
                raise ValueError('No se pueden programar turnos en el pasado')
        
        # Verificar disponibilidad si se cambia fecha, hora o profesional
        if any(key in data for key in ['fecha', 'hora', 'profesional_id']):
            fecha_check = data.get('fecha', turno.fecha.isoformat())
            hora_check = data.get('hora', turno.hora.strftime('%H:%M'))
            profesional_check = data.get('profesional_id', turno.profesional_id)
            
            fecha_obj = datetime.strptime(fecha_check, '%Y-%m-%d').date()
            hora_obj = datetime.strptime(hora_check, '%H:%M').time()
            
            if not TurnoService._verificar_disponibilidad(
                profesional_check, fecha_obj, hora_obj, 
                turno.servicio.duracion, turno.id
            ):
                raise ValueError('El profesional no está disponible en ese horario')
        
        # Validar estado si se actualiza
        if 'estado' in data and data['estado']:
            if not validar_estado_turno(data['estado']):
                raise ValueError('Estado no válido')
        
        # Validar precio final si se actualiza
        if 'precio_final' in data and data['precio_final']:
            if not validar_precio(data['precio_final']):
                raise ValueError('Precio final no válido')
        
        # Actualizar campos
        if 'fecha' in data and data['fecha']:
            turno.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        
        if 'hora' in data and data['hora']:
            turno.hora = datetime.strptime(data['hora'], '%H:%M').time()
        
        if 'estado' in data and data['estado']:
            turno.estado = data['estado']
        
        if 'observaciones' in data:
            turno.observaciones = data['observaciones'].strip() or None
        
        if 'precio_final' in data:
            turno.precio_final = float(data['precio_final']) if data['precio_final'] else None
        
        if 'cliente_id' in data and data['cliente_id']:
            cliente = Cliente.query.filter_by(id=data['cliente_id'], activo=True).first()
            if not cliente:
                raise ValueError('Cliente no encontrado')
            turno.cliente_id = data['cliente_id']
        
        if 'profesional_id' in data and data['profesional_id']:
            profesional = Profesional.query.filter_by(id=data['profesional_id'], activo=True).first()
            if not profesional:
                raise ValueError('Profesional no encontrado')
            turno.profesional_id = data['profesional_id']
        
        if 'servicio_id' in data and data['servicio_id']:
            servicio = Servicio.query.filter_by(id=data['servicio_id'], activo=True).first()
            if not servicio:
                raise ValueError('Servicio no encontrado')
            turno.servicio_id = data['servicio_id']
        
        db.session.commit()
        return turno
    
    @staticmethod
    def cambiar_estado_turno(id, nuevo_estado):
        """Cambiar estado de un turno"""
        turno = TurnoService.get_turno_by_id(id)
        if not turno:
            return None
        
        if not validar_estado_turno(nuevo_estado):
            raise ValueError('Estado no válido')
        
        turno.estado = nuevo_estado
        db.session.commit()
        
        return turno
    
    @staticmethod
    def cancelar_turno(id, motivo=''):
        """Cancelar un turno"""
        turno = TurnoService.get_turno_by_id(id)
        if not turno:
            return None
        
        turno.estado = 'cancelado'
        if motivo:
            turno.observaciones = f"Cancelado: {motivo}"
        
        db.session.commit()
        return turno
    
    @staticmethod
    def get_horarios_disponibles(fecha_str, profesional_id, servicio_id=None):
        """Obtener horarios disponibles para un profesional en una fecha"""
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return []
        
        # No permitir fechas pasadas
        if fecha < date.today():
            return []
        
        # Obtener duración del servicio
        duracion = 60  # Por defecto 60 minutos
        if servicio_id:
            servicio = Servicio.query.get(servicio_id)
            if servicio:
                duracion = servicio.duracion
        
        # Horario de trabajo (configuración básica)
        hora_inicio = time(9, 0)
        hora_fin = time(18, 0)
        intervalo = 30  # minutos
        
        # Obtener turnos ocupados
        turnos_ocupados = Turno.query.filter(
            Turno.profesional_id == profesional_id,
            Turno.fecha == fecha,
            Turno.estado.in_(['pendiente', 'confirmado'])
        ).all()
        
        horarios_disponibles = []
        hora_actual = datetime.combine(fecha, hora_inicio)
        hora_limite = datetime.combine(fecha, hora_fin)
        
        while hora_actual + timedelta(minutes=duracion) <= hora_limite:
            # Verificar solapamiento con turnos existentes
            disponible = True
            
            for turno in turnos_ocupados:
                inicio_turno = datetime.combine(fecha, turno.hora)
                fin_turno = inicio_turno + timedelta(minutes=turno.servicio.duracion)
                fin_nuevo = hora_actual + timedelta(minutes=duracion)
                
                if hora_actual < fin_turno and fin_nuevo > inicio_turno:
                    disponible = False
                    break
            
            if disponible:
                horarios_disponibles.append(hora_actual.time().strftime('%H:%M'))
            
            hora_actual += timedelta(minutes=intervalo)
        
        return horarios_disponibles
    
    @staticmethod
    def get_resumen_dia(fecha_str, profesional_id=None):
        """Obtener resumen de turnos del día"""
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return {}
        
        query = Turno.query.filter_by(fecha=fecha)
        if profesional_id:
            query = query.filter_by(profesional_id=profesional_id)
        
        turnos = query.all()
        
        return {
            'fecha': fecha.isoformat(),
            'total_turnos': len(turnos),
            'pendientes': len([t for t in turnos if t.estado == 'pendiente']),
            'confirmados': len([t for t in turnos if t.estado == 'confirmado']),
            'completados': len([t for t in turnos if t.estado == 'completado']),
            'cancelados': len([t for t in turnos if t.estado == 'cancelado']),
            'ingresos': sum([
                float(t.precio_final or t.servicio.precio or 0) 
                for t in turnos if t.estado == 'completado'
            ])
        }
    
    @staticmethod
    def get_proximos_turnos(limite=5, profesional_id=None):
        """Obtener próximos turnos"""
        query = Turno.query.filter(
            Turno.fecha >= date.today(),
            Turno.estado.in_(['pendiente', 'confirmado'])
        )
        
        if profesional_id:
            query = query.filter_by(profesional_id=profesional_id)
        
        return query.order_by(Turno.fecha, Turno.hora).limit(limite).all()
    
    @staticmethod
    def _verificar_disponibilidad(profesional_id, fecha, hora, duracion, excluir_turno_id=None):
        """Verificar si un profesional está disponible en un horario"""
        # Buscar turnos que se solapen
        query = Turno.query.filter(
            Turno.profesional_id == profesional_id,
            Turno.fecha == fecha,
            Turno.estado.in_(['pendiente', 'confirmado'])
        )
        
        if excluir_turno_id:
            query = query.filter(Turno.id != excluir_turno_id)
        
        turnos_existentes = query.all()
        
        inicio_nuevo = datetime.combine(fecha, hora)
        fin_nuevo = inicio_nuevo + timedelta(minutes=duracion)
        
        for turno in turnos_existentes:
            inicio_existente = datetime.combine(fecha, turno.hora)
            fin_existente = inicio_existente + timedelta(minutes=turno.servicio.duracion)
            
            # Verificar solapamiento
            if inicio_nuevo < fin_existente and fin_nuevo > inicio_existente:
                return False
        
        return True
    
    @staticmethod
    def exportar_excel(fecha_desde=None, fecha_hasta=None):
        """Exportar turnos a Excel"""
        query = Turno.query
        
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
        
        turnos = query.order_by(Turno.fecha, Turno.hora).all()
        
        data = []
        for turno in turnos:
            data.append({
                'ID': turno.id,
                'Fecha': turno.fecha.strftime('%d/%m/%Y'),
                'Hora': turno.hora.strftime('%H:%M'),
                'Cliente': turno.cliente.nombre_completo,
                'Profesional': turno.profesional.nombre_completo,
                'Servicio': turno.servicio.nombre,
                'Estado': turno.estado.title(),
                'Precio': f'${float(turno.precio_final or turno.servicio.precio):,.2f}',
                'Observaciones': turno.observaciones or ''
            })
        
        filename = f'turnos_{date.today().strftime("%Y%m%d")}'
        return generar_excel(data, filename, 'Turnos')
    
    @staticmethod
    def exportar_csv(fecha_desde=None, fecha_hasta=None):
        """Exportar turnos a CSV"""
        query = Turno.query
        
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
        
        turnos = query.order_by(Turno.fecha, Turno.hora).all()
        
        data = []
        for turno in turnos:
            data.append({
                'ID': turno.id,
                'Fecha': turno.fecha.strftime('%d/%m/%Y'),
                'Hora': turno.hora.strftime('%H:%M'),
                'Cliente': turno.cliente.nombre_completo,
                'Profesional': turno.profesional.nombre_completo,
                'Servicio': turno.servicio.nombre,
                'Estado': turno.estado.title(),
                'Precio': float(turno.precio_final or turno.servicio.precio),
                'Observaciones': turno.observaciones or ''
            })
        
        filename = f'turnos_{date.today().strftime("%Y%m%d")}'
        return generar_csv(data, filename)
    
    @staticmethod
    def get_turnos_by_fecha_range(fecha_inicio, fecha_fin, profesional_id=None):
        """Obtener turnos en un rango de fechas"""
        query = Turno.query.filter(
            Turno.fecha >= fecha_inicio,
            Turno.fecha <= fecha_fin
        )
        
        if profesional_id:
            query = query.filter(Turno.profesional_id == profesional_id)
        
        return query.order_by(Turno.fecha, Turno.hora).all()

    @staticmethod
    def organizar_turnos_por_fecha(turnos):
        """Organizar lista de turnos por fecha"""
        turnos_por_fecha = {}
        
        for turno in turnos:
            fecha_str = turno.fecha.isoformat()
            if fecha_str not in turnos_por_fecha:
                turnos_por_fecha[fecha_str] = []
            
            turnos_por_fecha[fecha_str].append({
                'id': turno.id,
                'hora': turno.hora.strftime('%H:%M'),
                'cliente': turno.cliente.nombre_completo,
                'profesional': turno.profesional.nombre_completo,
                'servicio': turno.servicio.nombre,
                'estado': turno.estado,
                'duracion': turno.servicio.duracion,
                'precio': float(turno.precio_final or turno.servicio.precio or 0)
            })
        
        return turnos_por_fecha

    @staticmethod
    def calcular_estadisticas_periodo(turnos):
        """Calcular estadísticas para un período de turnos"""
        if not turnos:
            return {
                'total_turnos': 0,
                'pendientes': 0,
                'confirmados': 0,
                'completados': 0,
                'cancelados': 0,
                'ingresos_total': 0
            }
        
        estadisticas = {
            'total_turnos': len(turnos),
            'pendientes': sum(1 for t in turnos if t.estado == 'pendiente'),
            'confirmados': sum(1 for t in turnos if t.estado == 'confirmado'),
            'completados': sum(1 for t in turnos if t.estado == 'completado'),
            'cancelados': sum(1 for t in turnos if t.estado == 'cancelado'),
            'ingresos_total': sum(
                float(t.precio_final or t.servicio.precio or 0) 
                for t in turnos if t.estado == 'completado'
            )
        }
        
        return estadisticas