# BYTEREDAPP — Instrucciones para agentes de IA

## Reglas globales

1. **Leer siempre** `ia/architecture.md` antes de hacer cambios grandes.
2. **Respetar las reglas** de `ia/rules/` según el lenguaje/módulo.
3. **No modificar** archivos sin preguntar si hay dudas.
4. **Actualizar** `ia/context/` cuando se añadan nuevas rutas, modelos o componentes.
5. **Código en español** (mensajes, comentarios si los hay, nombres de tablas).
6. **React con JavaScript** (no TypeScript), CSS plano (no Tailwind).
7. **pnpm** para el frontend, **pip** para el backend.

## Agentes configurados en OpenCode

Los agentes están definidos en `.opencode/opencode.json` y sus instrucciones detalladas en `.opencode/agents/`:

| Agente | Archivo | Rol |
|---|---|---|
| **agente-general** | `.opencode/agents/agente-general.md` | Orquestador full-stack (por defecto) |
| **agente-frontend** | `.opencode/agents/agente-frontend.md` | Especialista React/JS/CSS |
| **agente-backend** | `.opencode/agents/agente-backend.md` | Especialista FastAPI/Python |
| **agente-bd** | `.opencode/agents/agente-bd.md` | Especialista MySQL/SQL |
| **agente-profesor** | `.opencode/agents/agente-profesor.md` | Profesor universitario (solo explica) |
| **agente-comentador** | `.opencode/agents/agente-comentador.md` | Comenta código en español |
| **agente-ciberseguridad** | `.opencode/agents/agente-ciberseguridad.md` | Auditoría OWASP y contra medidas |

## Flujo de trabajo con OpenCode

1. El usuario habla con el **agente-general** (agente por defecto)
2. El agente-general lee `ia/AGENTS.md` + `ia/architecture.md`
3. Para tareas específicas, el agente-general invoca al subagente correspondiente mediante la herramienta `task`
4. Cada subagente sigue sus reglas en `.opencode/agents/<nombre>.md`
5. Las soluciones se devuelven al agente-general para integrar

## Documentación complementaria

| Archivo | Propósito |
|---|---|
| `ia/architecture.md` | Resumen de la arquitectura |
| `ia/rules/react-rules.md` | Reglas específicas frontend |
| `ia/rules/backend-rules.md` | Reglas específicas backend |
| `ia/rules/bd-rules.md` | Reglas específicas base de datos |
| `ia/rules/security-rules.md` | Reglas OWASP de ciberseguridad |
| `ia/context/database-schema.md` | Esquema actualizado de la BD |
| `ia/context/api-endpoints.md` | Endpoints actualizados de la API |
