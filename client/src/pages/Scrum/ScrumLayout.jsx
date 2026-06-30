import { NavLink, Outlet } from "react-router-dom"

// Layout tipo shell para las rutas hijas del módulo Scrum
// NavLink proporciona el booleano isActive, permitiendo aplicar la clase "activo"
// al tab correspondiente sin necesidad de lógica manual de detección de ruta
// Outlet es el mecanismo de React Router para renderizar la ruta hija (Board o Sprints)
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
