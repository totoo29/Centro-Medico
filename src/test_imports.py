# test_imports.py
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Probando importación de src...")
    import src
    print("✅ src importado correctamente")
except Exception as e:
    print(f"❌ Error importando src: {e}")

try:
    print("Probando importación de src.routes...")
    import src.routes
    print("✅ src.routes importado correctamente")
except Exception as e:
    print(f"❌ Error importando src.routes: {e}")

try:
    print("Probando importación de src.routes.main...")
    from src.routes import main
    print("✅ src.routes.main importado correctamente")
except Exception as e:
    print(f"❌ Error importando src.routes.main: {e}")

try:
    print("Probando importación de src.routes.clientes...")
    from src.routes import clientes
    print("✅ src.routes.clientes importado correctamente")
except Exception as e:
    print(f"❌ Error importando src.routes.clientes: {e}")