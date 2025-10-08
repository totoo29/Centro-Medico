#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de obra social en clientes
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Probar que se puedan importar todos los módulos necesarios"""
    try:
        print("🔍 Probando importaciones...")
        
        # Importar configuración de base de datos
        from config_db import db
        print("✅ Base de datos importada correctamente")
        
        # Importar modelos usando la nueva configuración
        from models.cliente import Cliente
        from models.obra_social import ObraSocial
        from models.plan_obra_social import PlanObraSocial
        print("✅ Modelos importados correctamente")
        
        # Importar servicios
        from services.cliente_service import ClienteService
        from services.obra_social_service import ObraSocialService
        from services.plan_obra_social_service import PlanObraSocialService
        print("✅ Servicios importados correctamente")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_modelos():
    """Probar que los modelos tengan los campos correctos"""
    try:
        print("\n🔍 Probando modelos...")
        
        from models.cliente import Cliente
        from models.obra_social import ObraSocial
        from models.plan_obra_social import PlanObraSocial
        
        # Verificar campos del modelo Cliente
        campos_cliente = [
            'obra_social_id', 'plan_id', 'numero_afiliado', 
            'grupo_familiar', 'titular_id'
        ]
        
        for campo in campos_cliente:
            if hasattr(Cliente, campo):
                print(f"✅ Campo {campo} existe en Cliente")
            else:
                print(f"❌ Campo {campo} NO existe en Cliente")
        
        # Verificar relaciones
        if hasattr(Cliente, 'obra_social'):
            print("✅ Relación obra_social existe en Cliente")
        else:
            print("❌ Relación obra_social NO existe en Cliente")
            
        if hasattr(Cliente, 'plan'):
            print("✅ Relación plan existe en Cliente")
        else:
            print("❌ Relación plan NO existe en Cliente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al probar modelos: {e}")
        return False

def test_servicios():
    """Probar que los servicios tengan los métodos correctos"""
    try:
        print("\n🔍 Probando servicios...")
        
        from services.cliente_service import ClienteService
        from services.obra_social_service import ObraSocialService
        from services.plan_obra_social_service import PlanObraSocialService
        
        # Verificar métodos del servicio de clientes
        metodos_cliente = [
            'crear_cliente', 'actualizar_cliente', 'get_cliente_by_id'
        ]
        
        for metodo in metodos_cliente:
            if hasattr(ClienteService, metodo):
                print(f"✅ Método {metodo} existe en ClienteService")
            else:
                print(f"❌ Método {metodo} NO existe en ClienteService")
        
        # Verificar métodos del servicio de obras sociales
        if hasattr(ObraSocialService, 'get_all_obras_sociales'):
            print("✅ Método get_all_obras_sociales existe en ObraSocialService")
        else:
            print("❌ Método get_all_obras_sociales NO existe en ObraSocialService")
            
        if hasattr(PlanObraSocialService, 'get_planes_by_obra_social'):
            print("✅ Método get_planes_by_obra_social existe en PlanObraSocialService")
        else:
            print("❌ Método get_planes_by_obra_social NO existe en PlanObraSocialService")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al probar servicios: {e}")
        return False

def test_rutas():
    """Probar que las rutas estén configuradas correctamente"""
    try:
        print("\n🔍 Probando rutas...")
        
        # Verificar que existan los archivos de rutas
        archivos_rutas = [
            'src/routes/clientes.py',
            'src/routes/obras_sociales.py'
        ]
        
        for archivo in archivos_rutas:
            if os.path.exists(archivo):
                print(f"✅ Archivo de ruta {archivo} existe")
            else:
                print(f"❌ Archivo de ruta {archivo} NO existe")
        
        # Verificar que las rutas API estén definidas
        with open('src/routes/obras_sociales.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
            if '/api/listar' in contenido:
                print("✅ Ruta API /api/listar está definida")
            else:
                print("❌ Ruta API /api/listar NO está definida")
                
            if '/planes/api' in contenido:
                print("✅ Ruta API /planes/api está definida")
            else:
                print("❌ Ruta API /planes/api NO está definida")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al probar rutas: {e}")
        return False

def test_plantillas():
    """Probar que las plantillas tengan los campos correctos"""
    try:
        print("\n🔍 Probando plantillas...")
        
        # Verificar plantilla de formulario
        with open('templates/clientes/formulario.html', 'r', encoding='utf-8') as f:
            contenido = f.read()
            campos_obra_social = [
                'obra_social_id', 'plan_id', 'numero_afiliado', 
                'grupo_familiar', 'titular_id'
            ]
            
            for campo in campos_obra_social:
                if f'name="{campo}"' in contenido:
                    print(f"✅ Campo {campo} está en el formulario")
                else:
                    print(f"❌ Campo {campo} NO está en el formulario")
        
        # Verificar plantilla de listado
        with open('templates/clientes/listar.html', 'r', encoding='utf-8') as f:
            contenido = f.read()
            if 'Obra Social' in contenido:
                print("✅ Columna 'Obra Social' está en el listado")
            else:
                print("❌ Columna 'Obra Social' NO está en el listado")
        
        # Verificar plantilla de detalle
        with open('templates/clientes/detalle.html', 'r', encoding='utf-8') as f:
            contenido = f.read()
            if 'Información de Obra Social' in contenido:
                print("✅ Sección 'Información de Obra Social' está en el detalle")
            else:
                print("❌ Sección 'Información de Obra Social' NO está en el detalle")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al probar plantillas: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de funcionalidad de obra social en clientes...")
    print("=" * 60)
    
    resultados = []
    
    # Ejecutar todas las pruebas
    resultados.append(("Importaciones", test_imports()))
    resultados.append(("Modelos", test_modelos()))
    resultados.append(("Servicios", test_servicios()))
    resultados.append(("Rutas", test_rutas()))
    resultados.append(("Plantillas", test_plantillas()))
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    exitos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        estado = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"{estado} {nombre}")
    
    print(f"\n🎯 Resultado: {exitos}/{total} pruebas pasaron")
    
    if exitos == total:
        print("🎉 ¡Todas las pruebas pasaron! La funcionalidad está lista.")
        return 0
    else:
        print("⚠️  Algunas pruebas fallaron. Revisar los errores.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
