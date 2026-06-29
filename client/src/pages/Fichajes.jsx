import { useState, useEffect, useCallback } from "react"
import api from "../api/axios"

// Vista de fichajes: historial + boton para registrar salida
export default function Fichajes() {
  const [fichajes, setFichajes] = useState([])
  const [abierto, setAbierto] = useState(null)  // Fichaje actual (sin salida)

  // useCallback para evitar que se recree la funcion en cada render
  const fetchData = useCallback(async () => {
    try {
      // Carga paralela: historial y estado actual
      // Promise.allSettled no falla si una peticion da error (ej: no hay fichaje abierto)
      const [resFichajes, resActual] = await Promise.allSettled([
        api.get("/fichajes"),
        api.get("/fichajes/actual"),
      ])
      if (resFichajes.status === "fulfilled") setFichajes(resFichajes.value.data)
      if (resActual.status === "fulfilled") setAbierto(resActual.value.data)
      else setAbierto(null)
    } catch {
      // ignore
    }
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  async function ficharSalida() {
    try {
      await api.post("/fichajes/salida")
      fetchData()  // Recargar datos tras registrar salida
    } catch (err) {
      alert("Error: " + (err.response?.data?.detail || err.message))
    }
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
