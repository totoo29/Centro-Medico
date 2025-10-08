from flask import Flask, render_template, redirect, url_for
from flask_login import current_user
from src.config_db import configure_db, init_db_tables
from src.routes import register_blueprints
from src.auth import init_auth
from config import Config
from datetime import datetime, date
import click
from dotenv import load_dotenv

# Cargar variables de entorno desde .flaskenv
load_dotenv()

def create_app(config=None):
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configuración
    if config:
        app.config.update(config)
    else:
        app.config.from_object(Config)
    
    # Inicializar base de datos
    configure_db(app)
    init_db_tables(app)
    
    # Inicializar modelos de forma segura
    try:
        from src.models_init import init_models
        init_models()
    except Exception as e:
        print(f"⚠️  Advertencia al inicializar modelos: {e}")
    
    # Inicializar autenticación
    init_auth(app)
    
    # SOLUCIÓN: Hacer current_user disponible globalmente en plantillas
    @app.context_processor
    def inject_user():
        """Inyectar current_user y fecha actual en todas las plantillas"""
        from flask_login import current_user
        return dict(
            current_user=current_user,
            today=date.today(),
            now=datetime.now()
        )
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Registrar filtros de plantillas
    register_template_filters(app)
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    # Registrar comandos CLI personalizados
    register_cli_commands(app)
    
    # Ruta raíz redirige al login
    @app.route('/')
    def root():
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        return redirect(url_for('auth.login'))
    
    return app

def register_template_filters(app):
    """Registrar filtros personalizados para las plantillas"""
    try:
        from src.utils.helpers import (
            formatear_telefono, formatear_precio, formatear_fecha, 
            formatear_hora, capitalizar_nombre, formatear_fecha_personalizada,
            fecha_hoy_iso, es_fecha_pasada, dias_hasta_fecha
        )
        
        # Filtros básicos
        app.jinja_env.filters['telefono'] = formatear_telefono
        app.jinja_env.filters['precio'] = formatear_precio
        app.jinja_env.filters['fecha'] = formatear_fecha
        app.jinja_env.filters['hora'] = formatear_hora
        app.jinja_env.filters['capitalizar'] = capitalizar_nombre
        
        # NUEVO: Filtros de fecha mejorados
        app.jinja_env.filters['date'] = formatear_fecha_personalizada
        app.jinja_env.filters['fecha_personalizada'] = formatear_fecha_personalizada
        app.jinja_env.filters['es_pasada'] = es_fecha_pasada
        app.jinja_env.filters['dias_hasta'] = dias_hasta_fecha
        
        # Funciones globales para plantillas
        app.jinja_env.globals['fecha_hoy_iso'] = fecha_hoy_iso
        app.jinja_env.globals['date_today'] = lambda: date.today().isoformat()
        
        # CORRECCIÓN ESPECÍFICA PARA EL CALENDARIO
        @app.template_filter('strftime')
        def strftime_filter(fecha, formato='%Y-%m-%d'):
            """Filtro strftime para fechas"""
            if not fecha:
                return ''
            
            if isinstance(fecha, str):
                try:
                    fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
                except ValueError:
                    return fecha
            
            if hasattr(fecha, 'strftime'):
                return fecha.strftime(formato)
            
            return str(fecha)
        
        print("✅ Filtros de plantillas registrados correctamente")
        
    except ImportError as e:
        print(f"⚠️ Error importando filtros: {e}")
        # Definir filtros básicos como fallback
        
        @app.template_filter('telefono')
        def telefono_filter(s):
            return s or ''
        
        @app.template_filter('precio')
        def precio_filter(s):
            return f'${s:.2f}' if s else '$0.00'
        
        @app.template_filter('date')
        def date_filter(fecha_obj, formato='%Y-%m-%d'):
            """Filtro de fecha con fallback mejorado"""
            if not fecha_obj:
                return ''
            
            if isinstance(fecha_obj, str):
                if fecha_obj == 'now':
                    return datetime.now().strftime(formato)
                elif fecha_obj == 'today':
                    return date.today().strftime(formato)
                return fecha_obj
            
            if isinstance(fecha_obj, (datetime, date)):
                return fecha_obj.strftime(formato)
            
            return str(fecha_obj)
        
        @app.template_filter('strftime')
        def strftime_filter(fecha, formato='%Y-%m-%d'):
            """Filtro strftime de fallback"""
            return date_filter(fecha, formato)
        
        # Función global para fecha de hoy
        app.jinja_env.globals['date_today'] = lambda: date.today().isoformat()
        
        print("⚠️ Usando filtros básicos de fallback")

def register_error_handlers(app):
    """Registrar manejadores de errores"""
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from src.database import db
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    
    print("✅ Manejadores de errores registrados")

def register_cli_commands(app):
    """Registrar comandos CLI personalizados"""
    
    @app.cli.command('reset-db')
    @click.option('--confirm', is_flag=True, help='Confirmar que quieres resetear la base de datos')
    def reset_db_command(confirm):
        """Resetear la base de datos (eliminar todas las tablas y recrearlas)"""
        if not confirm:
            click.echo("⚠️  ADVERTENCIA: Esto eliminará TODOS los datos de la base de datos!")
            click.echo("Para confirmar, usa: flask reset-db --confirm")
            return
        
        with app.app_context():
            from src.database import db
            from src.models import Usuario, Cliente, Categoria, Profesional, Servicio, Turno
            
            click.echo("🗑️  Eliminando todas las tablas...")
            db.drop_all()
            
            click.echo("🔨 Creando nuevas tablas...")
            db.create_all()
            
            click.echo("✅ Base de datos reseteada exitosamente")
    
    @app.cli.command('create-admin')
    @click.option('--username', default='admin', help='Nombre de usuario del administrador')
    @click.option('--email', default='admin@consultorio.com', help='Email del administrador')
    @click.option('--password', default='admin123', help='Contraseña del administrador')
    def create_admin_command(username, email, password):
        """Crear un usuario administrador"""
        with app.app_context():
            from src.database import db
            from src.models.usuario import Usuario
            
            # Verificar si ya existe un usuario con ese username o email
            existing_user = Usuario.query.filter(
                db.or_(Usuario.username == username, Usuario.email == email)
            ).first()
            
            if existing_user:
                click.echo(f"❌ Ya existe un usuario con username '{username}' o email '{email}'")
                return
            
            # Crear nuevo usuario administrador
            admin = Usuario(
                username=username,
                email=email,
                nombre='Administrador',
                apellido='Sistema',
                rol='admin',
                activo=True
            )
            admin.set_password(password)
            
            db.session.add(admin)
            db.session.commit()
            
            click.echo(f"✅ Usuario administrador creado exitosamente:")
            click.echo(f"   Username: {username}")
            click.echo(f"   Email: {email}")
            click.echo(f"   Contraseña: {password}")
            click.echo(f"   Rol: {admin.rol}")
    
    @app.cli.command('init-db')
    def init_db_command():
        """Inicializar la base de datos con datos de ejemplo"""
        with app.app_context():
            from src.database import db
            from src.models.usuario import Usuario
            from src.models.categoria import Categoria
            from src.models.servicio import Servicio
            
            click.echo("🔨 Inicializando base de datos con datos de ejemplo...")
            
            # Crear usuario administrador si no existe
            if not Usuario.query.filter_by(username='admin').first():
                admin = Usuario(
                    username='admin',
                    email='admin@consultorio.com',
                    nombre='Administrador',
                    apellido='Sistema',
                    rol='admin',
                    activo=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                click.echo("✅ Usuario administrador creado")
            
            # Crear categorías de ejemplo
            categorias_ejemplo = [
                'Medicina General',
                'Cardiología',
                'Dermatología',
                'Ginecología',
                'Pediatría',
                'Traumatología',
                'Oftalmología',
                'Odontología'
            ]
            
            for nombre_cat in categorias_ejemplo:
                if not Categoria.query.filter_by(nombre=nombre_cat).first():
                    categoria = Categoria(nombre=nombre_cat, descripcion=f'Especialidad de {nombre_cat}')
                    db.session.add(categoria)
                    click.echo(f"✅ Categoría '{nombre_cat}' creada")
            
            db.session.commit()
            click.echo("🎯 Base de datos inicializada exitosamente")
            click.echo("📋 Credenciales de acceso:")
            click.echo("   Username: admin")
            click.echo("   Contraseña: admin123")
    
    @app.cli.command('create-sample-data')
    def create_sample_data_command():
        """Crear datos de ejemplo completos para el consultorio"""
        with app.app_context():
            from src.database import db
            from src.models.categoria import Categoria
            from src.models.profesional import Profesional
            from src.models.servicio import Servicio
            from src.models.cliente import Cliente
            from src.models.obra_social import ObraSocial
            from src.models.plan_obra_social import PlanObraSocial
            
            click.echo("🔨 Creando datos de ejemplo completos...")
            
            # Crear categorías de ejemplo
            categorias = [
                {'nombre': 'Consultas Generales', 'descripcion': 'Consultas médicas generales y chequeos', 'color': '#007bff'},
                {'nombre': 'Especialidades', 'descripcion': 'Consultas con médicos especialistas', 'color': '#28a745'},
                {'nombre': 'Estudios y Análisis', 'descripcion': 'Laboratorio y estudios médicos', 'color': '#ffc107'},
                {'nombre': 'Procedimientos', 'descripcion': 'Procedimientos médicos menores', 'color': '#dc3545'},
                {'nombre': 'Controles', 'descripcion': 'Controles y seguimientos', 'color': '#6f42c1'}
            ]
            
            for cat_data in categorias:
                if not Categoria.query.filter_by(nombre=cat_data['nombre']).first():
                    categoria = Categoria(**cat_data)
                    db.session.add(categoria)
                    click.echo(f"✅ Categoría '{cat_data['nombre']}' creada")
            
            db.session.commit()
            
            # Crear obras sociales de ejemplo
            obras_sociales = [
                {
                    'nombre': 'OSDE',
                    'codigo': 'OSDE001',
                    'tipo': 'obra_social',
                    'cuit': '30-12345678-9',
                    'porcentaje_cobertura': 80.0,
                    'requiere_autorizacion': True,
                    'dias_autorizacion': 7
                },
                {
                    'nombre': 'Swiss Medical',
                    'codigo': 'SWISS001',
                    'tipo': 'prepaga',
                    'cuit': '30-87654321-0',
                    'porcentaje_cobertura': 90.0,
                    'requiere_autorizacion': False,
                    'dias_autorizacion': 0
                },
                {
                    'nombre': 'Particular',
                    'codigo': 'PART001',
                    'tipo': 'particular',
                    'porcentaje_cobertura': 0.0,
                    'requiere_autorizacion': False,
                    'dias_autorizacion': 0
                }
            ]
            
            for os_data in obras_sociales:
                if not ObraSocial.query.filter_by(codigo=os_data['codigo']).first():
                    obra_social = ObraSocial(**os_data)
                    db.session.add(obra_social)
                    click.echo(f"✅ Obra social '{os_data['nombre']}' creada")
            
            db.session.commit()
            
            # Crear planes de obra social
            osde = ObraSocial.query.filter_by(codigo='OSDE001').first()
            swiss = ObraSocial.query.filter_by(codigo='SWISS001').first()
            
            planes = [
                {
                    'nombre': 'OSDE 310',
                    'codigo': 'OSDE310',
                    'obra_social_id': osde.id if osde else None,
                    'porcentaje_cobertura': 80.0,
                    'copago': 500.0,
                    'coseguro': 0.0,
                    'requiere_autorizacion': True,
                    'dias_autorizacion': 7
                },
                {
                    'nombre': 'OSDE 410',
                    'codigo': 'OSDE410',
                    'obra_social_id': osde.id if osde else None,
                    'porcentaje_cobertura': 90.0,
                    'copago': 200.0,
                    'coseguro': 0.0,
                    'requiere_autorizacion': True,
                    'dias_autorizacion': 5
                },
                {
                    'nombre': 'Swiss Medical Premium',
                    'codigo': 'SWISS_PREMIUM',
                    'obra_social_id': swiss.id if swiss else None,
                    'porcentaje_cobertura': 90.0,
                    'copago': 0.0,
                    'coseguro': 0.0,
                    'requiere_autorizacion': False,
                    'dias_autorizacion': 0
                }
            ]
            
            for plan_data in planes:
                if not PlanObraSocial.query.filter_by(codigo=plan_data['codigo']).first():
                    plan = PlanObraSocial(**plan_data)
                    db.session.add(plan)
                    click.echo(f"✅ Plan '{plan_data['nombre']}' creado")
            
            db.session.commit()
            
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
                if not Profesional.query.filter_by(email=prof_data['email']).first():
                    profesional = Profesional(**prof_data)
                    db.session.add(profesional)
                    click.echo(f"✅ Profesional '{prof_data['nombre']} {prof_data['apellido']}' creado")
            
            db.session.commit()
            
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
                    'categoria_id': categoria_generales.id if categoria_generales else None
                },
                {
                    'nombre': 'Consulta Cardiológica',
                    'descripcion': 'Consulta con especialista en cardiología',
                    'precio': 8000.00,
                    'duracion': 45,
                    'categoria_id': categoria_especialidades.id if categoria_especialidades else None
                },
                {
                    'nombre': 'Consulta Traumatológica',
                    'descripcion': 'Consulta con especialista en traumatología',
                    'precio': 7500.00,
                    'duracion': 40,
                    'categoria_id': categoria_especialidades.id if categoria_especialidades else None
                },
                {
                    'nombre': 'Consulta Dermatológica',
                    'descripcion': 'Consulta con especialista en dermatología',
                    'precio': 7000.00,
                    'duracion': 35,
                    'categoria_id': categoria_especialidades.id if categoria_especialidades else None
                },
                {
                    'nombre': 'Análisis de Sangre',
                    'descripcion': 'Extracción y análisis de sangre completo',
                    'precio': 2500.00,
                    'duracion': 15,
                    'categoria_id': categoria_estudios.id if categoria_estudios else None
                },
                {
                    'nombre': 'Electrocardiograma',
                    'descripcion': 'Estudio cardiológico ECG',
                    'precio': 3000.00,
                    'duracion': 20,
                    'categoria_id': categoria_estudios.id if categoria_estudios else None
                },
                {
                    'nombre': 'Control de Presión',
                    'descripcion': 'Control y seguimiento de presión arterial',
                    'precio': 1500.00,
                    'duracion': 15,
                    'categoria_id': categoria_controles.id if categoria_controles else None
                },
                {
                    'nombre': 'Curación',
                    'descripcion': 'Curación de heridas y procedimientos menores',
                    'precio': 2000.00,
                    'duracion': 20,
                    'categoria_id': categoria_procedimientos.id if categoria_procedimientos else None
                },
                {
                    'nombre': 'Inyección Intramuscular',
                    'descripcion': 'Aplicación de inyecciones intramusculares',
                    'precio': 1000.00,
                    'duracion': 10,
                    'categoria_id': categoria_procedimientos.id if categoria_procedimientos else None
                },
                {
                    'nombre': 'Control Post-Operatorio',
                    'descripcion': 'Control y seguimiento post-operatorio',
                    'precio': 4000.00,
                    'duracion': 25,
                    'categoria_id': categoria_controles.id if categoria_controles else None
                }
            ]
            
            for serv_data in servicios:
                if not Servicio.query.filter_by(nombre=serv_data['nombre']).first():
                    servicio = Servicio(**serv_data)
                    db.session.add(servicio)
                    click.echo(f"✅ Servicio '{serv_data['nombre']}' creado")
            
            db.session.commit()
            
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
                if not Cliente.query.filter_by(email=cli_data['email']).first():
                    cliente = Cliente(**cli_data)
                    db.session.add(cliente)
                    click.echo(f"✅ Cliente '{cli_data['nombre']} {cli_data['apellido']}' creado")
            
            db.session.commit()
            
            click.echo("\n🎉 ¡Datos de ejemplo creados exitosamente!")
            click.echo("📋 Resumen:")
            click.echo(f"   • {len(categorias)} categorías médicas")
            click.echo(f"   • {len(obras_sociales)} obras sociales")
            click.echo(f"   • {len(planes)} planes de obra social")
            click.echo(f"   • {len(profesionales)} médicos especialistas")
            click.echo(f"   • {len(servicios)} servicios médicos")
            click.echo(f"   • {len(clientes)} pacientes")
    
    print("✅ Comandos CLI registrados")

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)