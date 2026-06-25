# Endpoints de la API

Base URL: `http://localhost:8000/api/v1`

Autenticación: JWT en header `Authorization: Bearer <token>`

## Auth (`/auth`)

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| POST | `/auth/register` | Registrar nuevo usuario | No |
| POST | `/auth/login` | Iniciar sesión (devuelve JWT + registra fichaje) | No |
| POST | `/auth/refresh` | Refrescar token | Refresh token |
| GET | `/auth/me` | Obtener perfil del usuario actual | Sí |

## Empresas (`/companies`) — Solo admin_total

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/companies` | Listar todas las empresas |
| POST | `/companies` | Crear empresa |
| GET | `/companies/{id}` | Obtener empresa |
| PUT | `/companies/{id}` | Actualizar empresa |
| DELETE | `/companies/{id}` | Eliminar empresa |
| GET | `/companies/{id}/services` | Obtener servicios de la empresa |
| PUT | `/companies/{id}/services` | Actualizar servicios (feature flags) |

## Usuarios (`/users`)

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| GET | `/users` | Listar usuarios (admin_total: todos, admin_empresa: su empresa) | Sí |
| POST | `/users` | Crear usuario en la empresa | Sí |
| GET | `/users/{id}` | Obtener usuario | Sí |
| PUT | `/users/{id}` | Actualizar usuario | Sí |
| DELETE | `/users/{id}` | Eliminar usuario | admin_total/admin_empresa |

## Tareas (`/tasks`) — Scrum

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/tasks` | Listar tareas de la empresa |
| POST | `/tasks` | Crear tarea |
| GET | `/tasks/{id}` | Obtener tarea |
| PUT | `/tasks/{id}` | Actualizar tarea (incluye mover columna) |
| DELETE | `/tasks/{id}` | Eliminar tarea |

## Documentos (`/documents`) — DPD/ISO

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/documents` | Listar documentos accesibles |
| POST | `/documents` | Subir documento |
| GET | `/documents/{id}` | Obtener documento |
| DELETE | `/documents/{id}` | Eliminar documento |
| GET | `/documents/{id}/permissions` | Ver permisos del documento |
| POST | `/documents/{id}/permissions` | Añadir permiso a usuario |
| DELETE | `/documents/{id}/permissions/{userId}` | Revocar permiso |

## Tickets (`/tickets`)

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/tickets` | Crear ticket (público o autenticado) |
| GET | `/tickets` | Listar tickets (empresa o admin) |
| GET | `/tickets/{id}` | Obtener ticket |
| PUT | `/tickets/{id}/status` | Actualizar estado del ticket |

## Fichajes (`/fichajes`)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/fichajes` | Histórico de fichajes del usuario |
| POST | `/fichajes/entrada` | Registrar hora de entrada |
| PUT | `/fichajes/{id}/salida` | Registrar hora de salida |

## Admin (`/admin`) — Solo admin_total

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/admin/stats` | Estadísticas generales |
| GET | `/admin/audit` | Registro de actividad |
