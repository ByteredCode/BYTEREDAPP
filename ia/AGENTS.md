# BYTEREDAPP — Instrucciones para agentes de IA

## Reglas globales

1. **Leer siempre** `ia/architecture.md` antes de hacer cambios grandes.
2. **Respetar las reglas** de `ia/rules/` según el lenguaje/modulo.
3. **No modificar** archivos sin preguntar si hay dudas.
4. **Actualizar** `ia/context/` cuando se añadan nuevas rutas, modelos o componentes.
5. **Código en español** (mensajes, comentarios si los hay, nombres de tablas).
6. **React con JavaScript** (no TypeScript), CSS plano (no Tailwind).
7. **pnpm** para el frontend, **pip** para el backend.

## Agentes disponibles

| Agente | Rol | Cuándo usarlo |
|---|---|---|
| **agente-general** | Full-stack, tareas generales | Por defecto |
| **agente-frontend** | Solo React/JS/CSS | Issues visuales, componentes nuevos |
| **agente-backend** | Solo Python/FastAPI/BD | Endpoints, modelos, lógica de negocio |
| **agente-bd** | Solo SQL, migraciones, esquemas | Diseño de BD, consultas complejas |

## Flujo de trabajo

1. El agente principal lee este archivo + architecture.md
2. Delega tareas específicas a los subagentes si es necesario
3. Cada subagente sigue sus propias reglas en `ia/rules/`
4. Las soluciones se devuelven al agente principal para integrar
