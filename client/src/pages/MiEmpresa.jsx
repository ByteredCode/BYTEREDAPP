import { useEffect, useState } from "react"
import { useAuth } from "../context/AuthContext"
import api from "../api/axios"

export default function MiEmpresa() {
  const { usuario } = useAuth()
  const [empresa, setEmpresa] = useState(null)
  const [editando, setEditando] = useState(false)
  const [nombre, setNombre] = useState("")
  const [web, setWeb] = useState("")
  const [error, setError] = useState("")
  const puedeEditar = usuario?.rol?.startsWith("admin")

  useEffect(() => {
    api.get("/empresa/mi-empresa").then((res) => {
      setEmpresa(res.data)
      setNombre(res.data.nombre)
      setWeb(res.data.web || "")
    }).catch(() => setError("Error al cargar datos de la empresa"))
  }, [])

  async function guardar(e) {
    e.preventDefault()
    setError("")
    try {
      const res = await api.patch("/empresa/mi-empresa", { nombre, web })
      setEmpresa(res.data)
      setEditando(false)
    } catch {
      setError("Error al guardar los cambios")
    }
  }

  if (!empresa) {
    return <div className="empresa-portal"><p>Cargando...</p></div>
  }

  return (
    <div className="empresa-portal">
      <h1>Mi Empresa</h1>

      {error && <div className="alert alert-error">{error}</div>}

      {editando ? (
        <form onSubmit={guardar} className="empresa-form">
          <label>
            Nombre
            <input value={nombre} onChange={(e) => setNombre(e.target.value)} required />
          </label>
          <label>
            Sitio web
            <input value={web} onChange={(e) => setWeb(e.target.value)} placeholder="https://" />
          </label>
          <div className="form-actions">
            <button type="submit" className="btn">Guardar</button>
            <button type="button" className="btn btn-secundario" onClick={() => setEditando(false)}>Cancelar</button>
          </div>
        </form>
      ) : (
        <div className="empresa-info">
          <p><strong>Nombre:</strong> {empresa.nombre}</p>
          <p><strong>Código:</strong> {empresa.codigo_empresa}</p>
          <p><strong>Sitio web:</strong> {empresa.web || "—"}</p>
          {puedeEditar && (
            <button className="btn" onClick={() => setEditando(true)}>Editar</button>
          )}
        </div>
      )}
    </div>
  )
}
