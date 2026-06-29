# Servicios del Backend — Explicación Didáctica

## ¿Qué son los servicios?

En una arquitectura limpia, los **servicios** son la capa intermedia entre los routers (controladores) y los modelos (base de datos). Contienen la lógica de negocio: las reglas que definen cómo se crean, modifican, consultan y eliminan los datos. Los routers llaman a los servicios, y los servicios usan los modelos para interactuar con MySQL.

Todos los servicios comparten un patrón común:
- Reciben una sesión de base de datos (`db: AsyncSession`)
- Usan SQLAlchemy `select()` para construir consultas
- Filtran siempre por `codigo_empresa` (multi-tenant)
- Usan `model_dump()` de Pydantic para convertir datos de entrada
- Lanzan `HTTPException` si algo no se encuentra

---

## 1. `scrum_service.py` — Gestión de tareas y sprints

Este servicio implementa el corazón del módulo Scrum con tablero Kanban. Sus responsabilidades:

### Tareas
- **`listar_tareas()`**: Consulta todas las tareas de una empresa, opcionalmente filtradas por sprint. Las ordena por `columna` y `orden` para que el tablero las muestre correctamente.
- **`obtener_tablero()`**: Agrupa las tareas en un diccionario con 4 claves (`Todo`, `Haciendose`, `En revision`, `Done`) — esto es justo lo que necesita el frontend para pintar las columnas del Kanban.
- **`crear_tarea()`**: Crea una tarea a partir de un schema Pydantic. Usa `model_dump()` para convertir el schema en diccionario y lo pasa como kwargs al constructor del modelo.
- **`obtener_tarea()`**: Busca por ID, pero siempre filtrando también por empresa. Devuelve 404 si no existe.
- **`actualizar_tarea()`**: Actualización parcial: solo modifica los campos enviados en el body (PATCH semantics). Usa `exclude_unset=True` para ignorar campos no enviados.
- **`mover_tarea()`**: Endpoint específico para drag & drop. Solo cambia `columna` y `orden` — así el frontend puede arrastrar tarjetas sin enviar todo el objeto tarea.
- **`eliminar_tarea()`**: Borra la tarea de la BD.

### Sprints
- Los 5 métodos (`listar`, `crear`, `obtener`, `actualizar`, `eliminar`) siguen exactamente el mismo patrón que las tareas. El multi-tenant se aplica igual: cada sprint pertenece a una empresa.

---

## 2. `ticket_service.py` — Tickets de soporte

Gestiona el formulario de contacto/soporte. Puntos clave:

- **`crear_ticket()`**: Acepta un `codigo_usuario` opcional (None = ticket anónimo). Después de guardar, intenta enviar un email de notificación al administrador si SMTP está configurado. El email se envía con los datos básicos del ticket (asunto, contacto, importancia, mensaje).
- **`listar_tickets()`**: Lista todos los tickets de una empresa, ordenados por fecha descendente.
- **`obtener_ticket()`**: Filtra por `id_reporte` + `codigo_empresa` (protección multi-tenant).
- **`actualizar_estado_ticket()`**: Cambia el estado del ticket (Pendiente → Leido → Respondido → Cerrado). Es el único campo modificable después de creado.

---

## 3. `email_service.py` — Envío de correos

Servicio auxiliar para enviar emails vía SMTP con TLS:

- Si SMTP no está configurado (`SMTP_HOST` vacío), falla silenciosamente con un warning en log. Esto permite que la app funcione sin email configurado.
- Usa `starttls()` para cifrar la conexión antes de autenticar.
- Nunca propaga excepciones al usuario: si el email falla, se loguea el error y se devuelve `False`. El flujo principal no se interrumpe.

---

## 4. `documento_service.py` — Subida, descarga y permisos de documentos

Este es el servicio más completo. Gestiona archivos (DPD/ISO) con un sistema de permisos granular.

### Subida de documentos
- Crea carpetas por empresa en `server/uploads/`.
- Genera un nombre único con `uuid.uuid4().hex` para evitar colisiones y path traversal.
- Guarda el archivo en disco y los metadatos (nombre original, tipo, fecha, ruta relativa) en la BD.

### Listado con permisos
- **`listar_documentos()`**: Si el usuario es admin, ve todos los documentos de la empresa. Si no, solo ve los que él subió o aquellos para los que tiene permiso explícito en `documento_permisos`.
- Usa una subquery para obtener los IDs de documentos con permiso.

### Permisos
- **`agregar_permiso()` / `quitar_permiso()`**: CRUD básico sobre `DocumentoPermiso`. Captura excepciones de integridad (permiso duplicado).

### Descarga
- **`obtener_ruta_archivo()`**: Devuelve la ruta absoluta del archivo para que FastAPI lo sirva como `FileResponse`.

---

## 5. `fichaje_service.py` — Control horario (entrada/salida)

Lógica simple pero con una regla de negocio importante:

- **`registrar_entrada()`**: Crea un fichaje con `hora_salida = NULL` (abierto).
- **`registrar_salida()`**: Busca el fichaje abierto más reciente del usuario (el único con `hora_salida IS NULL`) y le asigna la hora actual. Si no hay fichaje abierto, lanza 404.
- **`listar_fichajes()`**: Historial completo del usuario en su empresa.
- **`fichaje_abierto()`**: Verifica si hay un fichaje sin salida. Se usa en el router para prevenir doble entrada.

---

## 6. `admin_service.py` — Administración de empresas, usuarios y servicios

### Empresas
- CRUD completo con verificación de existencia. Al crear una empresa, se activan automáticamente los 5 servicios por defecto (scrum, tickets, documentacion, fichaje, redireccion). Usa `db.flush()` para obtener el ID antes de crear los servicios.

### Usuarios
- **`crear_usuario_admin()`**: Valida email único y que la empresa exista antes de crear. Hashea la contraseña.
- **`listar_usuarios()`**: Puede listar todos o filtrar por empresa.
- Actualización parcial con `exclude_unset=True`.

### Servicios (feature flags)
- **`listar_servicios()`**: Devuelve los servicios de una empresa.
- **`toggle_servicio()`**: Lógica upsert: si el servicio ya existe, actualiza el estado; si no, lo crea. Esto permite activar/desactivar módulos dinámicamente.

---

## Patrones comunes en todos los servicios

| Patrón | Descripción |
|---|---|
| **AsyncSession** | Todas las operaciones son asíncronas con `async/await` |
| **Filtro multi-tenant** | Cada query incluye `WHERE codigo_empresa = ?` |
| **HTTPException** | Errores controlados con mensajes y códigos HTTP |
| **model_dump()** | Convierte schemas Pydantic a diccionarios |
| **exclude_unset=True** | Solo actualiza campos enviados (PATCH semantics) |
| **db.refresh()** | Recarga el objeto después de commit para obtener valores generados |
