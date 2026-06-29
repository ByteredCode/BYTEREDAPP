import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import api from "../../api/axios"

export default function Empresas() {
  const [empresas, setEmpresas] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    api
      .get("/admin/empresas")
      .then((res) => setEmpresas(res.data))
      .catch((err) => {
        setError(err.response?.data?.detalle || "Error al cargar empresas")
      })
      .finally(() => setCargando(false))
  }, [])

  if (cargando) return <p className="cargando">Cargando empresas...</p>
  if (error) return <p className="error">{error}</p>

  return (
    <div className="pagina-admin">
      <div className="pagina-admin-header">
        <h1>Empresas</h1>
        <Link to="/admin/empresas/nueva" className="btn btn-primario">
          Nueva empresa
        </Link>
      </div>

      {empresas.length === 0 ? (
        <p className="sin-datos">No hay empresas registradas.</p>
      ) : (
        <table className="tabla-admin">
          <thead>
            <tr>
              <th>Codigo</th>
              <th>Nombre</th>
              <th>Web</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {empresas.map((empresa) => (
              <tr key={empresa.codigo_empresa}>
                <td>{empresa.codigo_empresa}</td>
                <td>{empresa.nombre}</td>
                <td>
                  {empresa.web ? (
                    <a
                      href={empresa.web}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {empresa.web}
                    </a>
                  ) : (
                    "-"
                  )}
                </td>
                <td className="acciones">
                  <Link
                    to={`/admin/empresas/${empresa.codigo_empresa}/editar`}
                    className="btn btn-secundario btn-sm"
                  >
                    Editar
                  </Link>
                  <Link
                    to={`/admin/empresas/${empresa.codigo_empresa}/servicios`}
                    className="btn btn-secundario btn-sm"
                  >
                    Servicios
                  </Link>
                  <Link
                    to={`/admin/empresas/${empresa.codigo_empresa}/usuarios`}
                    className="btn btn-secundario btn-sm"
                  >
                    Usuarios
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
