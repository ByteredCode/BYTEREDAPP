# Modelos de datos (SQLAlchemy ORM)

## Conceptos fundamentales

SQLAlchemy es un **ORM (Object-Relational Mapper)**: permite trabajar con la base de datos usando objetos y métodos de Python en lugar de escribir SQL directamente. La versión 2.0 es asíncrona nativa.

### `Base`
Clase base declarativa de SQLAlchemy. Todas las clases que heredan de `Base` se convierten en tablas de la base de datos.

### `Column`
Define una columna. Primer argumento: tipo SQL. Argumentos adicionales: constraints.

### `SAEnum`
Tipo `Enum` de SQLAlchemy para columnas con valores fijos.

### `ForeignKey("tabla.columna", ondelete="CASCADE")`
Clave foránea con acción en cascada al eliminar.

### `relationship`
Mapeo ORM que permite navegar entre objetos Python. No crea columnas en BD.

---

## Archivo: `server/app/models/usuario.py`

Tabla `usuario`. Clave primaria autoincremental, email único, contraseña hasheada (255 chars para bcrypt). Roles: `admin_total`, `admin_empresa`, `usuario`. FK a `empresa.codigo_empresa` con CASCADE.

## Archivo: `server/app/models/empresa.py`

Modelo central del multi-tenant. Cada empresa es un "inquilino". Todas las demás tablas referencian `codigo_empresa`. Campos: `codigo_scrum`, `usuario_admin_dpd`, `web` (para redirección). La relación con `EmpresaServicio` usa `cascade="all, delete-orphan"`.

## Archivo: `server/app/models/empresa_servicio.py`

Clave compuesta (`codigo_empresa`, `servicio`). Patrón **feature flags**: cada empresa tiene filas con servicio + activo/desactivado. Escalable: añadir servicio = nueva fila, no columna.

## Archivo: `server/app/models/tarea.py`

Tabla `tareas`. Campos clave: `columna` (enum: Todo/Haciendose/En revision/Done) para Kanban, `orden` (Integer) para posicionamiento drag & drop, `prioridad` (enum), `fecha_limite`, `asignacion` (FK usuario con SET NULL), `codigo_sprint` (FK sprint con SET NULL).

## Archivo: `server/app/models/sprint.py`

Tabla `sprints`. Ciclo de vida: `Planificado → Activo → Completado`. Relación bidireccional con Tarea.

## Archivo: `server/app/models/ticket.py`

Diseño híbrido: `codigo_usuario` nullable (tickets anónimos o autenticados). Campos de contacto para anónimos. `server_default=func.current_timestamp()` asigna fecha desde el servidor BD.

## Archivo: `server/app/models/documento.py`

Tabla `documentos`. Metadatos: nombre, tipo (DPD/ISO), usuario que subió, fecha, ruta_archivo. El archivo físico se almacena en disco, no en BD.

## Archivo: `server/app/models/documento_permiso.py`

Clave compuesta (`id_documento`, `codigo_usuario`). Relación muchos-a-muchos entre documentos y usuarios para control de acceso granular.

## Archivo: `server/app/models/fichaje.py`

Modelo simple: `hora_entrada` (obligatoria), `hora_salida` (opcional). NULL en salida = fichaje actualmente abierto.
