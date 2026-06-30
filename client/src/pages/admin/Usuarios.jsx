import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import api from "../../api/axios"
import { useAuth } from "../../context/AuthContext"
import Pagination from "../../components/common/Pagination"

const LIMITE = 50

export default function Usuarios() {
  const { usuario } = useAuth()
  const [usuarios, setUsuarios] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState("")
  const [pagina, setPagina] = useState(1)
  const [total, setTotal] = useState(0)

  useEffect(() => {
    const esAdminTotal = usuario?.rol === "admin_total"
    const skip = (pagina - 1) * LIMITE
    const params = `?skip=${skip}&limit=${LIMITE}`
    const urlBase = esAdminTotal
      ? "/admin/usuarios"
      : `/admin/empresas/${usuario.codigo_empresa}/usuarios`

    api
      .get(urlBase + params)
      .then((res) => {
        setUsuarios(res.data.items)
        setTotal(res.data.total)
      })
      .catch((err) => {
        setError(err.response?.data?.detalle || "Error al cargar usuarios")
      })
      .finally(() => setCargando(false))
  }, [usuario, pagina])

  async function eliminarUsuario(id) {
    if (!confirm("¿Eliminar usuario? Esta accion no se puede deshacer.")) return
    try {
      await api.delete(`/admin/usuarios/${id}`)
      setUsuarios(usuarios.filter((u) => u.codigo_usuario !== id))
    } catch (err) {
      setError(err.response?.data?.detail || "Error al eliminar usuario")
    }
  }

  if (cargando) return <p className="cargando">Cargando usuarios...</p>
  if (error) return <p className="error">{error}</p>

  return (
    <div className="pagina-admin">
      <div className="pagina-admin-header">
        <h1>Usuarios</h1>
        {/* Usamos Link en vez de button porque queremos navegación SPA sin recargar la página */}
        <Link to="/admin/usuarios/nueva" className="btn btn-primario">
          Nuevo usuario
        </Link>
      </div>

        {usuarios.length === 0 ? (
        // Mensaje vacío para evitar renderizar una tabla sin filas (mejor accesibilidad que una tabla vacía)
        <p className="sin-datos">No hay usuarios registrados.</p>
      ) : (
        // Tabla HTML semántica porque es datos tabulares; permite screen readers y estilos predecibles
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
              // Usamos codigo_usuario como key porque es único y evita re-renderizados innecesarios
              <tr key={user.codigo_usuario}>
                <td>{user.codigo_usuario}</td>
                <td>{user.correo}</td>
                <td>{user.nombre}</td>
                <td>{user.rol}</td>
                <td>{user.codigo_empresa || "-"}</td>
                <td className="acciones">
                  <Link to={`/admin/usuarios/${user.codigo_usuario}/editar`} className="btn btn-secundario btn-sm">Editar</Link>
                  <button className="btn-danger btn-sm" onClick={() => eliminarUsuario(user.codigo_usuario)}>Eliminar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <Pagination pagina={pagina} totalPaginas={Math.ceil(total / LIMITE)} total={total} onCambiarPagina={setPagina} />
    </div>
  )
}
