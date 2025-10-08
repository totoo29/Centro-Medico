# Integración con Obras Sociales y Prepagas

## Descripción General

Este módulo implementa la gestión completa de obras sociales, prepagas y planes de cobertura para el sistema médico. Permite administrar la información de contacto, cobertura, autorizaciones y planes asociados a cada entidad de salud.

## Características Principales

### 🏥 Gestión de Obras Sociales
- **Tipos de entidades**: Obra Social, Prepaga, Particular
- **Información completa**: Nombre, código, CUIT, dirección, contactos
- **Configuración de cobertura**: Porcentaje por defecto, requisitos de autorización
- **Gestión de estados**: Activa/Inactiva con validaciones de integridad

### 📋 Planes de Cobertura
- **Planes por obra social**: Múltiples planes con diferentes niveles de cobertura
- **Detalles de cobertura**: Porcentaje, copago, coseguro
- **Límites configurables**: Anuales y por consulta
- **Especialidades cubiertas**: Lista de especialidades médicas incluidas

### ✅ Sistema de Autorizaciones
- **Flujo completo**: Solicitud → Aprobación/Rechazo → Vencimiento
- **Validaciones automáticas**: Verificación de fechas y requisitos
- **Seguimiento de estado**: Pendiente, Aprobada, Rechazada, Vencida
- **Generación automática**: Números únicos de autorización

## Estructura de la Base de Datos

### Tabla: `obras_sociales`
```sql
CREATE TABLE obras_sociales (
    id INTEGER PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    tipo VARCHAR(50) NOT NULL, -- 'obra_social', 'prepaga', 'particular'
    cuit VARCHAR(20),
    direccion VARCHAR(300),
    telefono VARCHAR(20),
    email VARCHAR(120),
    contacto_nombre VARCHAR(100),
    contacto_telefono VARCHAR(20),
    contacto_email VARCHAR(120),
    porcentaje_cobertura FLOAT DEFAULT 0.0,
    requiere_autorizacion BOOLEAN DEFAULT FALSE,
    dias_autorizacion INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    notas TEXT
);
```

### Tabla: `planes_obra_social`
```sql
CREATE TABLE planes_obra_social (
    id INTEGER PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    codigo VARCHAR(50) NOT NULL,
    obra_social_id INTEGER NOT NULL,
    porcentaje_cobertura FLOAT NOT NULL DEFAULT 0.0,
    copago FLOAT DEFAULT 0.0,
    coseguro FLOAT DEFAULT 0.0,
    limite_anual FLOAT,
    limite_por_consulta FLOAT,
    requiere_autorizacion BOOLEAN DEFAULT FALSE,
    dias_autorizacion INTEGER DEFAULT 0,
    especialidades_cubiertas TEXT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    notas TEXT,
    FOREIGN KEY (obra_social_id) REFERENCES obras_sociales(id)
);
```

### Tabla: `autorizaciones`
```sql
CREATE TABLE autorizaciones (
    id INTEGER PRIMARY KEY,
    numero_autorizacion VARCHAR(100) UNIQUE NOT NULL,
    cliente_id INTEGER NOT NULL,
    obra_social_id INTEGER NOT NULL,
    plan_id INTEGER,
    servicio_id INTEGER,
    profesional_id INTEGER,
    fecha_solicitud DATETIME NOT NULL,
    fecha_autorizacion DATETIME,
    fecha_vencimiento DATETIME,
    fecha_turno DATE,
    estado VARCHAR(50) DEFAULT 'pendiente',
    motivo_rechazo TEXT,
    porcentaje_cobertura FLOAT,
    copago FLOAT,
    coseguro FLOAT,
    limite_autorizacion FLOAT,
    cantidad_autorizada INTEGER DEFAULT 1,
    observaciones TEXT,
    usuario_solicitante VARCHAR(100),
    usuario_autorizador VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (obra_social_id) REFERENCES obras_sociales(id),
    FOREIGN KEY (plan_id) REFERENCES planes_obra_social(id),
    FOREIGN KEY (servicio_id) REFERENCES servicios(id),
    FOREIGN KEY (profesional_id) REFERENCES profesionales(id)
);
```

## Funcionalidades Implementadas

### 1. Gestión de Obras Sociales
- ✅ Crear, editar, eliminar obras sociales
- ✅ Búsqueda y filtrado por tipo
- ✅ Exportación a Excel/CSV
- ✅ Validaciones de integridad
- ✅ Gestión de contactos y información fiscal

### 2. Gestión de Planes
- ✅ Crear, editar, eliminar planes por obra social
- ✅ Configuración de cobertura y límites
- ✅ Gestión de copagos y coseguros
- ✅ Especialidades cubiertas
- ✅ Requisitos de autorización

### 3. Sistema de Autorizaciones
- ✅ Solicitud de autorizaciones
- ✅ Flujo de aprobación/rechazo
- ✅ Generación automática de números
- ✅ Control de fechas de vencimiento
- ✅ Seguimiento de estado

### 4. Integración con Clientes
- ✅ Asociación de clientes con obras sociales
- ✅ Selección de planes específicos
- ✅ Números de afiliado
- ✅ Gestión de grupos familiares

## Rutas de la API

### Obras Sociales
- `GET /obras-sociales/` - Listar todas las obras sociales
- `GET /obras-sociales/nuevo` - Formulario de nueva obra social
- `POST /obras-sociales/crear` - Crear nueva obra social
- `GET /obras-sociales/<id>` - Ver detalle de obra social
- `GET /obras-sociales/<id>/editar` - Formulario de edición
- `POST /obras-sociales/<id>/actualizar` - Actualizar obra social
- `POST /obras-sociales/<id>/eliminar` - Eliminar obra social
- `GET /obras-sociales/buscar` - API de búsqueda (AJAX)
- `GET /obras-sociales/exportar` - Exportar a Excel/CSV

### Planes
- `GET /obras-sociales/<obra_social_id>/planes` - Listar planes
- `GET /obras-sociales/<obra_social_id>/planes/nuevo` - Nuevo plan
- `POST /obras-sociales/<obra_social_id>/planes/crear` - Crear plan

### Autorizaciones
- `GET /autorizaciones/` - Listar autorizaciones
- `GET /autorizaciones/nuevo` - Nueva autorización
- `POST /autorizaciones/crear` - Crear autorización
- `GET /autorizaciones/<id>` - Ver autorización
- `POST /autorizaciones/<id>/aprobar` - Aprobar autorización
- `POST /autorizaciones/<id>/rechazar` - Rechazar autorización
- `GET /autorizaciones/exportar` - Exportar autorizaciones

## Uso del Sistema

### 1. Configurar Obra Social
1. Ir a **Obras Sociales** → **Nueva Obra Social**
2. Completar información básica (nombre, código, tipo)
3. Configurar información de contacto y fiscal
4. Establecer porcentaje de cobertura por defecto
5. Configurar requisitos de autorización si aplica

### 2. Crear Planes de Cobertura
1. Desde el detalle de la obra social, ir a **Ver Planes**
2. Hacer clic en **Nuevo Plan**
3. Configurar cobertura, copagos y límites
4. Establecer especialidades cubiertas
5. Configurar requisitos de autorización del plan

### 3. Solicitar Autorización
1. Ir a **Autorizaciones** → **Nueva Autorización**
2. Seleccionar cliente y obra social
3. El plan se selecciona automáticamente
4. Especificar servicio y profesional si aplica
5. Establecer fecha del turno
6. Enviar solicitud

### 4. Gestionar Autorizaciones
1. **Pendientes**: Revisar y aprobar/rechazar
2. **Aprobadas**: Controlar fechas de vencimiento
3. **Rechazadas**: Registrar motivo del rechazo
4. **Vencidas**: Archivar automáticamente

## Validaciones y Reglas de Negocio

### Obras Sociales
- Código único por obra social
- Nombre obligatorio
- Tipo obligatorio (obra_social, prepaga, particular)
- No se puede eliminar si tiene clientes asociados

### Planes
- Código único por obra social
- Porcentaje de cobertura obligatorio (0-100%)
- Copago y coseguro opcionales
- Límites anuales y por consulta opcionales

### Autorizaciones
- Cliente y obra social obligatorios
- Número único generado automáticamente
- Estado inicial: pendiente
- Solo se pueden editar autorizaciones pendientes
- Aprobación automática de fecha de vencimiento (30 días)

## Archivos Principales

### Modelos
- `src/models/obra_social.py` - Modelo de obra social
- `src/models/plan_obra_social.py` - Modelo de plan
- `src/models/autorizacion.py` - Modelo de autorización

### Servicios
- `src/services/obra_social_service.py` - Lógica de negocio de obras sociales
- `src/services/plan_obra_social_service.py` - Lógica de negocio de planes
- `src/services/autorizacion_service.py` - Lógica de negocio de autorizaciones

### Rutas
- `src/routes/obras_sociales.py` - Rutas de obras sociales y planes
- `src/routes/autorizaciones.py` - Rutas de autorizaciones

### Plantillas
- `templates/obras_sociales/` - Plantillas de obras sociales
- `templates/autorizaciones/` - Plantillas de autorizaciones

## Próximas Mejoras

### Funcionalidades Planificadas
- [ ] Dashboard de estadísticas de cobertura
- [ ] Notificaciones automáticas de vencimiento
- [ ] Integración con sistemas externos de obras sociales
- [ ] Reportes de utilización de cobertura
- [ ] Gestión de reembolsos
- [ ] Historial de cambios de planes

### Mejoras Técnicas
- [ ] Cache de información de obras sociales
- [ ] Validación en tiempo real de CUIT
- [ ] API REST completa para integraciones
- [ ] Logs de auditoría detallados
- [ ] Backup automático de autorizaciones

## Soporte y Mantenimiento

### Verificación del Sistema
- Ejecutar `python -m pytest tests/test_obras_sociales.py`
- Verificar migraciones de base de datos
- Comprobar permisos de usuario

### Logs y Debugging
- Los logs se guardan en `src/utils/log/app.log`
- Errores de validación se muestran en la interfaz
- Excepciones se capturan y registran automáticamente

### Contacto
Para soporte técnico o consultas sobre la implementación, contactar al equipo de desarrollo.
