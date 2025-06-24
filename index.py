#!/usr/bin/env python3
"""
Punto de entrada principal para la aplicación Flask
Sistema de Gestión de Consultorio Médico
"""

import os
import sys
from flask import render_template

# Agregar el directorio actual al path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import db
from src.models import Cliente, Categoria, Profesional, Servicio, Turno
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
        'Turno': Turno
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
                'precio': 50.00,
                'duracion': 30,
                'categoria_id': categoria_generales.id
            },
            {
                'nombre': 'Consulta Cardiológica',
                'descripcion': 'Consulta con especialista en cardiología',
                'precio': 80.00,
                'duracion': 45,
                'categoria_id': categoria_especialidades.id
            },
            {
                'nombre': 'Consulta Traumatológica',
                'descripcion': 'Consulta con especialista en traumatología',
                'precio': 75.00,
                'duracion': 40,
                'categoria_id': categoria_especialidades.id
            },
            {
                'nombre': 'Consulta Dermatológica',
                'descripcion': 'Consulta con especialista en dermatología',
                'precio': 70.00,
                'duracion': 35,
                'categoria_id': categoria_especialidades.id
            },
            {
                'nombre': 'Análisis de Sangre',
                'descripcion': 'Extracción y análisis de sangre completo',
                'precio': 25.00,
                'duracion': 15,
                'categoria_id': categoria_estudios.id
            },
            {
                'nombre': 'Electrocardiograma',
                'descripcion': 'Estudio cardiológico ECG',
                'precio': 30.00,
                'duracion': 20,
                'categoria_id': categoria_estudios.id
            },
            {
                'nombre': 'Control de Presión',
                'descripcion': 'Control y seguimiento de presión arterial',
                'precio': 15.00,
                'duracion': 15,
                'categoria_id': categoria_controles.id
            },
            {
                'nombre': 'Curación',
                'descripcion': 'Curación de heridas y procedimientos menores',
                'precio': 20.00,
                'duracion': 20,
                'categoria_id': categoria_procedimientos.id
            },
            {
                'nombre': 'Inyección Intramuscular',
                'descripcion': 'Aplicación de inyecciones intramusculares',
                'precio': 10.00,
                'duracion': 10,
                'categoria_id': categoria_procedimientos.id
            },
            {
                'nombre': 'Control Post-Operatorio',
                'descripcion': 'Control y seguimiento post-operatorio',
                'precio': 40.00,
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
    print("📊 Dashboard disponible en: http://localhost:5000/")
    print("\n💡 Comandos útiles:")
    print("   • flask init-db          - Inicializar base de datos")
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
    