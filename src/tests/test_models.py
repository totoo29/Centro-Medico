import pytest
from datetime import date, time
from src.models import Cliente, Categoria, Profesional, Servicio, Turno
from src.database import db

class TestCliente:
    
    def test_crear_cliente(self, app):
        """Test crear cliente básico"""
        with app.app_context():
            cliente = Cliente(
                nombre='Test',
                apellido='Usuario',
                telefono='1234567890',
                email='test@example.com'
            )
            db.session.add(cliente)
            db.session.commit()
            
            assert cliente.id is not None
            assert cliente.nombre == 'Test'
            assert cliente.apellido == 'Usuario'
            assert cliente.activo is True
    
    def test_nombre_completo(self, cliente_ejemplo):
        """Test propiedad nombre_completo"""
        assert cliente_ejemplo.nombre_completo == 'Juan Pérez'
    
    def test_to_dict(self, cliente_ejemplo):
        """Test método to_dict"""
        cliente_dict = cliente_ejemplo.to_dict()
        
        assert 'id' in cliente_dict
        assert cliente_dict['nombre'] == 'Juan'
        assert cliente_dict['apellido'] == 'Pérez'
        assert cliente_dict['activo'] is True

class TestCategoria:
    
    def test_crear_categoria(self, app):
        """Test crear categoría"""
        with app.app_context():
            categoria = Categoria(
                nombre='Test Categoría',
                descripcion='Descripción de prueba'
            )
            db.session.add(categoria)
            db.session.commit()
            
            assert categoria.id is not None
            assert categoria.nombre == 'Test Categoría'
            assert categoria.color == '#007bff'  # Color por defecto
    
    def test_to_dict(self, categoria_ejemplo):
        """Test método to_dict"""
        categoria_dict = categoria_ejemplo.to_dict()
        
        assert 'id' in categoria_dict
        assert categoria_dict['nombre'] == 'Corte de Cabello'
        assert categoria_dict['color'] == '#007bff'

class TestProfesional:
    
    def test_crear_profesional(self, app):
        """Test crear profesional"""
        with app.app_context():
            profesional = Profesional(
                nombre='Test',
                apellido='Profesional',
                especialidad='Test'
            )
            db.session.add(profesional)
            db.session.commit()
            
            assert profesional.id is not None
            assert profesional.nombre == 'Test'
            assert profesional.activo is True
    
    def test_nombre_completo(self, profesional_ejemplo):
        """Test propiedad nombre_completo"""
        assert profesional_ejemplo.nombre_completo == 'María González'

class TestServicio:
    
    def test_crear_servicio(self, app, categoria_ejemplo):
        """Test crear servicio"""
        with app.app_context():
            servicio = Servicio(
                nombre='Test Servicio',
                precio=50.00,
                duracion=45,
                categoria_id=categoria_ejemplo.id
            )
            db.session.add(servicio)
            db.session.commit()
            
            assert servicio.id is not None
            assert servicio.nombre == 'Test Servicio'
            assert float(servicio.precio) == 50.00
    
    def test_precio_formateado(self, servicio_ejemplo):
        """Test propiedad precio_formateado"""
        assert servicio_ejemplo.precio_formateado == '$25.00'
    
    def test_duracion_formateada(self, servicio_ejemplo):
        """Test propiedad duracion_formateada"""
        assert servicio_ejemplo.duracion_formateada == '30min'

class TestTurno:
    
    def test_crear_turno(self, app, cliente_ejemplo, profesional_ejemplo, servicio_ejemplo):
        """Test crear turno"""
        with app.app_context():
            turno = Turno(
                fecha=date(2024, 12, 20),
                hora=time(15, 0),
                cliente_id=cliente_ejemplo.id,
                profesional_id=profesional_ejemplo.id,
                servicio_id=servicio_ejemplo.id
            )
            db.session.add(turno)
            db.session.commit()
            
            assert turno.id is not None
            assert turno.fecha == date(2024, 12, 20)
            assert turno.estado == 'pendiente'  # Estado por defecto
    
    def test_estado_badge_class(self, turno_ejemplo):
        """Test propiedad estado_badge_class"""
        turno_ejemplo.estado = 'confirmado'
        assert turno_ejemplo.estado_badge_class == 'info'
        
        turno_ejemplo.estado = 'completado'
        assert turno_ejemplo.estado_badge_class == 'success'
        
        turno_ejemplo.estado = 'cancelado'
        assert turno_ejemplo.estado_badge_class == 'danger'
    
    def test_to_dict(self, turno_ejemplo):
        """Test método to_dict"""
        turno_dict = turno_ejemplo.to_dict()
        
        assert 'id' in turno_dict
        assert turno_dict['estado'] == 'confirmado'
        assert 'cliente' in turno_dict
        assert 'profesional' in turno_dict
        assert 'servicio' in turno_dict