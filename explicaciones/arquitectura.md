# Arquitectura de BYTEREDAPP

## Tipo: Monolítica modular con API REST

Un solo backend desplegable, pero organizado en **módulos independientes** (auth, scrum, tickets, docs, admin...).

**¿Por qué no microservicios?** Para un proyecto de gestión empresarial pequeña/mediana, un monolito modular es más simple de desarrollar, desplegar y mantener. La clave está en que sea **modular**: si un día hace falta partir un módulo en un servicio independiente, la separación ya existe en el código.

**Analogía:** Un edificio de apartamentos (monolito) vs casas individuales (microservicios). En el edificio compartes infraestructura (agua, electricidad), pero cada apartamento es independiente por dentro.

---

## Frontend: React + Vite (JavaScript)

| Componente | Rol |
|---|---|
| **React** | Librería para construir interfaces de usuario basadas en componentes |
| **Vite** | Bundler / dev server — reemplaza a Create React App, mucho más rápido |
| **JavaScript** (no TypeScript) | Decisión deliberada para simplificar el desarrollo inicial |

**Flujo:** El usuario interactúa con la SPA (Single Page Application). Cuando necesita datos, la app hace peticiones HTTP (con axios) al backend.

---

## Backend: FastAPI (Python 3.11+)

FastAPI es un framework web moderno con tres características clave:

1. **Async:** Soporta peticiones asíncronas de forma nativa (con `async/await`)
2. **Tipado con Pydantic:** Validación automática de datos de entrada/salida basada en tipos Python
3. **OpenAPI automático:** Genera documentación Swagger sin esfuerzo

**Python 3.11+** aporta mejoras de rendimiento y sintaxis como `Self` type, `except*`, y pattern matching.

---

## Base de datos: MySQL 8 con aislamiento multi-tenant por fila

### ¿Qué es multi-tenant?

Multi-tenant significa que **una sola instancia del sistema sirve a múltiples clientes (empresas)** , pero cada empresa solo ve sus propios datos.

### Estrategias de aislamiento

| Estrategia | Descripción | Cuándo usarla |
|---|---|---|
| **Base de datos por tenant** | Cada empresa tiene su propia BD | Alta seguridad, más coste |
| **Esquema por tenant** | Misma BD, esquemas separados | Medio |
| **Fila por tenant (Row-level)** | Misma BD, misma tabla, columna `company_id` | **La que usa este proyecto** |

BYTEREDAPP usa la estrategia **Row-level Tenant Isolation**. Cada tabla tiene una columna `company_id` (en español: `codigo_empresa`), y un middleware se encarga de **inyectar automáticamente el filtro** en cada consulta.

**Ejemplo práctico:**

```sql
-- Sin multi-tenant: ves todas las tareas de todas las empresas
SELECT * FROM tareas;

-- Con multi-tenant: solo las de tu empresa
SELECT * FROM tareas WHERE codigo_empresa = 5;
```

El **middleware** (capa intermedia en el backend) extrae el `company_id` del JWT y lo añade automáticamente a cada query, así el desarrollador no tiene que acordarse de hacerlo manualmente.

---

## Autenticación: JWT con access + refresh token

**JWT (JSON Web Token)** es un estándar para transmitir información de forma segura entre frontend y backend.

### Flujo de autenticación

```
FRONTEND                         BACKEND
   │                                │
   │──── POST /login (email, pass) ──→│
   │                                │─ Verifica credenciales
   │←── { access_token, refresh_token } ─│
   │                                │
   │──── GET /tasks (Authorization: Bearer <access_token>) ──→│
   │                                │─ Verifica JWT
   │                                │─ Extrae company_id
   │                                │─ Filtra por company_id
   │←── [tareas de su empresa] ──────│
```

### Access token vs Refresh token

| Token | Duración | Propósito |
|---|---|---|
| **Access** | 60 min (configurable) | Autenticar cada petición |
| **Refresh** | 7 días | Obtener un nuevo access token cuando expire |

**¿Por qué dos tokens?** Por seguridad. Si alguien roba el access token, solo sirve por 60 minutos. El refresh token tiene más duración pero viaja menos veces por la red.

---

## Flujo de datos

```
Usuario → React SPA → API REST (JWT) → FastAPI → Service → Model → MySQL
```

Camino que sigue cada petición:

1. **Usuario** hace clic en el frontend
2. **React SPA** decide qué componente mostrar y qué datos necesita
3. **API REST** (axios) hace una petición HTTP con el JWT en el header
4. **FastAPI** recibe la petición, valida el JWT, extrae usuario y empresa
5. **Service** contiene la lógica de negocio (reglas, validaciones, cálculos)
6. **Model** (SQLAlchemy) construye la consulta SQL con el filtro de tenant
7. **MySQL** ejecuta la consulta y devuelve los datos

**Principio importante:** Los endpoints NO contienen lógica de negocio. Los endpoints solo reciben la petición, llaman a un service, y devuelven la respuesta. Toda la lógica está en `services/`.

---

## Los 6 módulos del sistema

| # | Módulo | ¿Qué hace? | Tecnologías clave |
|---|---|---|---|
| 1 | **Scrum** | Tareas, sprints, kanban drag & drop | `@dnd-kit` en frontend |
| 2 | **Tickets** | Formulario de incidencias → email + histórico | SMTP (envío de correos) |
| 3 | **Documentación DPD/ISO** | Repositorio con control de permisos | Subida de archivos, permisos por usuario |
| 4 | **Fichaje** | Registro de login con timestamp | Se dispara automáticamente al hacer login |
| 5 | **Redirección** | Enlace a la web externa de la empresa | Simple, un campo en la BD |
| 6 | **Admin total** | CRUD usuarios/empresas, estadísticas, histórico | Panel completo solo para super-admin |

---

## Resumen visual de la arquitectura

```
┌──────────────────────────────────────────────────┐
│                   FRONTEND                        │
│            React + Vite (JavaScript)              │
│                                                    │
│  ┌─────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ Auth    │  │ Dashboard│  │ Scrum / Docs /   │ │
│  │ Pages   │  │ Pages    │  │ Tickets / Admin   │ │
│  └────┬────┘  └────┬─────┘  └────────┬─────────┘ │
│       │            │                 │            │
│  ┌────┴────────────┴─────────────────┴─────────┐ │
│  │         API Service (axios + JWT)           │ │
│  └────────────────────┬────────────────────────┘ │
└───────────────────────┼──────────────────────────┘
                        │ HTTP (REST)
┌───────────────────────┼──────────────────────────┐
│                   BACKEND (FastAPI)               │
│                       │                          │
│  ┌────────────────────┴────────────────────────┐ │
│  │           Middleware (JWT + Tenant)         │ │
│  └────────────────────┬────────────────────────┘ │
│                       │                          │
│  ┌────────────────────┴────────────────────────┐ │
│  │           API Routes (endpoints)            │ │
│  └────────────────────┬────────────────────────┘ │
│                       │                          │
│  ┌────────────────────┴────────────────────────┐ │
│  │           Services (lógica negocio)          │ │
│  └────────────────────┬────────────────────────┘ │
│                       │                          │
│  ┌────────────────────┴────────────────────────┐ │
│  │    Models (SQLAlchemy + filtro tenant)      │ │
│  └────────────────────┬────────────────────────┘ │
└───────────────────────┼──────────────────────────┘
                        │ SQL
                 ┌──────┴──────┐
                 │   MySQL 8   │
                 └─────────────┘
```
