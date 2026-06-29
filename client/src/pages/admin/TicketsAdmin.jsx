import { useState, useEffect, useCallback } from "react"
import api from "../../api/axios"
import { useToast } from "../../context/ToastContext"

const ESTADOS = ["Pendiente", "Leido", "Respondido", "Cerrado"]
const IMPORTANCIA_CLASE = { Baja: "prioridad-baja", Media: "prioridad-media", Alta: "prioridad-alta", Critica: "prioridad-critica" }

export default function TicketsAdmin() {
  const { showToast } = useToast()
  const [tickets, setTickets] = useState([])
  const [detalle, setDetalle] = useState(null)
  const [respuesta, setRespuesta] = useState("")

  const fetchTickets = useCallback(async () => {
    try {
      const res = await api.get("/tickets")
      setTickets(res.data)
    } catch {
      // ignore
    }
  }, [])

  useEffect(() => { fetchTickets() }, [fetchTickets])

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

  function abrirDetalle(t) {
    setDetalle(t)
    setRespuesta("")
  }

  return (
    <div className="pagina-admin">
      <div className="pagina-admin-header">
        <h1>Tickets de soporte</h1>
      </div>

      {detalle && (
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
                <button className="btn-secundario btn-sm" onClick={() => abrirDetalle(t)}>Ver</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
