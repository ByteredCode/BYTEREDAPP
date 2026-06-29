import { useState, useEffect, useCallback, useMemo } from "react"
import { DndContext, DragOverlay, PointerSensor, useSensor, useSensors } from "@dnd-kit/core"
import { SortableContext, useSortable, verticalListSortingStrategy } from "@dnd-kit/sortable"
import { CSS } from "@dnd-kit/utilities"
import api from "../../api/axios"
import TareaForm from "./TareaForm"

// Definicion de las 4 columnas clasicas de Kanban
const COLUMNAS = [
  { id: "Todo", titulo: "Por hacer" },
  { id: "Haciendose", titulo: "En proceso" },
  { id: "En revision", titulo: "En revisión" },
  { id: "Done", titulo: "Terminado" },
]

// Componente de tarjeta arrastrable usando @dnd-kit/sortable
function SortableCard({ tarea, onClick }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: tarea.codigo_tarea,
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,  // Efecto fantasma durante el arrastre
  }

  const prioridadClase = `prioridad-${tarea.prioridad?.toLowerCase() || "media"}`

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners} className="kanban-card" onClick={() => onClick(tarea)}>
      <div className="kanban-card-titulo">{tarea.titulo}</div>
      <div className="kanban-card-meta">
        <span className={`prioridad-badge ${prioridadClase}`}>{tarea.prioridad || "Media"}</span>
        {tarea.fecha_limite && <span className="fecha-limite">{tarea.fecha_limite}</span>}
      </div>
      {tarea.asignacion && <div className="kanban-card-asignacion">#{tarea.asignacion}</div>}
    </div>
  )
}

// Vista previa que sigue al cursor durante el arrastre (DragOverlay)
function CardPreview({ tarea }) {
  if (!tarea) return null
  return (
    <div className="kanban-card kanban-card-drag">
      <div className="kanban-card-titulo">{tarea.titulo}</div>
      <div className="kanban-card-meta">
        <span className={`prioridad-badge prioridad-${tarea.prioridad?.toLowerCase() || "media"}`}>
          {tarea.prioridad || "Media"}
        </span>
      </div>
    </div>
  )
}

// Columna del Kanban con lista ordenable
function Columna({ id, titulo, tareas, onAgregar, onEditar }) {
  const ids = tareas.map((t) => t.codigo_tarea)

  return (
    <div className="kanban-columna">
      <div className="kanban-columna-header">
        <h3>{titulo}</h3>
        <span className="kanban-count">{tareas.length}</span>
        <button className="btn-add-tarea" onClick={onAgregar} title="Agregar tarea">+</button>
      </div>
      {/* SortableContext agrupa tarjetas ordenables dentro de la columna */}
      <SortableContext items={ids} strategy={verticalListSortingStrategy}>
        <div className="kanban-columna-body">
          {tareas.map((tarea) => (
            <SortableCard key={tarea.codigo_tarea} tarea={tarea} onClick={() => onEditar(tarea)} />
          ))}
        </div>
      </SortableContext>
    </div>
  )
}

export default function Board() {
  const [columnas, setColumnas] = useState({ Todo: [], Haciendose: [], "En revision": [], Done: [] })
  const [sprints, setSprints] = useState([])
  const [sprintActivo, setSprintActivo] = useState("")
  const [activeId, setActiveId] = useState(null)  // ID de la tarea siendo arrastrada
  const [mostrarForm, setMostrarForm] = useState(false)
  const [editando, setEditando] = useState(null)
  const [columnaForm, setColumnaForm] = useState("Todo")

  // Sensor que activa el drag solo tras moverse 5px (evita drags accidentales)
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }))

  const fetchTablero = useCallback(async () => {
    try {
      const params = sprintActivo ? { codigo_sprint: Number(sprintActivo) } : {}
      const res = await api.get("/scrum/tablero", { params })
      setColumnas(res.data)
    } catch {
      // ignore
    }
  }, [sprintActivo])

  const fetchSprints = useCallback(async () => {
    try {
      const res = await api.get("/scrum/sprints")
      setSprints(res.data)
    } catch {
      // ignore
    }
  }, [])

  useEffect(() => { fetchTablero() }, [fetchTablero])
  useEffect(() => { fetchSprints() }, [fetchSprints])

  // Aplanar todas las tareas para busquedas rapidas
  const todasLasTareas = useMemo(() => {
    return Object.values(columnas).flat()
  }, [columnas])

  const activeTarea = useMemo(() => {
    return todasLasTareas.find((t) => t.codigo_tarea === activeId)
  }, [todasLasTareas, activeId])

  function handleDragStart(event) {
    setActiveId(event.active.id)
  }

  async function handleDragEnd(event) {
    const { active, over } = event
    setActiveId(null)
    if (!over) return

    const tareaId = active.id
    let columnaDestino = null
    let nuevoOrden = 0

    // Determinar columna destino: si se solto sobre una columna o sobre otra tarjeta
    if (COLUMNAS.some((c) => c.id === over.id)) {
      columnaDestino = over.id
      nuevoOrden = columnas[over.id]?.length || 0
    } else {
      const tareaOver = todasLasTareas.find((t) => t.codigo_tarea === over.id)
      if (!tareaOver) return
      columnaDestino = tareaOver.columna
      nuevoOrden = columnas[columnaDestino]?.findIndex((t) => t.codigo_tarea === over.id)
      if (nuevoOrden === -1) nuevoOrden = columnas[columnaDestino]?.length || 0
    }

    if (!columnaDestino) return

    const tareaMovida = todasLasTareas.find((t) => t.codigo_tarea === tareaId)
    if (!tareaMovida) return

    if (tareaMovida.columna === columnaDestino && tareaMovida.orden === nuevoOrden) return

    // Optimistic update: actualizar UI inmediatamente antes de la respuesta del servidor
    const nuevas = { ...columnas }
    for (const col of Object.keys(nuevas)) {
      nuevas[col] = nuevas[col].filter((t) => t.codigo_tarea !== tareaId)
    }
    const itemActualizado = { ...tareaMovida, columna: columnaDestino, orden: nuevoOrden }
    nuevas[columnaDestino].splice(nuevoOrden, 0, itemActualizado)
    nuevas[columnaDestino] = nuevas[columnaDestino].map((t, i) => ({ ...t, orden: i }))
    setColumnas(nuevas)

    try {
      await api.put(`/scrum/tareas/${tareaId}/mover`, { columna: columnaDestino, orden: itemActualizado.orden })
    } catch {
      fetchTablero()  // Revertir si falla (rollback)
    }
  }

  function abrirForm(columna) {
    setColumnaForm(columna)
    setEditando(null)
    setMostrarForm(true)
  }

  function editarTarea(tarea) {
    setColumnaForm(tarea.columna)
    setEditando(tarea)
    setMostrarForm(true)
  }

  return (
    <div className="scrum-board">
      <div className="board-header">
        <h2>Tablero Kanban</h2>
        <div className="board-filtros">
          <select value={sprintActivo} onChange={(e) => setSprintActivo(e.target.value)}>
            <option value="">Todos los sprints</option>
            {sprints.map((s) => (
              <option key={s.codigo_sprint} value={s.codigo_sprint}>{s.nombre}</option>
            ))}
          </select>
        </div>
      </div>

      <DndContext sensors={sensors} onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
        <div className="kanban-board">
          {COLUMNAS.map((col) => (
            <Columna
              key={col.id}
              id={col.id}
              titulo={col.titulo}
              tareas={columnas[col.id] || []}
              onAgregar={() => abrirForm(col.id)}
              onEditar={editarTarea}
            />
          ))}
        </div>
        <DragOverlay>
          {activeId ? <CardPreview tarea={activeTarea} /> : null}
        </DragOverlay>
      </DndContext>

      {mostrarForm && (
        <TareaForm
          editando={editando}
          columna={columnaForm}
          sprints={sprints}
          sprintActivo={sprintActivo}
          onClose={() => setMostrarForm(false)}
          onSaved={fetchTablero}
        />
      )}
    </div>
  )
}
