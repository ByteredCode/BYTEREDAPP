# Explicación de los modelos SQLAlchemy

## Visión general

Hay **8 modelos** que representan las tablas de la base de datos. Cada modelo hereda de `Base` (definido en `core/database.py`) y mapea una tabla en MySQL.

**¿Por qué un archivo por modelo?** Cuando un equipo trabaja en paralelo, tener todos los modelos en un solo archivo genera conflictos en git. Con un archivo por modelo, dos personas pueden modificar `usuario.py` y `tarea.py` sin pisarse.

---

## models/**init**.py — Fábrica de importaciones

```python
from app.models.empresa import Empresa
from app.models.empresa_servicio import EmpresaServicio
from app.models.usuario import Usuario
from app.models.tarea import Tarea
from app.models.documento import Documento
from app.models.documento_permiso import DocumentoPermiso
from app.models.ticket import Ticket
from app.models.fichaje import Fichaje

__all__ = ["Empresa", "EmpresaServicio", "Usuario", "Tarea", "Documento",
           "DocumentoPermiso", "Ticket", "Fichaje"]
```

Facilita la importación: en lugar de importar cada modelo individual, puedes hacer `from app.models import Usuario, Tarea`. Alembic también usa este `__init__` para detectar todos los modelos al autogenerar migraciones.

---

## modelos/empresa.py — La empresa (tenant)

```python
class Empresa(Base):
    __tablename__ = "empresa"

    codigo_empresa = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    codigo_scrum = Column(String(100))
    usuario_admin_dpd = Column(Integer)
    web = Column(String(255))

    usuarios = relationship("Usuario", back_populates="empresa")
    tareas = relationship("Tarea", back_populates="empresa")
    documentos = relationship("Documento", back_populates="empresa")
    tickets = relationship("Ticket", back_populates="empresa")
    fichajes = relationship("Fichaje", back_populates="empresa")
    servicios = relationship("EmpresaServicio", back_populates="empresa", cascade="all, delete-orphan")
```

### ¿Qué representa?

Cada fila de `empresa` es un **cliente** del sistema multi-tenant. Cuando un usuario se registra, se asocia a una empresa mediante `codigo_empresa`.

### Columnas especiales

- **codigo_scrum**: Identificador para el módulo Scrum (ej: tablero Kanban). Opcional.
- **usuario_admin_dpd**: ID del usuario que administra los documentos DPD/ISO. Opcional.
- **web**: URL de la página externa de la empresa para el módulo de redirección.

### Relaciones con cascade

```python
servicios = relationship("EmpresaServicio", back_populates="empresa", cascade="all, delete-orphan")
```

`cascade="all, delete-orphan"` significa: si borras la empresa, SQLAlchemy borrará automáticamente sus servicios asociados en Python. Además, la FK tiene `ondelete="CASCADE"` en la BD, así que también se borran a nivel SQL. Las otras relaciones (usuarios, tareas...) no tienen cascade en Python, pero sí tienen `ondelete="CASCADE"` en la FK a nivel BD.

---

## modelos/empresa_servicio.py — Feature flags

```python
class EmpresaServicio(Base):
    __tablename__ = "empresa_servicios"

    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa", ondelete="CASCADE"), primary_key=True)
    servicio = Column(String(50), primary_key=True)
    activo = Column(Boolean, default=True)

    empresa = relationship("Empresa", back_populates="servicios")
```

### Clave primaria compuesta

```python
codigo_empresa = Column(..., primary_key=True)
servicio = Column(..., primary_key=True)
```

Dos columnas forman la PK. Esto significa que no puede haber dos filas con el mismo `codigo_empresa` + `servicio`.

### ¿Qué es un feature flag?

Cada empresa paga por ciertos módulos (Scrum, Tickets, Documentos...). `empresa_servicios` almacena qué módulos tiene activos cada empresa. Ejemplo:

| codigo_empresa | servicio | activo |
|---|---|---|
| 1 | scrum | true |
| 1 | tickets | false |
| 2 | scrum | true |
| 2 | tickets | true |

La empresa 1 tiene Scrum pero no Tickets; la empresa 2 tiene ambos.

---

## modelos/usuario.py — Usuarios del sistema

```python
class Usuario(Base):
    __tablename__ = "usuario"

    codigo_usuario = Column(Integer, primary_key=True, autoincrement=True)
    correo = Column(String(150), nullable=False, unique=True)
    contrasena = Column(String(255), nullable=False)
    nombre = Column(String(150), nullable=False)
    rol = Column(SAEnum("admin_total", "admin_empresa", "usuario", name="rol_enum"), nullable=False, default="usuario")
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa", ondelete="CASCADE"), nullable=False)

    empresa = relationship("Empresa", back_populates="usuarios")
```

### Enumeración de roles

```python
SAEnum("admin_total", "admin_empresa", "usuario", name="rol_enum")
```

`SAEnum` (renombrado para no confundir con el `Enum` de Python) crea una columna ENUM en MySQL:

- **admin_total**: Superadministrador, ve todas las empresas
- **admin_empresa**: Administrador de una empresa, gestiona usuarios y configuración
- **usuario**: Usuario normal, solo usa los módulos asignados

### UniqueConstraint

```python
correo = Column(String(150), nullable=False, unique=True)
```

No puede haber dos usuarios con el mismo correo (ni siquiera en empresas diferentes). Esto es intencional: el correo es el identificador único para login.

### ¿Por qué `contrasena` es de 255 caracteres?

El hash de bcrypt tiene una longitud fija de 60 caracteres. Pero si en el futuro cambiamos a argon2, el hash puede ser más largo. 255 es un margen seguro.

---

## modelos/tarea.py — Tareas Scrum

```python
class Tarea(Base):
    __tablename__ = "tareas"

    codigo_tarea = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    asignacion = Column(Integer, ForeignKey("usuario.codigo_usuario", ondelete="SET NULL"))
    columna = Column(SAEnum("Todo", "Haciendose", "En revision", "Done", name="columna_enum"), default="Todo")
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa", ondelete="CASCADE"), nullable=False)

    empresa = relationship("Empresa", back_populates="tareas")
```

### Columnas del kanban

Las columnas imitan un tablero Kanban:
- **Todo** — Por hacer
- **Haciendose** — En progreso
- **En revision** — En revisión (pendiente de aprobación)
- **Done** — Terminado

### ondelete="SET NULL"

Si se borra un usuario, las tareas asignadas a él no se borran. En lugar de eso, `asignacion` pasa a ser `NULL`. La tarea queda sin asignar, pero no se pierde.

---

## modelos/documento.py — Documentos DPD/ISO

```python
class Documento(Base):
    __tablename__ = "documentos"

    id_documento = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa", ondelete="CASCADE"), nullable=False)
    usuario_subio = Column(Integer, ForeignKey("usuario.codigo_usuario"), nullable=False)
    fecha = Column(Date, nullable=False)
    ruta_archivo = Column(String(255))
    tipo_documento = Column(SAEnum("DPD", "ISO", name="tipo_doc_enum"))
```

### Tipo de documento

- **DPD**: Documento de Protección de Datos (RGPD/LOPD)
- **ISO**: Documento de calidad (normas ISO)

### Ruta de archivo

`ruta_archivo` almacena la ruta en el sistema de archivos donde se guardó el documento subido. El archivo no se guarda en la BD (la BD solo almacena metadatos). Esto es una práctica recomendada.

---

## modelos/documento_permiso.py — Permisos de documentos

```python
class DocumentoPermiso(Base):
    __tablename__ = "documento_permisos"

    id_documento = Column(Integer, ForeignKey("documentos.id_documento", ondelete="CASCADE"), primary_key=True)
    codigo_usuario = Column(Integer, ForeignKey("usuario.codigo_usuario", ondelete="CASCADE"), primary_key=True)
```

### Clave primaria compuesta bidireccional

Ambas columnas son PK y ambas son FK. Esto crea una **tabla de relación muchos a muchos** entre documentos y usuarios.

Cada fila significa "el usuario X tiene permiso para ver el documento Y". Si no hay fila, no tiene permiso.

### ¿Por qué no hay columna de tipo de permiso?

En este diseño, el permiso es binario: o tienes acceso o no. No hay permisos de solo lectura vs. edición. Simplifica la implementación.

---

## modelos/ticket.py — Incidencias (Tickets)

```python
class Ticket(Base):
    __tablename__ = "tickets"

    id_reporte = Column(Integer, primary_key=True, autoincrement=True)
    codigo_usuario = Column(Integer, ForeignKey("usuario.codigo_usuario", ondelete="CASCADE"), nullable=False)
    nivel_importancia = Column(SAEnum("Baja", "Media", "Alta", "Critica", name="importancia_enum"), nullable=False)
    mensaje = Column(Text, nullable=False)
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa", ondelete="CASCADE"), nullable=False)
    estado = Column(SAEnum("Pendiente", "Leido", "Respondido", "Cerrado", name="estado_ticket_enum"), default="Pendiente")
    fecha_reporte = Column(DateTime, server_default=func.current_timestamp())
```

### Fecha automática

```python
fecha_reporte = Column(DateTime, server_default=func.current_timestamp())
```

`server_default=func.current_timestamp()` hace que MySQL ponga la fecha y hora actual automáticamente al insertar. No hace falta enviarla desde el código.

### Estados del ticket

- **Pendiente**: Acabado de crear, nadie lo ha visto
- **Leido**: Un administrador lo ha abierto
- **Respondido**: Se ha contestado al usuario
- **Cerrado**: El usuario confirmó o el administrador lo cerró

---

## modelos/fichaje.py — Control horario

```python
class Fichaje(Base):
    __tablename__ = "fichajes"

    id_fichaje = Column(Integer, primary_key=True, autoincrement=True)
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa", ondelete="CASCADE"), nullable=False)
    codigo_usuario = Column(Integer, ForeignKey("usuario.codigo_usuario", ondelete="CASCADE"), nullable=False)
    hora_entrada = Column(DateTime, nullable=False)
    hora_salida = Column(DateTime)
```

### ¿Cómo funciona el fichaje?

Cada día, cuando un usuario hace login, se crea un registro con `hora_entrada` = ahora. Cuando hace logout, se actualiza `hora_salida` con la hora actual. Si `hora_salida` es NULL, significa que el usuario sigue "fichado".

### Diseño simple

Una sola tabla que almacena cada registro de entrada/salida. No hay tabla separada para "sesiones". Esto facilita generar informes: "¿cuántas horas trabajó el usuario X en enero?" se responde con una consulta simple.

---

## Relaciones entre modelos (diagrama mental)

```
empresa ──┬── empresa_servicios  (1:N — una empresa tiene muchos servicios)
          ├── usuario              (1:N — una empresa tiene muchos usuarios)
          ├── tarea                (1:N — una empresa tiene muchas tareas)
          ├── documento ─── documento_permiso  (1:N — un documento tiene muchos permisos)
          ├── ticket               (1:N — una empresa tiene muchos tickets)
          └── fichaje              (1:N — una empresa tiene muchos fichajes)

usuario ──┬── tarea (asignacion)  (1:N — un usuario puede tener muchas tareas asignadas)
          ├── documento (usuario_subio)  (1:N — un usuario subió muchos documentos)
          ├── documento_permiso   (1:N — un usuario tiene permisos sobre documentos)
          ├── ticket              (1:N — un usuario reportó muchos tickets)
          └── fichaje             (1:N — un usuario tiene muchos fichajes)
```
