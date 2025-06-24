import pytest
import tempfile
import os
from src.app import create_app
from src.database import db
from src.models import Cliente, Categoria, Profesional, Servicio, Turno

@pytest.fixture
def app():
    """Fixture para crear la aplicación Flask para testing"""
    # Crear archivo temporal para la base de datos de prueba
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Fixture para crear cliente de testing"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Fixture para crear runner de comandos CLI"""
    return app.test_cli_runner()

@pytest.fixture
def cliente_ejemplo():
    """Fixture para crear un cliente de ejemplo"""
    cliente = Cliente(
        nombre='Juan',
        apellido='Pérez',
        telefono='+541234567890',
        email='juan.perez@example.com'
    )
    db.session.add(cliente)
    db.session.commit()
    return cliente

@pytest.fixture
def categoria_ejemplo():
    """Fixture para crear una categoría de ejemplo"""
    categoria = Categoria(
        nombre='Corte de Cabello',
        descripcion='Servicios de corte y peinado',
        color='#007bff'
    )
    db.session.add(categoria)
    db.session.commit()
    return categoria

@pytest.fixture
def profesional_ejemplo():
    """Fixture para crear un profesional de ejemplo"""
    profesional = Profesional(
        nombre='María',
        apellido='González',
        telefono='+540987654321',
        email='maria.gonzalez@salon.com',
        especialidad='Estilista'
    )
    db.session.add(profesional)
    db.session.commit()
    return profesional

@pytest.fixture
def servicio_ejemplo(categoria_ejemplo):
    """Fixture para crear un servicio de ejemplo"""
    servicio = Servicio(
        nombre='Corte Masculino',
        descripcion='Corte de cabello para hombres',
        precio=25.00,
        duracion=30,
        categoria_id=categoria_ejemplo.id
    )
    db.session.add(servicio)
    db.session.commit()
    return servicio

@pytest.fixture
def turno_ejemplo(cliente_ejemplo, profesional_ejemplo, servicio_ejemplo):
    """Fixture para crear un turno de ejemplo"""
    from datetime import date, time
    
    turno = Turno(
        fecha=date(2024, 12, 15),
        hora=time(14, 30),
        estado='confirmado',
        cliente_id=cliente_ejemplo.id,
        profesional_id=profesional_ejemplo.id,
        servicio_id=servicio_ejemplo.id
    )
    db.session.add(turno)
    db.session.commit()
    return turno