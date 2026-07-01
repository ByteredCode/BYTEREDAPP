// Usamos @dnd-kit en lugar de HTML5 Drag & Drop nativo porque:
// - Permite un DragOverlay personalizado que sigue al cursor
// - PointerSensor evita que clicks accidentales activen el drag
// - SortableContext maneja el reordenamiento interno de cada columna
import { useState, useEffect, useCallback, useMemo } from "react"
import { DndContext, DragOverlay, PointerSensor, useSensor, useSensors } from "@dnd-kit/core"
import { SortableContext, useSortable, verticalListSortingStrategy } from "@dnd-kit/sortable"
import { CSS } from "@dnd-kit/utilities"
import api from "../../api/axios"
import { useAuth } from "../../context/AuthContext"
import LoadingSpinner from "../../components/common/LoadingSpinner"
import TareaForm from "./TareaForm"

// Las 4 columnas clásicas de Kanban. Separamos id (clave técnica en la BD)
// de titulo (texto visible en español) para poder cambiar los nombres
// sin afectar la lógica del backend ni el mapeo de datos
const COLUMNAS = [
  { id: "Todo", titulo: "Por hacer" },
  { id: "Haciendose", titulo: "En proceso" },
  { id: "En revision", titulo: "En revisión" },
  { id: "Done", titulo: "Terminado" },
]

// Cada tarjeta es un componente independiente con su propio hook useSortable.
// Lo separamos de Columna para que React solo re-renderice la tarjeta que se
// está arrastrando, no todas las tarjetas del tablero
function SortableCard({ tarea, onClick, usuarioMap }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: tarea.codigo_tarea,
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,  // Efecto fantasma durante el arrastre
  }

  const prioridadClase = `prioridad-${tarea.prioridad?.toLowerCase() || "media"}`

  // setNodeRef, attributes y listeners son inyectados por useSortable y son obligatorios:
  // - setNodeRef vincula este nodo DOM al sistema de detección de @dnd-kit
  // - attributes añade los atributos ARIA necesarios para accesibilidad
  // - listeners captura los eventos de puntero/ratón para iniciar el arrastre
  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners} className="kanban-card" onClick={() => onClick(tarea)}>
      <div className="kanban-card-titulo">{tarea.titulo}</div>
      <div className="kanban-card-meta">
        <span className={`prioridad-badge ${prioridadClase}`}>{tarea.prioridad || "Media"}</span>
        {tarea.fecha_limite && <span className="fecha-limite">{tarea.fecha_limite}</span>}
      </div>
      {tarea.asignacion && <div className="kanban-card-asignacion">{usuarioMap?.[tarea.asignacion] || `#${tarea.asignacion}`}</div>}
    </div>
  )
}

// Vista previa que sigue al cursor durante el arrastre (DragOverlay)
// @dnd-kit necesita un componente separado para el overlay porque
// la tarjeta original se vuelve transparente (opacity 0.4) y el overlay
// es el que realmente se ve moviendose con el cursor
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
// SortableContext envuelve cada columna individualmente para que @dnd-kit
// sepa que las tarjetas solo se reordenan dentro de su propia columna
// (no se pueden mezclar entre columnas a nivel de lista, el cambio de columna
// se maneja en handleDragEnd)
function Columna({ id, titulo, tareas, onAgregar, onEditar, usuarioMap }) {
  // SortableContext necesita un array plano de identificadores para gestionar
  // el orden interno de la columna; extraemos solo los IDs de las tareas
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
            <SortableCard key={tarea.codigo_tarea} tarea={tarea} onClick={() => onEditar(tarea)} usuarioMap={usuarioMap} />
          ))}
        </div>
      </SortableContext>
    </div>
  )
}

export default function Board() {
  // columnas es un objeto indexado por el id de cada columna para acceso directo:
  // columnas["Todo"], columnas["Done"], etc. La estructura refleja la respuesta del backend.
  const [columnas, setColumnas] = useState({ Todo: [], Haciendose: [], "En revision": [], Done: [] })
  const [sprints, setSprints] = useState([])
  const [sprintActivo, setSprintActivo] = useState("")
  const [activeId, setActiveId] = useState(null)  // ID de la tarea siendo arrastrada (para el DragOverlay)
  const [mostrarForm, setMostrarForm] = useState(false)
  const [editando, setEditando] = useState(null)
  const [columnaForm, setColumnaForm] = useState("Todo")  // Columna preseleccionada al crear tarea
  const [cargando, setCargando] = useState(true)
  const { usuario } = useAuth()
  const [usuarios, setUsuarios] = useState([])
  const [filtroUsuario, setFiltroUsuario] = useState("")

  // PointerSensor con distance:5 para que un click normal NO inicie el drag.
  // El usuario debe mover el ratón al menos 5px para que se active el arrastre,
  // evitando falsos positivos al seleccionar texto o hacer click rápido
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }))

  // useCallback evita que la función se recre en cada render, rompiendo la
  // dependencia de useEffect y provocando un bucle infinito de peticiones
  const fetchTablero = useCallback(async () => {
    try {
      const params = sprintActivo ? { codigo_sprint: Number(sprintActivo) } : {}
      const res = await api.get("/scrum/tablero", { params })
      setColumnas(res.data)
    } catch {
      // Error silencioso intencionado: fetchTablero también se usa en el catch del
      // optimistic update para hacer rollback; si el rollback falla, no queremos otra alerta
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
    try {
      const res = await api.get("/empresa/mi-empresa/usuarios")
      setUsuarios(res.data)
    } catch {
      try {
        const res = await api.get("/admin/usuarios", { params: { limit: 200 } })
        setUsuarios(res.data.items || res.data)
      } catch {
        if (usuario?.codigo_empresa) {
          try {
            const res = await api.get(`/admin/empresas/${usuario.codigo_empresa}/usuarios`, { params: { limit: 200 } })
            setUsuarios(res.data.items || res.data)
          } catch { /* silent */ }
        }
      }
    }
  }, [usuario])

  useEffect(() => { fetchTablero() }, [fetchTablero])
  useEffect(() => { fetchSprints() }, [fetchSprints])
  useEffect(() => { fetchUsuarios() }, [fetchUsuarios])

  // Aplanamos el objeto columnas en un único array para poder buscar tareas
  // por ID en una sola pasada en vez de iterar columna por columna.
  // useMemo evita recalcularlo si columnas no ha cambiado entre renders
  const todasLasTareas = useMemo(() => {
    return Object.values(columnas).flat()
  }, [columnas])

  // Tarea actualmente arrastrada: se obtiene del listado aplanado y se pasa
  // a DragOverlay para mostrar la vista previa que sigue al cursor
  const activeTarea = useMemo(() => {
    return todasLasTareas.find((t) => t.codigo_tarea === activeId)
  }, [todasLasTareas, activeId])

  // Mapa de codigo_usuario -> nombre para mostrar el nombre en las tarjetas
  // en vez del ID numerico
  const usuarioMap = useMemo(() => {
    const map = {}
    usuarios.forEach((u) => { map[u.codigo_usuario] = u.nombre })
    return map
  }, [usuarios])

  // Filtro por usuario: si hay un usuario seleccionado, filtramos las tareas
  // de cada columna por su asignacion. El filtro es solo visual; el drag & drop
  // y el resto de la lógica interna siguen usando el conjunto completo de datos.
  const columnasFiltradas = useMemo(() => {
    if (!filtroUsuario) return columnas
    const usuarioNum = Number(filtroUsuario)
    const filtradas = {}
    for (const [colId, tareas] of Object.entries(columnas)) {
      filtradas[colId] = tareas.filter((t) => t.asignacion === usuarioNum)
    }
    return filtradas
  }, [columnas, filtroUsuario])

  // Guardamos el ID de la tarea al empezar el arrastre para:
  // 1) Mostrar el DragOverlay con los datos de la tarea mientras se mueve
  // 2) Poder identificar qué tarea movieron cuando termine el arrastre
  function handleDragStart(event) {
    setActiveId(event.active.id)
  }

  async function handleDragEnd(event) {
    const { active, over } = event
    setActiveId(null)
    // Si el usuario suelta la tarjeta fuera de cualquier zona de soltado (columna o tarjeta),
    // cancelamos el movimiento: @dnd-kit dispara dragEnd incluso si se suelta en área vacía
    if (!over) return

    const tareaId = active.id
    let columnaDestino = null
    let nuevoOrden = 0

    // @dnd-kit nos dice en over.id sobre qué elemento se soltó la tarjeta.
    // Pueden darse dos casos:
    // 1) Se soltó sobre una columna (el área vacía) → añadimos al final de esa columna
    // 2) Se soltó sobre otra tarjeta → insertamos justo en la posición de esa tarjeta
    if (COLUMNAS.some((c) => c.id === over.id)) {
      columnaDestino = over.id
      nuevoOrden = columnas[over.id]?.length || 0
    } else {
      const tareaOver = todasLasTareas.find((t) => t.codigo_tarea === over.id)
      if (!tareaOver) return
      columnaDestino = tareaOver.columna
      // findIndex nos da la posición de la tarjeta sobre la que soltamos
      nuevoOrden = columnas[columnaDestino]?.findIndex((t) => t.codigo_tarea === over.id)
      if (nuevoOrden === -1) nuevoOrden = columnas[columnaDestino]?.length || 0
    }

    if (!columnaDestino) return

    const tareaMovida = todasLasTareas.find((t) => t.codigo_tarea === tareaId)
    if (!tareaMovida) return

    // Si la tarea no cambió de columna ni de posición, evitamos una llamada API innecesaria
    if (tareaMovida.columna === columnaDestino && tareaMovida.orden === nuevoOrden) return

    // --- OPTIMISTIC UPDATE ---
    // Actualizamos el estado local INMEDIATAMENTE para que el usuario vea el cambio
    // sin esperar la respuesta del servidor. Si la API falla, hacemos rollback.
    const nuevas = { ...columnas }
    // 1. Quitamos la tarea de su columna de origen
    for (const col of Object.keys(nuevas)) {
      nuevas[col] = nuevas[col].filter((t) => t.codigo_tarea !== tareaId)
    }
    // 2. Insertamos la tarea en la posición correcta de la columna destino
    const itemActualizado = { ...tareaMovida, columna: columnaDestino, orden: nuevoOrden }
    nuevas[columnaDestino].splice(nuevoOrden, 0, itemActualizado)
    // 3. Reasignamos el orden secuencial para que no haya huecos (0, 1, 2, 3...)
    nuevas[columnaDestino] = nuevas[columnaDestino].map((t, i) => ({ ...t, orden: i }))
    setColumnas(nuevas)

    try {
      await api.put(`/scrum/tareas/${tareaId}/mover`, { columna: columnaDestino, orden: itemActualizado.orden })
    } catch {
      fetchTablero()  // Si la API falla, recargamos el estado desde el servidor (rollback)
    }
  }

  // Al crear: limpiamos editando (modo "nueva tarea") y pre-seleccionamos la columna
  // donde el usuario pulsó el botón "+"
  function abrirForm(columna) {
    setColumnaForm(columna)
    setEditando(null)
    setMostrarForm(true)
  }

  // Al editar: pasamos la tarea completa para que TareaForm inicialice el formulario
  // con los valores actuales (modo "editar tarea")
  function editarTarea(tarea) {
    setColumnaForm(tarea.columna)
    setEditando(tarea)
    setMostrarForm(true)
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
    </div>
  )
}
