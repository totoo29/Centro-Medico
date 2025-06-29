"""
Punto de entrada principal para la aplicación Flask
Sistema de Gestión de Consultorio Médico con Autenticación
"""

import os
import sys
from flask import render_template, Flask
import click
from flask import Flask
from src.database import db
from src.models import Usuario

# Agregar el directorio actual al path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import db
from src.models import Cliente, Categoria, Profesional, Servicio, Turno
from src.models.usuario import Usuario
from src.app import create_app

# Crear la aplicación Flask
app = create_app()

@app.shell_context_processor
def make_shell_context():
    """
    Registra variables que estarán disponibles en el shell de Flask
    Útil para debugging y testing desde la consola
    """
    return {
        'db': db,
        'Cliente': Cliente,
        'Categoria': Categoria,
        'Profesional': Profesional,
        'Servicio': Servicio,
        'Turno': Turno,
        'Usuario': Usuario
    }

@app.cli.command()
def init_db():
    """
    Comando CLI para inicializar la base de datos
    Uso: flask init-db
    """
    db.create_all()
    print("✅ Base de datos inicializada correctamente")

@app.cli.command()
def create_admin():
    """
    Comando CLI para crear usuario administrador
    Uso: flask create-admin
    """
    try:
        # Verificar si ya existe un admin
        admin_existente = Usuario.query.filter_by(rol='admin').first()
        if admin_existente:
            print(f"⚠️ Ya existe un usuario administrador: {admin_existente.username}")
            respuesta = input("¿Desea crear otro usuario admin? (y/N): ")
            if respuesta.lower() != 'y':
                return
        
        print("🔧 Creando usuario administrador...")
        print("Por favor, complete la siguiente información:")
        
        # Solicitar datos
        username = input("Nombre de usuario: ").strip()
        while not username or Usuario.query.filter_by(username=username).first():
            if not username:
                print("❌ El nombre de usuario no puede estar vacío")
            else:
                print("❌ El nombre de usuario ya existe")
            username = input("Nombre de usuario: ").strip()
        
        email = input("Email: ").strip()
        while not email or Usuario.query.filter_by(email=email).first():
            if not email:
                print("❌ El email no puede estar vacío")
            else:
                print("❌ El email ya está registrado")
            email = input("Email: ").strip()
        
        nombre = input("Nombre: ").strip()
        while not nombre:
            print("❌ El nombre no puede estar vacío")
            nombre = input("Nombre: ").strip()
        
        apellido = input("Apellido: ").strip()
        while not apellido:
            print("❌ El apellido no puede estar vacío")
            apellido = input("Apellido: ").strip()
        
        import getpass
        password = getpass.getpass("Contraseña (mínimo 6 caracteres): ")
        while len(password) < 6:
            print("❌ La contraseña debe tener al menos 6 caracteres")
            password = getpass.getpass("Contraseña (mínimo 6 caracteres): ")
        
        # Crear usuario administrador
        admin = Usuario(
            username=username,
            email=email,
            nombre=nombre,
            apellido=apellido,
            rol='admin'
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"✅ Usuario administrador creado exitosamente!")
        print(f"   👤 Usuario: {username}")
        print(f"   📧 Email: {email}")
        print(f"   🏥 Nombre: {nombre} {apellido}")
        print(f"   🔑 Rol: Administrador")
        print(f"\n🚀 Ya puedes iniciar sesión en: http://localhost:5000")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al crear usuario administrador: {str(e)}")

@app.cli.command()
def create_user():
    """
    Comando CLI para crear un usuario normal
    Uso: flask create-user
    """
    try:
        print("👤 Creando nuevo usuario...")
        
        username = input("Nombre de usuario: ").strip()
        while not username or Usuario.query.filter_by(username=username).first():
            if not username:
                print("❌ El nombre de usuario no puede estar vacío")
            else:
                print("❌ El nombre de usuario ya existe")
            username = input("Nombre de usuario: ").strip()
        
        email = input("Email: ").strip()
        while not email or Usuario.query.filter_by(email=email).first():
            if not email:
                print("❌ El email no puede estar vacío")
            else:
                print("❌ El email ya está registrado")
            email = input("Email: ").strip()
        
        nombre = input("Nombre: ").strip()
        apellido = input("Apellido: ").strip()
        
        print("\nRoles disponibles:")
        print("1. usuario - Usuario normal")
        print("2. medico - Médico")
        print("3. admin - Administrador")
        
        rol_opcion = input("Seleccione rol (1-3) [1]: ").strip() or "1"
        roles = {"1": "usuario", "2": "medico", "3": "admin"}
        rol = roles.get(rol_opcion, "usuario")
        
        import getpass
        password = getpass.getpass("Contraseña: ")
        while len(password) < 6:
            print("❌ La contraseña debe tener al menos 6 caracteres")
            password = getpass.getpass("Contraseña: ")
        
        # Crear usuario
        usuario = Usuario(
            username=username,
            email=email,
            nombre=nombre,
            apellido=apellido,
            rol=rol
        )
        usuario.set_password(password)
        
        db.session.add(usuario)
        db.session.commit()
        
        print(f"✅ Usuario creado exitosamente!")
        print(f"   👤 Usuario: {username}")
        print(f"   🔑 Rol: {rol}")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al crear usuario: {str(e)}")

@app.cli.command()
def list_users():
    """
    Comando CLI para listar usuarios
    Uso: flask list-users
    """
    usuarios = Usuario.query.filter_by(activo=True).order_by(Usuario.fecha_creacion.desc()).all()
    
    if not usuarios:
        print("📭 No hay usuarios registrados")
        return
    
    print(f"👥 Usuarios registrados ({len(usuarios)}):")
    print("-" * 80)
    print(f"{'ID':<4} {'Usuario':<15} {'Nombre':<25} {'Rol':<10} {'Último Login':<20}")
    print("-" * 80)
    
    for usuario in usuarios:
        ultimo_login = usuario.ultimo_login.strftime('%d/%m/%Y %H:%M') if usuario.ultimo_login else 'Nunca'
        print(f"{usuario.id:<4} {usuario.username:<15} {usuario.nombre_completo:<25} {usuario.rol:<10} {ultimo_login:<20}")

@app.cli.command()
def create_sample_data():
    """
    Comando CLI para crear datos de ejemplo
    Uso: flask create-sample-data
    """
    try:
        # Crear categorías de ejemplo para consultorio médico
        categorias = [
            {'nombre': 'Consultas Generales', 'descripcion': 'Consultas médicas generales y chequeos', 'color': '#007bff'},
            {'nombre': 'Especialidades', 'descripcion': 'Consultas con médicos especialistas', 'color': '#28a745'},
            {'nombre': 'Estudios y Análisis', 'descripcion': 'Laboratorio y estudios médicos', 'color': '#ffc107'},
            {'nombre': 'Procedimientos', 'descripcion': 'Procedimientos médicos menores', 'color': '#dc3545'},
            {'nombre': 'Controles', 'descripcion': 'Controles y seguimientos', 'color': '#6f42c1'}
        ]
        
        for cat_data in categorias:
            categoria = Categoria(**cat_data)
            db.session.add(categoria)
        
        db.session.commit()
        print("✅ Categorías de ejemplo creadas")
        
        # Crear profesionales médicos de ejemplo
        profesionales = [
            {
                'nombre': 'Dr. Carlos',
                'apellido': 'Mendoza',
                'telefono': '+541234567890',
                'email': 'carlos.mendoza@consultorio.com',
                'especialidad': 'Médico Clínico'
            },
            {
                'nombre': 'Dra. Ana',
                'apellido': 'García',
                'telefono': '+541234567891',
                'email': 'ana.garcia@consultorio.com',
                'especialidad': 'Cardióloga'
            },
            {
                'nombre': 'Dr. Luis',
                'apellido': 'Rodríguez',
                'telefono': '+541234567892',
                'email': 'luis.rodriguez@consultorio.com',
                'especialidad': 'Traumatólogo'
            },
            {
                'nombre': 'Dra. María',
                'apellido': 'López',
                'telefono': '+541234567893',
                'email': 'maria.lopez@consultorio.com',
                'especialidad': 'Dermatóloga'
            }
        ]
        
        for prof_data in profesionales:
            profesional = Profesional(**prof_data)
            db.session.add(profesional)
        
        db.session.commit()
        print("✅ Profesionales de ejemplo creados")
        
        # Crear servicios médicos de ejemplo
        categoria_generales = Categoria.query.filter_by(nombre='Consultas Generales').first()
        categoria_especialidades = Categoria.query.filter_by(nombre='Especialidades').first()
        categoria_estudios = Categoria.query.filter_by(nombre='Estudios y Análisis').first()
        categoria_procedimientos = Categoria.query.filter_by(nombre='Procedimientos').first()
        categoria_controles = Categoria.query.filter_by(nombre='Controles').first()
        
        servicios = [
            {
                'nombre': 'Consulta Médica General',
                'descripcion': 'Consulta médica clínica general',
                'precio': 5000.00,
                'duracion': 30,
                'categoria_id': categoria_generales.id
            },
            {
                'nombre': 'Consulta Cardiológica',
                'descripcion': 'Consulta con especialista en cardiología',
                'precio': 8000.00,
                'duracion': 45,
                'categoria_id': categoria_especialidades.id
            },
            {
                'nombre': 'Consulta Traumatológica',
                'descripcion': 'Consulta con especialista en traumatología',
                'precio': 7500.00,
                'duracion': 40,
                'categoria_id': categoria_especialidades.id
            },
            {
                'nombre': 'Consulta Dermatológica',
                'descripcion': 'Consulta con especialista en dermatología',
                'precio': 7000.00,
                'duracion': 35,
                'categoria_id': categoria_especialidades.id
            },
            {
                'nombre': 'Análisis de Sangre',
                'descripcion': 'Extracción y análisis de sangre completo',
                'precio': 2500.00,
                'duracion': 15,
                'categoria_id': categoria_estudios.id
            },
            {
                'nombre': 'Electrocardiograma',
                'descripcion': 'Estudio cardiológico ECG',
                'precio': 3000.00,
                'duracion': 20,
                'categoria_id': categoria_estudios.id
            },
            {
                'nombre': 'Control de Presión',
                'descripcion': 'Control y seguimiento de presión arterial',
                'precio': 1500.00,
                'duracion': 15,
                'categoria_id': categoria_controles.id
            },
            {
                'nombre': 'Curación',
                'descripcion': 'Curación de heridas y procedimientos menores',
                'precio': 2000.00,
                'duracion': 20,
                'categoria_id': categoria_procedimientos.id
            },
            {
                'nombre': 'Inyección Intramuscular',
                'descripcion': 'Aplicación de inyecciones intramusculares',
                'precio': 1000.00,
                'duracion': 10,
                'categoria_id': categoria_procedimientos.id
            },
            {
                'nombre': 'Control Post-Operatorio',
                'descripcion': 'Control y seguimiento post-operatorio',
                'precio': 4000.00,
                'duracion': 25,
                'categoria_id': categoria_controles.id
            }
        ]
        
        for serv_data in servicios:
            servicio = Servicio(**serv_data)
            db.session.add(servicio)
        
        db.session.commit()
        print("✅ Servicios de ejemplo creados")
        
        # Crear pacientes de ejemplo
        clientes = [
            {
                'nombre': 'Juan Carlos',
                'apellido': 'Pérez',
                'telefono': '+541987654321',
                'email': 'juan.perez@email.com'
            },
            {
                'nombre': 'María Elena',
                'apellido': 'García',
                'telefono': '+541987654322',
                'email': 'maria.garcia@email.com'
            },
            {
                'nombre': 'Pedro Alberto',
                'apellido': 'López',
                'telefono': '+541987654323',
                'email': 'pedro.lopez@email.com'
            },
            {
                'nombre': 'Ana Sofía',
                'apellido': 'Martínez',
                'telefono': '+541987654324',
                'email': 'ana.martinez@email.com'
            },
            {
                'nombre': 'Roberto Carlos',
                'apellido': 'Fernández',
                'telefono': '+541987654325',
                'email': 'roberto.fernandez@email.com'
            },
            {
                'nombre': 'Laura Beatriz',
                'apellido': 'Ruiz',
                'telefono': '+541987654326',
                'email': 'laura.ruiz@email.com'
            }
        ]
        
        for cli_data in clientes:
            cliente = Cliente(**cli_data)
            db.session.add(cliente)
        
        db.session.commit()
        print("✅ Pacientes de ejemplo creados")
        
        print("\n🎉 ¡Datos de ejemplo creados exitosamente!")
        print("📋 Resumen:")
        print(f"   • {len(categorias)} categorías médicas")
        print(f"   • {len(profesionales)} médicos especialistas")
        print(f"   • {len(servicios)} servicios médicos")
        print(f"   • {len(clientes)} pacientes")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al crear datos de ejemplo: {str(e)}")

@app.cli.command()
def reset_db():
    """
    Comando CLI para resetear la base de datos
    Uso: flask reset-db
    """
    if input("⚠️  ¿Estás seguro de que quieres resetear la base de datos? (y/N): ").lower() == 'y':
        db.drop_all()
        db.create_all()
        print("✅ Base de datos reseteada correctamente")
        print("💡 Recuerda crear un usuario administrador con: flask create-admin")
    else:
        print("❌ Operación cancelada")

@app.errorhandler(404)
def not_found_error(error):
    """Manejador de error 404"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejador de error 500"""
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Variable global para controlar si ya se ejecutó
_database_initialized = False

@app.before_request
def create_tables():
    global _database_initialized
    if not _database_initialized:
        db.create_all()
        print("🟢 Tablas de base de datos verificadas/creadas")
        _database_initialized = True

if __name__ == '__main__':
    # Configuración para desarrollo
    print("🚀 Iniciando aplicación...")
    print("📍 Servidor corriendo en: http://localhost:5000")
    print("🔧 Modo: Desarrollo")
    print("🔐 Primera página: Login")
    print("\n💡 Comandos útiles:")
    print("   • flask init-db          - Inicializar base de datos")
    print("   • flask create-admin     - Crear usuario administrador")
    print("   • flask create-user      - Crear usuario normal")
    print("   • flask list-users       - Listar usuarios")
    print("   • flask create-sample-data - Crear datos de ejemplo")
    print("   • flask reset-db         - Resetear base de datos")
    print("   • Ctrl+C                 - Detener servidor")
    print("-" * 50)
    
    # Ejecutar la aplicación en modo debug
    app.run(
        debug=True,
        host='0.0.0.0',  # Permite conexiones externas
        port=5000,
        use_reloader=True,  # Recarga automática al cambiar código
        threaded=True  # Manejo de múltiples requests
    )