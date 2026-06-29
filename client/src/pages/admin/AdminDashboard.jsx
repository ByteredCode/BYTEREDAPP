import { useEffect, useState } from "react"
import api from "../../api/axios"

export default function AdminDashboard() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState("")

  useEffect(() => {
    api.get("/admin/stats").then((res) => setStats(res.data)).catch(() => setError("Error al cargar estadisticas"))
  }, [])

  if (error) return <div className="admin-dashboard"><p className="alert alert-error">{error}</p></div>
  if (!stats) return <div className="admin-dashboard"><p>Cargando...</p></div>

  return (
    <div className="admin-dashboard">
      <h1>Dashboard</h1>

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
          <span className="stats-num">{stats.fichajes_abiertos}</span>
          <span className="stats-label">Fichajes abiertos</span>
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
