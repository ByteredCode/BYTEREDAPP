import { useState, useEffect, useCallback } from "react"
import api from "../../api/axios"
import PermisosDoc from "./PermisosDoc"

// Administracion de documentos: subida, listado, descarga, permisos, eliminacion
export default function DocumentosAdmin() {
  const [docs, setDocs] = useState([])
  const [mostrarSubida, setMostrarSubida] = useState(false)
  const [archivo, setArchivo] = useState(null)
  const [tipoDoc, setTipoDoc] = useState("")
  const [permisoDoc, setPermisoDoc] = useState(null)

  const fetchDocs = useCallback(async () => {
    try {
      const res = await api.get("/documentos")
      setDocs(res.data)
    } catch {
      // ignore
    }
  }, [])

  useEffect(() => { fetchDocs() }, [fetchDocs])

  async function subir(e) {
    e.preventDefault()
    if (!archivo) return
    try {
      const fd = new FormData()
      fd.append("archivo", archivo)
      if (tipoDoc) fd.append("tipo_documento", tipoDoc)
      // Importante: no establecer Content-Type manualmente para multipart
      await api.post("/documentos", fd, { headers: { "Content-Type": "multipart/form-data" } })
      setMostrarSubida(false)
      setArchivo(null)
      setTipoDoc("")
      fetchDocs()
    } catch (err) {
      alert("Error: " + (err.response?.data?.detail || err.message))
    }
  }

  async function eliminar(id) {
    if (!confirm("¿Eliminar documento?")) return
    try {
      await api.delete(`/documentos/${id}`)
      fetchDocs()
    } catch (err) {
      alert("Error: " + (err.response?.data?.detail || err.message))
    }
  }

  async function descargar(id) {
    try {
      // Descarga usando blob + ObjectURL para forzar descarga en el cliente
      const res = await api.get(`/documentos/${id}/descargar`, { responseType: "blob" })
      const url = URL.createObjectURL(res.data)
      const a = document.createElement("a")
      a.href = url
      a.download = ""
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      alert("Error al descargar")
    }
  }

  return (
    <div className="pagina-admin">
      <div className="pagina-admin-header">
        <h1>Documentos DPD/ISO</h1>
        <button className="btn-primary" onClick={() => setMostrarSubida(true)}>Subir documento</button>
      </div>

      {mostrarSubida && (
        <div className="modal-overlay" onClick={() => setMostrarSubida(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Subir documento</h3>
            <form onSubmit={subir}>
              <div className="campo">
                <label>Archivo</label>
                <input type="file" onChange={(e) => setArchivo(e.target.files[0])} required />
              </div>
              <div className="campo">
                <label>Tipo de documento</label>
                <select value={tipoDoc} onChange={(e) => setTipoDoc(e.target.value)}>
                  <option value="">Sin clasificar</option>
                  <option value="DPD">DPD</option>
                  <option value="ISO">ISO</option>
                </select>
              </div>
              <div className="modal-acciones">
                <button type="button" className="btn-secondary" onClick={() => setMostrarSubida(false)}>Cancelar</button>
                <button type="submit" className="btn-primary">Subir</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {permisoDoc && (
        <PermisosDoc doc={permisoDoc} onClose={() => setPermisoDoc(null)} onUpdated={fetchDocs} />
      )}

      <table className="tabla-admin">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Tipo</th>
            <th>Subido por</th>
            <th>Fecha</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {docs.length === 0 && <tr><td colSpan="5" className="sin-datos">No hay documentos</td></tr>}
          {docs.map((d) => (
            <tr key={d.id_documento}>
              <td>{d.nombre}</td>
              <td>{d.tipo_documento || "—"}</td>
              <td>#{d.usuario_subio}</td>
              <td>{d.fecha}</td>
              <td>
                <div className="acciones">
                  <button className="btn-secundario btn-sm" onClick={() => descargar(d.id_documento)}>Descargar</button>
                  <button className="btn-secundario btn-sm" onClick={() => setPermisoDoc(d)}>Permisos</button>
                  <button className="btn-danger btn-sm" onClick={() => eliminar(d.id_documento)}>Eliminar</button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
