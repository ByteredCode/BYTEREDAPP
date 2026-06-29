import { useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import api from "../../api/axios"

const SERVICIOS_DISPONIBLES = [
  { clave: "scrum", etiqueta: "Scrum" },
  { clave: "tickets", etiqueta: "Tickets" },
  { clave: "documentacion", etiqueta: "Documentacion DPD/ISO" },
  { clave: "fichaje", etiqueta: "Fichaje" },
  { clave: "redireccion", etiqueta: "Redireccion a web externa" },
]

export default function Servicios() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [servicios, setServicios] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState("")
  const [nombreEmpresa, setNombreEmpresa] = useState("")

  useEffect(() => {
    Promise.all([
      api.get(`/admin/empresas/${id}/servicios`),
      api.get(`/admin/empresas/${id}`),
    ])
      .then(([resServicios, resEmpresa]) => {
        setServicios(resServicios.data)
        setNombreEmpresa(resEmpresa.data.nombre || "")
      })
      .catch((err) => {
        setError(
          err.response?.data?.detalle || "Error al cargar servicios"
        )
      })
      .finally(() => setCargando(false))
  }, [id])

  const handleToggle = async (servicio, activo) => {
    try {
      await api.put(`/admin/empresas/${id}/servicios`, {
        servicio,
        activo,
      })
      setServicios((prev) =>
        prev.map((s) =>
          s.servicio === servicio ? { ...s, activo } : s
        )
      )
    } catch (err) {
      setError(
        err.response?.data?.detalle || "Error al actualizar servicio"
      )
    }
  }

  if (cargando) return <p className="cargando">Cargando servicios...</p>
  if (error) return <p className="error">{error}</p>

  const serviciosMap = {}
  servicios.forEach((s) => {
    serviciosMap[s.servicio] = s.activo
  })

  return (
    <div className="pagina-admin">
      <h1>Servicios de {nombreEmpresa || `empresa #${id}`}</h1>
      <p className="subtitulo">
        Activa o desactiva los servicios para esta empresa
      </p>

      <button
        type="button"
        className="btn btn-secundario btn-sm"
        onClick={() => navigate("/admin/empresas")}
        style={{ marginBottom: "1rem" }}
      >
        &larr; Volver a empresas
      </button>

      <div className="servicios-lista">
        {SERVICIOS_DISPONIBLES.map((s) => {
          const activo = serviciosMap[s.clave] === true
          return (
            <div key={s.clave} className="servicio-item">
              <span className="servicio-nombre">{s.etiqueta}</span>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={activo}
                  onChange={(e) => handleToggle(s.clave, e.target.checked)}
                />
                <span className="switch-slider"></span>
              </label>
              <span className={activo ? "estado-activo" : "estado-inactivo"}>
                {activo ? "Activado" : "Desactivado"}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
