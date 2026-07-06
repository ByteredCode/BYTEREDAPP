import { useState, useEffect } from "react"
import api from "../../api/axios"
import { useToast } from "../../context/ToastContext"
import { useAuth } from "../../context/AuthContext"

// Arrays fijos para los select del formulario; se definen fuera del componente
// para que no se recree la referencia en cada renderizado
const PRIORIDADES = ["Baja", "Media", "Alta", "Critica"]
const COLUMNAS = [
  { id: "Todo", label: "Por hacer" },
  { id: "Haciendose", label: "En proceso" },
  { id: "En revision", label: "En revisión" },
  { id: "Done", label: "Terminado" },
]

// Modal de formulario para crear/editar tareas; recibe la tarea a editar (o null),
// la columna por defecto, la lista de sprints y callbacks para notificar cambios
export default function TareaForm({ editando, columna, sprints, sprintActivo, onClose, onSaved }) {
  const { showToast } = useToast()
  const { usuario } = useAuth()
  const [usuarios, setUsuarios] = useState([])

  useEffect(() => {
    let cancel = false
    async function cargarUsuarios() {
      try {
        const res = await api.get("/empresa/mi-empresa/usuarios")
        if (!cancel) setUsuarios(res.data)
      } catch {
        try {
          const res = await api.get("/admin/usuarios", { params: { limit: 200 } })
          if (!cancel) setUsuarios(res.data.items || res.data)
        } catch {
          if (usuario?.codigo_empresa) {
            try {
              const res = await api.get(`/admin/empresas/${usuario.codigo_empresa}/usuarios`, { params: { limit: 200 } })
              if (!cancel) setUsuarios(res.data.items || res.data)
            } catch { /* silent */ }
          }
        }
      }
    }
    cargarUsuarios()
    return () => { cancel = true }
  }, [usuario])
  // Inicializamos el formulario con los datos de la tarea a editar (si existe)
  // o con valores por defecto. Usamos || en vez de ?? porque queremos tratar
  // los strings vacíos igual que undefined (ej. fecha_limite "")
  const [form, setForm] = useState({
    titulo: editando?.titulo || "",
    descripcion: editando?.descripcion || "",
    prioridad: editando?.prioridad || "Media",
    columna: editando?.columna || columna || "Todo",
    fecha_limite: editando?.fecha_limite || "",
    asignacion: editando?.asignacion || "",
    codigo_sprint: editando?.codigo_sprint || sprintActivo || "",
  })

  async function guardar(e) {
    e.preventDefault()
    try {
      const payload = { ...form }
      // El backend espera null explícito para campos opcionales vacíos;
      // si enviamos string vacío, la BD almacenaría '' en lugar de NULL
      if (!payload.fecha_limite) payload.fecha_limite = null
      if (!payload.asignacion) payload.asignacion = null
      else payload.asignacion = Number(payload.asignacion)
      if (!payload.codigo_sprint) payload.codigo_sprint = null
      if (!payload.descripcion) payload.descripcion = null

      if (editando) {
        await api.put(`/scrum/tareas/${editando.codigo_tarea}`, payload)
      } else {
        await api.post("/scrum/tareas", payload)
      }
      // onSaved() refresca el tablero para reflejar la nueva tarea sin recargar la página
      onSaved()
      onClose()
    } catch (err) {
      showToast(err.response?.data?.detail || "Error al guardar tarea")
    }
  }

  return (
    // El overlay cierra el modal al hacer click fuera;
    // stopPropagation en el modal evita que el click en el formulario lo cierre
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>{editando ? "Editar tarea" : "Nueva tarea"}</h3>
        <form onSubmit={guardar}>
          <div className="campo">
            <label>Título</label>
            <input value={form.titulo} onChange={(e) => setForm({ ...form, titulo: e.target.value })} required />
          </div>
          <div className="campo">
            <label>Descripción</label>
            <textarea value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} />
          </div>
          <div className="campo-row">
            <div className="campo">
              <label>Prioridad</label>
              <select value={form.prioridad} onChange={(e) => setForm({ ...form, prioridad: e.target.value })}>
                {PRIORIDADES.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            <div className="campo">
              <label>Columna</label>
              <select value={form.columna} onChange={(e) => setForm({ ...form, columna: e.target.value })}>
                {COLUMNAS.map((c) => <option key={c.id} value={c.id}>{c.label}</option>)}
              </select>
            </div>
          </div>
          <div className="campo-row">
            <div className="campo">
              <label>Fecha límite</label>
              <input type="date" value={form.fecha_limite} onChange={(e) => setForm({ ...form, fecha_limite: e.target.value })} />
            </div>
            <div className="campo">
              <label>Asignado a</label>
              <select value={form.asignacion} onChange={(e) => setForm({ ...form, asignacion: e.target.value })}>
                <option value="">Sin asignar</option>
                {usuarios.map((u) => (
                  <option key={u.codigo_usuario} value={u.codigo_usuario}>{u.nombre}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="campo">
            <label>Sprint</label>
            <select value={form.codigo_sprint} onChange={(e) => setForm({ ...form, codigo_sprint: e.target.value })}>
              <option value="">Sin sprint</option>
              {sprints.map((s) => (
                <option key={s.codigo_sprint} value={s.codigo_sprint}>{s.nombre}</option>
              ))}
            </select>
          </div>
          <div className="modal-acciones">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
            <button type="submit" className="btn-primary">Guardar</button>
          </div>
        </form>
      </div>
    </div>
  )
}
