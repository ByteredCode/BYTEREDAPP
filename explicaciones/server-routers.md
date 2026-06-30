# Routers de la API — Explicación Didáctica

## ¿Qué son los routers?

En FastAPI, los routers son **controladores** que agrupan endpoints relacionados. Cada router tiene un prefijo (`/scrum`, `/tickets`, etc.) y etiquetas para la documentación Swagger. Los routers reciben las peticiones HTTP, delegan la lógica a los servicios y devuelven respuestas.

Todos los routers comparten:
- Dependencias de inyección: `Depends(get_db)` para la sesión de BD, `Depends(get_tenant_filter)` para multi-tenant
- Validación automática mediante schemas Pydantic
- Códigos de estado HTTP estándar (201 para creación, 204 para borrado)

---

## 1. `auth.py` — Autenticación (prefijo `/auth`)

### `POST /auth/register` — Registro de usuario
- Recibe `RegisterRequest` (correo, contraseña, nombre, empresa).
- Llama a `registrar_usuario()` que verifica email único y hashea la contraseña.
- Devuelve `UsuarioResponse` (sin contraseña, obviamente).

### `POST /auth/login` — Inicio de sesión
- Recibe credenciales, llama a `iniciar_sesion()` que verifica contraseña y genera JWT.
- **Side effect**: registra automáticamente un fichaje de entrada al hacer login. Si falla, no bloquea el login.
- Devuelve `TokenResponse` (access + refresh tokens).

### `POST /auth/refresh` — Renovar tokens
- Recibe el refresh token en el body. Lo decodifica, verifica que sea de tipo "refresh".
- Genera un nuevo par access + refresh.
- **Debilidad**: no invalida el refresh token anterior (no hay rotación).

### `GET /auth/me` — Datos del usuario autenticado
- Usa `Depends(get_usuario_actual)` para obtener el usuario del token.
- Útil para que el frontend verifique la sesión al cargar.

---

## 2. `scrum.py` — Módulo Scrum (prefijo `/scrum`)

Endpoints para el tablero Kanban. Todos requieren autenticación y filtro multi-tenant.

### Tablero
- `GET /scrum/tablero`: Devuelve las tareas agrupadas en 4 columnas para el Kanban.

### Tareas (CRUD + mover)
- `GET /scrum/tareas`: Lista filtrada por sprint.
- `POST /scrum/tareas`: Crea una tarea en la columna especificada.
- `GET /scrum/tareas/{id}`: Obtiene una tarea por ID.
- `PUT /scrum/tareas/{id}`: Actualización parcial.
- `PUT /scrum/tareas/{id}/mover`: Endpoint especial para drag & drop.
- `DELETE /scrum/tareas/{id}`: Elimina una tarea.

### Sprints (CRUD)
- Mismos patrones: GET list, POST, GET by id, PUT, DELETE.

**Patrón interesante**: `codigo_empresa: int = Depends(get_tenant_filter)` aparece en TODOS los endpoints. Es la clave del multi-tenant: el tenant filter extrae el `codigo_empresa` del JWT y lo inyecta automáticamente.

---

## 3. `tickets.py` — Tickets de soporte (prefijo `/tickets`)

### `POST /tickets` — Crear ticket (público)
- **NO requiere autenticación**. Intenta obtener el usuario actual pero no falla si no hay token.
- Así, usuarios anónimos pueden enviar tickets, pero si hay sesión iniciada se asocia el ticket al usuario.

### `GET /tickets` — Listar tickets (autenticado)
- Filtrado por empresa mediante `get_tenant_filter`.

### `GET /tickets/{id}` — Detalle del ticket
- Con filtro multi-tenant.

### `PUT /tickets/{id}/estado` — Cambiar estado
- Solo permite cambiar el estado del ticket.

---

## 4. `documentos.py` — Documentos DPD/ISO (prefijo `/documentos`)

### Subida y descarga
- `POST /documentos`: Sube un archivo (`UploadFile` + `Form`). Requiere autenticación.
- `GET /documentos/{id}/descargar`: Sirve el archivo como `FileResponse`.

### Listado con permisos
- `GET /documentos`: Los admins ven todos; los usuarios normales solo los propios o con permiso.

### Gestión de permisos
- `GET /documentos/{id}/permisos`: Lista quién tiene acceso.
- `POST /documentos/{id}/permisos`: Otorga permiso a un usuario.
- `DELETE /documentos/{id}/permisos/{userId}`: Revoca permiso.

---

## 5. `fichajes.py` — Control horario (prefijo `/fichajes`)

### `GET /fichajes` — Historial del usuario
### `GET /fichajes/actual` — Ver si hay fichaje abierto
### `POST /fichajes/entrada` — Registrar entrada (validación: no permite doble entrada)
### `POST /fichajes/salida` — Registrar salida

Todos usan `get_usuario_actual` para saber qué usuario está fichando.

---

## 6. `redireccion.py` — Redirección externa (público)

### `GET /r/{codigo_empresa}` — Redirige a la web de la empresa
- **Sin autenticación**: es un endpoint público (los clientes externos deben poder acceder).
- Busca la empresa por ID, obtiene su URL (`empresa.web`) y hace un redirect 302.

---

## 7. `admin.py` — Panel de administración (prefijo `/admin`)

### Empresas (solo admin_total)
- CRUD completo con verificación de rol `admin_total`.
- `GET /admin/empresas` — lista todas
- `POST /admin/empresas` — crea (activa servicios por defecto)
- `PUT/DELETE /admin/empresas/{id}` — actualiza/elimina

### Usuarios
- `GET /admin/empresas/{id}/usuarios` — usuarios de una empresa
- `GET /admin/usuarios` — admin_total ve todos, admin_empresa ve los suyos
- `POST /admin/usuarios` — admin_total puede crear en cualquier empresa, admin_empresa solo en la suya
- `PUT/DELETE /admin/usuarios/{id}` — con verificación de permisos

### Servicios
- `GET /admin/empresas/{id}/servicios` — lista servicios de una empresa
- `PUT /admin/empresas/{id}/servicios` — toggle (solo admin_total)

### Utilidad interna
- `_verificar_acceso_empresa()`: función auxiliar que permite a admin_total acceder a cualquier empresa y a admin_empresa solo a la suya.

---

## Resumen de acceso

| Router | Auth requerida | Multi-tenant | Roles |
|---|---|---|---|
| auth | Parcial | No aplica | Todos |
| scrum | Sí | Sí | Todos |
| tickets | No (POST) / Sí (GET) | Sí | Todos |
| documentos | Sí | Sí | Admins ven todo |
| fichajes | Sí | Sí | Todos (solo datos propios) |
| redireccion | No | No aplica | Público |
| admin | Sí | No aplica | admin_total / admin_empresa |
