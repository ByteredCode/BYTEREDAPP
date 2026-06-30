import { useState, useEffect, useCallback } from "react"
import api from "../../api/axios"
import { useToast } from "../../context/ToastContext"
import LoadingSpinner from "../../components/common/LoadingSpinner"
import Pagination from "../../components/common/Pagination"

// Los sprints solo transitan entre estos tres estados;
// el backend valida que no se asignen valores fuera de este conjunto
const ESTADOS = ["Planificado", "Activo", "Completado"]

// CRUD completo de sprints con modal de formulario y confirmación de borrado
export default function Sprints() {
  const { showToast } = useToast()
  const [sprints, setSprints] = useState([])
  const [mostrarForm, setMostrarForm] = useState(false)
  const [editando, setEditando] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [pagina, setPagina] = useState(1)
  const [totalPaginas, setTotalPaginas] = useState(1)
  const [form, setForm] = useState({ nombre: "", objetivo: "", fecha_inicio: "", fecha_fin: "", estado: "Planificado" })

  const fetchSprints = useCallback(async () => {
    setCargando(true)
    try {
      const res = await api.get("/scrum/sprints", { params: { skip: (pagina - 1) * 50, limit: 50 } })
      setSprints(res.data.items)
      setTotalPaginas(Math.ceil(res.data.total / 50) || 1)
    } catch {
    } finally {
      setCargando(false)
    }
  }, [pagina])

  useEffect(() => { fetchSprints() }, [fetchSprints])

  function abrirNuevo() {
    setEditando(null)
    setForm({ nombre: "", objetivo: "", fecha_inicio: "", fecha_fin: "", estado: "Planificado" })
    setMostrarForm(true)
  }

  function abrirEditar(s) {
    setEditando(s)
    setForm({
      nombre: s.nombre,
      objetivo: s.objetivo || "",
      fecha_inicio: s.fecha_inicio || "",
      fecha_fin: s.fecha_fin || "",
      estado: s.estado,
    })
    setMostrarForm(true)
  }

  async function guardar(e) {
    e.preventDefault()
    try {
      const payload = { ...form }
      // El backend espera null explícito para campos opcionales vacíos;
      // si enviamos string vacío, la BD almacenaría '' en lugar de NULL
      if (!payload.fecha_inicio) payload.fecha_inicio = null
      if (!payload.fecha_fin) payload.fecha_fin = null
      if (!payload.objetivo) payload.objetivo = null

      if (editando) {
        await api.put(`/scrum/sprints/${editando.codigo_sprint}`, payload)
      } else {
        await api.post("/scrum/sprints", payload)
      }
      setMostrarForm(false)
      fetchSprints()
    } catch (err) {
      showToast(err.response?.data?.detail || "Error al guardar sprint")
    }
  }

  // Usamos confirm() del navegador para evitar borrados accidentales;
  // es una alternativa ligera sin necesidad de un modal de confirmación personalizado
  async function eliminar(id) {
    if (!confirm("¿Eliminar sprint?")) return
    try {
      await api.delete(`/scrum/sprints/${id}`)
      fetchSprints()
    } catch (err) {
      showToast(err.response?.data?.detail || "Error al eliminar sprint")
    }
  }

  if (cargando) return <LoadingSpinner mensaje="Cargando sprints..." />

  return (
    <div className="scrum-sprints">
      <div className="sprints-header">
        <h2>Sprints</h2>
        <button className="btn-primary" onClick={abrirNuevo}>Nuevo sprint</button>
      </div>

      {mostrarForm && (
        // El overlay cierra el modal al hacer click fuera;
        // stopPropagation en el modal evita que el click dentro cierre el modal accidentalmente
        <div className="modal-overlay" onClick={() => setMostrarForm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>{editando ? "Editar sprint" : "Nuevo sprint"}</h3>
            <form onSubmit={guardar}>
              <div className="campo">
                <label>Nombre</label>
                <input value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} required />
              </div>
              <div className="campo">
                <label>Objetivo</label>
                <textarea value={form.objetivo} onChange={(e) => setForm({ ...form, objetivo: e.target.value })} />
              </div>
              <div className="campo-row">
                <div className="campo">
                  <label>Fecha inicio</label>
                  <input type="date" value={form.fecha_inicio} onChange={(e) => setForm({ ...form, fecha_inicio: e.target.value })} />
                </div>
                <div className="campo">
                  <label>Fecha fin</label>
                  <input type="date" value={form.fecha_fin} onChange={(e) => setForm({ ...form, fecha_fin: e.target.value })} />
                </div>
              </div>
              <div className="campo">
                <label>Estado</label>
                <select value={form.estado} onChange={(e) => setForm({ ...form, estado: e.target.value })}>
                  {ESTADOS.map((e) => <option key={e} value={e}>{e}</option>)}
                </select>
              </div>
              <div className="modal-acciones">
                <button type="button" className="btn-secondary" onClick={() => setMostrarForm(false)}>Cancelar</button>
                <button type="submit" className="btn-primary">Guardar</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="sprints-lista">
        {sprints.length === 0 && <p className="sin-datos">No hay sprints aún</p>}
        {sprints.map((s) => (
          <div key={s.codigo_sprint} className="sprint-card">
            <div className="sprint-info">
              <h4>{s.nombre}</h4>
              {s.objetivo && <p>{s.objetivo}</p>}
              <div className="sprint-fechas">
                {s.fecha_inicio && <span>Inicio: {s.fecha_inicio}</span>}
                {s.fecha_fin && <span>Fin: {s.fecha_fin}</span>}
              </div>
              <span className={`sprint-estado sprint-estado-${s.estado?.toLowerCase()}`}>{s.estado}</span>
            </div>
            <div className="sprint-acciones">
              <button className="btn-secondary" onClick={() => abrirEditar(s)}>Editar</button>
              <button className="btn-danger" onClick={() => eliminar(s.codigo_sprint)}>Eliminar</button>
            </div>
          </div>
        ))}
      </div>
      <Pagination pagina={pagina} totalPaginas={totalPaginas} onPaginaChange={setPagina} />
    </div>
  )
}
