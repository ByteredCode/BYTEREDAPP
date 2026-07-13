# BYTEREDAPP

**Trabajo de Fin de Máster — Gestión Empresarial Multi-Tenant**

Sistema web completo para la gestión de empresas de mantenimiento informático. Plataforma multi-tenant donde cada empresa tiene acceso a los servicios contratados (Scrum, Tickets, Documentación DPD/ISO), y un panel de administración total para gestionar usuarios, empresas y configuración global.

---

## 1. Descripción general

BYTEREDAPP es una aplicación web de arquitectura monolítica modular con API REST, diseñada para gestionar múltiples empresas de forma aislada. Cada empresa opera con sus propios datos, usuarios y servicios activos, siguiendo un modelo multi-tenant por fila (`company_id` en cada tabla).

El sistema fue desarrollado como solución real para la gestión de una empresa de mantenimiento informático, pero está diseñado para ser escalable y adaptable a otros sectores.

### Público objetivo

- Empresas de mantenimiento informático que necesitan centralizar la gestión de clientes, documentación y soporte técnico.
- Equipos que trabajan con metodología ágil (Scrum/Kanban).
- Organizaciones que requieren cumplimiento normativo DPD/ISO para documentación.

---

## 2. Objetivos

### Objetivo principal

Desarrollar una aplicación web real, funcional y desplegada que demuestre los conocimientos adquiridos a lo largo del máster, abarcando desde el diseño de base de datos hasta el despliegue en producción.

### Objetivos específicos

- Implementar un sistema multi-tenant completo con aislamiento por fila.
- Desarrollar una API RESTful asíncrona con FastAPI y Python.
- Crear un frontend moderno con React, JavaScript vanilla y CSS plano.
- Integrar autenticación JWT con roles y permisos (admin total, admin empresa, usuario).
- Implementar feature flags para activar/desactivar servicios por empresa.
- Añadir un sistema de agentes de IA para desarrollo (diferenciador del proyecto).
- Lograr tests con cobertura alta y pipelines CI/CD automatizadas.

---

## 3. Stack tecnológico

| Capa | Tecnología | Justificación |
|---|---|---|
| **Frontend** | React + JavaScript + Vite | Ecosistema maduro, rápido desarrollo, despliegue estático en Hostinger |
| **Estilos** | CSS plano | Sin dependencias extra, control total del diseño |
| **Backend** | FastAPI (Python 3.11+) | Alto rendimiento asíncrono, tipado con Pydantic, documentación OpenAPI automática |
| **Base de datos** | MySQL 8 | Disponibilidad en Hostinger, costo cero, rendimiento probado |
| **ORM** | SQLAlchemy 2.0 + Alembic | Estándar en Python, migraciones versionadas |
| **Autenticación** | JWT (access + refresh tokens) | Stateless, escalable, multi-tenant nativo |
| **Cache/Lock** | Redis | Blocklist de tokens, rate limiting |
| **Email** | Resend API | Envío asíncrono de emails para tickets |
| **Despliegue Frontend** | Hostinger | Hosting contratado, archivos estáticos |
| **Despliegue Backend** | Render (free tier) | Despliegue automático desde GitHub |
| **CI/CD** | GitHub Actions | Pipelines automatizadas de test y deploy |
| **Contenedores** | Docker + Docker Compose | Entorno local consistente |

---

## 4. Arquitectura

### Tipo: Monolítica modular con API REST

```
Usuario → React SPA → API REST (JWT) → FastAPI → Service → Model → MySQL
```

### Principios de diseño

- **Multi-tenant por fila:** Cada tabla tiene `company_id`. Un middleware inyecta automáticamente el tenant del JWT en cada query.
- **Feature flags:** Tabla `empresa_servicio` que determina qué módulos tiene activos cada empresa.
- **Separación por capas:** Routes → Services → Models → Schemas (Pydantic).
- **Roles:** Tres niveles de acceso — `admin_total`, `admin_empresa`, `usuario`.
- **Middleware de tenant:** Filtro automático por empresa en todas las queries.

### Modelo de datos (simplificado)

```
empresa (1) ──→ (N) usuario
empresa (1) ──→ (N) empresa_servicio
empresa (1) ──→ (N) tarea
empresa (1) ──→ (N) ticket
empresa (1) ──→ (N) documento
usuario (1) ──→ (N) tarea (asignación)
usuario (1) ──→ (N) documento_permiso
```

---

## 5. Estructura del proyecto

```
📁 byteredapp/
├── client/                 → Aplicación React (Vite + JavaScript)
├── server/                 → API Backend (FastAPI + Python)
├── ia/                     → Documentación para agentes de IA de desarrollo
├── .github/workflows/      → CI/CD (GitHub Actions)
├── .opencode/              → Configuración de agentes de OpenCode
├── docker-compose.yml      → Entorno local con MySQL + Redis
├── .env.example            → Plantilla de variables de entorno
├── .gitignore
└── README.md
```

### `client/` — Frontend React

| Carpeta | Contenido |
|---|---|
| `src/components/` | Componentes reutilizables: Layout, ProtectedRoute, AdminOnlyRoute, LoadingSpinner, ErrorAlert, NotFound |
| `src/pages/` | Páginas: Login, Dashboard, MiEmpresa |
| `src/pages/Scrum/` | Tablero Kanban, Sprints con sub-layout |
| `src/pages/Tickets/` | Formulario de incidencias (NuevoTicket) |
| `src/pages/admin/` | Panel admin: Dashboard, Empresas, Usuarios, Servicios, Tickets, Documentos |
| `src/pages/Documentos/` | Gestión de documentos DPD/ISO con permisos |
| `src/context/` | Contextos: AuthContext (JWT), ToastContext (notificaciones) |
| `src/api/` | Instancia axios con interceptores (token + refresh automático) |
| `src/hooks/` | Hooks personalizados (useUsuarios) |
| `src/styles/` | CSS organizado por módulo |

### `server/` — Backend FastAPI

| Carpeta | Contenido |
|---|---|
| `app/api/v1/` | Endpoints: auth, admin, empresa, scrum, tickets, documentos, redireccion |
| `app/core/` | Config: conexión BD (async), JWT, seguridad, middleware tenant, Redis |
| `app/models/` | Modelos SQLAlchemy: Empresa, Usuario, Tarea, Sprint, Ticket, Documento |
| `app/schemas/` | Esquemas Pydantic (validación entrada/salida) |
| `app/services/` | Lógica de negocio: auth, admin, scrum, ticket, documento, email |
| `run.py` | Punto de entrada de la aplicación FastAPI |
| `alembic/` | Migraciones de la base de datos |
| `tests/` | Tests unitarios y de integración |

### `ia/` — Sistema de agentes de IA para desarrollo

| Archivo | Contenido |
|---|---|
| `AGENTS.md` | Instrucciones globales y lista de agentes disponibles |
| `architecture.md` | Resumen de la arquitectura para contexto rápido |
| `rules/` | Reglas de estilo: react-rules.md, backend-rules.md, bd-rules.md, security-rules.md |
| `context/` | Documentación viva: database-schema.md, api-endpoints.md |
| `docs/explicacion-byteredapp.md` | Documentación detallada del proyecto |

---

## 6. Funcionalidades principales

| # | Módulo | Descripción |
|---|---|---|
| 1 | **Tablero Scrum** | Tablero Kanban con drag & drop, sprints (backlog, activo, completado), asignación de tareas a miembros |
| 2 | **Tickets de contacto** | Formulario que genera un correo electrónico + histórico visible en el panel de administración |
| 3 | **Documentación DPD/ISO** | Repositorio de documentos con control de permisos por usuario (solo usuarios autorizados acceden) |
| 4 | **Redirección a web** | Enlace dinámico por empresa a su web externa |
| 5 | **Panel admin total** | Estadísticas de uso, CRUD completo de usuarios/empresas, configuración de servicios, histórico de tickets |
| 6 | **Gestión de servicios** | Feature flags por empresa — cada empresa activa/desactiva los módulos que necesita |
| 7 | **Multi-tenant** | Aislamiento completo de datos por empresa con filtro automático |
| 8 | **Sistema de roles** | Tres niveles: admin_total (control total), admin_empresa (gestión de su empresa), usuario (uso básico) |

---

## 7. Despliegue

### Producción

| Componente | URL | Tecnología |
|---|---|---|
| **Frontend** | https://byteredapp.com | Hostinger (estáticos) |
| **Backend API** | https://byteredapp.onrender.com | Render (free tier) |
| **API Docs** | https://byteredapp.onrender.com/docs | Swagger UI (solo en desarrollo) |
| **Repositorio** | https://github.com/ByteredCode/BYTEREDAPP | GitHub (público) |

### Despliegue automático

- **Backend:** Render detecta cambios en `main` y despliega automáticamente.
- **Frontend:** GitHub Actions construye y sube los estáticos a Hostinger.
- **Ping de keep-alive:** Script `scripts/ping-render.ps1` ejecutado cada 15 minutos via Windows Task Scheduler para evitar spin-down del tier gratuito.

---

## 8. Credenciales de prueba

El sistema tiene 3 roles con diferentes niveles de acceso:

| Rol | Email | Contraseña | Permisos |
|---|---|---|---|
| **Admin total** | `antonio@bytered.es` | `admin1234A` | Gestión completa: usuarios, empresas, servicios, documentos, tickets |
| **Admin empresa** | `adminempresa@bytered.es` | `Admin1234A!` | Gestión de su propia empresa: usuarios, scrum, documentos |
| **Usuario** | `usuario@bytered.es` | `Usuario1234A!` | Uso básico: scrum, tickets, documentos con permiso |

> Todos los usuarios están asignados a la empresa **ByteRed 2018 SL** (ID 3).

---

## 9. Instalación y ejecución local

### Requisitos previos

- Node.js 20+
- pnpm (`npm install -g pnpm`)
- Python 3.11+
- Docker y Docker Compose (para MySQL + Redis)

### 1. Clonar el repositorio

```bash
git clone https://github.com/ByteredCode/BYTEREDAPP.git
cd BYTEREDAPP
```

### 2. Base de datos (MySQL con Docker)

```bash
docker compose up -d
docker ps  # Verificar que está corriendo
```

### 3. Backend (FastAPI)

```bash
cd server
python -m venv venv
.\venv\Scripts\activate       # Windows
# source venv/bin/activate    # Linux/Mac
pip install -r requirements.txt

# Copiar variables de entorno
Copy-Item ..\.env.example .env   # Windows
# cp ..\.env.example .env       # Linux/Mac

# Iniciar servidor
uvicorn run:app --reload
```

### 4. Frontend (React + Vite)

```bash
cd client
pnpm install
pnpm dev
```

### 5. Verificar

| Servicio | URL |
|---|---|
| Frontend | http://localhost:5173 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Base de datos | MySQL en localhost:3306 |

---

## 10. CI/CD

El repositorio incluye pipelines de GitHub Actions:

| Pipeline | Archivo | Disparador | Jobs |
|---|---|---|---|
| **CI** | `.github/workflows/ci.yml` | Push/PR a main | Backend (pytest + cobertura), Frontend (lint + vitest + build), Docker (build imágenes) |
| **Deploy Frontend** | `.github/workflows/deploy-frontend.yml` | Push a main | Build + deploy a Hostinger |

---

## 11. Agentes de IA para desarrollo

Diferenciador principal del proyecto: BYTEREDAPP incorpora un **sistema de agentes de IA especializados** que aceleran el desarrollo y mantienen la consistencia del código.

### Arquitectura del sistema de agentes

```
┌─────────────────────────────┐
│     agente-general          │  ← Orquestador (por defecto)
│  Lee ia/ y delega tareas    │
└──────────┬──────────────────┘
           │ task()
    ┌──────┴──────┐
    ▼             ▼
┌──────────┐ ┌──────────┐
│ frontend │ │ backend  │  ← Subagentes especializados
│ React/JS │ │ FastAPI  │
└──────────┘ └──────────┘
    ▼             ▼
┌──────────┐ ┌──────────┐
│    bd    │ │seguridad │  ← Subagentes de soporte
│  MySQL   │ │  OWASP   │
└──────────┘ └──────────┘
```

### Agentes disponibles

| Agente | Rol | Archivo de instrucciones |
|---|---|---|
| `agente-general` | Full-stack, orquestador (por defecto) | `.opencode/agents/agente-general.md` |
| `agente-frontend` | Especialista React/JS/CSS | `.opencode/agents/agente-frontend.md` |
| `agente-backend` | Especialista FastAPI/Python | `.opencode/agents/agente-backend.md` |
| `agente-bd` | Especialista MySQL/SQL | `.opencode/agents/agente-bd.md` |
| `agente-profesor` | Profesor universitario (solo explica) | `.opencode/agents/agente-profesor.md` |
| `agente-comentador` | Comenta código en español | `.opencode/agents/agente-comentador.md` |
| `agente-ciberseguridad` | Auditoría OWASP | `.opencode/agents/agente-ciberseguridad.md` |

### Flujo de trabajo

1. El usuario habla con el **agente-general** (agente por defecto).
2. El agente-general lee `ia/AGENTS.md` + `ia/architecture.md`.
3. Para tareas específicas, invoca al subagente correspondiente mediante la herramienta `task`.
4. Cada subagente sigue sus reglas en `.opencode/agents/<nombre>.md`.
5. Las soluciones se devuelven al agente-general para integrar.

### Documentación de agentes

| Archivo | Propósito |
|---|---|
| `ia/AGENTS.md` | Instrucciones globales para todos los agentes |
| `ia/architecture.md` | Resumen de la arquitectura del proyecto |
| `ia/rules/react-rules.md` | Reglas específicas para frontend |
| `ia/rules/backend-rules.md` | Reglas específicas para backend |
| `ia/rules/bd-rules.md` | Reglas específicas para base de datos |
| `ia/rules/security-rules.md` | Reglas OWASP de ciberseguridad |
| `ia/context/database-schema.md` | Esquema actualizado de la BD |
| `ia/context/api-endpoints.md` | Endpoints actualizados de la API |

---

## 12. Futuras mejoras

- **Módulo de facturación** — Planes, facturas recurrentes y seguimiento de pagos.
- **Auditoría de accesos a documentos** — Logging obligatorio para cumplimiento DPD/ISO.
- **Firma digital** — Validación y firma de documentos.
- **API pública** — Para que empresas consulten sus datos desde fuera.
- **App móvil** — Fichaje y gestión de Scrum desde el teléfono.
- **Automatizaciones** — Reglas del tipo "si no ficha en 3 días, notificar".
- **Multi-idioma** — Soporte para empresas extranjeras.

---

## 13. Enlaces

| Recurso | URL |
|---|---|
| **Repositorio GitHub** | https://github.com/ByteredCode/BYTEREDAPP |
| **Despliegue (Frontend)** | https://byteredapp.com |
| **Despliegue (Backend)** | https://byteredapp.onrender.com |
| **Slides de presentación** | https://docs.google.com/presentation/d/PLACEHOLDER |
| **Vídeo explicativo** | https://youtube.com/watch?v=PLACEHOLDER |
