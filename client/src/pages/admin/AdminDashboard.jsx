import { useEffect, useState } from "react"
import api from "../../api/axios"

export default function AdminDashboard() {
  // stats empieza en null para distinguir "aún cargando" de "array vacío",
  // así podemos mostrar un estado de carga inicial mientras llegan los datos.
  const [stats, setStats] = useState(null)
  const [error, setError] = useState("")

  // El array de dependencias vacío asegura que la petición se ejecute una sola vez
  // al montar el componente, no en cada renderizado.
  // Usamos .then().catch() en lugar de async/await porque es una sola petición
  // simple; así evitamos el patrón (async () => { ... })() dentro del useEffect,
  // que es menos legible para un caso tan breve.
  useEffect(() => {
    api.get("/admin/stats").then((res) => setStats(res.data)).catch(() => setError("Error al cargar estadisticas"))
  }, [])

  // Evaluamos primero el error, luego la carga, y por último el contenido:
  // este orden evita que un error se enmascare tras un estado intermedio y
  // permite que cada estado tenga su propio render sin anidar condicionales.
  if (error) return <div className="admin-dashboard"><p className="alert alert-error">{error}</p></div>
  if (!stats) return <div className="admin-dashboard"><p>Cargando...</p></div>

  return (
    <div className="admin-dashboard">
      <h1>Dashboard</h1>

      {/* Las cards muestran métricas clave de un vistazo (KPIs); al ser pocos
          números, una card es más escaneable que una tabla. Debajo, en tabs,
          van los desgloses detallados que requieren más contexto. */}
      <div className="stats-grid">
        <div className="stats-card">
          <span className="stats-num">{stats.total_empresas}</span>
          <span className="stats-label">Empresas</span>
        </div>
        <div className="stats-card">
          <span className="stats-num">{stats.total_usuarios}</span>
          <span className="stats-label">Usuarios</span>
        </div>
        <div className="stats-card">
          <span className="stats-num">{stats.empresas_sin_web}</span>
          <span className="stats-label">Empresas sin web</span>
        </div>
        <div className="stats-card">
          <span className="stats-num">{stats.tickets_ultimo_mes}</span>
          <span className="stats-label">Tickets (30d)</span>
        </div>
      </div>

      {/* Las tablas anidadas muestran desgloses con pares clave/valor; usamos
          tablas en vez de cards porque son datos estructurados con muchas filas
          y el formato tabular permite comparar valores verticalmente. */}
      <div className="stats-detalle">
        <div className="stats-tabla">
          <h3>Usuarios por rol</h3>
          <table>
            <thead><tr><th>Rol</th><th>Total</th></tr></thead>
            <tbody>
              {stats.usuarios_por_rol.map((r) => (
                <tr key={r.clave}><td>{r.clave}</td><td>{r.total}</td></tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="stats-tabla">
          <h3>Tickets por estado</h3>
          <table>
            <thead><tr><th>Estado</th><th>Total</th></tr></thead>
            <tbody>
              {stats.tickets_por_estado.map((r) => (
                <tr key={r.clave}><td>{r.clave}</td><td>{r.total}</td></tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="stats-tabla">
          <h3>Tareas por columna</h3>
          <table>
            <thead><tr><th>Columna</th><th>Total</th></tr></thead>
            <tbody>
              {stats.tareas_por_columna.map((r) => (
                <tr key={r.clave}><td>{r.clave}</td><td>{r.total}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
