import { useState, useEffect, useCallback } from "react"
import api from "../../api/axios"
import { useToast } from "../../context/ToastContext"

// Modal para gestionar permisos de acceso a un documento
export default function PermisosDoc({ doc, onClose, onUpdated }) {
  const { showToast } = useToast()
  const [permisos, setPermisos] = useState([])
  const [nuevoId, setNuevoId] = useState("")

  const fetchPermisos = useCallback(async () => {
    try {
      const res = await api.get(`/documentos/${doc.id_documento}/permisos`)
      setPermisos(res.data)
    } catch {
      // ignore
    }
  }, [doc.id_documento])

  useEffect(() => { fetchPermisos() }, [fetchPermisos])

  async function agregar() {
    if (!nuevoId) return
    try {
      await api.post(`/documentos/${doc.id_documento}/permisos`, { codigo_usuario: Number(nuevoId) })
      setNuevoId("")
      fetchPermisos()
    } catch (err) {
      showToast(err.response?.data?.detail || "Error al añadir permiso")
    }
  }

  async function quitar(userId) {
    try {
      await api.delete(`/documentos/${doc.id_documento}/permisos/${userId}`)
      fetchPermisos()
    } catch (err) {
      showToast(err.response?.data?.detail || "Error al quitar permiso")
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal modal-lg" onClick={(e) => e.stopPropagation()}>
        <h3>Permisos: {doc.nombre}</h3>

        <div className="permisos-agregar">
          <input
            type="number"
            placeholder="ID de usuario"
            value={nuevoId}
            onChange={(e) => setNuevoId(e.target.value)}
          />
          <button className="btn-primary btn-sm" onClick={agregar}>Añadir</button>
        </div>

        <table className="tabla-admin" style={{ marginTop: "1rem" }}>
          <thead>
            <tr><th>Usuario ID</th><th>Acción</th></tr>
          </thead>
          <tbody>
            {permisos.length === 0 && <tr><td colSpan="2" className="sin-datos">Sin permisos adicionales</td></tr>}
            {permisos.map((p) => (
              <tr key={p.codigo_usuario}>
                <td>#{p.codigo_usuario}</td>
                <td>
                  <button className="btn-danger btn-sm" onClick={() => quitar(p.codigo_usuario)}>Quitar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="modal-acciones">
          <button className="btn-secondary" onClick={onClose}>Cerrar</button>
        </div>
      </div>
    </div>
  )
}
