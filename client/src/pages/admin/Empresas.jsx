import { useEffect, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import api from "../../api/axios"
import { useToast } from "../../context/ToastContext"
import Pagination from "../../components/common/Pagination"

const LIMITE = 50

export default function Empresas() {
  const navigate = useNavigate()
  const { showToast } = useToast()
  const [empresas, setEmpresas] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState("")
  const [pagina, setPagina] = useState(1)
  const [total, setTotal] = useState(0)

  useEffect(() => {
    const skip = (pagina - 1) * LIMITE
    api
      .get(`/admin/empresas?skip=${skip}&limit=${LIMITE}`)
      .then((res) => {
        setEmpresas(res.data.items)
        setTotal(res.data.total)
      })
      .catch((err) => {
        setError(err.response?.data?.detalle || "Error al cargar empresas")
      })
      .finally(() => setCargando(false))
  }, [pagina])

  async function eliminarEmpresa(id) {
    if (!confirm("¿Eliminar empresa? Esta accion no se puede deshacer.")) return
    try {
      await api.delete(`/admin/empresas/${id}`)
      setEmpresas(empresas.filter((e) => e.codigo_empresa !== id))
    } catch (err) {
      setError(err.response?.data?.detail || "Error al eliminar empresa")
    }
  }

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
                <td>{empresa.web ? <a href={empresa.web} target="_blank" rel="noopener noreferrer">{empresa.web}</a> : "-"}</td>
                <td className="acciones">
                  <Link to={`/admin/empresas/${empresa.codigo_empresa}/editar`} className="btn btn-secundario btn-sm">Editar</Link>
                  <Link to={`/admin/empresas/${empresa.codigo_empresa}/servicios`} className="btn btn-secundario btn-sm">Servicios</Link>
                  <Link to={`/admin/empresas/${empresa.codigo_empresa}/usuarios`} className="btn btn-secundario btn-sm">Usuarios</Link>
                  <button className="btn-danger btn-sm" onClick={() => eliminarEmpresa(empresa.codigo_empresa)}>Eliminar</button>
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
