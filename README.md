# BYTEREDAPP

Sistema web multi-tenant para la gestión de empresas. Cada empresa tiene acceso a los servicios contratados, y nosotros como administradores totales gestionamos todo desde un panel central.

## Servicios del sistema

| # | Servicio | Descripción |
|---|---|---|
| 1 | **Tablero Scrum** | La empresa asigna tareas a sus propios usuarios con sprints y kanban |
| 2 | **Tickets (contacto)** | Formulario que los usuarios rellenan y genera un correo para nosotros + histórico visible en el admin |
| 3 | **Documentación DPD/ISO** | Repositorio de documentos con control de permisos (solo usuarios autorizados acceden) |
| 4 | **Fichaje (login register)** | Cada inicio de sesión queda registrado con timestamp para control horario |
| 5 | **Redirección a web** | Enlace directo a la web de la empresa si gestionamos su mantenimiento |
| 6 | **Panel admin total** | Estadísticas de uso, CRUD de usuarios/empresas, configuración global, histórico de tickets |

## Stack Tecnológico

| Capa | Tecnología | Justificación |
|---|---|---|
| **Frontend** | React + JavaScript + Vite | Ecosistema maduro, rápido desarrollo, Hostinger (estáticos) |
| **Estilos** | CSS plano | Sin dependencias extra, control total |
| **Backend** | FastAPI (Python 3.11+) | Async, tipado con Pydantic, OpenAPI automático |
| **Base de datos** | MySQL | Disponible en Hostinger, costo cero |
| **ORM** | SQLAlchemy 2.0 + Alembic | Estándar Python, migrations |
| **Autenticación** | JWT (access + refresh) | Stateless, multi-tenant nativo |
| **Despliegue Frontend** | Hostinger (estáticos) | Contratado actualmente |
| **Despliegue Backend** | Por definir (Render / Railway / VPS) | |

## Arquitectura

**Tipo:** Monolítica modular con API REST

- **Frontend:** SPA en React que consume API REST
- **Backend:** FastAPI organizado en capas (routes → services → models)
- **Multi-tenant:** Aislamiento por fila (cada tabla tiene `company_id`)
- **Servicios por empresa:** Feature flags — una tabla `company_services` que determina qué módulos tiene activos cada empresa
- **Separación por dominios:** auth, companies, tickets, scrum, docs, fichaje, admin

### Estructura de carpetas

```
📁 byteredapp/
├── client/                 → Aplicación React (Vite + JavaScript) ✔
├── server/                 → API Backend (FastAPI + Python)
├── ia/                     → Documentación para agentes de IA de desarrollo ✔
├── .github/workflows/      → CI/CD (GitHub Actions) ✔
├── .opencode/              → Configuración de agentes de OpenCode ✔
├── scripts/                → Scripts de utilidad para desarrollo
├── docker-compose.yml      → Entorno local con MySQL ✔
├── .env.example            → Plantilla de variables de entorno ✔
├── .gitignore              ✔
└── README.md               ✔
```

#### `client/` — Frontend React

| Carpeta | Contenido |
|---|---|
| `public/` | Archivos estáticos (favicon, imágenes) |
| `src/components/common/` | Componentes reutilizables: botones, inputs, modales, tablas |
| `src/components/layout/` | Estructura visual: sidebar, header, footer, layout principal |
| `src/pages/Auth/` | Páginas de login y registro |
| `src/pages/Dashboard/` | Panel principal post-login |
| `src/pages/Companies/` | Portal de empresa: perfil, configuración, datos |
| `src/pages/Scrum/` | Tablero Scrum: proyectos, sprints, tareas kanban |
| `src/pages/Docs/` | Documentación DPD/ISO: visor y gestor de documentos |
| `src/pages/Tickets/` | Formulario de incidencias y listado histórico |
| `src/pages/Admin/` | Panel admin: usuarios, empresas, estadísticas, histórico |
| `src/hooks/` | Custom hooks de React (lógica reutilizable) |
| `src/context/` | Contextos globales: AuthContext, TenantContext |
| `src/services/` | Llamadas a la API (axios) |
| `src/utils/` | Funciones auxiliares (formatos, validaciones, constantes) |
| `src/styles/` | Archivos CSS globales y por página |

#### `server/` — Backend FastAPI

| Carpeta | Contenido |
|---|---|
| `app/api/v1/` | Endpoints de la API organizados por módulo (auth, companies, scrum, tickets, docs, admin) |
| `app/core/` | Configuración global: conexión BD, JWT, seguridad, middleware multi-tenant |
| `app/models/` | Modelos SQLAlchemy (tablas de la BD) |
| `app/schemas/` | Esquemas Pydantic (validación de datos de entrada/salida) |
| `app/services/` | Lógica de negocio (reglas, cálculos, procesos) |
| `app/ai/` | Agentes de IA integrados en el producto (a futuro) |
| `app/main.py` | Punto de entrada de la aplicación FastAPI |
| `alembic/` | Migraciones de la base de datos |
| `tests/` | Tests unitarios y de integración |

#### `ia/` — Sistema de agentes de IA para desarrollo

| Carpeta / Archivo | Contenido |
|---|---|
| `AGENTS.md` | Instrucciones globales y lista de agentes disponibles |
| `architecture.md` | Resumen de la arquitectura para contexto rápido |
| `rules/react-rules.md` | Reglas de estilo para frontend (React, JS, CSS plano) |
| `rules/backend-rules.md` | Reglas de estilo para backend (FastAPI, Python) |
| `context/database-schema.md` | Esquema actualizado de la base de datos |
| `context/api-endpoints.md` | Lista actualizada de endpoints de la API |

## Plan de desarrollo por fases

### Fase 0 — Setup del proyecto (1-2 semanas)
- Monorepo: `client/` (React+Vite+JS) y `server/` (FastAPI)
- Conexión a MySQL + SQLAlchemy + Alembic
- Autenticación JWT (register/login)
- Middleware multi-tenant + feature flags por empresa
- Layout base del frontend (sidebar, header, auth flow)
- Docker Compose para entorno local
- Creación de `ia/` con documentación para agentes de desarrollo

### Fase 1 — Autenticación y fichaje (2 semanas)
- Login / registro con JWT
- Sistema de roles (admin total, admin empresa, usuario)
- Registro de timestamp en cada login (fichaje)
- Dashboard básico post-login

### Fase 2 — Panel admin total (3 semanas)
- CRUD de empresas (alta, baja, modificación)
- CRUD de usuarios (asignar a empresas, roles)
- Asignación de servicios por empresa (feature flags)
- Estadísticas de uso de la plataforma
- Histórico de tickets recibidos

### Fase 3 — Documentación DPD/ISO (2-3 semanas)
- Subida y gestión de documentos
- Control de permisos por documento/usuario
- Visor de documentos en el frontend
- Auditoría de accesos (quién, cuándo, qué documento)

### Fase 4 — Tablero Scrum (3-4 semanas)
- Proyectos asociados a empresas
- Sprints (backlog, activo, completado)
- Tarjetas drag & drop (@dnd-kit)
- Asignación de miembros a tareas
- Burndown chart y estadísticas

### Fase 5 — Tickets (formulario + email) (1-2 semanas)
- Formulario público o privado para enviar incidencias
- Envío de correo con los datos del formulario
- Histórico de tickets visible en el admin
- Posible respuesta desde el admin

### Fase 6 — Redirección a web y extras (1 semana)
- Enlace dinámico por empresa a su web externa
- Pequeños ajustes y mejoras

## Futuras modificaciones previstas

- **Módulo de facturación** — planes, facturas recurrentes
- **Auditoría de accesos a documentos** — logging obligatorio para cumplimiento DPD/ISO
- **Firma digital** — validación de documentos
- **API pública** — para que empresas consulten sus datos desde fuera
- **App móvil** — fichaje y scrum desde el teléfono
- **Automatizaciones** — reglas del tipo "si no ficha en 3 días, notificar"
- **Multi-idioma** — soporte para empresas extranjeras

## Sistema de agentes de IA

### Para el desarrollo (arquitectura actual)

El proyecto está preparado para trabajar con múltiples agentes de IA especializados:

| Archivo / Carpeta | Propósito |
|---|---|
| `ia/AGENTS.md` | Instrucciones globales que todo agente debe leer al empezar |
| `ia/architecture.md` | Resumen rápido de la arquitectura para contexto |
| `ia/rules/react-rules.md` | Reglas específicas para el agente de frontend |
| `ia/rules/backend-rules.md` | Reglas específicas para el agente de backend |
| `ia/context/` | Documentación viva del esquema BD y endpoints |
| `.opencode/opencode.json` | Configuración de agentes para OpenCode |
| `.github/copilot-instructions.md` | Instrucciones para GitHub Copilot |

**Agentes disponibles en OpenCode:**

| Agente | Rol |
|---|---|
| `agente-general` | Full-stack, tareas generales (por defecto) |
| `agente-frontend` | Especialista en React/JS/CSS |
| `agente-backend` | Especialista en FastAPI/Python |
| `agente-bd` | Especialista en MySQL/SQL |

**Flujo:** El agente general lee `ia/` y delega tareas específicas a los subagentes según el módulo.

### Dentro del producto (a futuro)
| Agente | Servicio | Descripción |
|---|---|---|
| Document Classifier | Documentación | Clasifica automáticamente documentos DPD/ISO |
| Scrum Advisor | Tablero Scrum | Sugiere duración de sprint, detecta bloqueos |
| Report Generator | Admin | Genera resúmenes automáticos de actividad |

## Cómo empezar

### Requisitos previos
- Node.js 20+
- pnpm (`npm install -g pnpm`)
- Python 3.11+
- Docker y Docker Compose (para la BD MySQL)

### 1. Base de datos (MySQL con Docker)

```bash
# Iniciar MySQL
docker compose up -d

# Verificar que está corriendo
docker ps
```

### 2. Frontend (React + Vite)

```bash
cd client
pnpm install
pnpm add axios
pnpm dev
```

### 3. Backend (FastAPI)

```bash
cd server
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Copiar variables de entorno
Copy-Item ..\.env.example .env

# Iniciar servidor
uvicorn app.main:app --reload
```

### 4. Verificar

- Frontend: `http://localhost:5173`
- API Docs (Swagger): `http://localhost:8000/docs`
- Base de datos: MySQL en `localhost:3306`

## Docker (producción)

```bash
# Construir y arrancar todo (BD + API + Frontend nginx)
docker compose up --build -d

# Servicios:
# - Frontend: http://localhost
# - API:      http://localhost:8000
# - Docs:     http://localhost:8000/docs
# - BD:       localhost:3306

# Ver logs
docker compose logs -f

# Detener
docker compose down
```

## CI/CD

El repositorio incluye un pipeline de GitHub Actions en `.github/workflows/ci.yml` que ejecuta:

| Job | Descripción |
|---|---|
| **backend** | Tests con pytest + cobertura ≥80% sobre MySQL real |
| **frontend** | Lint + tests con vitest + cobertura ≥80% + build |
| **docker** | Build de imágenes (server + client) tras tests exitosos |

Para activarlo, el repositorio debe estar en GitHub. Las credenciales de base de datos se configuran vía `secrets.MYSQL_*` en el repositorio.

## Arquitectura multi-tenant

Ver `ia/architecture.md` para detalles completos del modelo de datos, flujo de autorización y diseño de módulos.