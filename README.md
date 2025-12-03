# Sistema de Gestión - Consultorio Médico

Sistema completo de gestión para consultorios médicos desarrollado con Flask. Permite administrar pacientes, profesionales, turnos, servicios, obras sociales y autorizaciones de manera eficiente y centralizada.

## 📋 Tabla de Contenidos

- [Características Principales](#características-principales)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Comandos Disponibles](#comandos-disponibles)
- [Funcionalidades por Módulo](#funcionalidades-por-módulo)
- [Desarrollo](#desarrollo)
- [Soporte](#soporte)

<a id="características-principales"></a>
## ✨ Características Principales

### 🏥 Gestión Integral
- **Pacientes/Clientes**: Registro completo con datos personales, contacto y obra social
- **Profesionales**: Administración de médicos y especialistas con horarios
- **Servicios Médicos**: Catálogo de servicios organizados por categorías
- **Turnos**: Sistema de agendamiento con calendario y disponibilidad
- **Obras Sociales**: Gestión completa de obras sociales, prepagas y planes
- **Autorizaciones**: Flujo completo de solicitud, aprobación y seguimiento

### 🔐 Seguridad y Autenticación
- Sistema de autenticación con Flask-Login
- Roles de usuario (admin, usuario)
- Protección de rutas y sesiones
- Validación de permisos

### 📊 Funcionalidades Adicionales
- Exportación de datos a Excel/CSV
- Búsqueda y filtrado avanzado
- Paginación de resultados
- Dashboard con información relevante
- Logs de actividad
- Manejo de errores personalizado

<a id="tecnologías-utilizadas"></a>
## 🛠️ Tecnologías Utilizadas

- **Backend**: Flask 3.1.1
- **Base de Datos**: SQLite
- **ORM**: SQLAlchemy 2.0.41
- **Migraciones**: Flask-Migrate 4.1.0
- **Autenticación**: Flask-Login 0.6.3
- **Exportación**: pandas 2.3.0, openpyxl 3.1.5
- **Templates**: Jinja2 3.1.3
- **Utilidades**: python-dotenv 1.0.0

<a id="requisitos-previos"></a>
## 📦 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

<a id="instalación"></a>
## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd Centro-Medico
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno (opcional)

Crear un archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=sqlite:///consultorio.db
FLASK_ENV=development
```

### 5. Inicializar la base de datos

```bash
# Opción 1: Inicializar con datos básicos
flask init-db

# Opción 2: Crear datos de ejemplo completos
flask create-sample-data

# Opción 3: Crear solo usuario administrador
flask create-admin --username admin --email admin@consultorio.com --password admin123
```

<a id="configuración"></a>
## ⚙️ Configuración

El archivo `config.py` contiene todas las configuraciones del sistema. Puedes modificar:

- **Base de datos**: URI de conexión (SQLite por defecto)
- **Paginación**: Cantidad de elementos por página
- **Zona horaria**: Configurada para Argentina (Buenos Aires)
- **Horarios**: Horario de trabajo y duración de turnos
- **Archivos**: Límite de tamaño para uploads

### Configuraciones Disponibles

- `development`: Desarrollo con SQLite y debug activado
- `production`: Producción con SQLite
- `testing`: Testing con base de datos en memoria

Para cambiar la configuración, modifica la variable de entorno `FLASK_ENV` o edita `config.py`.

<a id="uso"></a>
## 🎯 Uso

### Iniciar la aplicación

```bash
python run_app.py
```

O usando Flask directamente:

```bash
flask run
```

La aplicación estará disponible en: `http://localhost:5000`

### Credenciales por defecto

Después de ejecutar `flask init-db` o `flask create-sample-data`:

- **Usuario**: `admin`
- **Contraseña**: `admin123`

⚠️ **Importante**: Cambia estas credenciales en producción.

<a id="estructura-del-proyecto"></a>
## 📁 Estructura del Proyecto

```
Centro-Medico/
│
├── src/                          # Código fuente principal
│   ├── app.py                    # Factory de la aplicación Flask
│   ├── auth.py                  # Configuración de autenticación
│   ├── config_db.py             # Configuración de base de datos
│   ├── database.py              # Instancia de SQLAlchemy
│   ├── models_init.py           # Inicialización de modelos
│   │
│   ├── models/                   # Modelos de base de datos
│   │   ├── usuario.py           # Usuarios del sistema
│   │   ├── cliente.py           # Pacientes/clientes
│   │   ├── profesional.py       # Médicos y profesionales
│   │   ├── servicio.py           # Servicios médicos
│   │   ├── categoria.py         # Categorías de servicios
│   │   ├── turno.py             # Turnos/agendamientos
│   │   ├── obra_social.py       # Obras sociales
│   │   ├── plan_obra_social.py  # Planes de cobertura
│   │   └── autorizacion.py      # Autorizaciones médicas
│   │
│   ├── routes/                   # Rutas/Controladores
│   │   ├── main.py              # Dashboard principal
│   │   ├── auth.py              # Autenticación
│   │   ├── clientes.py          # Gestión de clientes
│   │   ├── profesionales.py     # Gestión de profesionales
│   │   ├── servicios.py         # Gestión de servicios
│   │   ├── categorias.py        # Gestión de categorías
│   │   ├── turnos.py            # Gestión de turnos
│   │   ├── obras_sociales.py    # Gestión de obras sociales
│   │   └── autorizaciones.py    # Gestión de autorizaciones
│   │
│   ├── services/                 # Lógica de negocio
│   │   ├── cliente_service.py
│   │   ├── profesional_service.py
│   │   ├── servicio_service.py
│   │   ├── turno_service.py
│   │   ├── obra_social_service.py
│   │   └── autorizacion_service.py
│   │
│   ├── utils/                    # Utilidades
│   │   ├── helpers.py           # Funciones auxiliares
│   │   ├── validators.py        # Validadores
│   │   ├── exports.py           # Exportación de datos
│   │   └── log/                 # Logs del sistema
│   │
│   └── tests/                    # Tests unitarios
│       ├── conftest.py
│       └── test_models.py
│
├── templates/                     # Plantillas HTML (Jinja2)
│   ├── base.html                # Plantilla base
│   ├── dashboard.html           # Dashboard principal
│   ├── auth/                    # Autenticación
│   ├── clientes/                # Gestión de clientes
│   ├── profesionales/            # Gestión de profesionales
│   ├── servicios/               # Gestión de servicios
│   ├── categorias/              # Gestión de categorías
│   ├── turnos/                  # Gestión de turnos
│   ├── obras_sociales/          # Gestión de obras sociales
│   ├── autorizaciones/          # Gestión de autorizaciones
│   └── errors/                  # Páginas de error
│
├── instance/                      # Instancia de la aplicación
│   └── consultorio.db           # Base de datos SQLite (generada)
│
├── config.py                     # Configuración del sistema
├── run_app.py                    # Script de inicio
├── requirements.txt              # Dependencias Python
├── README.md                     # Este archivo
└── README_OBRAS_SOCIALES.md      # Documentación de obras sociales
```

<a id="comandos-disponibles"></a>
## 🔧 Comandos Disponibles

### Comandos Flask CLI

```bash
# Inicializar base de datos con datos básicos
flask init-db

# Crear datos de ejemplo completos
flask create-sample-data

# Crear usuario administrador
flask create-admin --username admin --email admin@consultorio.com --password admin123

# Resetear base de datos (¡CUIDADO! Elimina todos los datos)
flask reset-db --confirm
```

### Comandos de Desarrollo

```bash
# Ejecutar en modo desarrollo
python run_app.py

# Ejecutar con Flask
flask run

# Ejecutar con debug
flask run --debug

# Ejecutar en puerto específico
flask run --port 5001
```

<a id="funcionalidades-por-módulo"></a>
## 📚 Funcionalidades por Módulo

### 👥 Gestión de Clientes
- Registro completo de pacientes
- Búsqueda y filtrado
- Asociación con obras sociales
- Historial de turnos
- Exportación de datos

### 👨‍⚕️ Gestión de Profesionales
- Registro de médicos y especialistas
- Gestión de horarios de atención
- Asociación con servicios
- Disponibilidad para turnos

### 🏥 Gestión de Servicios
- Catálogo de servicios médicos
- Organización por categorías
- Precios y duración
- Asociación con profesionales

### 📅 Gestión de Turnos
- Calendario de turnos
- Disponibilidad en tiempo real
- Asociación con clientes, profesionales y servicios
- Estados: programado, confirmado, completado, cancelado

### 🏥 Gestión de Obras Sociales
- Registro de obras sociales y prepagas
- Gestión de planes de cobertura
- Configuración de porcentajes y copagos
- Requisitos de autorización

### ✅ Sistema de Autorizaciones
- Solicitud de autorizaciones
- Flujo de aprobación/rechazo
- Control de vencimientos
- Generación automática de números

Para más detalles sobre obras sociales, consulta [README_OBRAS_SOCIALES.md](README_OBRAS_SOCIALES.md).

<a id="desarrollo"></a>
## 💻 Desarrollo

### Estructura de Código

El proyecto sigue una arquitectura en capas:

1. **Models**: Definición de entidades y relaciones
2. **Services**: Lógica de negocio
3. **Routes**: Controladores HTTP
4. **Templates**: Vistas HTML
5. **Utils**: Utilidades y helpers

### Agregar Nuevas Funcionalidades

1. Crear el modelo en `src/models/`
2. Implementar el servicio en `src/services/`
3. Crear las rutas en `src/routes/`
4. Desarrollar las plantillas en `templates/`
5. Registrar las rutas en `src/routes/__init__.py`

### Testing

```bash
# Ejecutar tests
python -m pytest

# Con cobertura
python -m pytest --cov=src
```

## 🐛 Solución de Problemas

### Error de base de datos

Si hay problemas con la base de datos:

```bash
# Eliminar y recrear
flask reset-db --confirm
flask init-db
```

### Error de importación

Asegúrate de estar en el directorio raíz y que el entorno virtual esté activado.

### Puerto en uso

Si el puerto 5000 está ocupado:

```bash
flask run --port 5001
```

## 📝 Notas Adicionales

- La base de datos SQLite se crea automáticamente en `instance/consultorio.db`
- Los logs se guardan en `src/utils/log/app.log`
- Cambiar `SECRET_KEY` en producción
- Configurar variables de entorno para datos sensibles

## 📄 Licencia

Este proyecto es de uso interno. Todos los derechos reservados.

## 👥 Contribución

Para contribuir al proyecto:

1. Crear una rama para la nueva funcionalidad
2. Realizar los cambios
3. Probar exhaustivamente
4. Crear un pull request con descripción detallada

<a id="soporte"></a>
## 📞 Soporte

Para soporte técnico o consultas:

- Revisar la documentación en `README_OBRAS_SOCIALES.md`
- Consultar los logs en `src/utils/log/app.log`
- Verificar la configuración en `config.py`

---

**Versión**: 1.0.0  
**Última actualización**: 2025
