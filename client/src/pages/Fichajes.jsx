import { useState, useEffect, useCallback } from "react"
import api from "../api/axios"
import { useToast } from "../context/ToastContext"

export default function Fichajes() {
  const { showToast } = useToast()
  const [fichajes, setFichajes] = useState([])
  const [abierto, setAbierto] = useState(null)
  const [resumen, setResumen] = useState(null)

  const fetchData = useCallback(async () => {
    try {
      const [resFichajes, resActual, resResumen] = await Promise.allSettled([
        api.get("/fichajes"),
        api.get("/fichajes/actual"),
        api.get("/fichajes/resumen"),
      ])
      if (resFichajes.status === "fulfilled") setFichajes(resFichajes.value.data)
      if (resActual.status === "fulfilled") setAbierto(resActual.value.data)
      else setAbierto(null)
      if (resResumen.status === "fulfilled") setResumen(resResumen.value.data)
    } catch { /* ignore */ }
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  async function ficharSalida() {
    try {
      await api.post("/fichajes/salida")
      fetchData()
    } catch (err) {
      showToast(err.response?.data?.detail || err.message)
    }
  }

  function exportarCSV() {
    const url = api.defaults?.baseURL ? api.defaults.baseURL + "/fichajes/exportar" : "/api/v1/fichajes/exportar"
    window.open(url, "_blank")
  }

  return (
    <div className="pagina-admin">
      <div className="pagina-admin-header">
        <h1>Fichajes</h1>
        {abierto && (
          <div className="fichaje-abierto">
            <span>Abierto desde: {new Date(abierto.hora_entrada).toLocaleTimeString()}</span>
            <button className="btn-danger" onClick={ficharSalida}>Registrar salida</button>
          </div>
        )}
      </div>

      {resumen && (
        <div className="stats-grid fichajes-resumen">
          <div className="stats-card">
            <span className="stats-num">{resumen.horas_hoy}</span>
            <span className="stats-label">Horas hoy</span>
          </div>
          <div className="stats-card">
            <span className="stats-num">{resumen.horas_semana}</span>
            <span className="stats-label">Horas esta semana</span>
          </div>
          <div className="stats-card">
            <span className="stats-num">{resumen.horas_mes}</span>
            <span className="stats-label">Horas este mes</span>
          </div>
          <div className="stats-card">
            <span className="stats-num">{resumen.total_fichajes}</span>
            <span className="stats-label">Total fichajes</span>
          </div>
        </div>
      )}

      <div className="pagina-admin-header">
        <button className="btn btn-sm" onClick={exportarCSV}>Exportar CSV</button>
      </div>

      <table className="tabla-admin">
        <thead>
          <tr>
            <th>#</th>
            <th>Entrada</th>
            <th>Salida</th>
            <th>Duración</th>
          </tr>
        </thead>
        <tbody>
          {fichajes.length === 0 && <tr><td colSpan="4" className="sin-datos">Sin fichajes</td></tr>}
          {fichajes.map((f) => {
            const entrada = new Date(f.hora_entrada)
            const salida = f.hora_salida ? new Date(f.hora_salida) : null
            const duracion = salida ? Math.round((salida - entrada) / 60000) + " min" : "—"
            return (
              <tr key={f.id_fichaje}>
                <td>{f.id_fichaje}</td>
                <td>{entrada.toLocaleString()}</td>
                <td>{salida ? salida.toLocaleString() : "—"}</td>
                <td>{duracion}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
