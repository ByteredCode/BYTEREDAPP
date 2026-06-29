import { useState, useEffect, useCallback } from "react"
import api from "../../api/axios"

const ESTADOS = ["Pendiente", "Leido", "Respondido", "Cerrado"]
const IMPORTANCIA_CLASE = { Baja: "prioridad-baja", Media: "prioridad-media", Alta: "prioridad-alta", Critica: "prioridad-critica" }

// Administracion de tickets: listado + modal detalle + cambio de estado
export default function TicketsAdmin() {
  const [tickets, setTickets] = useState([])
  const [detalle, setDetalle] = useState(null)

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
      await api.put(`/tickets/${id}/estado`, { estado })
      fetchTickets()
    } catch (err) {
      alert("Error: " + (err.response?.data?.detail || err.message))
    }
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
                <button className="btn-secundario btn-sm" onClick={() => setDetalle(t)}>Ver</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
