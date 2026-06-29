import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import api from "../../api/axios"

export default function EmpresaForm() {
  const { id } = useParams()
  const navigate = useNavigate()
  const esEdicion = Boolean(id)

  const [nombre, setNombre] = useState("")
  const [web, setWeb] = useState("")
  const [cargando, setCargando] = useState(esEdicion)
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    if (!id) return
    api
      .get(`/admin/empresas/${id}`)
      .then((res) => {
        setNombre(res.data.nombre || "")
        setWeb(res.data.web || "")
      })
      .catch((err) => {
        setError(err.response?.data?.detalle || "Error al cargar empresa")
      })
      .finally(() => setCargando(false))
  }, [id])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!nombre.trim()) {
      setError("El nombre es obligatorio")
      return
    }
    setEnviando(true)
    setError("")

    try {
      const datos = { nombre: nombre.trim(), web: web.trim() || null }
      if (esEdicion) {
        await api.put(`/admin/empresas/${id}`, datos)
      } else {
        await api.post("/admin/empresas", datos)
      }
      navigate("/admin/empresas")
    } catch (err) {
      setError(err.response?.data?.detalle || "Error al guardar empresa")
    } finally {
      setEnviando(false)
    }
  }

  if (cargando) return <p className="cargando">Cargando empresa...</p>

  return (
    <div className="pagina-admin">
      <h1>{esEdicion ? "Editar empresa" : "Nueva empresa"}</h1>

      {error && <p className="error">{error}</p>}

      <form onSubmit={handleSubmit} className="form-admin">
        <div className="form-campo">
          <label htmlFor="nombre">Nombre *</label>
          <input
            id="nombre"
            type="text"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            required
            placeholder="Nombre de la empresa"
          />
        </div>

        <div className="form-campo">
          <label htmlFor="web">Web</label>
          <input
            id="web"
            type="url"
            value={web}
            onChange={(e) => setWeb(e.target.value)}
            placeholder="https://ejemplo.com"
          />
        </div>

        <div className="form-acciones">
          <button
            type="button"
            className="btn btn-secundario"
            onClick={() => navigate("/admin/empresas")}
          >
            Volver
          </button>
          <button
            type="submit"
            className="btn btn-primario"
            disabled={enviando}
          >
            {enviando
              ? "Guardando..."
              : esEdicion
                ? "Actualizar empresa"
                : "Crear empresa"}
          </button>
        </div>
      </form>
    </div>
  )
}
