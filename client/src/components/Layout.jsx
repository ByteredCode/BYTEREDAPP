import { Link, Outlet, useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

// Layout principal: Outlet renderiza las rutas hijas, el nav solo aparece si hay sesión activa
export default function Layout() {
  // `useAuth` expone el usuario logueado y la función logout desde el contexto global
  const { usuario, logout } = useAuth()
  const navigate = useNavigate()

  // Separamos el cierre de sesión en una función propia para navegar al login justo después del logout
  function cerrarSesion() {
    logout()
    navigate("/login")
  }

  return (
    <div>
      {/* Sin usuario no tiene sentido mostrar la navegación; se oculta en páginas públicas como el login */}
      {usuario && (
        <nav className="nav-principal">
          <div className="nav-left">
            <Link to="/dashboard" className="nav-logo">BYTERED</Link>
            <Link to="/mi-empresa" className="nav-link">Mi Empresa</Link>
            <Link to="/scrum/tablero" className="nav-link">Scrum</Link>
            <Link to="/fichajes" className="nav-link">Fichajes</Link>
            <Link to="/tickets/nuevo" className="nav-link">Nuevo Ticket</Link>
            <Link to="/admin/tickets" className="nav-link">Tickets</Link>
            <Link to="/admin/documentos" className="nav-link">Documentos</Link>
            {/* startsWith("admin") cubre admin_total y admin_empresa sin duplicar condiciones */}
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
      {/* Outlet es el marcador de React Router donde se injecta la ruta hija activa */}
      <Outlet />
    </div>
  )
}
