#!/usr/bin/env python3
"""
Script para ejecutar la aplicación Flask del Sistema de Gestión de Consultorio Médico
"""

from src.app import create_app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Iniciando aplicación Flask...")
    print("📱 Accede a: http://localhost:5000")
    print("🔑 Credenciales: admin / admin123")
    print("⏹️  Presiona Ctrl+C para detener")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Aplicación detenida por el usuario")
    except Exception as e:
        print(f"❌ Error al ejecutar la aplicación: {e}")
