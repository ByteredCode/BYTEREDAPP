import { Link, Outlet, useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

// Layout principal: barra de navegacion + contenido con Outlet
export default function Layout() {
  const { usuario, logout } = useAuth()
  const navigate = useNavigate()

  function cerrarSesion() {
    logout()
    navigate("/login")
  }

  return (
    <div>
      {usuario && (
        <nav className="nav-principal">
          <div className="nav-left">
            <Link to="/dashboard" className="nav-logo">BYTERED</Link>
            <Link to="/mi-empresa" className="nav-link">Mi Empresa</Link>
            <Link to="/scrum/tablero" className="nav-link">Scrum</Link>
            <Link to="/fichajes" className="nav-link">Fichajes</Link>
            <Link to="/admin/tickets" className="nav-link">Tickets</Link>
            <Link to="/admin/documentos" className="nav-link">Documentos</Link>
            {usuario.rol?.startsWith("admin") && (
              <Link to="/admin/empresas" className="nav-link">Admin</Link>
            )}
          </div>
          <div className="nav-right">
            <span className="nav-usuario">{usuario.nombre}</span>
            <button className="btn-link" onClick={cerrarSesion}>Salir</button>
          </div>
        </nav>
      )}
      <Outlet />  {/* Aqui se renderizan las rutas hijas */}
    </div>
  )
}
