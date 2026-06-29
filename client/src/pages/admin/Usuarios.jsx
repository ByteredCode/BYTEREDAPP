import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import api from "../../api/axios"
import { useAuth } from "../../context/AuthContext"

export default function Usuarios() {
  const { usuario } = useAuth()
  const [usuarios, setUsuarios] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    const esAdminTotal = usuario?.rol === "admin_total"
    const url = esAdminTotal
      ? "/admin/usuarios"
      : `/admin/empresas/${usuario.codigo_empresa}/usuarios`

    api
      .get(url)
      .then((res) => setUsuarios(res.data))
      .catch((err) => {
        setError(err.response?.data?.detalle || "Error al cargar usuarios")
      })
      .finally(() => setCargando(false))
  }, [usuario])

  if (cargando) return <p className="cargando">Cargando usuarios...</p>
  if (error) return <p className="error">{error}</p>

  return (
    <div className="pagina-admin">
      <div className="pagina-admin-header">
        <h1>Usuarios</h1>
        <Link to="/admin/usuarios/nueva" className="btn btn-primario">
          Nuevo usuario
        </Link>
      </div>

      {usuarios.length === 0 ? (
        <p className="sin-datos">No hay usuarios registrados.</p>
      ) : (
        <table className="tabla-admin">
          <thead>
            <tr>
              <th>ID</th>
              <th>Correo</th>
              <th>Nombre</th>
              <th>Rol</th>
              <th>Empresa</th>
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
                <td>{user.codigo_empresa || "-"}</td>
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
