# Resumen de la Fase 0 — Setup del proyecto

## ¿Qué se ha hecho?

La Fase 0 consistió en montar todo el andamiaje del proyecto: desde la estructura de directorios hasta tener un flujo de autenticación funcional (registro → login → perfil).

---

## 1. Estructura de directorios

Se creó la carpeta `server/` con la siguiente organización interna:

```
server/
├── run.py                  ← Punto de entrada de la aplicación
├── requirements.txt        ← Dependencias Python
└── app/
    ├── __init__.py
    ├── core/               ← Configuración general
    │   ├── config.py       ← Variables de entorno (Settings)
    │   ├── database.py     ← Engine asíncrono + sesión SQLAlchemy
    │   ├── security.py     ← bcrypt + JWT
    │   └── dependencies.py ← Dependencias para FastAPI
    ├── models/             ← Modelos SQLAlchemy (1 por archivo)
    ├── schemas/            ← Schemas Pydantic
    ├── services/           ← Lógica de negocio
    └── api/
        └── v1/             ← Endpoints REST
```

**¿Por qué separar core/, models/, services/, api/?** Para mantener separación de responsabilidades:
- `core/` — configuraciones e infraestructura general
- `models/` — definición de la base de datos
- `schemas/` — validación de datos de entrada/salida
- `services/` — reglas de negocio
- `api/` — rutas HTTP

---

## 2. Punto de entrada (`run.py`)

Crea la aplicación FastAPI, configura CORS (para que el frontend en localhost:5173 pueda hablar con el backend en localhost:8004), monta los routers y arranca la aplicación.

**Detalle importante:** originalmente se llamó `server/app.py`, pero se renombró a `run.py` porque al tener un paquete `server/app/` (el directorio), Python da prioridad al paquete sobre el archivo `app.py`.

---

## 3. Capa Core

### config.py
Usa **Pydantic Settings** para leer las variables de entorno desde un archivo `.env`:

| Variable | Qué configura |
|---|---|
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | Conexión a MySQL |
| `JWT_SECRET`, `JWT_ACCESS_EXPIRE`, `JWT_REFRESH_EXPIRE` | Generación de tokens JWT |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` | Envío de correos (módulo Tickets) |

**¿Por qué Pydantic Settings?** Valida tipos automáticamente y permite tener valores por defecto. Si olvidas una variable, te avisa en el arranque.

### database.py
Crea el engine asíncrono de SQLAlchemy usando **aiomysql** (driver MySQL asíncrono).

**¿Por qué async?** FastAPI soporta peticiones asíncronas de forma nativa. Usar async evita bloquear el servidor mientras espera respuesta de la BD.

**Componentes creados:**
- `engine` — conexión a la BD
- `async_session` — fábrica de sesiones
- `Base` — clase base declarativa para los modelos
- `get_db()` — generador async que da una sesión y la cierra al terminar

### security.py
Dos sistemas de seguridad:

1. **bcrypt** — para hash de contraseñas (hash_contrasena, verificar_contrasena)
2. **JWT** — para tokens de acceso (crear_access_token, crear_refresh_token, decodificar_token)

**Detalle:** bcrypt tuvo que ser versionado a `<5.0.0` porque la versión 5 rompe la compatibilidad con passlib. Se usa bcrypt directamente (no passlib) para evitar dependencias problemáticas.

### dependencies.py
Dependencias reutilizables para los endpoints de FastAPI:

- `get_db` — inyecta una sesión de BD
- `get_usuario_actual` — extrae el usuario del JWT, falla si no es válido
- `get_tenant_filter` — prepara el filtro multi-tenant por empresa

---

## 4. Modelos SQLAlchemy (8 tablas)

Se creó un archivo por modelo para mantener el código ordenado:

| Archivo | Tabla | Propósito |
|---|---|---|
| `empresa.py` | `empresa` | Clientes del sistema multi-tenant |
| `empresa_servicio.py` | `empresa_servicios` | Feature flags por empresa |
| `usuario.py` | `usuario` | Usuarios del sistema |
| `tarea.py` | `tareas` | Tareas Scrum (kanban) |
| `documento.py` | `documentos` | Archivos DPD/ISO |
| `documento_permiso.py` | `documento_permisos` | Permisos por documento |
| `ticket.py` | `tickets` | Incidencias/consultas |
| `fichaje.py` | `fichajes` | Registro horario |

**¿Por qué un archivo por modelo y no todo en `models.py`?** Porque con 8+ modelos, un solo archivo se vuelve difícil de mantener y genera conflictos en git. Cada modelo es independiente y fácil de localizar.

---

## 5. Migración con Alembic

Se configuró **Alembic** para manejar migraciones de la base de datos:

- `alembic.ini` — configuración general
- `env.py` modificado para usar el engine asíncrono (con `asyncio.run()`)
- Migración inicial generada con las 8 tablas

**Comandos ejecutados:**
```
alembic revision --autogenerate -m "init"   ← genera la migración
alembic upgrade head                         ← la aplica a MySQL
```

---

## 6. Autenticación (Auth)

### Schemas Pydantic
- `RegisterRequest` — correo, contraseña, nombre, código de empresa
- `LoginRequest` — correo, contraseña
- `TokenResponse` — access_token, refresh_token, token_type
- `UsuarioResponse` — datos del usuario (sin contraseña)

### Servicio Auth
- `registrar_usuario()` — verifica que el correo no exista, hashea la contraseña, crea el usuario
- `iniciar_sesion()` — busca por correo, verifica contraseña, genera tokens

### Endpoints
| Método | Ruta | Qué hace |
|---|---|---|
| POST | `/auth/register` | Crea un nuevo usuario |
| POST | `/auth/login` | Inicia sesión, devuelve tokens |
| POST | `/auth/refresh` | Renueva el access token con el refresh token |
| GET | `/auth/me` | Devuelve datos del usuario autenticado |

### Problema resuelto: JWT exige "sub" como string
El estándar JWT dicta que el claim `sub` (subject) debe ser un string. python-jose lanza un error si se pasa un entero. Se corrigió usando `str(codigo_usuario)` al crear el token y `int(sub)` al leerlo.

---

## 7. Frontend React

### Dependencias
Se añadieron `react-router-dom` (para navegación SPA) y `axios` (para peticiones HTTP).

### Archivos creados

| Archivo | Función |
|---|---|
| `api/axios.js` | Instancia de axios con interceptor que adjunta el JWT y maneja refresh automático |
| `context/AuthContext.jsx` | Estado global de autenticación (usuario, login, logout) |
| `pages/Login.jsx` | Formulario de inicio de sesión |
| `pages/Register.jsx` | Formulario de registro |
| `pages/Dashboard.jsx` | Página principal post-login |
| `components/Layout.jsx` | Layout base con `<Outlet />` de React Router |
| `components/ProtectedRoute.jsx` | Redirige a `/login` si no hay sesión |
| `App.jsx` | Configuración de rutas |
| `index.css` | Estilos básicos |

---

## 8. Docker para MySQL

Se usó `docker-compose.yml` para levantar MySQL 8.0:

```yaml
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: byteredapp
    ports:
      - "3306:3306"
```

**¿Por qué Docker?** Aislamiento: la BD corre en un contenedor sin instalar MySQL directamente en el sistema. Se puede destruir y recrear fácilmente.

---

## Verificación final

Se probó el flujo completo:
1. Crear empresa en BD
2. Registrar usuario → 201 Created
3. Iniciar sesión → JWT devuelto
4. Obtener perfil con JWT → datos del usuario

Todo funciona correctamente.
