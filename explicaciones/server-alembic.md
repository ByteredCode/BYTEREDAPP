# Explicación de Alembic (migraciones)

## ¿Qué es Alembic?

Alembic es una herramienta de **migración de bases de datos** para SQLAlchemy. Permite:

1. **Generar automáticamente** el script SQL necesario para sincronizar la BD con los modelos Python
2. **Aplicar** esos cambios a la BD
3. **Revertir** cambios si algo sale mal

## Archivos involucrados

```
server/
├── alembic.ini              ← Configuración general
└── alembic/
    ├── env.py               ← Configuración específica del proyecto
    ├── script.py.mako       ← Plantilla para nuevas migraciones
    └── versions/
        └── 3e03f2cf94fe_init.py  ← La migración inicial
```

---

## alembic.ini

### sqlalchemy.url (línea 63)

```ini
sqlalchemy.url = mysql+aiomysql://root:root@localhost:3306/byteredapp
```

Esta es la URL de conexión que Alembic usa para conectarse a la BD. Normalmente se pondría una variable de entorno, pero aquí está hardcodeada porque la BD de desarrollo siempre es la misma.

**¿Por qué está definida aquí y también en config.py?** Alembic.ini es la configuración de Alembic (la herramienta). Config.py es la configuración de la aplicación. Alembic necesita su propia URL porque se ejecuta como un comando independiente, no como parte de la app.

### prepend_sys_path (línea 16)

```ini
prepend_sys_path = .
```

Añade el directorio `server/` al path de Python. Así cuando Alembic hace `from app.models import Usuario`, encuentra el paquete `server/app/`.

---

## env.py — El corazón de la integración

```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.database import Base
from app.models import Empresa, EmpresaServicio, Usuario, Tarea, Documento, DocumentoPermiso, Ticket, Fichaje

target_metadata = Base.metadata

def run_migrations_offline():
    # Genera SQL sin conectar a BD
    ...

def run_migrations_online():
    asyncio.run(run_async_migrations())

async def run_async_migrations():
    connectable = create_async_engine(config.get_main_option("sqlalchemy.url"))
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()
```

### ¿Por qué es tan diferente de una configuración síncrona?

La mayoría de proyectos SQLAlchemy usan un `env.py` síncrono. Pero nosotros usamos **async** (aiomysql). Alembic no soporta async nativamente, así que necesitamos:

1. Crear el engine asíncrono manualmente
2. Obtener una conexión async
3. Ejecutar las migraciones dentro de `connection.run_sync()` (que ejecuta código síncrono en el contexto de una conexión async)

### Importación de modelos explícita

```python
from app.models import Empresa, EmpresaServicio, Usuario, Tarea, Documento, DocumentoPermiso, Ticket, Fichaje
```

Alembic necesita que los modelos estén importados para detectar cambios. Si no importas un modelo, Alembic no lo ve y no generará migraciones para él. **Este es un error común:** añadir un modelo nuevo y olvidar importarlo aquí.

---

## Migración inicial: 3e03f2cf94fe_init.py

```python
def upgrade():
    op.create_table('empresa', ...)
    op.create_table('empresa_servicios', ...)
    op.create_table('usuario', ...)
    op.create_table('documentos', ...)
    op.create_table('fichajes', ...)
    op.create_table('tareas', ...)
    op.create_table('tickets', ...)
    op.create_table('documento_permisos', ...)

def downgrade():
    op.drop_table('documento_permisos')
    op.drop_table('tickets')
    op.drop_table('tareas')
    op.drop_table('fichajes')
    op.drop_table('documentos')
    op.drop_table('usuario')
    op.drop_table('empresa_servicios')
    op.drop_table('empresa')
```

### upgrade vs downgrade

- **upgrade()**: Cómo llegar desde la versión anterior a esta
- **downgrade()**: Cómo volver a la versión anterior

La migración inicial no tiene versión anterior (`down_revision = None`), así que `upgrade` crea todas las tablas desde cero.

### Orden de las tablas

En `upgrade()`, las tablas se crean en orden de dependencias:
1. `empresa` (no depende de nadie)
2. `empresa_servicios`, `usuario` (dependen de empresa)
3. `documentos`, `fichajes`, `tareas`, `tickets` (dependen de empresa y usuario)
4. `documento_permisos` (depende de documentos y usuario)

En `downgrade()`, el orden se invierte para respetar las foreign keys.

---

## ¿Cómo se usa en el día a día?

### 1. Modificar un modelo existente

```python
# En empresa.py, añadir una columna
telefono = Column(String(20))
```

### 2. Generar la migración

```bash
cd server
alembic revision --autogenerate -m "add telefono to empresa"
```

Esto crea un nuevo archivo en `versions/` con los cambios detectados.

### 3. Revisar la migración generada

Alembic no es perfecto. A veces detecta cambios incorrectos o se salta algunos. **Siempre** hay que revisar el archivo generado antes de aplicarlo.

### 4. Aplicar la migración

```bash
alembic upgrade head
```

`head` significa "hasta la última versión disponible".

### 5. Si algo sale mal

```bash
alembic downgrade -1  # Retrocede una versión
```

---

## Versiones en la BD

Alembic mantiene una tabla `alembic_version` en la BD:

```
revision
────────────
3e03f2cf94fe
```

Cuando ejecutas `alembic upgrade head`, Alembic:
1. Lee la versión actual de `alembic_version`
2. Busca el camino desde esa versión hasta `head`
3. Ejecuta todos los `upgrade()` en orden
4. Actualiza `alembic_version` con la última revisión

Si la tabla no existe (primera ejecución), Alembic la crea automáticamente.
