import { useEffect, useState } from "react"
import { Link, useParams, useNavigate } from "react-router-dom"
import api from "../../api/axios"

export default function EmpresaUsuarios() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [usuarios, setUsuarios] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState("")
  const [nombreEmpresa, setNombreEmpresa] = useState("")

  useEffect(() => {
    Promise.all([
      api.get(`/admin/empresas/${id}/usuarios`),
      api.get(`/admin/empresas/${id}`),
    ])
      .then(([resUsuarios, resEmpresa]) => {
        setUsuarios(resUsuarios.data)
        setNombreEmpresa(resEmpresa.data.nombre || "")
      })
      .catch((err) => {
        setError(
          err.response?.data?.detalle || "Error al cargar usuarios de la empresa"
        )
      })
      .finally(() => setCargando(false))
  }, [id])

  if (cargando) return <p className="cargando">Cargando usuarios...</p>
  if (error) return <p className="error">{error}</p>

  return (
    <div className="pagina-admin">
      <div className="pagina-admin-header">
        <div>
          <h1>Usuarios de {nombreEmpresa || `empresa #${id}`}</h1>
          <p className="subtitulo">Codigo de empresa: {id}</p>
        </div>
        <Link
          to={`/admin/usuarios/nueva?empresa=${id}`}
          className="btn btn-primario"
        >
          Nuevo usuario
        </Link>
      </div>

      <button
        type="button"
        className="btn btn-secundario btn-sm"
        onClick={() => navigate("/admin/empresas")}
        style={{ marginBottom: "1rem" }}
      >
        &larr; Volver a empresas
      </button>

      {usuarios.length === 0 ? (
        <p className="sin-datos">
          No hay usuarios en esta empresa.
        </p>
      ) : (
        <table className="tabla-admin">
          <thead>
            <tr>
              <th>ID</th>
              <th>Correo</th>
              <th>Nombre</th>
              <th>Rol</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {usuarios.map((user) => (
              <tr key={user.codigo_usuario}>
                <td>{user.codigo_usuario}</td>
                <td>{user.correo}</td>
                <td>{user.nombre}</td>
                <td>{user.rol}</td>
                <td className="acciones">
                  <Link
                    to={`/admin/usuarios/${user.codigo_usuario}/editar`}
                    className="btn btn-secundario btn-sm"
                  >
                    Editar
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
