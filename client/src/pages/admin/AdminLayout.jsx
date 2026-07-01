// Usamos NavLink en vez de Link para que React Router añada automáticamente
// la clase "active" al enlace que coincide con la ruta actual, facilitando el
// estilo visual de navegación sin tener que trackear la ruta manualmente.
import { NavLink, Outlet } from "react-router-dom"
import { useAuth } from "../../context/AuthContext"

// Layout de administracion con sidebar de navegacion
export default function AdminLayout() {
  // Obtenemos el usuario desde el contexto en vez de recibirlo por props para
  // evitar "prop drilling": el layout necesita el rol, pero ese dato lo gestiona
  // AuthContext, no el router ni la página padre.
  const { usuario } = useAuth()

  return (
    <div className="admin-layout">
      <aside className="admin-sidebar">
        <h2 className="admin-sidebar-titulo">Administracion</h2>
        <nav className="admin-sidebar-nav">
          {/* end evita que este enlace se marque como activo para TODAS las rutas
              que empiecen por /admin (ej. /admin/empresas). Sin end, el Dashboard
              aparecería resaltado siempre. */}
          <NavLink to="/admin" end className="admin-sidebar-link">
            Dashboard
          </NavLink>
          {/* Solo admin_total ve el enlace a Empresas */}
          {usuario?.rol === "admin_total" && (
            <NavLink to="/admin/empresas" className="admin-sidebar-link">
              Empresas
            </NavLink>
          )}
          {usuario?.rol === "admin_total" && (
            <NavLink to="/admin/usuarios" className="admin-sidebar-link">
              Usuarios
            </NavLink>
          )}
          <NavLink to="/admin/tickets" className="admin-sidebar-link">
            Tickets
          </NavLink>
          <NavLink to="/admin/documentos" className="admin-sidebar-link">
            Documentos
          </NavLink>
        </nav>
      </aside>
      <main className="admin-content">
        {/* Outlet renderiza aquí el hijo de la ruta anidada (Dashboard, Empresas, etc.)
            evitando tener que repetir el sidebar en cada página hija. */}
        <Outlet />
      </main>
    </div>
  )
}
