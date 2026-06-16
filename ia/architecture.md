# Arquitectura del proyecto

**Tipo:** Monolítica modular con API REST
**Frontend:** React + Vite (JavaScript) — Hostinger
**Backend:** FastAPI (Python 3.11+)
**BD:** MySQL 8 (aislamiento multi-tenant por fila: company_id)
**Auth:** JWT (access + refresh) con middleware de tenant

## Flujo de datos

Usuario → React SPA → API REST (JWT) → FastAPI → Service → Model → MySQL

## Multi-tenant

Cada tabla tiene `company_id`. Un middleware inyecta automáticamente el tenant del JWT en cada query.

## Servicios (feature flags)

Cada empresa tiene una tabla `company_services` que activa/desactiva módulos.

## Módulos del sistema

1. Scrum (tareas, sprints, kanban)
2. Tickets (formulario → email + histórico admin)
3. Documentación DPD/ISO (con permisos)
4. Fichaje (login register timestamp)
5. Redirección a web externa
6. Admin total (estadísticas, CRUD usuarios/empresas)
