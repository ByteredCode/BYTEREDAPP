import { useState, useEffect, useCallback } from "react"
import api from "../../api/axios"
import { useToast } from "../../context/ToastContext"

// Modal para gestionar permisos de acceso a un documento
// Recibe el doc como prop para evitar tener que volver a buscarlo del backend
export default function PermisosDoc({ doc, onClose, onUpdated }) {
  const { showToast } = useToast()
  const [permisos, setPermisos] = useState([])
  // Almacenamos el ID como string y lo convertimos a número solo al enviar,
  // así el input type="number" no da problemas con valores vacíos
  const [nuevoId, setNuevoId] = useState("")

  // La dependencia es doc.id_documento (no doc completo) para que
  // la referencia se recalcule solo cuando cambie el ID real,
  // no cuando el padre re-cree el objeto doc por otros motivos
  const fetchPermisos = useCallback(async () => {
    try {
      const res = await api.get(`/documentos/${doc.id_documento}/permisos`)
      setPermisos(res.data)
    } catch {
      // El catch vacío evita ruido en consola si el usuario cierra el modal
      // justo cuando la petición está en curso
    }
  }, [doc.id_documento])

  useEffect(() => { fetchPermisos() }, [fetchPermisos])

  async function agregar() {
    // No permitimos enviar IDs vacíos; la validación extra del backend
    // atraparía igualmente el error, pero evitamos una llamada innecesaria
    if (!nuevoId) return
    try {
      // Convertimos a número porque la BD almacena el usuario como entero
      // y la API espera el tipo correcto en el body
      await api.post(`/documentos/${doc.id_documento}/permisos`, { codigo_usuario: Number(nuevoId) })
      setNuevoId("")
      fetchPermisos()
    } catch (err) {
      showToast(err.response?.data?.detail || "Error al añadir permiso")
    }
  }

  // No pedimos confirmación aquí porque la acción tiene botón dedicado
  // y el modal ya representa una operación delicada (gestión de permisos)
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
