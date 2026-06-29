import { NavLink, Outlet } from "react-router-dom"
import { useAuth } from "../../context/AuthContext"

// Layout de administracion con sidebar de navegacion
export default function AdminLayout() {
  const { usuario } = useAuth()

  return (
    <div className="admin-layout">
      <aside className="admin-sidebar">
        <h2 className="admin-sidebar-titulo">Administracion</h2>
        <nav className="admin-sidebar-nav">
          {/* Solo admin_total ve el enlace a Empresas */}
          {usuario?.rol === "admin_total" && (
            <NavLink to="/admin/empresas" className="admin-sidebar-link">
              Empresas
            </NavLink>
          )}
          <NavLink to="/admin/usuarios" className="admin-sidebar-link">
            Usuarios
          </NavLink>
          <NavLink to="/admin/tickets" className="admin-sidebar-link">
            Tickets
          </NavLink>
          <NavLink to="/admin/documentos" className="admin-sidebar-link">
            Documentos
          </NavLink>
        </nav>
      </aside>
      <main className="admin-content">
        <Outlet />
      </main>
    </div>
  )
}
