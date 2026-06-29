import { NavLink, Outlet } from "react-router-dom"

// Layout con tabs de navegacion para el modulo Scrum
export default function ScrumLayout() {
  return (
    <div className="scrum-layout">
      <nav className="scrum-nav">
        <NavLink to="/scrum/tablero" className={({ isActive }) => isActive ? "activo" : ""}>
          Tablero
        </NavLink>
        <NavLink to="/scrum/sprints" className={({ isActive }) => isActive ? "activo" : ""}>
          Sprints
        </NavLink>
      </nav>
      <div className="scrum-content">
        <Outlet />  {/* Renderiza Board o Sprints segun la ruta */}
      </div>
    </div>
  )
}
