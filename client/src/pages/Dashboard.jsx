import { Link } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

// useAuth expone el usuario logueado desde el contexto; así cualquier componente hijo
// puede acceder a rol, nombre y empresa sin tener que parsear el JWT manualmente.
// El Dashboard actúa como hub de navegación: desde aquí el usuario accede
// a los distintos módulos protegidos. No se renderiza si no hay sesión activa
// porque el layout principal (App.jsx) ya verifica la autenticación antes.
export default function Dashboard() {
  // usuario se obtiene del contexto de autenticación; contiene los datos del JWT
  // (nombre, rol, empresa) que determinan qué módulos están disponibles.
  const { usuario } = useAuth()

  return (
    <div className="dashboard">
      <h1>Panel de control</h1>
      {/* Optional chaining (?.) porque usuario puede ser null si el contexto
          aún no se ha inicializado (ej. refresco de página con JWT expirado). */}
      <p>Bienvenido, {usuario?.nombre}</p>

      <div className="dashboard-modulos">
        {/* Cada tarjeta es un Link de React Router para navegación SPA sin recarga */}
        <Link to="/mi-empresa" className="modulo-card">
          <h3>Mi Empresa</h3>
          <p>Datos corporativos</p>
        </Link>
        <Link to="/scrum/tablero" className="modulo-card">
          <h3>Scrum</h3>
          <p>Tablero Kanban y sprints</p>
        </Link>
        <Link to="/tickets/nuevo" className="modulo-card">
          <h3>Ticket de soporte</h3>
          <p>Enviar incidencia</p>
        </Link>
        {usuario?.rol === "admin_total" && (
          <Link to="/fichajes" className="modulo-card">
            <h3>Fichajes</h3>
            <p>Control horario</p>
          </Link>
        )}
        {/* Los enlaces a /admin/* son rutas protegidas; el backend también
            valida el rol, pero filtrar la UI evita que usuarios no-admin
            vean siquiera la opción (defense in depth). */}
        <Link to="/admin/tickets" className="modulo-card">
          <h3>Tickets</h3>
          <p>Gestión de incidencias</p>
        </Link>
        <Link to="/admin/documentos" className="modulo-card">
          <h3>Documentos</h3>
          <p>DPD / ISO</p>
        </Link>
        {/* La card de Administración solo se muestra si el rol empieza por "admin".
            Se usa startsWith para cubrir variantes como "admin_total", "admin_empresa", etc. */}
        {usuario?.rol?.startsWith("admin") && (
          <Link to="/admin/empresas" className="modulo-card">
            <h3>Administración</h3>
            <p>Empresas, usuarios y servicios</p>
          </Link>
        )}
      </div>
    </div>
  )
}
