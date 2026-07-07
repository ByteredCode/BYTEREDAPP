import { useState, useEffect, useCallback, useMemo } from "react"
import { DndContext, DragOverlay, PointerSensor, useDroppable, useSensor, useSensors } from "@dnd-kit/core"
import { SortableContext, useSortable, verticalListSortingStrategy } from "@dnd-kit/sortable"
import { CSS } from "@dnd-kit/utilities"
import api from "../../api/axios"
import { useAuth } from "../../context/AuthContext"
import { useToast } from "../../context/ToastContext"
import LoadingSpinner from "../../components/common/LoadingSpinner"
import TareaForm from "./TareaForm"

const COLUMNAS = [
  { id: "Todo", titulo: "Por hacer" },
  { id: "Haciendose", titulo: "En proceso" },
  { id: "En revision", titulo: "En revisión" },
  { id: "Done", titulo: "Terminado" },
]

function SortableCard({ tarea, onClick, usuarioMap }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: tarea.codigo_tarea,
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  }

  const prioridadClase = `prioridad-${tarea.prioridad?.toLowerCase() || "media"}`

  return (
    <div ref={setNodeRef} style={style} className="kanban-card" {...attributes} {...listeners}>
      <div className="kanban-card-content" onClick={() => onClick(tarea)}>
        <div className="kanban-card-titulo">{tarea.titulo}</div>
        <div className="kanban-card-meta">
          <span className={`prioridad-badge ${prioridadClase}`}>{tarea.prioridad || "Media"}</span>
          {tarea.fecha_limite && <span className="fecha-limite">{tarea.fecha_limite}</span>}
        </div>
        {tarea.asignacion && <div className="kanban-card-asignacion">{usuarioMap?.[tarea.asignacion] || `#${tarea.asignacion}`}</div>}
      </div>
    </div>
  )
}

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

function Columna({ id, titulo, tareas, onAgregar, onEditar, onEliminarFinalizadas, usuarioMap }) {
  const { setNodeRef, isOver } = useDroppable({ id })
  const ids = tareas.map((t) => t.codigo_tarea)
  const esDone = id === "Done"

  return (
    <div className="kanban-columna">
      <div className="kanban-columna-header">
        <h3>{titulo}</h3>
        <span className="kanban-count">{tareas.length}</span>
        {esDone && tareas.length > 0 && (
          <button className="btn-eliminar-finalizadas" onClick={onEliminarFinalizadas} title="Eliminar todas las tareas finalizadas">
            Eliminar finalizadas
          </button>
        )}
        <button className="btn-add-tarea" onClick={onAgregar} title="Agregar tarea">+</button>
      </div>
      <SortableContext items={ids} strategy={verticalListSortingStrategy}>
        <div ref={setNodeRef} className={`kanban-columna-body${isOver ? " kanban-columna-over" : ""}`}>
          {tareas.map((tarea) => (
            <SortableCard key={tarea.codigo_tarea} tarea={tarea} onClick={() => onEditar(tarea)} usuarioMap={usuarioMap} />
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
  const [activeId, setActiveId] = useState(null)
  const [mostrarForm, setMostrarForm] = useState(false)
  const [editando, setEditando] = useState(null)
  const [columnaForm, setColumnaForm] = useState("Todo")
  const [cargando, setCargando] = useState(true)
  const { usuario } = useAuth()
  const { success, error: toastError } = useToast()
  const [usuarios, setUsuarios] = useState([])
  const [filtroUsuario, setFiltroUsuario] = useState("")
  const [mostrarConfirmEliminar, setMostrarConfirmEliminar] = useState(false)

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }))

  const fetchTablero = useCallback(async () => {
    try {
      const params = sprintActivo ? { codigo_sprint: Number(sprintActivo) } : {}
      const res = await api.get("/scrum/tablero", { params })
      setColumnas(res.data)
    } catch {
      // silent
    } finally {
      setCargando(false)
    }
  }, [sprintActivo])

  const fetchSprints = useCallback(async () => {
    try {
      const res = await api.get("/scrum/sprints")
      setSprints(res.data.items || res.data)
    } catch {
      // ignore
    }
  }, [])

  const fetchUsuarios = useCallback(async () => {
    const intentos = [
      api.get("/empresa/mi-empresa/usuarios").then(r => r.data),
      api.get("/admin/usuarios", { params: { limit: 200 } }).then(r => r.data.items || r.data),
      usuario?.codigo_empresa
        ? api.get(`/admin/empresas/${usuario.codigo_empresa}/usuarios`, { params: { limit: 200 } }).then(r => r.data.items || r.data)
        : Promise.reject(),
    ]
    const resultados = await Promise.allSettled(intentos)
    const exitoso = resultados.find(r => r.status === "fulfilled")
    if (exitoso) setUsuarios(exitoso.value)
  }, [usuario])

  useEffect(() => { fetchTablero() }, [fetchTablero])
  useEffect(() => { fetchSprints() }, [fetchSprints])
  useEffect(() => { fetchUsuarios() }, [fetchUsuarios])

  const todasLasTareas = useMemo(() => Object.values(columnas).flat(), [columnas])
  const activeTarea = useMemo(() => todasLasTareas.find((t) => t.codigo_tarea === activeId), [todasLasTareas, activeId])

  const usuarioMap = useMemo(() => {
    const map = {}
    usuarios.forEach((u) => { map[u.codigo_usuario] = u.nombre })
    return map
  }, [usuarios])

  const columnasFiltradas = useMemo(() => {
    if (!filtroUsuario) return columnas
    const usuarioNum = Number(filtroUsuario)
    const filtradas = {}
    for (const [colId, tareas] of Object.entries(columnas)) {
      filtradas[colId] = tareas.filter((t) => t.asignacion === usuarioNum)
    }
    return filtradas
  }, [columnas, filtroUsuario])

  const tareasFinalizadas = useMemo(() => columnas.Done || [], [columnas])

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
      fetchTablero()
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

  async function eliminarFinalizadas() {
    const tareas = tareasFinalizadas
    if (tareas.length === 0) return
    let eliminadas = 0
    for (const t of tareas) {
      try {
        await api.delete(`/scrum/tareas/${t.codigo_tarea}`)
        eliminadas++
      } catch {
        // continue with next
      }
    }
    setMostrarConfirmEliminar(false)
    success(`${eliminadas} tarea${eliminadas !== 1 ? "s" : ""} eliminada${eliminadas !== 1 ? "s" : ""}`)
    fetchTablero()
  }

  if (cargando) return <LoadingSpinner mensaje="Cargando tablero..." />

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
          <select value={filtroUsuario} onChange={(e) => setFiltroUsuario(e.target.value)}>
            <option value="">Todos los usuarios</option>
            {usuarios.map((u) => (
              <option key={u.codigo_usuario} value={u.codigo_usuario}>{u.nombre}</option>
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
              tareas={columnasFiltradas[col.id] || []}
              onAgregar={() => abrirForm(col.id)}
              onEditar={editarTarea}
              onEliminarFinalizadas={() => setMostrarConfirmEliminar(true)}
              usuarioMap={usuarioMap}
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

      {mostrarConfirmEliminar && (
        <div className="modal-overlay" onClick={() => setMostrarConfirmEliminar(false)}>
          <div className="modal-content modal-confirm" onClick={(e) => e.stopPropagation()}>
            <h3>Eliminar tareas finalizadas</h3>
            <p>Se eliminaran <strong>{tareasFinalizadas.length}</strong> tarea{tareasFinalizadas.length !== 1 ? "s" : ""} de la columna "Terminado".</p>
            <div className="modal-actions">
              <button className="btn-secundario" onClick={() => setMostrarConfirmEliminar(false)}>Cancelar</button>
              <button className="btn-peligro" onClick={eliminarFinalizadas}>Eliminar {tareasFinalizadas.length} tarea{tareasFinalizadas.length !== 1 ? "s" : ""}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
