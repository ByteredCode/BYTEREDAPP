import { useState } from "react"
import api from "../../api/axios"

const PRIORIDADES = ["Baja", "Media", "Alta", "Critica"]
const COLUMNAS = ["Todo", "Haciendose", "En revision", "Done"]

// Modal de formulario para crear/editar tareas
export default function TareaForm({ editando, columna, sprints, sprintActivo, onClose, onSaved }) {
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
      // Limpiar campos vacios para que el backend los interprete como null
      if (!payload.fecha_limite) payload.fecha_limite = null
      if (!payload.asignacion) payload.asignacion = null
      if (!payload.codigo_sprint) payload.codigo_sprint = null
      if (!payload.descripcion) payload.descripcion = null

      if (editando) {
        await api.put(`/scrum/tareas/${editando.codigo_tarea}`, payload)
      } else {
        await api.post("/scrum/tareas", payload)
      }
      onSaved()  // Recargar el tablero despues de guardar
      onClose()
    } catch (err) {
      alert("Error: " + (err.response?.data?.detail || err.message))
    }
  }

  return (
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
                {COLUMNAS.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
          </div>
          <div className="campo-row">
            <div className="campo">
              <label>Fecha límite</label>
              <input type="date" value={form.fecha_limite} onChange={(e) => setForm({ ...form, fecha_limite: e.target.value })} />
            </div>
            <div className="campo">
              <label>Asignado a (ID usuario)</label>
              <input type="number" value={form.asignacion} onChange={(e) => setForm({ ...form, asignacion: e.target.value })} />
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
