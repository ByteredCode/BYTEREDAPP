# Componentes Scrum — Explicación Didáctica

## Arquitectura del módulo Scrum

El módulo Scrum sigue un patrón de **layout con rutas anidadas**: ScrumLayout envuelve a Board y Sprints, y React Router las intercambia según la navegación.

```
/scrum/tablero  →  Board.jsx
/scrum/sprints  →  Sprints.jsx
```

Ambos componentes usan TareaForm.jsx como modal para crear/editar tareas.

---

## 1. `ScrumLayout.jsx` — Contenedor con pestañas

Es un layout mínimo que proporciona navegación entre el tablero y los sprints:

- Usa `<NavLink>` de React Router para mostrar la pestaña activa.
- `<Outlet />` es el marcador donde React Router inyecta el componente hijo (Board o Sprints).
- No tiene estado propio, solo estructura.

---

## 2. `Board.jsx` — Tablero Kanban con Drag & Drop

Este es el componente más complejo de la aplicación. Implementa un tablero Kanban completo con 4 columnas y arrastrar-y-soltar.

### Columnas
```javascript
const COLUMNAS = [
  { id: "Todo", titulo: "Por hacer" },
  { id: "Haciendose", titulo: "En proceso" },
  { id: "En revision", titulo: "En revisión" },
  { id: "Done", titulo: "Terminado" },
]
```

### Drag & Drop con @dnd-kit

Usa la librería `@dnd-kit` que proporciona:
- **`DndContext`**: el contexto que maneja todo el evento de arrastre. Define `sensors`, `onDragStart` y `onDragEnd`.
- **`SortableContext`**: agrupa tarjetas dentro de cada columna para que se reordenen entre sí.
- **`useSortable`**: hook que hace que una tarjeta sea arrastrable. Proporciona `listeners` (eventos de mouse/touch), `transform` (posición durante el arrastre) y `isDragging` (para efectos visuales).
- **`DragOverlay`**: muestra una vista previa de la tarjeta mientras se arrastra.

### Sensores
```javascript
const sensors = useSensors(
  useSensor(PointerSensor, { activationConstraint: { distance: 5 } })
)
```
Requiere mover el ratón 5px antes de activar el drag. Esto evita arrastres accidentales al hacer clic para editar.

### Flujo de arrastre (handleDragEnd)

1. Se determina la columna destino: si se soltó sobre una columna o sobre otra tarjeta.
2. Se calcula la nueva posición (orden).
3. **Optimistic update**: se actualiza el estado local INMEDIATAMENTE, antes de la respuesta del servidor. Esto hace que la UI se sienta instantánea.
4. Si la llamada a la API falla, se revierte llamando a `fetchTablero()` (rollback).

### Carga de datos
- `fetchTablero()` obtiene las tareas agrupadas por columna.
- `fetchSprints()` obtiene la lista de sprints para el filtro.
- Un `<select>` permite filtrar el tablero por sprint.
- `useMemo` aplana todas las tareas en un solo array para búsquedas rápidas durante el drag.

---

## 3. `Sprints.jsx` — CRUD de Sprints

Componente más tradicional con tabla de sprints y modal de formulario:

- **Listado**: cada sprint se muestra en una tarjeta con nombre, objetivo, fechas y estado.
- **Crear/Editar**: modal con formulario para nombre, objetivo, fechas y estado.
- **Eliminar**: con confirmación (`confirm()`).
- Los estados posibles son: Planificado → Activo → Completado.

### Conversión de datos
Antes de enviar al backend, convierte strings vacías a `null` para que el servicio las interprete correctamente.

---

## 4. `TareaForm.jsx` — Modal de creación/edición de tareas

Formulario reutilizable para crear y editar tareas:

- **Props**: `editando` (null para crear, objeto para editar), `columna` (columna predeterminada), `sprints` (lista para el selector), `sprintActivo` (filtro actual), `onClose` y `onSaved`.
- **Campos**: título (obligatorio), descripción, prioridad (Baja/Media/Alta/Crítica), columna, fecha límite, asignación (ID de usuario), sprint.
- Al guardar, limpia campos vacíos a `null` y llama a `onSaved()` para recargar el tablero.

---

## Patrones de React utilizados

| Patrón | Uso |
|---|---|
| **useState** | Estado de columnas, sprints, formularios, modales |
| **useEffect** | Carga inicial de datos y recarga tras cambios |
| **useCallback** | Memoriza fetchTablero y fetchSprints para evitar bucles infinitos |
| **useMemo** | Aplana tareas para búsquedas O(1) durante drag & drop |
| **render prop** | DragOverlay recibe una función que renderiza según el estado |
| **Optimistic UI** | Actualiza el estado antes de la respuesta del servidor |
