import { useState, useEffect, useCallback } from "react"
import api from "../../api/axios"
import { useToast } from "../../context/ToastContext"
import { useAuth } from "../../context/AuthContext"
import LoadingSpinner from "../../components/common/LoadingSpinner"
import Pagination from "../../components/common/Pagination"

// El ciclo de vida del ticket sigue un orden lógico (Pendiente → Leido → Respondido → Cerrado);
// esta constante centraliza los estados válidos para que coincidan frontend y backend
const ESTADOS = ["Pendiente", "Leido", "Respondido", "Cerrado"]
// Mapeo directo de nivel de importancia a clase CSS; al ser un objeto fuera del componente evitamos recrearlo en cada render
const IMPORTANCIA_CLASE = { Baja: "prioridad-baja", Media: "prioridad-media", Alta: "prioridad-alta", Critica: "prioridad-critica" }

export default function TicketsAdmin() {
  const { showToast } = useToast()
  const { usuario } = useAuth()
  const esAdminTotal = usuario?.rol === "admin_total"
  const [tickets, setTickets] = useState([])
  const [detalle, setDetalle] = useState(null)
  const [respuesta, setRespuesta] = useState("")
  const [cargando, setCargando] = useState(true)
  const [pagina, setPagina] = useState(1)
  const [totalPaginas, setTotalPaginas] = useState(1)

  const fetchTickets = useCallback(async () => {
    setCargando(true)
    try {
      const res = await api.get("/tickets", { params: { skip: (pagina - 1) * 50, limit: 50 } })
      setTickets(res.data.items)
      setTotalPaginas(Math.ceil(res.data.total / 50) || 1)
    } catch {
    } finally {
      setCargando(false)
    }
  }, [pagina])

  // El efecto depende de fetchTickets (que es estable por useCallback), así que solo se ejecuta al montar el componente
  useEffect(() => { fetchTickets() }, [fetchTickets])

  // Enviamos estado y respuesta en un solo PUT para que el backend haga una transacción atómica;
  // si el admin escribe una respuesta, el estado pasa automáticamente a "Respondido" en el backend
  async function cambiarEstado(id, estado) {
    try {
      const body = { estado }
      if (respuesta) body.respuesta = respuesta
      await api.put(`/tickets/${id}/estado`, body)
      setRespuesta("")
      fetchTickets()
    } catch (err) {
      showToast(err.response?.data?.detail || "Error al cambiar estado")
    }
  }

  // Al abrir un ticket guardamos el objeto completo en detalle para usarlo como "tienda local" del modal,
  // y reseteamos la respuesta para que el textarea empiece limpio
  function abrirDetalle(t) {
    setDetalle(t)
    setRespuesta("")
  }

  async function eliminarTicket(id) {
    if (!confirm("¿Eliminar este ticket? Esta acción no se puede deshacer.")) return
    try {
      await api.delete(`/tickets/${id}`)
      showToast("Ticket eliminado")
      setDetalle(null)
      fetchTickets()
    } catch (err) {
      showToast(err.response?.data?.detail || "Error al eliminar ticket")
    }
  }

  if (cargando) return <LoadingSpinner mensaje="Cargando tickets..." />

  return (
    <div className="pagina-admin">
      <div className="pagina-admin-header">
        <h1>Tickets de soporte</h1>
      </div>

      {/* El modal se muestra condicionalmente: si detalle es null no existe en el DOM, evitando problemas de tabulación y accesibilidad */}
      {detalle && (
        // El overlay oscuro cierra el modal al hacer clic fuera (UX estándar); stopPropagation en el modal evita que el clic interno cierre
        <div className="modal-overlay" onClick={() => setDetalle(null)}>
          <div className="modal modal-lg" onClick={(e) => e.stopPropagation()}>
            <h3>Ticket #{detalle.id_reporte}</h3>
            <div className="ticket-detalle">
              <div className="ticket-detalle-campo">
                <strong>Asunto:</strong> {detalle.asunto || "Sin asunto"}
              </div>
              <div className="ticket-detalle-campo">
                <strong>De:</strong> {detalle.nombre_contacto || "Anónimo"} {detalle.correo_contacto && `(${detalle.correo_contacto})`}
              </div>
              <div className="ticket-detalle-campo">
                <strong>Importancia:</strong> <span className={`prioridad-badge ${IMPORTANCIA_CLASE[detalle.nivel_importancia] || ""}`}>{detalle.nivel_importancia}</span>
              </div>
              <div className="ticket-detalle-campo">
                <strong>Estado:</strong> {detalle.estado}
              </div>
              <div className="ticket-detalle-campo">
                <strong>Fecha:</strong> {detalle.fecha_reporte ? new Date(detalle.fecha_reporte).toLocaleString() : ""}
              </div>
              <div className="ticket-detalle-campo">
                <strong>Usuario ID:</strong> {detalle.codigo_usuario || "No autenticado"}
              </div>
              <div className="ticket-detalle-mensaje">
                <strong>Mensaje:</strong>
                <p>{detalle.mensaje}</p>
              </div>

              {detalle.respuesta && (
                <div className="ticket-detalle-respuesta">
                  <strong>Respuesta:</strong>
                  <p>{detalle.respuesta}</p>
                  <small>{detalle.fecha_respuesta ? new Date(detalle.fecha_respuesta).toLocaleString() : ""}</small>
                </div>
              )}

              <div className="modal-acciones">
                <select
                  value={detalle.estado}
                  onChange={(e) => {
                    const nuevoEstado = e.target.value
                    cambiarEstado(detalle.id_reporte, nuevoEstado)
                    // Optimistic update: actualizamos el estado local del modal inmediatamente sin esperar la respuesta del servidor
                    setDetalle({ ...detalle, estado: nuevoEstado })
                  }}
                >
                  {ESTADOS.map((e) => <option key={e} value={e}>{e}</option>)}
                </select>
              </div>

              <div className="ticket-respuesta-area">
                <strong>Responder:</strong>
                <textarea
                  value={respuesta}
                  onChange={(e) => setRespuesta(e.target.value)}
                  placeholder="Escribe una respuesta..."
                  rows={4}
                />
                <button
                  className="btn btn-sm"
                  disabled={!respuesta.trim()}
                  onClick={() => {
                    cambiarEstado(detalle.id_reporte, "Respondido")
                    setDetalle({ ...detalle, estado: "Respondido", respuesta, fecha_respuesta: new Date().toISOString() })
                  }}
                >
                  Enviar respuesta
                </button>
              </div>
            </div>
            <div className="modal-acciones">
              {esAdminTotal && (
                <button className="btn-danger btn-sm" onClick={() => eliminarTicket(detalle.id_reporte)}>Eliminar ticket</button>
              )}
              <button className="btn-secondary" onClick={() => setDetalle(null)}>Cerrar</button>
            </div>
          </div>
        </div>
      )}

      <table className="tabla-admin">
        <thead>
          <tr>
            <th>#</th>
            <th>Asunto</th>
            <th>De</th>
            <th>Importancia</th>
            <th>Estado</th>
            <th>Fecha</th>
            <th>Acción</th>
          </tr>
        </thead>
        <tbody>
          {/* colSpan="7" porque la tabla tiene 7 columnas; así el mensaje ocupa todo el ancho en vez de aparecer en una sola celda */}
          {tickets.length === 0 && (
            <tr><td colSpan="7" className="sin-datos">No hay tickets</td></tr>
          )}
          {tickets.map((t) => (
            <tr key={t.id_reporte}>
              <td>{t.id_reporte}</td>
              <td>{t.asunto || "Sin asunto"}</td>
              <td>{t.nombre_contacto || `Usuario #${t.codigo_usuario || "—"}`}</td>
              <td><span className={`prioridad-badge ${IMPORTANCIA_CLASE[t.nivel_importancia] || ""}`}>{t.nivel_importancia}</span></td>
              <td>{t.estado}</td>
              <td>{t.fecha_reporte ? new Date(t.fecha_reporte).toLocaleDateString() : ""}</td>
              <td>
                <div className="acciones">
                  <button className="btn-secundario btn-sm" onClick={() => abrirDetalle(t)}>Ver</button>
                  {esAdminTotal && (
                    <button className="btn-danger btn-sm" onClick={() => eliminarTicket(t.id_reporte)}>Eliminar</button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination pagina={pagina} totalPaginas={totalPaginas} onPaginaChange={setPagina} />
    </div>
  )
}
