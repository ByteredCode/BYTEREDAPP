import { useState, useEffect } from "react"
import api from "../api/axios"
import { useAuth } from "../context/AuthContext"
import LoadingSpinner from "../components/common/LoadingSpinner"

export default function Fichajes() {
  const { usuario } = useAuth()
  const [grupos, setGrupos] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (usuario?.rol !== "admin_total") return
    api.get("/fichajes/por-empresa")
      .then((res) => setGrupos(res.data))
      .catch((err) => setError(err.response?.data?.detail || "Error al cargar fichajes"))
      .finally(() => setCargando(false))
  }, [usuario])

  function exportarCSV() {
    const base = api.defaults?.baseURL || ""
    window.open(base + "/fichajes/exportar", "_blank")
  }

  if (usuario?.rol !== "admin_total") {
    return (
      <div className="pagina-admin" style={{ maxWidth: 600, margin: "0 auto", textAlign: "center", paddingTop: "3rem" }}>
        <h2>Acceso restringido</h2>
        <p style={{ color: "var(--text-secondary)" }}>Solo el administrador principal puede ver los fichajes.</p>
      </div>
    )
  }

  if (cargando) return <LoadingSpinner mensaje="Cargando fichajes..." />

  return (
    <div className="pagina-admin" style={{ maxWidth: 1000, margin: "0 auto" }}>
      <div className="pagina-admin-header">
        <h1>Fichajes</h1>
        <button className="btn btn-sm" onClick={exportarCSV}>Exportar CSV</button>
      </div>

      {error && <div className="alerta-error">{error}</div>}

      {grupos.length === 0 && <p className="sin-datos">No hay fichajes registrados</p>}

      {grupos.map((g) => (
        <section key={g.codigo_empresa} className="grupo-fichajes">
          <h2 className="grupo-fichajes-titulo">{g.nombre_empresa}</h2>
          {g.fichajes.length === 0 ? (
            <p className="sin-datos" style={{ padding: "0.5rem 0" }}>Sin fichajes</p>
          ) : (
            <table className="tabla-admin">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Usuario</th>
                  <th>Entrada</th>
                  <th>Salida</th>
                  <th>Duración</th>
                </tr>
              </thead>
              <tbody>
                {g.fichajes.map((f) => {
                  const entrada = new Date(f.hora_entrada)
                  const salida = f.hora_salida ? new Date(f.hora_salida) : null
                  const duracion = salida
                    ? Math.round((salida - entrada) / 60000) + " min"
                    : "—"
                  return (
                    <tr key={f.id_fichaje}>
                      <td>{f.id_fichaje}</td>
                      <td>{f.usuario_nombre || `#${f.codigo_usuario}`}</td>
                      <td>{entrada.toLocaleString()}</td>
                      <td>{salida ? salida.toLocaleString() : "—"}</td>
                      <td>{duracion}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}
        </section>
      ))}
    </div>
  )
}
