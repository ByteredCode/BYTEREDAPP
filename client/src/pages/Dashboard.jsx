import { Link } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

// Pagina principal tras el login: muestra los modulos disponibles como tarjetas
export default function Dashboard() {
  const { usuario } = useAuth()

  return (
    <div className="dashboard">
      <h1>Panel de control</h1>
      <p>Bienvenido, {usuario?.nombre}</p>

      <div className="dashboard-modulos">
        <Link to="/scrum/tablero" className="modulo-card">
          <h3>Scrum</h3>
          <p>Tablero Kanban y sprints</p>
        </Link>
        <Link to="/tickets/nuevo" className="modulo-card">
          <h3>Ticket de soporte</h3>
          <p>Enviar incidencia</p>
        </Link>
        <Link to="/fichajes" className="modulo-card">
          <h3>Fichajes</h3>
          <p>Control horario</p>
        </Link>
        <Link to="/admin/tickets" className="modulo-card">
          <h3>Tickets</h3>
          <p>Gestión de incidencias</p>
        </Link>
        <Link to="/admin/documentos" className="modulo-card">
          <h3>Documentos</h3>
          <p>DPD / ISO</p>
        </Link>
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
