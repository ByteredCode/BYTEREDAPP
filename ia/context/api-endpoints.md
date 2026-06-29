# Endpoints de la API

Base URL: `http://localhost:8000`

Autenticación: JWT en header `Authorization: Bearer <token>`

## Auth (`/auth`)

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| POST | `/auth/register` | Registrar nuevo usuario | No |
| POST | `/auth/login` | Iniciar sesión (devuelve JWT) | No |
| POST | `/auth/refresh` | Refrescar token | Refresh token |
| GET | `/auth/me` | Obtener perfil del usuario actual | Sí |

## Admin (`/admin`) — Admin CRUD completo

Protegido por rol: `admin_total` o `admin_empresa` según el endpoint.

| Método | Ruta | Descripción | Rol |
|---|---|---|---|
| GET | `/admin/empresas` | Listar todas las empresas | admin_total |
| POST | `/admin/empresas` | Crear empresa + 5 feature flags por defecto | admin_total |
| GET | `/admin/empresas/{id}` | Obtener empresa | admin_total / admin_empresa (solo su empresa) |
| PUT | `/admin/empresas/{id}` | Actualizar empresa | admin_total |
| DELETE | `/admin/empresas/{id}` | Eliminar empresa | admin_total |
| GET | `/admin/empresas/{id}/usuarios` | Listar usuarios de una empresa | admin_total / admin_empresa (solo su empresa) |
| GET | `/admin/empresas/{id}/servicios` | Listar feature flags de una empresa | admin_total / admin_empresa (solo su empresa) |
| PUT | `/admin/empresas/{id}/servicios` | Activar/desactivar servicio | admin_total |
| GET | `/admin/usuarios` | Listar usuarios (admin_total: todos, admin_empresa: su empresa) | admin_total / admin_empresa |
| POST | `/admin/usuarios` | Crear usuario | admin_total / admin_empresa |
| PUT | `/admin/usuarios/{id}` | Actualizar usuario | admin_total / admin_empresa |
| DELETE | `/admin/usuarios/{id}` | Eliminar usuario | admin_total / admin_empresa |

### Feature flags por empresa (servicios)

| Servicio | Descripción |
|---|---|
| `scrum` | Kanban de tareas |
| `tickets` | Formulario de incidencias |
| `documentacion` | Repositorio DPD/ISO |
| `fichaje` | Control horario |
| `redireccion` | Enlace a web externa |

## Tareas (`/tasks`) — Scrum (futuro)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/tasks` | Listar tareas de la empresa |
| POST | `/tasks` | Crear tarea |
| GET | `/tasks/{id}` | Obtener tarea |
| PUT | `/tasks/{id}` | Actualizar tarea (incluye mover columna) |
| DELETE | `/tasks/{id}` | Eliminar tarea |

## Documentos (`/documents`) — DPD/ISO (futuro)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/documents` | Listar documentos accesibles |
| POST | `/documents` | Subir documento |
| GET | `/documents/{id}` | Obtener documento |
| DELETE | `/documents/{id}` | Eliminar documento |
| GET | `/documents/{id}/permissions` | Ver permisos del documento |
| POST | `/documents/{id}/permissions` | Añadir permiso a usuario |
| DELETE | `/documents/{id}/permissions/{userId}` | Revocar permiso |

## Tickets (`/tickets`) — futuro

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/tickets` | Crear ticket (público o autenticado) |
| GET | `/tickets` | Listar tickets (empresa o admin) |
| GET | `/tickets/{id}` | Obtener ticket |
| PUT | `/tickets/{id}/status` | Actualizar estado del ticket |

## Fichajes (`/fichajes`) — futuro

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/fichajes` | Histórico de fichajes del usuario |
| POST | `/fichajes/entrada` | Registrar hora de entrada |
| PUT | `/fichajes/{id}/salida` | Registrar hora de salida |
