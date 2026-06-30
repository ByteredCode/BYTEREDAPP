# Endpoints de la API

Base URL: `http://localhost:8000/api/v1`

Autenticación: JWT en header `Authorization: Bearer <token>`

## Auth (`/auth`)

| Método | Ruta | Descripción | Auth | Rate limit |
|--------|------|-------------|------|------------|
| POST | `/auth/register` | Registrar nuevo usuario | No | 10/min |
| POST | `/auth/login` | Iniciar sesión (devuelve JWT + auto-fichaje) | No | 10/min |
| POST | `/auth/refresh` | Refrescar token (rotación: invalida anterior) | Refresh token | No |
| POST | `/auth/logout` | Cerrar sesión (invalida refresh + access tokens) | Sí | No |
| GET | `/auth/me` | Obtener perfil del usuario actual | Sí | No |

## Admin (`/admin`)

Protegido por rol: `admin_total` o `admin_empresa` según el endpoint.

| Método | Ruta | Descripción | Rol | Paginación |
|--------|------|-------------|-----|------------|
| GET | `/admin/empresas` | Listar empresas | admin_total | skip, limit |
| POST | `/admin/empresas` | Crear empresa + feature flags por defecto | admin_total | No |
| GET | `/admin/empresas/{id}` | Obtener empresa | admin_total / admin_empresa | No |
| PUT | `/admin/empresas/{id}` | Actualizar empresa | admin_total | No |
| DELETE | `/admin/empresas/{id}` | Eliminar empresa | admin_total | No |
| GET | `/admin/empresas/{id}/usuarios` | Listar usuarios de una empresa | admin_total / admin_empresa | skip, limit |
| GET | `/admin/empresas/{id}/servicios` | Listar feature flags | admin_total / admin_empresa | No |
| PUT | `/admin/empresas/{id}/servicios` | Activar/desactivar servicio | admin_total | No |
| GET | `/admin/usuarios` | Listar usuarios (global o por empresa) | admin_total / admin_empresa | skip, limit |
| POST | `/admin/usuarios` | Crear usuario | admin_total / admin_empresa | No |
| PUT | `/admin/usuarios/{id}` | Actualizar usuario | admin_total / admin_empresa | No |
| DELETE | `/admin/usuarios/{id}` | Eliminar usuario | admin_total / admin_empresa | No |
| GET | `/admin/stats` | Estadísticas del dashboard | admin_total / admin_empresa | No |

## Empresa (`/empresa`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/empresa/mi-empresa` | Datos de la empresa del usuario autenticado |
| PATCH | `/empresa/mi-empresa` | Actualizar datos de la propia empresa |

## Scrum (`/scrum`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/scrum/tablero` | Tablero Kanban (tareas agrupadas por columna) |
| GET | `/scrum/tareas` | Listar tareas |
| POST | `/scrum/tareas` | Crear tarea |
| GET | `/scrum/tareas/{id}` | Obtener tarea |
| PUT | `/scrum/tareas/{id}` | Actualizar tarea |
| DELETE | `/scrum/tareas/{id}` | Eliminar tarea |
| PUT | `/scrum/tareas/{id}/mover` | Mover tarea de columna/posición |
| GET | `/scrum/sprints` | Listar sprints |
| POST | `/scrum/sprints` | Crear sprint |
| PUT | `/scrum/sprints/{id}` | Actualizar sprint |
| DELETE | `/scrum/sprints/{id}` | Eliminar sprint |

## Tickets (`/tickets`)

| Método | Ruta | Descripción | Auth | Rate limit |
|--------|------|-------------|------|------------|
| POST | `/tickets` | Crear ticket (público o autenticado) | Opcional | 10/min |
| GET | `/tickets` | Listar tickets de la empresa | Sí | No |
| GET | `/tickets/{id}` | Obtener ticket | Sí | No |
| PUT | `/tickets/{id}/estado` | Cambiar estado + responder | Sí (admin) | No |

## Documentos (`/documentos`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/documentos` | Listar documentos accesibles |
| POST | `/documentos` | Subir documento (multipart) |
| GET | `/documentos/{id}/descargar` | Descargar archivo |
| DELETE | `/documentos/{id}` | Eliminar documento |
| GET | `/documentos/{id}/permisos` | Ver permisos del documento |
| POST | `/documentos/{id}/permisos` | Añadir permiso a usuario |
| DELETE | `/documentos/{id}/permisos/{user_id}` | Revocar permiso |

## Fichajes (`/fichajes`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/fichajes` | Histórico de fichajes del usuario |
| GET | `/fichajes/actual` | Fichaje abierto (entrada sin salida) |
| GET | `/fichajes/resumen` | Estadísticas (hoy, semana, mes) |
| POST | `/fichajes/salida` | Registrar hora de salida |
| GET | `/fichajes/exportar` | Exportar CSV |

## Redirección (`/redireccion`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/redireccion/{codigo}` | Redirigir a web de la empresa por código |

## Health

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check |
