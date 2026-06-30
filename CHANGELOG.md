# Changelog

## [0.2.0] — 2026-06-30

### Seguridad
- Logout invalida refresh + access tokens (blocklist)
- Rate limiting en POST /auth/register (10/min)
- Rate limiting en POST /tickets (10/min)
- CSP ampliada para permitir assets de Vite
- Secretos por defecto detectados en startup (log error)

### Frontend
- ErrorBoundary global atrapa errores no capturados
- Loading states añadidos a TicketsAdmin, DocumentosAdmin, Board, Sprints, Fichajes

### Infraestructura
- Limiter extraído a módulo compartido app/core/limiter.py
- Puertos de MySQL y Redis en docker-compine pasan a expose (red interna)
- Secretos docker-compose usan variables de entorno con fallback
- .env.example actualizado con CORS_ORIGINS y MYSQL_DATABASE correcto

### Desarrollo
- Script de seed: scripts/seed.py

## [0.1.0] — 2026-06-XX

- API REST bajo /api/v1
- Módulos: Auth, Admin, Empresa, Scrum, Tickets, Documentos, Fichajes, Redirección
- Frontend React con autenticación JWT, tablero Kanban, fichajes
- Multi-tenant por company_id
- Tests: 89 backend, 64 frontend
